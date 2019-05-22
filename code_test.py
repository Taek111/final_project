import threading
import time
import queue
# def print_test():
#     print("실행중")
#     threading.Timer(0.5, print_test).start()
# if __name__ == '__main__':
#     print_test()
q = queue.Queue()
q.put(1)
q.put(2)
q.get()
print(q.get())
print(int(time.time()))