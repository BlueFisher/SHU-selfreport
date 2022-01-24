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
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from PIL import Image, ImageDraw, ImageFont

from login import login


RETRY = 5
RETRY_TIMEOUT = 120


class element_has_value():
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(*self.locator)   # Finding the referenced element
        if element.get_attribute('value') != '':
            return element
        else:
            return False


class element_has_no_value():
    def __init__(self, locator):
        self.locator = locator

    def __call__(self, driver):
        element = driver.find_element(*self.locator)   # Finding the referenced element
        if element.get_attribute('value') == '':
            return element
        else:
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


def get_last_report(browser: webdriver.Chrome, t):
    print('正在获取手机号...')
    browser.get('https://selfreport.shu.edu.cn/PersonInfo.aspx')
    time.sleep(1)

    # 手机号
    ShouJHM = browser.find_element(By.ID, 'persinfo_ctl00_ShouJHM-inputEl').get_attribute('value')

    print('正在获取前一天的填报信息...')

    t = t - dt.timedelta(days=1)
    browser.get(f'https://selfreport.shu.edu.cn/ViewDayReport.aspx?day={t.year}-{t.month}-{t.day}')
    time.sleep(1)

    # 是否在上海，在上海（校内），在上海（不在校内），不在上海
    ShiFSH = browser.find_element(By.CSS_SELECTOR, '#ctl03_ShiFSH #ctl03_ShiFSH-inputEl').text
    # 是否住校
    ShiFZX = 'f-checked' in browser.find_element(By.CSS_SELECTOR, '#ctl03_ShiFZX .f-field-checkbox-icon').get_attribute('class')
    # 省
    ddlSheng = browser.find_element(By.CSS_SELECTOR, '#ctl03_ddlSheng #ctl03_ddlSheng-inputEl').get_attribute('value')
    # 市
    ddlShi = browser.find_element(By.CSS_SELECTOR, '#ctl03_ddlShi #ctl03_ddlShi-inputEl').get_attribute('value')
    # 县
    ddlXian = browser.find_element(By.CSS_SELECTOR, '#ctl03_ddlXian #ctl03_ddlXian-inputEl').get_attribute('value')
    # 详细地址
    XiangXDZ = browser.find_element(By.CSS_SELECTOR, '#ctl03_XiangXDZ #ctl03_XiangXDZ-inputEl').get_attribute('value')
    # 是否家庭地址
    ShiFZJ = 'f-checked' in browser.find_element(By.CSS_SELECTOR, '#ctl03_ShiFZJ .f-field-checkbox-icon').get_attribute('class')

    return ShouJHM, ShiFSH, ShiFZX, ddlSheng, ddlShi, ddlXian, XiangXDZ, ShiFZJ


def draw_XingCM(ShouJHM: str, t):
    image = Image.open('xingcm.jpg')

    font1 = ImageFont.truetype('yahei.ttf', 30)
    font2 = ImageFont.truetype('yahei.ttf', 36)
    draw = ImageDraw.Draw(image)
    draw.text((414, 380), f'{ShouJHM[:3]}****{ShouJHM[-4:]}的动态行程卡', font=font1, fill=(39, 39, 39), anchor='mm')
    draw.text((414, 460), '更新于：' + t.strftime('%Y-%m-%d %H:%M:%S'), font=font2, fill=(143, 142, 147), anchor='mm')
    image.save('xingcm_a.jpg', 'jpeg')

    return os.path.dirname(os.path.abspath(__file__)) + os.path.sep + 'xingcm_a.jpg'


def report_day(browser: webdriver.Chrome,
               ShouJHM, ShiFSH, ShiFZX, ddlSheng, ddlShi, ddlXian, XiangXDZ, ShiFZJ,
               t: dt.datetime):
    browser.get(f'https://selfreport.shu.edu.cn/DayReport.aspx?day={t.year}-{t.month}-{t.day}')
    time.sleep(1)

    print('承诺')
    browser.find_element(By.ID, 'p1_ChengNuo-inputEl-icon').click()

    print('答题')
    checkboxes = browser.find_elements(By.CSS_SELECTOR, '#p1_pnlDangSZS .f-field-checkbox-icon')
    checkboxes[0].click()

    print('是否在上海', ShiFSH)
    # 在上海（校内），在上海（不在校内），不在上海
    checkboxes = browser.find_elements(By.CSS_SELECTOR, '#p1_ShiFSH .f-field-checkbox-icon')
    if ShiFSH == '在上海（不在校内）':
        checkboxes[1].click()
    elif ShiFSH == '不在上海':
        checkboxes[2].click()
    else:
        checkboxes[0].click()
    time.sleep(1)

    print('是否住校', ShiFZX)
    try:
        checkboxes = browser.find_elements(By.CSS_SELECTOR, '#p1_ShiFZX .f-field-checkbox-icon')
        checkboxes[0 if ShiFZX else 1].click()
    except Exception as e:
        print('是否住校提交失败')

    print('省市县详细地址', ddlSheng, ddlShi, ddlXian, XiangXDZ[:2])
    elem = browser.find_element(By.CSS_SELECTOR, "#p1_ddlSheng input[name='p1$ddlSheng$Value']")
    browser.execute_script('''
        var elem = arguments[0];
        var value = arguments[1];
        elem.value = value;
    ''', elem, ddlSheng)

    elem = browser.find_element(By.CSS_SELECTOR, "#p1_ddlShi input[name='p1$ddlShi$Value']")
    browser.execute_script('''
        var elem = arguments[0];
        var value = arguments[1];
        elem.value = value;
    ''', elem, ddlShi)

    elem = browser.find_element(By.CSS_SELECTOR, "#p1_ddlXian input[name='p1$ddlXian$Value']")
    browser.execute_script('''
        var elem = arguments[0];
        var value = arguments[1];
        elem.value = value;
    ''', elem, ddlXian)

    elem = browser.find_element(By.CSS_SELECTOR, "#p1_XiangXDZ #p1_XiangXDZ-inputEl")
    browser.execute_script('''
        var elem = arguments[0];
        var value = arguments[1];
        elem.value = value;
    ''', elem, XiangXDZ)

    print('是否家庭地址', ShiFZJ)
    checkboxes = browser.find_elements(By.CSS_SELECTOR, '#p1_ShiFZJ .f-field-checkbox-icon')
    checkboxes[0 if ShiFZJ else 1].click()
    time.sleep(0.5)

    # 随申码
    try:
        SuiSM = browser.find_element(By.ID, 'p1_pImages_HFimgSuiSM-inputEl')
        if SuiSM.get_attribute('value') == '':
            print('未检测到已提交随申码')
            upload = browser.find_element(By.NAME, 'p1$pImages$fileSuiSM')
            upload.send_keys(draw_XingCM(ShouJHM, t))
            WebDriverWait(browser, 10).until(
                element_has_no_value((By.NAME, 'p1$pImages$fileSuiSM'))
            )

            browser.find_element(By.CSS_SELECTOR, '#p1_pImages_fileSuiSM a.f-btn').click()
            WebDriverWait(browser, 10).until(
                element_has_value((By.ID, 'p1_pImages_HFimgSuiSM-inputEl'))
            )

            print(SuiSM.get_attribute('value'))
        else:
            print(f'已提交随申码')
    except Exception as e:
        print(e)
        print('随申码提交失败')

    # 行程码
    try:
        XingCM = browser.find_element(By.ID, 'p1_pImages_HFimgXingCM-inputEl')
        if XingCM.get_attribute('value') == '':
            print('未检测到已提交行程码')
            upload = browser.find_element(By.NAME, 'p1$pImages$fileXingCM')
            upload.send_keys(draw_XingCM(ShouJHM, t))
            WebDriverWait(browser, 10).until(
                element_has_no_value((By.NAME, 'p1$pImages$fileXingCM'))
            )

            browser.find_element(By.CSS_SELECTOR, '#p1_pImages_fileXingCM a').click()
            WebDriverWait(browser, 10).until(
                element_has_value((By.ID, 'p1_pImages_HFimgXingCM-inputEl'))
            )

            print(XingCM.get_attribute('value'))
        else:
            print(f'已提交行程码')
    except Exception as e:
        print(e)
        print('行程码提交失败')

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
    try:
        r = sess.get('https://selfreport.shu.edu.cn/MyMessages.aspx')
        t = re.findall(r'^.*//\]', r.text, re.MULTILINE)[0]
        htmls = t.split(';var ')
        for h in htmls:
            if '未读' in h:
                f_items = json.loads(h[h.find('=') + 1:])['F_Items']
                for item in f_items:
                    if '未读' in item[1]:
                        sess.get(f'https://selfreport.shu.edu.cn{item[4]}')
                        print('已读', item[4])
                break
    except Exception as e:
        print(e)
        print('view_messages 失败，已忽略')


def notice(sess):
    try:
        sess.post('https://selfreport.shu.edu.cn/DayReportNotice.aspx')
    except Exception as e:
        print(e)
        print('notice 失败，已忽略')


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

        s = Service()
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
        for retry in range(RETRY):
            print(f'第{retry}次尝试填报')

            try:
                infos = get_last_report(browser, now)

                report_result = report_day(browser,
                                           *infos,
                                           now)

                break
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
            time.sleep(RETRY_TIMEOUT)

    if len(failed_users) != 0:
        succeeded_users = ", ".join(succeeded_users)
        failed_users = ", ".join(failed_users)
        print(f'[{succeeded_users}] 每日一报提交成功，[{failed_users}] 每日一报提交失败，查看日志获取详情')
        sys.exit(1)
