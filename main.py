import base64
import datetime as dt
import os
import time
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup

from fState import F_STATE_GENERATOR
import base64
import re

NEED_BEFORE = False  # 如需补报则置为True，否则False
START_DT = dt.datetime(2020, 11, 10)  # 需要补报的起始日期
XIAOQU = "宝山"  # 宝山、嘉定或延长


# 获取东八区时间
def get_time():
    # 获取0时区时间，变换为东八区时间
    # 原因：运行程序的服务器所处时区不确定
    t = dt.datetime.utcnow()
    t = t + dt.timedelta(hours=8)

    # 或者：
    # t = dt.datetime.utcnow()
    # tz_utc_8 = dt.timezone(dt.timedelta(hours=8))
    # t = t.astimezone(tz_utc_8)

    # 如果服务器位于东八区，也可用：
    # t = dt.datetime.now()

    return t


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

    print(f'{username} 登录成功')

    return sess


def myMessages(sess):
    url = f'https://selfreport.shu.edu.cn/MyMessages.aspx'
    unRead = sess.get(url).text
    unReadNum = len([i.start() for i in re.finditer('（未读）', unRead)])
    allAddrs = [i.start() for i in re.finditer('/ViewMessage.aspx', unRead)]

    for i in range(unReadNum):
        sess.get(f'https://selfreport.shu.edu.cn/ViewMessage.aspx?id=' + unRead[allAddrs[i] + 21:allAddrs[i] + 28])

    return


def report(sess, t, xiaoqu='宝山', temperature=37):
    ii = '1' if t.hour < 19 else '2'
    if xiaoqu == '宝山':
        xian = '宝山区'
    elif xiaoqu == '嘉定':
        xian = '嘉定区'
    elif xiaoqu == '延长':
        xian = '静安区'

    url = f'https://selfreport.shu.edu.cn/XueSFX/HalfdayReport.aspx?day={t.year}-{t.month}-{t.day}&t={ii}'
    while True:
        try:
            sess.get('https://newsso.shu.edu.cn/oauth/authorize?response_type=code&client_id=WUHWfrntnWYHZfzQ5QvXUCVy&redirect_uri=https%3a%2f%2fselfreport.shu.edu.cn%2fLoginSSO.aspx%3fReturnUrl%3d%252fDefault.aspx&scope=1')
            r = sess.get(url)
        except Exception as e:
            print(e)
            continue
        break

    soup = BeautifulSoup(r.text, 'html.parser')
    view_state = soup.find('input', attrs={'name': '__VIEWSTATE'})

    if view_state is None:
        if '上海大学统一身份认证' in r.text:
            print('登录信息过期')
        else:
            print(r.text)
        return False

    while True:
        try:
            r = sess.post(url, data={
                '__EVENTTARGET': 'p1$ctl00$btnSubmit',
                '__VIEWSTATE': view_state['value'],
                '__VIEWSTATEGENERATOR': 'DC4D08A3',
                'p1$ChengNuo': 'p1_ChengNuo',
                'p1$BaoSRQ': t.strftime('%Y-%m-%d'),
                'p1$DangQSTZK': '良好',
                'p1$TiWen': str(temperature),
                'p1$TiWen': '37',
                'p1$ZaiXiao': xiaoqu,
                'p1$ddlSheng$Value': '上海',
                'p1$ddlSheng': '上海',
                'p1$ddlShi$Value': '上海市',
                'p1$ddlShi': '上海市',
                'p1$ddlXian$Value': xian,
                'p1$ddlXian': xian,
                'p1$FengXDQDL': '否',
                'p1$TongZWDLH': '否',
                'p1$XiangXDZ': '上海大学',
                'p1$QueZHZJC$Value': '否',
                'p1$QueZHZJC': '否',
                'p1$DangRGL': '否',
                'p1$GeLDZ': '',
                'p1$CengFWH': '否',
                'p1$CengFWH_RiQi': '',
                'p1$CengFWH_BeiZhu': '',
                'p1$JieChu': '否',
                'p1$JieChu_RiQi': '',
                'p1$JieChu_BeiZhu': '',
                'p1$TuJWH': '否',
                'p1$TuJWH_RiQi': '',
                'p1$TuJWH_BeiZhu': '',
                'p1$JiaRen_BeiZhu': '',
                'p1$SuiSM': '绿色',
                'p1$LvMa14Days': '是',
                'p1$Address2': '',
                'p1_GeLSM_Collapsed': 'false',
                'p1_Collapsed': 'false',
                'F_TARGET': 'p1_ctl00_btnSubmit',
                'F_STATE': F_STATE_GENERATOR().updated_F_STATE(t, xiaoqu, xian, ii),
            }, headers={
                'X-Requested-With': 'XMLHttpRequest',
                'X-FineUI-Ajax': 'true'
            }, allow_redirects=False)
        except Exception as e:
            print(e)
            continue
        break

    if any(i in r.text for i in ['提交成功', '历史信息不能修改', '现在还没到晚报时间', '只能填报当天或补填以前的信息']):
        print(f'{t} 提交成功')
        return True
    else:
        print(f'{t} 提交失败')
        print(r.text)
        return False


if __name__ == "__main__":
    with open(Path(__file__).resolve().parent.joinpath('config.yaml'), encoding='utf8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if 'users' in os.environ:
        for user_password in os.environ['users'].split(';'):
            user, password = user_password.split(',')
            config[user] = {
                'pwd': password
            }

    for user in config:
        if user in ['00000000', '11111111']:
            continue

        print(f'======{user}======')
        sess = login(user, config[user]['pwd'])

        if sess:
            now = get_time()

            if NEED_BEFORE:
                t = START_DT
                while t < now:
                    report(sess, t + dt.timedelta(hours=8), XIAOQU)
                    report(sess, t + dt.timedelta(hours=20), XIAOQU)

                    t = t + dt.timedelta(days=1)

            report(sess, get_time(), XIAOQU)

        time.sleep(60)
