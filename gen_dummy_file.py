import os

def gen_10_mega_file():
    with open("10mb.bin", 'wb') as f:
        f.write(os.urandom(10 * 1024 * 1024))

def gen_50_mega_file():
    with open("50mb.bin", 'wb') as f:
        f.write(os.urandom(50 * 1024 * 1024))
        
def gen_100_mega_file():
    with open("100mb.bin", 'wb') as f:
        f.write(os.urandom(100 * 1024 * 1024))
        

gen_10_mega_file()
gen_50_mega_file()
gen_100_mega_file()