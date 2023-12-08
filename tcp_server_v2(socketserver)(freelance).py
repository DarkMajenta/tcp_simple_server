import os  # Модуль для работы с операционной системой
import json  # Модуль для работы с JSON
import re  # Модуль для работы с регулярными выражениями
import warnings  # Модуль для управления предупреждениями
import resource  # Модуль для управления ресурсами
import asyncio  # Модуль для асинхронного программирования

async def handle_client(reader, writer):
    data_full = ''
    while True:
        try:
            data_part = await reader.read(100000)  # Асинхронно читает данные от клиента
        except ConnectionError:
            break
        if not data_part:
            break
        if data_part == b"close":
            break

        data_full = data_full + data_part.decode()  # Записывает принятые данные в полную строку
        match = re.search(r'\}\]', data_full)  # Ищет совпадение в строке
        if match:
            data = json.loads(data_full)  # Преобразует строку JSON в объект Python
            data_full = ''

            '''
            мат.вычисления
            '''
            result = perform_mathematical_calculations(data)  # Вызов функции, выполняющей математические вычисления

            resp = json.dumps(result)  # Преобразует объект Python в строку JSON
            writer.write(resp.encode())  # Отправляет ответ клиенту
            await writer.drain()  # Асинхронно ожидает отправку данных

    writer.close()  # Закрывает соединение с клиентом

def perform_mathematical_calculations(data):
    # Выполнение математических вычислений
    return [{"qwe": 123}]

async def main(host, port):
    server = await asyncio.start_server(run, host, port)
    print(f"Start server {socket.gethostbyname(socket.gethostname())}...")  # Асинхронно запускает сервер

    addr = server.sockets[0].getsockname()  # Получает адрес сервера
    print(f"Serving on {addr}")

    await server.serve_forever()  # Асинхронно запускает бесконечный цикл обслуживания клиентов

if __name__ == "__main__":
    HOST = "192.168.1.111"  # Хост сервера
    PORT = 11000  # Порт сервера

    # Ограничение ресурсов памяти
    soft, hard = 200 * 1024 * 1024, 200 * 1024 * 1024  # Мягкое и жесткое ограничения памяти
    resource.setrlimit(resource.RLIMIT_AS, (soft, hard))  # Устанавливает ограничение памяти

    # Сохраняем PID процесса
    pid = os.getpid()  # Получает идентификатор процесса
    with open("pid.pid", "w") as f:  # Открывает файл для записи PID
        f.write(str(pid))  # Записывает PID в файл

    asyncio.run(main(HOST, PORT))  # Запускает главную функцию
