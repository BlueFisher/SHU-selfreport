import requests
from bs4 import BeautifulSoup
import datetime as dt
import time
import smtplib
from email.message import EmailMessage


def send_mail(to_email, subject, message):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = "xxxx@qq.com"
    msg['To'] = ', '.join(to_email)
    msg.set_content(message)
    server = smtplib.SMTP('smtp.qq.com')
    server.login("xxxx@qq.com", "xxxx")
    server.send_message(msg)
    server.quit()


while True:
    # 服务器上的时区是0时区，TODO 怎么在python里换时区？不想查了
    t = dt.datetime.utcnow()
    t = t + dt.timedelta(hours=8)

    # 早上7点与晚上20点2分、3分左右打卡
    if t.hour == 7 or t.hour == 20:
        if t.minute in [2, 3]:
            ii = '1' if t.hour == 7 else '2'

            # 登录，学号密码换成自己的
            sess = requests.Session()
            sess.post("https://newsso.shu.edu.cn/login", data={
                'username': 'xxxxxxxx',
                'password': 'xxxxxxxx',
                'login_submit': '%25E7%2599%25BB%25E5%25BD%2595%252FLogin'
            })
            sess.get('https://newsso.shu.edu.cn/oauth/authorize?response_type=code&client_id=WUHWfrntnWYHZfzQ5QvXUCVy&redirect_uri=https%3a%2f%2fselfreport.shu.edu.cn%2fLoginSSO.aspx%3fReturnUrl%3d%252fDefault.aspx&scope=1')

            # 打卡，这里是在校学生早晚打卡，没有返校的应该不是这个API
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
                'p1$ShiFJC': '早餐',
                'p1$ShiFJC': '午餐',
                'p1$ShiFJC': '晚餐',
                'F_TARGET': 'p1_ctl00_btnSubmit',
                'p1_Collapsed': 'false',
            }, headers={
                'X-Requested-With': 'XMLHttpRequest',
                'X-FineUI-Ajax': 'true'
            }, allow_redirects=False)

            if '提交成功' in r.text:
                # 可以发送邮件，以免发生错误，不需要的话删除即可
                send_mail(to_email=['xxxx@qq.com'],
                          subject=t.strftime('%Y-%m-%d %H:%M:%S') + '提交成功',
                          message=t.strftime('%Y-%m-%d %H:%M:%S') + '提交成功')
                print(t.strftime('%Y-%m-%d %H:%M:%S'), '提交成功')

                time.sleep(60)

    time.sleep(60)
