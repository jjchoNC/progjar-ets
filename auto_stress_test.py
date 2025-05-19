import subprocess

comb1 = ['post', 'get'] # operation
comb2 = [10, 50, 100] # volume mb
comb3 = [1, 5, 50] #client worker pool

for operation in comb1:
    temp = input(f"Jalankan operasi {operation} sekarang? (y/n): ")
    if temp.lower() != 'n':
        print("Operasi dibatalkan.")
        continue
    for size_mb in comb2:
        for client in comb3:
            print(f"\nTesting {operation} with {size_mb}MB and {client} clients\n")
            subprocess.run(["python", "file_client_stress.py", "--operation", operation, "--size", str(size_mb), "--clients", str(client)])