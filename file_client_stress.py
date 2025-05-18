import socket
import json
import base64
import time
import os
import string
import random
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed

SERVER_ADDRESS = ('localhost', 6666)
BUFFER_SIZE = 2**16
IDX_GET = 0

def send_command(command_str=""):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(SERVER_ADDRESS)
        s.sendall(command_str.encode())
        received = ""
        while True:
            data = s.recv(BUFFER_SIZE)
            if not data:
                break
            received += data.decode()
            if "\r\n\r\n" in received:
                break
        s.close()
        return json.loads(received)
    except Exception as e:
        logging.error(f"[CLIENT ERROR] {e}")
        return {"status": "ERROR", "data": str(e)}

def remote_post(filename):
    try:
        with open(filename, 'rb') as f:
            encoded = base64.b64encode(f.read()).decode()
        command = f"POST {filename} {encoded}\r\n\r\n"
        result = send_command(command)
        return result['status'] == 'OK'
    except Exception:
        return False

def remote_get(filename):
    try:
        command = f"GET {filename}\r\n\r\n"
        result = send_command(command)
        ext = filename.split('.')[-1]
        filename = filename.split('.')[0] + str(IDX_GET) + '.' + ext
        if result['status'] == 'OK':
            with open(f"{filename}", 'wb') as f:
                f.write(base64.b64decode(result['data_file']))
            IDX_GET += 1
            return True
        return False
    except Exception:
        return False

def remote_list():
    try:
        command = "LIST\r\n\r\n"
        result = send_command(command)
        return result['status'] == 'OK'
    except Exception:
        return False

def worker(operation="list", size_mb=10):
    if size_mb== 10:
        filename = "10mb.bin"
    elif size_mb == 50:
        filename = "50mb.bin"
    elif size_mb == 100:
        filename = "100mb.bin"
    try:
        if operation == "post":
            logging.debug(f"POST {filename}")
            start = time.time()
            success = remote_post(filename)
            end = time.time()
        elif operation == "get":
            logging.debug(f"GET {filename}")
            start = time.time()
            success = remote_get(filename)
            end = time.time()
        elif operation == "list":
            logging.debug("LIST")
            start = time.time()
            success = remote_list()
            end = time.time()
        else:
            return {"status": False, "duration": 0, "error": "Unknown operation"}

        duration = round(end - start, 4)
        throughput = int(size_mb * 1024 * 1024 / duration) if duration > 0 and operation != 'list' else "-"
        return {"status": success, "duration": duration, "throughput": throughput}
    except Exception as e:
        return {"status": False, "duration": 0, "error": str(e)}


def stress_test(operation, size_mb, n_clients, use_thread=True):
    results = []
    pool = ThreadPoolExecutor if use_thread else ProcessPoolExecutor
    with pool(max_workers=n_clients) as executor:
        futures = [executor.submit(worker, operation, size_mb) for _ in range(n_clients)]
        for future in as_completed(futures):
            results.append(future.result())
    return results

def summarize(results, operation):
    num = len(results)
    success = sum(1 for r in results if r["status"])
    fail = num - success
    total_time = sum(r["duration"] for r in results)
    avg_time = round(total_time / num, 4)
    if operation != 'list':
        total_throughput = sum(r["throughput"] for r in results if r["status"])
        avg_throughput = int(total_throughput / success) if success > 0 else 0
    else:
        avg_throughput = "-"
    print("\n=== STRESS TEST RESULT ===")
    print(f"Operation        : {operation.upper()}")
    print(f"Total Clients    : {num}")
    print(f"Success          : {success}")
    print(f"Fail             : {fail}")
    print(f"Average Time     : {avg_time} s")
    print(f"Average Throughput: {avg_throughput} bytes/sec")
    print("===========================")

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    parser = argparse.ArgumentParser()
    parser.add_argument('--operation', choices=['post', 'get', 'list'], default='list', help='operation to stress')
    parser.add_argument('--size', type=int, default=10, help='file size in MB (ignored for list)')
    parser.add_argument('--clients', type=int, default=5, help='number of concurrent clients')
    parser.add_argument('--thread', action='store_true', help='use ThreadPoolExecutor')
    parser.add_argument('--process', action='store_true', help='use ProcessPoolExecutor')

    args = parser.parse_args()
    use_thread = args.thread or not args.process

    print(f"Running stress test: operation={args.operation}, size={args.size}MB, clients={args.clients}, method={'Thread' if use_thread else 'Process'}")
    result = stress_test(args.operation, args.size, args.clients, use_thread)
    summarize(result, args.operation)
    
# python3 file_client_stress.py --operation list --clients 50 --thread
# python3 file_client_stress.py --operation get --size 10 --clients 50 --process
# python3 file_client_stress.py --operation post --size 10 --clients 1 --thread