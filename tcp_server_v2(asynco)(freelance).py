import os
import asyncio
import json
import re
import warnings
from multiprocessing import Process
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
            #print("json.loads "+str(round(time.time()*1000)-start_time)+" ms")
            #start_time = round(time.time()*1000)

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


def run_handle_connection(reader, writer):
    asyncio.run(handle_connection(reader, writer))


async def run(reader, writer):
    print("new connection")
    # получение цикла событий
    loop = asyncio.get_event_loop()

    # 1. вариант с потоками
    #await loop.run_in_executor(None, run_handle_connection, reader, writer)

    # Правка №1
    # Предыдущий вариант(оригинал)
    #     #2. вариант с ProcessPoolExecutor
    #with concurrent.futures.ProcessPoolExecutor() as pool:
        # выполнение функции в отдельном потоке
    #    await loop.run_in_executor(pool, run_handle_connection, reader, writer)

    # 2. вариант с ThreadPoolExecutor
    # ProcessPoolExecutor заменён на 'ThreadPoolExecutor', так как ограничение ресурсов памяти с multiprocessing может быть сложнее обрабатывать и может вызывать проблемы
    with concurrent.futures.ThreadPoolExecutor() as pool:
        # выполнение функции в отдельном потоке
        await loop.run_in_executor(pool, run_handle_connection, reader, writer)

    # 3. вариант с multiprocessing
    # process = Process(target=run_handle_connection, args=(reader, writer))
    # if not process.is_alive():
    #    process.start()


async def main(host, port):
    server = await asyncio.start_server(run, host, port)
    print(f"Start server {socket.gethostbyname(socket.gethostname())}...")

    # Правка №2
    # ограничение ресурсов памяти
    # установлено ограничение до 200 МБ
    soft, hard = 200 * 1024 * 1024, 200 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (soft, hard))

    # сохраняем PID процесса, чтоб можно было убить из консоли
    pid = os.getpid()
    f = open("pid.pid", "w")
    f.write(f"{pid}")
    f.close()

    async with server:
        await server.serve_forever()

HOST = "192.168.1.111"
PORT = 11000

if __name__ == "__main__":
    asyncio.run(main(HOST, PORT))
