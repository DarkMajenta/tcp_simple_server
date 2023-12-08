import os
import asyncio
import json
import re
import warnings
from multiprocessing import Process, Pool
import concurrent.futures
import socket
import time
import resource

async def handle_connection(reader, writer):
    # addr = writer.get_extra_info("peername")
    data_full = ''
    while True:
        # принимаем входные данные
        try:
            data_part = await reader.read(100000)  # New
        except ConnectionError:
            break
        if not data_part:
            break
        if data_part == b"close":
            break

        # накапливаем входные данные
        data_full = data_full + data_part.decode()
        # пока не получим конец json
        match = re.search(r'\}\]', data_full)
        if match:
            #start_time = round(time.time()*1000)

            # декодируем json
            data = json.loads(data_full)
            # обнуляем data_full для следующего сообщения
            data_full = ''

            '''
                мат.вычисления
            '''

            resp = '[{"qwe":123}]'  # формируем ответ
            # кодируем в байты
            resp = resp.encode()
            #print("json.dumps "+str(round(time.time()*1000)-start_time)+" ms")
            #start_time = round(time.time()*1000)

            try:
                writer.write(resp)  # отправляем ответ
                await writer.drain()
            except ConnectionError:
                #print(f"Client suddenly closed, cannot send")
                break
    writer.close()
    #print("Disconnected by", addr)

def run_multiprocess(reader, writer):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    asyncio.ensure_future(handle_connection(reader, writer))
    loop.run_forever()

async def run(reader, writer):
    print("new connection")
    # получение цикла событий
    loop = asyncio.get_event_loop()

    # Вариант с ProcessPoolExecutor
    with concurrent.futures.ProcessPoolExecutor() as pool:
        # выполнение функции в отдельном процессе
        await loop.run_in_executor(pool, run_multiprocess, reader, writer)


async def main(host, port):
    server = await asyncio.start_server(run, host, port)
    print(f"Start server {socket.gethostbyname(socket.gethostname())}...")

    # сохраняем PID процесса, чтоб можно было убить из консоли
    pid = os.getpid()
    with open("pid.pid", "w") as f:
        f.write(f"{pid}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    HOST = "192.168.1.111"
    PORT = 11000

    asyncio.run(main(HOST, PORT))
