import time
import threading
import pygame

def print_test():
    print("실행중")
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
    audio_test()
