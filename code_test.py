import time
import threading

def print_test():
    print("실행중")
    threading.Timer(0.5, print_test).start()

def thread_test():
    cnt = 0
    while(True):
        cnt += 1
        print(cnt)




def thread_test():
    cnt = 0
    while(True):
        print(cnt)
        cnt += 1


# t = threading.Thread(target=thread_test)
# print("Main Thread")
# for i in range(50):
#     print(time.time())
#     time.sleep(1)

s = [1, 2,3 ,0]
print(max(s))