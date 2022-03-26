import requests
import time
import random

r = requests.get('https://github.com/BlueFisher/SHU-selfreport/archive/refs/heads/master.zip')

with open("remote.zip", "wb") as f:
    f.write(r.content)

t = random.randrange(600, 1440)
print('wait', t)
time.sleep(t)
