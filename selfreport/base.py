# -- coding: utf-8 --

import os
import random
import smtplib
import requests
import datetime as dt

from email.message import EmailMessage
from bs4 import BeautifulSoup


# 每日一报模块
def report(t, username, password, temperature):
    ii = '1' if t.hour < 20 else '2'

    sess = requests.Session()
    sess.post("https://newsso.shu.edu.cn/login", data={
        'username': username,
        'password': password,
        'login_submit': '%25E7%2599%25BB%25E5%25BD%2595%252FLogin'
    })
    sess.get('https://newsso.shu.edu.cn/oauth/authorize?response_type=code&client_id=WUHWfrntnWYHZfzQ5QvXUCVy&redirect_uri=https%3a%2f%2fselfreport.shu.edu.cn%2fLoginSSO.aspx%3fReturnUrl%3d%252fDefault.aspx&scope=1')

    url = 'https://selfreport.shu.edu.cn/XueSFX/HalfdayReport.aspx?t=' + ii
    r = sess.get(url)

    soup = BeautifulSoup(r.text, 'html.parser')
    view_state = soup.find('input', attrs={'name': '__VIEWSTATE'})

    if view_state is None:
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
        server = smtplib.SMTP_SSL(
            sender_config['smtp'],
            port=sender_config['port'])
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


# 将日志信息写入文件中
def write_log(message, log_file_path):
    with open(log_file_path, 'a+', encoding="utf-8") as f:
        if not os.path.getsize(log_file_path):
            f.write(message)
        else:
            f.write("\n" + message)


# 将文件中的内容读取为字符串
def read_file_as_str(file_path):
    if not os.path.isfile(file_path):
        raise TypeError(file_path + " does not exist")

    all_the_text = open(file_path).read()
    return all_the_text
