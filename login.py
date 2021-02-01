import base64
import re

import requests
from bs4 import BeautifulSoup


def myMessages(sess):
    url = f'https://selfreport.shu.edu.cn/MyMessages.aspx'
    unRead = sess.get(url).text
    unReadNum = len([i.start() for i in re.finditer('（未读）', unRead)])
    allAddrs = [i.start() for i in re.finditer('/ViewMessage.aspx', unRead)]

    for i in range(unReadNum):
        sess.get(f'https://selfreport.shu.edu.cn/ViewMessage.aspx?id=' + unRead[allAddrs[i] + 21:allAddrs[i] + 28])

    return


def login(username, password):
    sess = requests.Session()
    while True:
        try:
            r = sess.get('https://selfreport.shu.edu.cn/Default.aspx')
            code = r.url.split('/')[-1]
            url_param = eval(base64.b64decode(code).decode("utf-8"))
            state = url_param['state']
            sess.post(r.url, data={
                'username': username,
                'password': password
            })
            messageBox = sess.get(f'https://newsso.shu.edu.cn/oauth/authorize?response_type=code&client_id=WUHWfrntnWYHZfzQ5QvXUCVy&redirect_uri=https%3a%2f%2fselfreport.shu.edu.cn%2fLoginSSO.aspx%3fReturnUrl%3d%252fDefault.aspx&scope=1&state={state}')
            if 'tz();' in messageBox.text:  # 调用tz()函数在首层提醒未读
                myMessages(sess)

        except Exception as e:
            print(e)
            continue
        break

    url = f'https://selfreport.shu.edu.cn/XueSFX/HalfdayReport.aspx?day=2020-11-21&t=1'
    while True:
        try:
            r = sess.get(url)
        except Exception as e:
            print(e)
            continue
        break

    soup = BeautifulSoup(r.text, 'html.parser')
    view_state = soup.find('input', attrs={'name': '__VIEWSTATE'})

    if view_state is None or 'invalid_grant' in r.text:
        print(f'{username} 登录失败')
        print(r.text)
        return

    print(f'登录成功')

    return sess
