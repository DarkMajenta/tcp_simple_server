import os
import json
import re
import socketserver
import socket
import resource
import asyncio  # Добавляем модуль для асинхронного выполнения

# Функция для установки ограничения использования памяти
def set_memory_limit():
    # Ограничение установлено в 200 мегабайт
    limit = 200 * 1024 * 1024
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))

class MyTCPHandler(socketserver.StreamRequestHandler):
    async def handle_data(self, data):
        '''
        Асинхронные математические вычисления
        '''

        # Искусственная задержка для демонстрации асинхронности
        await asyncio.sleep(1)

        # Генерация ответа
        resp = '[{"qwe":123}]'
        resp = resp.encode()

        try:
            self.request.sendall(resp)
        except ConnectionError:
            return

    def handle(self):
        data_full = ''
        while True:
            try:
                data_part = self.request.recv(100000)
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

                asyncio.run(self.handle_data(data))  # Асинхронный вызов обработчика данных


def main(host, port):
    # Устанавливаем ограничение использования памяти
    set_memory_limit()

    server = socketserver.ThreadingTCPServer((host, port), MyTCPHandler)
    print(f"Start server {socket.gethostbyname(socket.gethostname())}...")

    pid = os.getpid()
    with open("pid.pid", "w") as f:
        f.write(str(pid))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


HOST = "0.0.0.0"
PORT = 11000

if __name__ == "__main__":
    main(HOST, PORT)
