from socket import *
import socket
import logging
import time
import argparse
from concurrent.futures import ThreadPoolExecutor

from file_protocol import FileProtocol
fp = FileProtocol()

BUFFER_SIZE = 1024 * 1024

def process_client(connection, address):
    d = ''
    try:
        while True:
            data = connection.recv(BUFFER_SIZE)
            # print(len(d))
            if data:
                d += data.decode()
                if "\r\n\r\n" in d:
                    # print("MASUK")
                    hasil = fp.proses_string(d.strip())
                    # print("SUDAH DI PROSES")
                    hasil = hasil + "\r\n\r\n"
                    connection.sendall(hasil.encode())
                    # print(f"Data dikirim ke {address}")
                    break
            else:
                break
    except Exception as e:
        logging.error(f"Error handling client {address}: {e}")
    finally:
        connection.close()


class Server:
    def __init__(self, ipaddress='0.0.0.0', port=8889, max_workers=10):
        self.ipinfo = (ipaddress, port)
        self.my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.max_workers = max_workers

    def run(self):
        logging.warning(f"server berjalan di ip address {self.ipinfo}")
        self.my_socket.bind(self.ipinfo)
        self.my_socket.listen(10)
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            try:
                while True:
                    connection, address = self.my_socket.accept()
                    logging.warning(f"Accepted connection from {address}")
                    executor.submit(process_client, connection, address, executor._max_workers)
            except KeyboardInterrupt:
                logging.warning("Server shutting down.")
            finally:
                self.my_socket.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-m", "--max_workers",
        type=int,
        default=10,
    )
    args = parser.parse_args()
    svr = Server(ipaddress='0.0.0.0', port=6667, max_workers=args.max_workers)
    svr.run()

if __name__ == "__main__":
    main()