import asyncio
import sys
import struct

if sys.platform == "win32":
    import os, msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

class ExtensionClient:
    def __init__(self, port=6969):
        self.port = port
        self.queue = asyncio.Queue()

        self.writer = None
        self.reader = None

    async def connect(self):
        conn_failures = 0
        while conn_failures < 5:
            try:
                self.reader, self.writer = await asyncio.open_connection('127.0.0.1', self.port)
                return True
            except:
                conn_failures += 1
                await asyncio.sleep(0.1)
        return False

    async def run_tasks(self):
        tasks = []
        tasks.append(asyncio.create_task(self.read_message_chrome()))
        tasks.append(asyncio.create_task(self.send_message_bank()))
        tasks.append(asyncio.create_task(self.pass_message_bank()))

        for task in tasks:
            await task

    async def shutdown(self):
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except:
            pass
        sys.exit(1)

    def send_message_chrome(self, message):
        sys.stdout.write(struct.pack('I', len(message)).decode('utf-8'))
        sys.stdout.write(message)
        sys.stdout.flush()

    async def read_message_chrome(self):
        while True:
            msg_len_b = sys.stdin.read(4)

            if len(msg_len_b) == 0:
                queue.put(None)
                await self.shutdown()

            print("msg-len = {}".format(msg_len_b), file=sys.stderr)

            msg_len = struct.unpack('i', msg_len_b)[0]
            msg = sys.stdin.read(msg_len)

            self.queue.put(struct.pack('I', msg_len))
            self.queue.put(msg)

    async def pass_message_bank(self):
        while True:
            message = await self.reader.read()
            self.send_message_chrome(message.decode('utf-8'))

    async def send_message_bank(self):
        while True:
            message = await self.queue.get()
            writer.write(message)
            await writer.drain()


async def main():
    cli = ExtensionClient()
    if not await cli.connect():
        print('Unable to connect to server - aborting', file=sys.stderr)
        await cli.shutdown()
    await cli.run_tasks()
    await cli.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
