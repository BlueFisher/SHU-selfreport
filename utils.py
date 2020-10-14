import datetime as dt
import random
import smtplib
import time
from email.message import EmailMessage

import requests
import yaml
from bs4 import BeautifulSoup


# 每日一报模块
def report(t, username, password, temperature):
    ii = '1' if t.hour < 20 else '2'

    sess = requests.Session()
    while True:
        try:
            r = sess.get('https://selfreport.shu.edu.cn/Default.aspx')
            sess.post(r.url, data={
                'username': username,
                'password': password
            })
            sess.get('https://newsso.shu.edu.cn/oauth/authorize?response_type=code&client_id=WUHWfrntnWYHZfzQ5QvXUCVy&redirect_uri=https%3a%2f%2fselfreport.shu.edu.cn%2fLoginSSO.aspx%3fReturnUrl%3d%252fDefault.aspx&scope=1')
        except Exception as e:
            print(e)
            continue
        break

    url = f'https://selfreport.shu.edu.cn/XueSFX/HalfdayReport.aspx?day={t.year}-{t.month}-{t.day}&t={ii}'
    while True:
        try:
            r = sess.get(url)
        except Exception as e:
            print(e)
            continue
        break

    soup = BeautifulSoup(r.text, 'html.parser')
    view_state = soup.find('input', attrs={'name': '__VIEWSTATE'})

    if view_state is None:
        print('登录失败')
        print(r.text)
        return False

    r = sess.post(url, data={
        '__EVENTTARGET': 'p1$ctl00$btnSubmit',
        '__VIEWSTATE': view_state['value'],
        '__VIEWSTATEGENERATOR': 'DC4D08A3',
        'p1$ChengNuo': 'p1_ChengNuo',
        'p1$BaoSRQ': t.strftime('%Y-%m-%d'),
        'p1$DangQSTZK': '良好',
        'p1$TiWen': str(round(random.uniform(temperature - 0.2, temperature + 0.2), 1)),
        'p1$SuiSM': '绿色',
        'p1$ShiFJC': ['早餐', '午餐', '晚餐'],
        'F_TARGET': 'p1_ctl00_btnSubmit',
        'p1_Collapsed': 'false',
    }, headers={
        'X-Requested-With': 'XMLHttpRequest',
        'X-FineUI-Ajax': 'true'
    }, allow_redirects=False)

    if '提交成功' in r.text:
        return True
    else:
        print(r.text)
        return False


# 邮件发送模块
def send_mail(sender_config, to_email, subject, message):
    if sender_config['from'] is None or sender_config['username'] is None \
            or sender_config['password'] is None or sender_config is None:
        return

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_config['from']
    msg['To'] = ', '.join(to_email)
    msg.set_content(message)

    try:
        server = smtplib.SMTP_SSL(sender_config['smtp'], port=sender_config['port'])
        server.login(sender_config['username'], sender_config['password'])
        server.send_message(msg)
        server.close()
        return True
    except smtplib.SMTPException:
        return False


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


# 加载yaml
def load_config(config_path):
    with open(config_path, encoding='utf8') as f:
        return yaml.load(f, Loader=yaml.FullLoader)


def test_report(report_config_path):
    users = load_config(report_config_path)['users']
    print("测试每日一报：")
    for user in users:
        t = get_time()
        is_successful = report(t, user['id'], user['pwd'], 36.2)
        if is_successful:
            print(t.strftime('%Y-%m-%d %H:%M:%S'), "{} 提交成功".format(user['id']))
        else:
            print(t.strftime('%Y-%m-%d %H:%M:%S'), "{} 提交失败".format(user['id']))

        time.sleep(5)


def test_send_email(addressee, report_config_path):
    sender_config = load_config(report_config_path)['email']

    if send_mail(sender_config, [addressee], "每日一报测试邮件", "每日一报邮件提醒功能正常开启"):
        print("邮件提醒功能测试成功")
    else:
        print("邮件提醒功能测试失败，可能为密钥错误或者您输入的邮箱错误！")


def auto_report(report_config_path, setting_config_path):
    setting_config = load_config(setting_config_path)
    reported = False
    while True:
        t = get_time()

        if t.hour == setting_config["morning_hour"] or t.hour == setting_config['night_hour']:
            if t.minute >= setting_config['minute'] and t.minute <= setting_config['minute'] + 10:
                if reported is True:
                    # 避免在时间范围内重复提交
                    time.sleep(int(random.uniform(60, 600)))
                    continue

                report_config = load_config(report_config_path)

                for user in report_config['users']:
                    is_successful = report(t, user['id'], user['pwd'], setting_config['temperature'])

                    print('report', user['id'])
                    now = get_time()
                    if is_successful:
                        print(now.strftime('%Y-%m-%d %H:%M:%S'), '提交成功')
                        reported = True
                        if setting_config['send_email'] and user['email_to'] is not None:
                            is_send = send_mail(report_config['email'], [user['email_to']],
                                                "{}月{}日每日一报提交成功".format(t.month, t.day),
                                                t.strftime('%Y-%m-%d %H:%M:%S') + "{}的每日一报提交成功".format(user['id']))
                            if not is_send:
                                print("发送每日一报成功邮件给{}失败!如您已对邮件发送模块进行测试，则可能为该发送对象的邮件错误。".format(user['id']))
                    else:
                        print(now.strftime('%Y-%m-%d %H:%M:%S'), '提交失败')
                        if user['email_to'] is not None:
                            is_send = send_mail(report_config['email'], [user['email_to']],
                                                "{}月{}日每日一报提交失败".format(t.month, t.day),
                                                t.strftime('%Y-%m-%d %H:%M:%S') + "{}的每日一报提交失败".format(user['id']))
                            if not is_send:
                                print("发送每日一报失败邮件给{}失败!如您已对邮件发送模块进行测试，则可能为该发送对象的邮件错误。".format(user['id']))

                    # 如果有多个账号需要提交，不让程序在短时间内多次提交
                    time.sleep(int(random.uniform(5, 10)))
                print('================================')
                time.sleep(60)
            else:
                # not in time
                reported = False

        delay_time = int(random.uniform(60, 600))
        time.sleep(delay_time)
