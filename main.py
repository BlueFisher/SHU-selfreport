import datetime as dt
import os
import time
from pathlib import Path

import yaml
from bs4 import BeautifulSoup

from fstate_generator import generate_fstate_day, generate_fstate_halfday, get_last_report
from login import login

NEED_BEFORE = False  # 如需补报则置为True，否则False
START_DT = dt.datetime(2020, 10, 10)  # 需要补报的起始日期


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


def report_day(sess, t):
    url = f'https://selfreport.shu.edu.cn/DayReport.aspx?day={t.year}-{t.month}-{t.day}'

    r = sess.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    view_state = soup.find('input', attrs={'name': '__VIEWSTATE'})

    if view_state is None:
        if '上海大学统一身份认证' in r.text:
            print('登录信息过期')
        else:
            print(r.text)
        return False

    BaoSRQ = t.strftime('%Y-%m-%d')
    ShiFSH, ShiFZX, ddlSheng, ddlShi, ddlXian, XiangXDZ, ShiFZJ = get_last_report(sess, t)
    print(f'是否在上海：{ShiFSH}', f'是否在校：{ShiFZX}')
    print(ddlSheng, ddlShi, ddlXian, f'###{XiangXDZ[-2:]}')
    print(f'是否为家庭地址：{ShiFZJ}')

    while True:
        try:
            r = sess.post(url, data={
                "__EVENTTARGET": "p1$ctl01$btnSubmit",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": view_state['value'],
                "__VIEWSTATEGENERATOR": "7AD7E509",
                "p1$ChengNuo": "p1_ChengNuo",
                "p1$BaoSRQ": BaoSRQ,
                "p1$DangQSTZK": "良好",
                "p1$TiWen": "",
                "p1$JiuYe_ShouJHM": "",
                "p1$JiuYe_Email": "",
                "p1$JiuYe_Wechat": "",
                "p1$QiuZZT": "",
                "p1$JiuYKN": "",
                "p1$JiuYSJ": "",
                "p1$GuoNei": "国内",
                "p1$ddlGuoJia$Value": "-1",
                "p1$ddlGuoJia": "选择国家",
                "p1$ShiFSH": ShiFSH,
                "p1$ShiFZX": ShiFZX,
                "p1$ddlSheng$Value": ddlSheng,
                "p1$ddlSheng": ddlSheng,
                "p1$ddlShi$Value": ddlShi,
                "p1$ddlShi": ddlShi,
                "p1$ddlXian$Value": ddlXian,
                "p1$ddlXian": ddlXian,
                "p1$XiangXDZ": XiangXDZ,
                "p1$ShiFZJ": ShiFZJ,
                "p1$FengXDQDL": "否",
                "p1$TongZWDLH": "否",
                "p1$CengFWH": "否",
                "p1$CengFWH_RiQi": "",
                "p1$CengFWH_BeiZhu": "",
                "p1$JieChu": "否",
                "p1$JieChu_RiQi": "",
                "p1$JieChu_BeiZhu": "",
                "p1$TuJWH": "否",
                "p1$TuJWH_RiQi": "",
                "p1$TuJWH_BeiZhu": "",
                "p1$QueZHZJC$Value": "否",
                "p1$QueZHZJC": "否",
                "p1$DangRGL": "否",
                "p1$GeLDZ": "",
                "p1$FanXRQ": "",
                "p1$WeiFHYY": "",
                "p1$ShangHJZD": "",
                "p1$DaoXQLYGJ": "没有",
                "p1$DaoXQLYCS": "没有",
                "p1$JiaRen_BeiZhu": "",
                "p1$SuiSM": "绿色",
                "p1$LvMa14Days": "是",
                "p1$Address2": "",
                "F_TARGET": "p1_ctl00_btnSubmit",
                "p1_ContentPanel1_Collapsed": "true",
                "p1_GeLSM_Collapsed": "false",
                "p1_Collapsed": "false",
                "F_STATE": generate_fstate_day(BaoSRQ, ShiFSH, ShiFZX,
                                               ddlSheng, ddlShi, ddlXian, XiangXDZ, ShiFZJ)
            }, headers={
                'X-Requested-With': 'XMLHttpRequest',
                'X-FineUI-Ajax': 'true'
            }, allow_redirects=False)
        except Exception as e:
            print(e)
            continue
        break

    if any(i in r.text for i in ['提交成功', '历史信息不能修改', '现在还没到晚报时间', '只能填报当天或补填以前的信息']):
        print(f'{t} 每日一报提交成功')
        return True
    else:
        print(f'{t} 每日一报提交失败')
        print(r.text)
        return False


def report_halfday(sess, t, temperature=37):
    ii = '1' if t.hour < 19 else '2'

    url = f'https://selfreport.shu.edu.cn/XueSFX/HalfdayReport.aspx?day={t.year}-{t.month}-{t.day}&t={ii}'

    r = sess.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    view_state = soup.find('input', attrs={'name': '__VIEWSTATE'})

    if view_state is None:
        if '上海大学统一身份认证' in r.text:
            print('登录信息过期')
        else:
            print(r.text)
        return False

    BaoSRQ = t.strftime('%Y-%m-%d')

    while True:
        try:
            r = sess.post(url, data={
                "__EVENTTARGET": "p1$ctl00$btnSubmit",
                "__EVENTARGUMENT": "",
                "__VIEWSTATE": "",
                "__VIEWSTATEGENERATOR": "DC4D08A3",
                "p1$ChengNuo": "p1_ChengNuo",
                "p1$BaoSRQ": BaoSRQ,
                "p1$DangQSTZK": "良好",
                "p1$TiWen": str(temperature),
                "p1$ZaiXiao": "宝山",
                "p1$ddlSheng$Value": "上海",
                "p1$ddlSheng": "上海",
                "p1$ddlShi$Value": "上海市",
                "p1$ddlShi": "上海市",
                "p1$ddlXian$Value": "宝山区",
                "p1$ddlXian": "宝山区",
                "p1$XiangXDZ": "上海大学",
                "p1$FengXDQDL": "否",
                "p1$TongZWDLH": "否",
                "p1$CengFWH": "否",
                "p1$CengFWH_RiQi": "",
                "p1$CengFWH_BeiZhu": "",
                "p1$JieChu": "否",
                "p1$JieChu_RiQi": "",
                "p1$JieChu_BeiZhu": "",
                "p1$TuJWH": "否",
                "p1$TuJWH_RiQi": "",
                "p1$TuJWH_BeiZhu": "",
                "p1$QueZHZJC$Value": "否",
                "p1$QueZHZJC": "否",
                "p1$DangRGL": "否",
                "p1$GeLDZ": "",
                "p1$JiaRen_BeiZhu": "",
                "p1$SuiSM": "绿色",
                "p1$LvMa14Days": "是",
                "p1$Address2": "",
                "F_TARGET": "p1_ctl00_btnSubmit",
                "p1_ContentPanel1_Collapsed": "true",
                "p1_GeLSM_Collapsed": "false",
                "p1_Collapsed": "false",
                'F_STATE': generate_fstate_halfday(BaoSRQ),
            }, headers={
                'X-Requested-With': 'XMLHttpRequest',
                'X-FineUI-Ajax': 'true'
            }, allow_redirects=False)
        except Exception as e:
            print(e)
            continue
        break

    if any(i in r.text for i in ['提交成功', '历史信息不能修改', '现在还没到晚报时间', '只能填报当天或补填以前的信息']):
        print(f'{t} 每日两报提交成功')
        return True
    else:
        print(f'{t} 每日两报提交失败')
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

        print(f'====={user[-4:]}=====')
        sess = login(user, config[user]['pwd'])

        if sess:
            now = get_time()

            if NEED_BEFORE:
                t = START_DT
                while t < now:
                    report_day(sess, t)
                    report_halfday(sess, t + dt.timedelta(hours=8))
                    report_halfday(sess, t + dt.timedelta(hours=20))

                    t = t + dt.timedelta(days=1)

            report_day(sess, get_time())
            # report_halfday(sess, get_time())

        time.sleep(60)
