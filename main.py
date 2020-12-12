import datetime as dt
import time

import requests
import yaml
import argparse
from bs4 import BeautifulSoup
from fState import F_STATE_GENERATOR
import base64

NEED_BEFORE = False  # 如需补报则置为True，否则False
MONTHS = [10, 11]  # 补报的月份，默认10月、11月
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
            sess.get(f'https://newsso.shu.edu.cn/oauth/authorize?response_type=code&client_id=WUHWfrntnWYHZfzQ5QvXUCVy&redirect_uri=https%3a%2f%2fselfreport.shu.edu.cn%2fLoginSSO.aspx%3fReturnUrl%3d%252fDefault.aspx&scope=1&state={state}')
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
        print(r.text)
        return False


def request_for_auto_report(username, sess):
    print(username)
    cookie = dict()
    for k, v in sess.cookies.items():
        cookie[k] = v

    token = sess.cookies['SHU_OAUTH2_SESSION'] + '#' + sess.cookies['.ncov2019selfreport']

    print(token)

    r = requests.post('http://shu-report.shusnjl.cn/update', json={
        'id': username,
        'campus': XIAOQU,
        'token': token
    })

    if r.status_code == 200:
        if r.json()['msg'] == 'insert success':
            print(f'已提交到自动填报服务器，可以去http://shu-report.shusnjl.cn/user/{username}查看')
        elif r.json()['msg'] == 'update success':
            print(f'已更新到自动填报服务器，可以去http://shu-report.shusnjl.cn/user/{username}查看')
        else:
            print(r.json())
    else:
        print('提交失败')
        print(r.text)


def request_for_saved_sess():
    while True:
        try:
            r = requests.get('http://shu-report.shusnjl.cn/token')
        except Exception as e:
            print(e)
            continue
        break
    if r.status_code == 200:
        res = r.json()
        sess = requests.Session()
        token = res['token'].split('#')
        if len(token) == 2:
            sess.cookies.set('SHU_OAUTH2_SESSION', token[0])
            sess.cookies.set('.ncov2019selfreport', token[1])

        return res['id'], res['campus'], sess


def send_report_result(username, status):
    try:
        r = requests.post('http://shu-report.shusnjl.cn/status', json={
            'id': username,
            'status': status
        })
    except Exception as e:
        print(e)
        return

    if r.status_code == 200:
        if status:
            print(f'{username} 已提交结果')
        else:
            print(f'{username} 已提交失败结果')


with open('config.yaml', encoding='utf8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

parser = argparse.ArgumentParser()
parser.add_argument('--request', action='store_true')
parser.add_argument('--server', action='store_true')

args = parser.parse_args()


if args.request and args.server:
    print("参数错误")
    exit()

if args.request:
    for i, user in enumerate(config):
        print(f'======{user}======')
        sess = login(user, config[user]['pwd'])
        if sess:
            request_for_auto_report(user, sess)

        if i < len(config) - 1:
            print(f'等待一分钟')
            time.sleep(60)
elif args.server:
    while True:
        response = request_for_saved_sess()
        if response:
            username, xiaoqu, sess = response
            t = get_time()
            result = report(sess, t, xiaoqu)
            send_report_result(username, result)
        else:
            print('没有需要填报的数据')

        time.sleep(2)
else:
    last_login_time = 0
    user_login_status = {user: {'sess': None, 'has_before': False} for user in config}

    while True:
        for user in config:
            print(f'======{user}======')
            if user_login_status[user]['sess'] is None:
                if time.time() - last_login_time > 60:
                    user_login_status[user]['sess'] = login(user, config[user]['pwd'])
                    last_login_time = time.time()
                else:
                    print('等待登录')

            sess = user_login_status[user]['sess']
            if sess:
                if NEED_BEFORE and not user_login_status[user]['has_before']:
                    for month in MONTHS:
                        for day in range(1, 32):
                            for hour in [9, 21]:
                                try:
                                    t = dt.datetime(2020, month, day, hour)
                                except ValueError:
                                    continue

                                if not report(sess, t, XIAOQU):
                                    user_login_status[user]['sess'] = None
                                    user_login_status[user]['has_before'] = False
                                    break
                                else:
                                    user_login_status[user]['has_before'] = True

                t = get_time()
                if not report(sess, t, XIAOQU):
                    user_login_status[user]['sess'] = None

        time.sleep(60 * 10)
