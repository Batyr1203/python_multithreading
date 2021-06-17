import socket
from select import select
import concurrent.futures
import queue
import threading
import time
from urllib.request import urlopen
from bs4 import BeautifulSoup
from collections import Counter
from time import sleep
import json
import sys

# Значения по умолчанию
n_threads = 11
n_words = 7



arg_len = len(sys.argv) - 1
if arg_len == 1:
    n_threads = int(sys.argv[1])
elif arg_len == 2:
    n_threads = int(sys.argv[1])
    n_words = int(sys.argv[2])

print('Using masters:', n_threads)
print(f'Looking for {n_words} words')


to_monitor = []

server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_sock.bind(('localhost', 15000))
server_sock.listen()
print('The server is listening now...')


to_monitor.append(server_sock)
queue_urls = queue.Queue()
lock = threading.Lock()




def accept_conn(server_sock):
    client_sock, addr = server_sock.accept()
    print('Connect', addr)
    to_monitor.append(client_sock)


def worker():
    
    while True:

        try:
            url, sock = queue_urls.get()

            res = get_common_words(url, n_words)
            #sock.send(bytes(url, 'utf-8'))
            sock.sendall(bytes(res, 'utf-8'))
            print('URL обработан')


        except Exception as e:
            print('Ошибка при выполнении потока:', e)

    

def master():
    while True:

        ready_to_read, _, _ = select(to_monitor, [], [])  # read, write, err
        for sock in ready_to_read:
            if sock is server_sock:
                accept_conn(sock)
            else:
                data = sock.recv(8192)
                list = data.split()
                for item in list:
                    #print('URL:', item.decode())
                    queue_urls.put((item.decode(), sock))
                


def get_common_words(url, k):

    html = urlopen(url).read()
    soup = BeautifulSoup(html, features='html.parser')

    text = soup.get_text()
    split_it = text.split()

    for i in range(len(split_it)):
        split_it[i] = split_it[i].lower()

    counter = Counter(split_it)
    most_occur = counter.most_common(k)

    res = {}
    res['url'] = url
    for key, val in most_occur:
        res[key] = val

    return json.dumps(res)




if __name__ == '__main__':
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads+1) as executor:
        executor.submit(master)
        
        for i in range(n_threads):
            executor.submit(worker)

