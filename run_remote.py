import requests
import zipfile
import os


def unzip_file(zip_src, dst_dir):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_dir)
    else:
        print('This is not zip')


if __name__ == '__main__':
    r = requests.get('https://github.com/BlueFisher/SHU-selfreport/archive/refs/heads/master.zip')

    with open("remote.zip", "wb") as f:
        f.write(r.content)

    unzip_file('remote.zip', '')

    os.system('python -u SHU-selfreport-master/main.py')
