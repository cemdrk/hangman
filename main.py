#!/usr/bin/env python3
import socket
import sys
import threading
import random

wordlist = ['apple', 'banana', 'orange', 'pineapple',
            'apricot', 'avocado', 'cherry', 'mango']


class ClientHandler(threading.Thread):
    def __init__(self, conn, addr):
        global wordlist
        super(ClientHandler, self).__init__()
        self.conn = conn
        self.addr = addr

        self.answer_index = random.randint(0, len(wordlist) - 1)
        self.answer = list(wordlist[self.answer_index])
        self.answer_len = len(self.answer)
        self.display = ['_' for _ in range(self.answer_len)]
        self.found = 0
        self.guessed = []
        self.incorrect = 5

        self.start()

    def run(self):
        try:
            while self.found < self.answer_len and self.incorrect > 0:
                self.conn.send(bytes(' '.join(self.display) +
                                     '\n' + 'Guess a letter : ', 'utf-8'))

                data = self.conn.recv(1024)
                guess = data.decode('utf-8').strip()

                if not data or guess == 'exit':
                    break

                guess = guess.lower()
                if len(guess) != 1:
                    continue

                if guess not in self.guessed:
                    for i, letter in enumerate(self.answer):
                        if guess == letter:
                            self.found += 1
                            self.display[i] = guess

                    if guess not in self.display:
                        self.incorrect -= 1
                        self.conn.send(b'Wrong guess!\n')
                        self.conn.send(bytes('%d chances left\n' %
                                             (self.incorrect), 'utf-8'))
                    self.guessed.append(guess)

        finally:
            if self.found == self.answer_len:
                self.conn.send(bytes(' '.join(self.display) + '\n', 'utf-8'))
                self.conn.send(b'Congratz!\n')
            else:
                self.conn.send(b'You Lost!\n')
                self.conn.send(bytes(' '.join(self.answer) + '\n', 'utf-8'))

            self.conn.close()
            print(addr, 'closed')


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

HOST = '127.0.0.1'
PORT = 9000


if __name__ == '__main__':
    try:
        s.bind((HOST, PORT))
    except BaseException as e:
        print(e)
        sys.exit()

    s.listen(1)

    try:
        while True:
            print('waiting client ...', HOST, PORT)

            conn, addr = s.accept()
            print(addr)

            ClientHandler(conn, addr)
    except BaseException as e:
        print(e)
    finally:
        s.close()
