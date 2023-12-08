import os
import asyncio
import json
import re
import warnings
from multiprocessing import Process
import concurrent.futures

import socket
import time

def perform_mathematical_calculations(data):
    # Выполнение реальных математических вычислений
    # Замените эту заглушку своей логикой
    return [{"qwe": 123}]

async def handle_connection(reader, writer):
    data_full = ''
    while True:
        try:
            data_part = await reader.read(100000)
        except ConnectionError:
            break
        if not data_part:
            break
        if data_part == b"close":
            break

        data_full = data_full + data_part.decode()
        match = re.search(r'\}\]', data_full)
        if match:
            data = json.loads(data_full)
            data_full = ''

            result = await asyncio.get_running_loop().run_in_executor(None, perform_mathematical_calculations, data)

            resp = json.dumps(result)
            resp = resp.encode()

            try:
                writer.write(resp)
                await writer.drain()
            except ConnectionError:
                break

    writer.close()

def run_handle_connection(reader, writer):
    asyncio.run(handle_connection(reader, writer))

async def run(reader, writer):
    print("New connection")
    loop = asyncio.get_event_loop()

    with concurrent.futures.ProcessPoolExecutor() as pool:
        await loop.run_in_executor(pool, run_handle_connection, reader, writer)

async def main(host, port):
    server = await asyncio.start_server(run, host, port)
    print(f"Start server {socket.gethostbyname(socket.gethostname())}...")

    pid = os.getpid()
    f = open("pid.pid", "w")
    f.write(f"{pid}")
    f.close()

    async with server:
        await server.serve_forever()

HOST = "0.0.0.0"
PORT = 11000

if __name__ == "__main__":
    asyncio.run(main(HOST, PORT))
