from multiprocessing import Process
import math
import time
def make_verbose(done, total, max_lines=100, start_with=""):
    num_lines = int((done/total)*max_lines)
    lines = "="*num_lines
    spaces = " "*(max_lines-num_lines)
    print(f"\r{start_with}  {lines}>{spaces}  {done}/{total}", end="", sep=" ", flush=True)


def job(counter, length, num, t):
    target = num
    while target < length:
        counter += t
        make_verbose(target, length, max_lines=25)
        time.sleep(0.1)
        target += t

if __name__ == '__main__':
    processes = []
    counter = 0
    length = 100
    for i in range(5):
        process = Process(target=job, args=(counter, length, i, 5))
        process.start()
        processes.append(process)
    
    for process in processes:
        process.join()