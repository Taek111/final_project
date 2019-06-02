import time
import threading
#import pygame
import queue
import matplotlib.pyplot as plt
import numpy as np

def print_test():

    threading.Timer(0.5, print_test).start()

def thread_test():
    cnt = 0
    while(True):
        cnt += 1
        print(cnt)

def audio_test():
    pygame.mixer.init()
    bang = pygame.mixer.Sound("data/alarm_1.wav")
    while True:
        bang.play
        time.sleep(2.0)


# t = threading.Thread(target=thread_test)
# print("Main Thread")
# for i in range(50):
#     print(time.time())
#     time.sleep(1)

if __name__ == '__main__':
    plt.style.use(['default'])
    test = list()
    cur_time = time.time()
    c = time.gmtime()
    print(cur_time)
    for i in range(80):
        test.append(i)
    tlist = np.linspace(cur_time - 79 * 600, cur_time, 80)
    fig = plt.plot(tlist, test)
    print(cur_time - 79 * 600, cur_time, 80)
    start, middle, end = time.localtime(cur_time - 79* 600), time.localtime(cur_time - 79 * 300), time.localtime(cur_time)
    plt.xticks([cur_time - 79* 600 , cur_time - 79 * 300 , cur_time],[str(start.tm_hour)+':'+str(start.tm_min),
                                                                      str(middle.tm_hour)+':'+str(middle.tm_min),
                                                                      str(end.tm_hour)+':'+str(end.tm_min)])
    plt.ylim(0,200)
    plt.xlabel("Time")
    plt.ylabel('Temperature ($^\circ$C)')
    plt.title(str(end.tm_year)+". "+str(end.tm_mon)+". "+str(end.tm_mday))
    plt.savefig("data/yellowdog.png", dpi=350)
    plt.show()
    print("save")