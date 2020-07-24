import time
import smtplib
import argparse
import requests
import datetime as dt

from bs4 import BeautifulSoup
import yaml
from email.message import EmailMessage


config_file_path = 'config.yaml'


def send_mail(to_email, subject, message):
    with open(config_file_path) as f:
        config_file = yaml.load(f, Loader=yaml.FullLoader)

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = config_file['email']['from']
    msg['To'] = ', '.join(to_email)
    msg.set_content(message)
    server = smtplib.SMTP(config_file['email']['smtp'])
    server.login(config_file['email']['username'], config_file['email']['password'])
    server.send_message(msg)
    server.quit()


def report(username, password, email, ii):
    print('report', username)
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
    r = sess.post(url, data={
        '__EVENTTARGET': 'p1$ctl00$btnSubmit',
        '__VIEWSTATE': soup.find('input', attrs={'name': '__VIEWSTATE'})['value'],
        '__VIEWSTATEGENERATOR': 'DC4D08A3',
        'p1$ChengNuo': 'p1_ChengNuo',
        'p1$BaoSRQ': t.strftime('%Y-%m-%d'),
        'p1$DangQSTZK': '良好',
        'p1$TiWen': '37',
        'p1$SuiSM': '绿色',
        'p1$ShiFJC': ['早餐', '午餐', '晚餐'],
        'F_TARGET': 'p1_ctl00_btnSubmit',
        'p1_Collapsed': 'false',
    }, headers={
        'X-Requested-With': 'XMLHttpRequest',
        'X-FineUI-Ajax': 'true'
    }, allow_redirects=False)

    if '提交成功' in r.text:
        print(t.strftime('%Y-%m-%d %H:%M:%S'), '提交成功')
        return

    if email is not None:
        send_mail(to_email=[email],
                  subject=t.strftime('%Y-%m-%d %H:%M:%S') + '提交不确定，请手动查看',
                  message=t.strftime('%Y-%m-%d %H:%M:%S') + '提交不确定，请手动查看')
    print(t.strftime('%Y-%m-%d %H:%M:%S'), '提交不确定，请手动查看')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # 配置文件
    parser.add_argument('--config', '-c', type=str, default='config.yaml', help='配置文件位置')
    args = parser.parse_args()
    config_file_path = args.config

    # 立即提交一次
    # 服务器上的时区是0时区，TODO 怎么在python里换时区？不想查了
    t = dt.datetime.utcnow()
    t = t + dt.timedelta(hours=8)

    ii = '1' if t.hour < 20 else '2'
    with open(config_file_path) as f:
        config_file = yaml.load(f, Loader=yaml.FullLoader)
        for user in config_file['users']:
            report(user['id'], user['pwd'], user['email_to'], ii)

    while True:
        t = dt.datetime.utcnow()
        t = t + dt.timedelta(hours=8)

        # 早上7点与晚上20点10分、11分左右打卡
        if t.hour == 7 or t.hour == 20:
            if t.minute in [10, 11]:
                ii = '1' if t.hour == 7 else '2'
                with open(config_file_path) as f:
                    config_file = yaml.load(f, Loader=yaml.FullLoader)
                    for user in config_file['users']:
                        report(user['id'], user['pwd'], user['email_to'], ii)

                time.sleep(60)

        time.sleep(60)
