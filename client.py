import socket
import threading
import sys
import queue
import concurrent.futures
from time import sleep


# Аргументы командной строки
# Значения по умолчанию
n_threads = 10
txt_file = 'urls.txt'

arg_len = len(sys.argv) - 1
if arg_len == 1:
    n_threads = int(sys.argv[1])
elif arg_len == 2:
    n_threads = int(sys.argv[1])
    txt_file = sys.argv[2]

print('Using masters:', n_threads)
print(f'Using {txt_file} file')
print()

# Чтение из файла
file = open(txt_file, 'r')
urls = file.readlines()
file.close()


# Подключение к сокету
server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.connect(('localhost', 15000))

# Делаем очередь из списка url
queue_urls = queue.Queue(maxsize=len(urls))
for url in urls:
    queue_urls.put(url)



def worker():
    while True:
        try:
            url = queue_urls.get()
            server_sock.send(bytes(url, 'utf-8'))
            response = server_sock.recv(1024)
            print(response.decode('utf-8'))
            print()
        except Exception as e:
            print('Ошибка при отправке url:', e)


if __name__ == '__main__':
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        
        for i in range(n_threads):
            executor.submit(worker)