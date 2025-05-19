import socket
import json
import base64
import time
import logging
import csv
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

SERVER_ADDRESS = ('172.16.16.102', 6667)
CONTROL_PORT = 6668
BUFFER_SIZE = 1024 * 1024

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
        filename = filename.split('.')[0] + "_" + str(time.time()) + '.' + ext
        if result['status'] == 'OK':
            with open(f"{filename}", 'wb') as f:
                f.write(base64.b64decode(result['data_file']))
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
    if size_mb == 10:
        filename = "10mb.bin"
    elif size_mb == 50:
        filename = "50mb.bin"
    elif size_mb == 100:
        filename = "100mb.bin"
    try:
        if operation == "post":
            start = time.time()
            success = remote_post(filename)
            end = time.time()
        elif operation == "get":
            start = time.time()
            success = remote_get(filename)
            end = time.time()
        elif operation == "list":
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

def stress_test(operation, size_mb, n_clients):
    results = []
    with ThreadPoolExecutor(max_workers=n_clients) as executor:
        futures = [executor.submit(worker, operation, size_mb) for _ in range(n_clients)]
        for future in as_completed(futures):
            results.append(future.result())
    return results

def gen_csv(results, operation, size, clients, server_workers):
    summary_file = 'stress_test_results.csv'
    detail_file = 'stress_test_client_details.csv'

    file_exists = os.path.isfile(summary_file)
    with open(summary_file, 'a', newline='') as csvfile:
        fieldnames = [
            'No', 'Operation', 'Volume', 'Client Workers', 'Server Workers',
            'Total Time (s)', 'Throughput (bytes/s)', 'Success Clients', 'Failed Clients'
        ]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()

        total_time = 0
        total_throughput = 0
        success = 0
        fail = 0
        for result in results:
            if result['status']:
                success += 1
                total_time += result['duration']
                if operation != 'list':
                    total_throughput += result['throughput']
                else:
                    total_throughput = "-"

            else:
                fail += 1

        writer.writerow({
            'No': sum(1 for _ in open(summary_file)) if file_exists else 1,
            'Operation': operation,
            'Volume': size,
            'Client Workers': clients,
            'Server Workers': server_workers,
            'Total Time (s)': round(total_time, 4),
            'Throughput (bytes/s)': total_throughput,
            'Success Clients': success,
            'Failed Clients': fail
        })

    file_exists = os.path.isfile(detail_file)
    with open(detail_file, 'a', newline='') as csvfile:
        fieldnames = ['Client ID', 'Status', 'Duration (s)', 'Throughput (bytes/s)', 'Operation']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        for idx, result in enumerate(results, 1):
            writer.writerow({
                'Client ID': idx,
                'Status': 'Success' if result['status'] else 'Fail',
                'Duration (s)': result['duration'],
                'Throughput (bytes/s)': result.get('throughput', '-'),
                'Operation': operation
            })

    print("\n=== STRESS TEST RESULT ===")
    print(f"Operation        : {operation.upper()}")
    print(f"File Size        : {size} MB")
    print(f"Clients          : {clients}")
    print(f"Success          : {success}")
    print(f"Fail             : {fail}")
    print(f"Time             : {round(total_time, 4)} s")
    print(f"Throughput       : {total_throughput} bytes/sec")
    print("===========================\n")

if __name__ == '__main__':
    logging.basicConfig(level=logging.WARNING)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((SERVER_ADDRESS[0], CONTROL_PORT))
        data = s.recv(1024)
        server_workers = int.from_bytes(data, byteorder='big')

    operations = ["post", "get"]
    sizes = [10, 50, 100]
    clients = [1, 5, 50]

    for operation in operations:
        for size in sizes:
            for client_count in clients:
                print(f"Running stress test: operation={operation}, size={size}MB, clients={client_count}")
                results = stress_test(operation, size, client_count)
                gen_csv(results, operation, size, client_count, server_workers)
