import socket
import logging
import time
import sys
from multiprocessing import Process

from file_protocol import FileProtocol
fp = FileProtocol()

def process_client(connection, address):
    d = ''
    try:
        while True:
            data = connection.recv(32)
            if data:
                d += data.decode()
                if "\r\n\r\n" in d:
                    hasil = fp.proses_string(d.strip())
                    hasil = hasil + "\r\n\r\n"
                    connection.sendall(hasil.encode())
                    break
            else:
                break
    except Exception as e:
        logging.error(f"Error handling client {address}: {e}")
    finally:
        connection.close()

class Server:
    def __init__(self, ipaddress='0.0.0.0', port=8889, backlog=5):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.backlog = backlog

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(self.backlog)
        try:
            while True:
                connection, address = self.my_socket.accept()
                logging.warning(f"connection from {address}")
                p = Process(target=process_client, args=(connection, address))
                p.start()
        except KeyboardInterrupt:
            logging.warning("Server shutting down.")
        finally:
            self.my_socket.close()

def main():
    svr = Server(ipaddress='0.0.0.0', port=6666)
    svr.run()

if __name__ == "__main__":
    main()