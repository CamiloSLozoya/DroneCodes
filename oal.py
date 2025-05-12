import time

t_next=1
while True:
    t=time.gmtime()
    print(t.tm_sec)
    time.sleep(1)