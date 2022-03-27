import requests

r = requests.get('https://github.com/BlueFisher/SHU-selfreport/archive/refs/heads/master.zip')

with open("remote.zip", "wb") as f:
    f.write(r.content)
