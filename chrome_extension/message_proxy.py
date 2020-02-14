#/usr/bin/env python3
import asyncio
import concurrent.futures
import struct
import sys


async def execute_read(nbytes) -> bytes:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, sys.stdin.buffer.read, nbytes)


async def execute_write(msg) -> None:
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, sys.stdout.buffer.write, msg)


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
        tasks.append(asyncio.create_task(self.bank_to_chrome()))

        for task in tasks:
            await task

    async def shutdown(self):
        try:
            self.writer.close()
            await self.writer.wait_closed()
        except:
            pass
        sys.exit(1)

    async def send_message_chrome(self, message):
        await execute_write(struct.pack('I', len(message)))
        await execute_write(message)
        sys.stdout.flush()

    async def read_message_chrome(self):
        while True:
            msg_len_b = await execute_read(4)

            if len(msg_len_b) == 0:
                await self.shutdown()

            msg_len = struct.unpack('i', msg_len_b)[0]
            print("msg-len = {} ({})".format(msg_len_b, msg_len), file=sys.stderr)
            msg = await execute_read(msg_len)
            print("msg = {}".format(msg), file=sys.stderr)

            await self.queue.put(struct.pack('I', msg_len))
            await self.queue.put(msg)

    async def bank_to_chrome(self):
        while True:
            message = await self.reader.read()
            await self.send_message_chrome(message)

    async def send_message_bank(self):
        while True:
            message = await self.queue.get()
            self.writer.write(message)
            await self.writer.drain()


async def main():
    cli = ExtensionClient()
    if not await cli.connect():
        print('Unable to connect to server - aborting', file=sys.stderr)
        await cli.shutdown()
    await cli.run_tasks()
    await cli.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
