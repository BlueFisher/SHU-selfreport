import base64
import time

import requests
import rsa
from bs4 import BeautifulSoup


RETRY = 1
RETRY_TIMEOUT = 1


# 2021.04.17 更新密码加密
def encryptPass(password):
    key_str = '''-----BEGIN PUBLIC KEY-----
    MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDl/aCgRl9f/4ON9MewoVnV58OL
    OU2ALBi2FKc5yIsfSpivKxe7A6FitJjHva3WpM7gvVOinMehp6if2UNIkbaN+plW
    f5IwqEVxsNZpeixc4GsbY9dXEk3WtRjwGSyDLySzEESH/kpJVoxO7ijRYqU+2oSR
    wTBNePOk1H+LRQokgQIDAQAB
    -----END PUBLIC KEY-----'''
    pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(key_str.encode('utf-8'))
    crypto = base64.b64encode(rsa.encrypt(password.encode('utf-8'), pub_key)).decode()
    return crypto


def login(username, password):
    sess = requests.Session()
    for _ in range(RETRY):
        try:
            r = sess.get('https://selfreport.shu.edu.cn/Default.aspx', timeout=5)
            code = r.url.split('/')[-1]
            url_param = eval(base64.b64decode(code).decode("utf-8"))
            state = url_param['state']
            sess.post(r.url, data={
                'username': username,
                'password': encryptPass(password)
            }, allow_redirects=False)
            sess.get(f'https://newsso.shu.edu.cn/oauth/authorize?response_type=code&client_id=WUHWfrntnWYHZfzQ5QvXUCVy&redirect_uri=https%3a%2f%2fselfreport.shu.edu.cn%2fLoginSSO.aspx%3fReturnUrl%3d%252fDefault.aspx&scope=1&state={state}')

        except Exception as e:
            print(e)
            time.sleep(RETRY_TIMEOUT)
            continue
        break
    else:
        print('登录超时')
        return

    url = f'https://selfreport.shu.edu.cn/DayReport.aspx'
    for _ in range(RETRY_TIMEOUT):
        try:
            r = sess.get(url)
        except Exception as e:
            print(e)
            time.sleep(RETRY_TIMEOUT)
            continue
        break
    else:
        print('登录后验证超时')
        return

    soup = BeautifulSoup(r.text, 'html.parser')
    view_state = soup.find('input', attrs={'name': '__VIEWSTATE'})

    if view_state is None or 'invalid_grant' in r.text:
        print(r.text)
        return

    return sess