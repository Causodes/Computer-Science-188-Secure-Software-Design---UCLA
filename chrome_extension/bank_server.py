import asyncio
import struct
import sys
import janus
import threading

class BankServer():
    """TCP server opened by Bank to listen for chome extension clients

    Automatically fills client_messages[cli_id] with messages from the client
    and sends messages from bank_messages[cli_id]

    Parameters
    ----------
    port : Union[str, int]
        Port number to serve on

    Attributes
    ----------
    port : Union[str, int]
        Port number serving on
    clients : Set[str]
        Set of strings of connected clients
    client_messages : Dict[str, janus.Queue[str]]
        Client id string to queue of messages from them
    bank_messages : Dict[str, janus.Queue[bytes]]
        Client id string to queue of messages to them
    """

    def __init__(self, port):
        self.port = port
        self.clients = set()
        self.clients_lock = threading.Lock()
        self.client_messages = {}
        self.bank_messages = {}

    async def run_server_forever(self):
        """Runs the server on localhost:port forever
        """
        server = await asyncio.start_server(
            self._handle_client, '127.0.0.1', self.port)

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}', file=sys.stderr, flush=True)

        async with server:
            await server.serve_forever()

    async def _handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        """Callback for asyncio.start_server() called for each client connected

        Parameters
        ----------
        reader : asyncio.StreamReader
            Client connection listener provided by asyncio.start_server()
        writer : asyncio.StreamWriter
            Client connection writer provided by asyncio.start_server()

        Returns
        -------
        None
        """

        cli_addr = writer.get_extra_info('peername')
        print(f'Client {cli_addr} joined', file=sys.stderr, flush=True)

        listening_queue = janus.Queue()
        writing_queue = janus.Queue()

        self.clients_lock.acquire()
        self.clients.add(cli_addr)
        self.client_messages[cli_addr] = listening_queue
        self.bank_messages[cli_addr] = writing_queue
        self.clients_lock.release()

        listening = asyncio.ensure_future(self._listen_client(reader, cli_addr))
        writing = asyncio.ensure_future(self._write_client(writer, cli_addr))

        await listening
        await writing_queue.async_q.put(None)
        await writing

        self.clients_lock.acquire()
        self.clients.remove(cli_addr)
        del self.client_messages[cli_addr]
        del self.bank_messages[cli_addr]
        self.clients_lock.release()

        print('returning from client callback', file=sys.stderr, flush=True)
        return True

    async def _listen_client(self, reader: asyncio.StreamReader, cli_addr: str) -> None:
        """Listens for messages on reader and puts in repsective client_messages queue

        Parameters
        ----------
        reader : asyncio.StreamReader
            Connection stream to listen to
        cli_addr : str
            ID of client to server
        """
        print('Starting listener', file=sys.stderr, flush=True)
        l_queue = self.client_messages[cli_addr]
        while True:
            msg_len_b = await reader.read(4)

            print(f'Message of size {msg_len_b} incoming', file=sys.stderr, flush=True)

            if msg_len_b == bytes():
                print(f'Client {cli_addr} disconnected', file=sys.stderr, flush=True)
                return

            msg_len = struct.unpack('i', msg_len_b)[0]
            text = (await reader.read(msg_len)).decode('utf-8')

            print(f'Received {text} from {cli_addr}', file=sys.stderr, flush=True)
            await l_queue.async_q.put(text)

    async def _write_client(self, writer: asyncio.StreamWriter, cli_addr: str) -> None:
        """Writes messages on writer from respective bank_messages queue

        Parameters
        ----------
        writer : asyncio.StreamWriter
            Connection stream to write to
        cli_addr : str
            ID of client to server
        """
        print('Starting writer', file=sys.stderr, flush=True)
        w_queue = self.bank_messages[cli_addr]
        while True:
            msg = await w_queue.async_q.get()

            print(f'Sending {msg} to {cli_addr}', file=sys.stderr, flush=True)

            if msg == None:
                print(f'Bank closing conn with {cli_addr}', file=sys.stderr, flush=True)
                writer.close()
                return

            writer.write(msg)
            await writer.drain()


async def main():
    server = BankServer(6969)
    clients = server.clients
    await server.run_server_forever()

if __name__ == '__main__':
    asyncio.run(main(), debug=True)
