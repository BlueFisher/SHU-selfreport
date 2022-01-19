import datetime as dt
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path

import requests
import yaml
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

from login import login


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


def get_last_report(browser, t):
    print('#正在获取前一天的填报信息...')

    t = t - dt.timedelta(days=1)
    browser.get(f'https://selfreport.shu.edu.cn/ViewDayReport.aspx?day={t.year}-{t.month}-{t.day}')

    # 是否家庭地址
    ShiFSH = '上海' in browser.find_element(By.CSS_SELECTOR, '#ctl03_ShiFSH #ctl03_ShiFSH-inputEl').text
    ShiFZJ = 'f-checked' in browser.find_element(By.CSS_SELECTOR, '#ctl03_ShiFZJ .f-field-checkbox-icon').get_attribute('class')

    return ShiFSH, ShiFZJ


def report_day(browser: webdriver.Chrome,
               ShiFSH: bool,
               ShiFZJ: bool,
               t: dt.datetime):
    browser.get(f'https://selfreport.shu.edu.cn/DayReport.aspx?day={t.year}-{t.month}-{t.day}')
    time.sleep(1)

    # 承诺
    print('承诺')
    browser.find_element(By.ID, 'p1_ChengNuo-inputEl-icon').click()
    time.sleep(0.5)

    # 答题
    print('答题')
    checkboxes = browser.find_elements(By.CSS_SELECTOR, '#p1_pnlDangSZS .f-field-checkbox-icon')
    checkboxes[0].click()
    time.sleep(0.5)

    # 是否在上海
    print('是否在上海')
    checkboxes = browser.find_elements(By.CSS_SELECTOR, '#p1_ShiFSH .f-field-checkbox-icon')
    checkboxes[1 if ShiFSH else 2].click()
    time.sleep(0.5)

    # 是否家庭地址
    print('是否家庭地址')
    checkboxes = browser.find_elements(By.CSS_SELECTOR, '#p1_ShiFZJ .f-field-checkbox-icon')
    checkboxes[0 if ShiFZJ else 1].click()
    time.sleep(0.5)

    # 随申码
    SuiSM = browser.find_element(By.ID, 'p1_pImages_HFimgSuiSM-inputEl')
    if SuiSM.get_attribute('value') == '':
        print('未检测到已提交随申码')
        upload = browser.find_element(By.NAME, 'p1$pImages$fileSuiSM')
        upload.send_keys(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'xingcm.jpg')
        time.sleep(1)

        browser.find_element(By.CSS_SELECTOR, '#p1_pImages_fileSuiSM a.f-btn').click()
        time.sleep(1)

        print(SuiSM.get_attribute('value'))
    else:
        print(f'已提交随申码')

    # 行程码
    XingCM = browser.find_element(By.ID, 'p1_pImages_HFimgXingCM-inputEl')
    if XingCM.get_attribute('value') == '':
        print('未检测到已提交行程码')
        upload = browser.find_element(By.NAME, 'p1$pImages$fileXingCM')
        upload.send_keys(os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'xingcm.jpg')
        time.sleep(1)

        browser.find_element(By.CSS_SELECTOR, '#p1_pImages_fileXingCM a').click()
        time.sleep(1)

        print(XingCM.get_attribute('value'))
    else:
        print(f'已提交行程码')

    # 确认提交
    browser.find_element(By.ID, 'p1_ctl02_btnSubmit').click()
    time.sleep(1)
    messagebox = browser.find_element(By.CLASS_NAME, 'f-messagebox')

    if '确定' in messagebox.text:
        for a in messagebox.find_elements(By.TAG_NAME, 'a'):
            if a.text == '确定':
                a.click()
                break

        messagebox = browser.find_element(By.CLASS_NAME, 'f-messagebox')
        if '提交成功' in messagebox.text:
            return True
        else:
            print(messagebox.text)
            return False
    else:
        print(messagebox.text)
        return False


def view_messages(sess):
    r = sess.get('https://selfreport.shu.edu.cn/MyMessages.aspx')
    t = re.findall(r'^.*//\]', r.text, re.MULTILINE)[0]
    htmls = t.split(';var ')
    for h in htmls:
        if '未读' in h:
            f_items = json.loads(h[h.find('=') + 1:])['F_Items']
            for item in f_items:
                if '未读' in item[1]:
                    sess.get(f'https://selfreport.shu.edu.cn{item[4]}', allow_redirects=False)
                    print('已读', item[4])
            break


def notice(sess):
    sess.post('https://selfreport.shu.edu.cn/DayReportNotice.aspx')


if __name__ == "__main__":
    with open(Path(__file__).resolve().parent.joinpath('config.yaml'), encoding='utf8') as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    if 'users' in os.environ:
        for user_password in os.environ['users'].split(';'):
            user, password = user_password.split(',')
            config[user] = {
                'pwd': password
            }

    succeeded_users = []
    failed_users = []
    for i, user in enumerate(config):
        if user in ['00000000', '11111111']:
            continue

        user_abbr = user[-4:]
        print(f'====={user_abbr}=====')

        chrome_options = webdriver.ChromeOptions()

        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')

        s = Service('C:/App/chromedriver.exe')
        # s = Service()
        browser = webdriver.Chrome(options=chrome_options, service=s)
        browser.implicitly_wait(10)

        login_result = login(browser, user, config[user]['pwd'])

        if login_result:
            print('登录成功')
        else:
            print('登录失败')
            failed_users.append(user_abbr)

        sess = requests.Session()
        for cookie in browser.get_cookies():
            sess.cookies.set(cookie['name'], cookie['value'])

        notice(sess)
        view_messages(sess)

        now = get_time()
        ShiFSH, ShiFZJ = get_last_report(browser, now)

        try:
            report_result = report_day(browser,
                                       ShiFSH,
                                       ShiFZJ,
                                       now)
        except:
            print(traceback.format_exc())
            report_result = False

        if report_result:
            print(f'{now} 每日一报提交成功')
            succeeded_users.append(user_abbr)
        else:
            print(f'{now} 每日一报提交失败')
            failed_users.append(user_abbr)

        if i < len(config) - 1:
            time.sleep(120)

    if len(failed_users) != 0:
        succeeded_users = ", ".join(succeeded_users)
        failed_users = ", ".join(failed_users)
        print(f'[{succeeded_users}] 每日一报提交成功，[{failed_users}] 每日一报提交失败，查看日志获取详情')
        sys.exit(1)
