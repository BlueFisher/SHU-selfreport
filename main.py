import datetime as dt
import time
import threading

import requests
import yaml
from bs4 import BeautifulSoup

NEED_BEFORE = True  # 如需补报则置为True，否则False
MONTHS = [10, 11]  # 补报的月份，默认10月、11月


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
            sess.post(r.url, data={
                'username': username,
                'password': password
            })
            sess.get('https://newsso.shu.edu.cn/oauth/authorize?response_type=code&client_id=WUHWfrntnWYHZfzQ5QvXUCVy&redirect_uri=https%3a%2f%2fselfreport.shu.edu.cn%2fLoginSSO.aspx%3fReturnUrl%3d%252fDefault.aspx&scope=1')
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

    if view_state is None:
        print(f'{username} 登录失败')
        print(r.text)
        return

    print(f'{username} 登录成功')

    return sess


def report(sess, t, temperature=37):
    ii = '1' if t.hour < 20 else '2'
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
        print(r.text)
        return False

    r = sess.post(url, data={
        '__EVENTTARGET': 'p1$ctl00$btnSubmit',
        '__VIEWSTATE': view_state['value'],
        '__VIEWSTATEGENERATOR': 'DC4D08A3',
        'p1$ChengNuo': 'p1_ChengNuo',
        'p1$BaoSRQ': t.strftime('%Y-%m-%d'),
        'p1$DangQSTZK': '良好',
        'p1$TiWen': str(temperature),
        'p1$TiWen': '37',
        'p1$ZaiXiao': '宝山',
        'p1$ddlSheng$Value': '上海',
        'p1$ddlSheng': '上海',
        'p1$ddlShi$Value': '上海市',
        'p1$ddlShi': '上海市',
        'p1$ddlXian$Value': '宝山区',
        'p1$ddlXian': '宝山区',
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
        'F_STATE': 'eyJwMV9CYW9TUlEiOnsiVGV4dCI6IjIwMjAtMTEtMjMifSwicDFfRGFuZ1FTVFpLIjp7IkZfSXRlbXMiOltbIuiJr+WlvSIsIuiJr+WlvSIsMV0sWyLkuI3pgIIiLCLkuI3pgIIiLDFdXSwiU2VsZWN0ZWRWYWx1ZSI6IuiJr+WlvSJ9LCJwMV9aaGVuZ1podWFuZyI6eyJIaWRkZW4iOnRydWUsIkZfSXRlbXMiOltbIuaEn+WGkiIsIuaEn+WGkiIsMV0sWyLlkrPll70iLCLlkrPll70iLDFdLFsi5Y+R54OtIiwi5Y+R54OtIiwxXV0sIlNlbGVjdGVkVmFsdWVBcnJheSI6W119LCJwMV9UaVdlbiI6eyJUZXh0IjoiMzcuMCJ9LCJwMV9aYWlYaWFvIjp7IlNlbGVjdGVkVmFsdWUiOiLlrp3lsbEiLCJGX0l0ZW1zIjpbWyLkuI3lnKjmoKEiLCLkuI3lnKjmoKEiLDFdLFsi5a6d5bGxIiwi5a6d5bGx5qCh5Yy6IiwxXSxbIuW7tumVvyIsIuW7tumVv+agoeWMuiIsMV0sWyLlmInlrpoiLCLlmInlrprmoKHljLoiLDFdLFsi5paw6Ze46LevIiwi5paw6Ze46Lev5qCh5Yy6IiwxXV19LCJwMV9kZGxTaGVuZyI6eyJGX0l0ZW1zIjpbWyItMSIsIumAieaLqeecgeS7vSIsMSwiIiwiIl0sWyLljJfkuqwiLCLljJfkuqwiLDEsIiIsIiJdLFsi5aSp5rSlIiwi5aSp5rSlIiwxLCIiLCIiXSxbIuS4iua1tyIsIuS4iua1tyIsMSwiIiwiIl0sWyLph43luoYiLCLph43luoYiLDEsIiIsIiJdLFsi5rKz5YyXIiwi5rKz5YyXIiwxLCIiLCIiXSxbIuWxseilvyIsIuWxseilvyIsMSwiIiwiIl0sWyLovr3lroEiLCLovr3lroEiLDEsIiIsIiJdLFsi5ZCJ5p6XIiwi5ZCJ5p6XIiwxLCIiLCIiXSxbIum7kem+meaxnyIsIum7kem+meaxnyIsMSwiIiwiIl0sWyLmsZ/oi48iLCLmsZ/oi48iLDEsIiIsIiJdLFsi5rWZ5rGfIiwi5rWZ5rGfIiwxLCIiLCIiXSxbIuWuieW+vSIsIuWuieW+vSIsMSwiIiwiIl0sWyLnpo/lu7oiLCLnpo/lu7oiLDEsIiIsIiJdLFsi5rGf6KW/Iiwi5rGf6KW/IiwxLCIiLCIiXSxbIuWxseS4nCIsIuWxseS4nCIsMSwiIiwiIl0sWyLmsrPljZciLCLmsrPljZciLDEsIiIsIiJdLFsi5rmW5YyXIiwi5rmW5YyXIiwxLCIiLCIiXSxbIua5luWNlyIsIua5luWNlyIsMSwiIiwiIl0sWyLlub/kuJwiLCLlub/kuJwiLDEsIiIsIiJdLFsi5rW35Y2XIiwi5rW35Y2XIiwxLCIiLCIiXSxbIuWbm+W3nSIsIuWbm+W3nSIsMSwiIiwiIl0sWyLotLXlt54iLCLotLXlt54iLDEsIiIsIiJdLFsi5LqR5Y2XIiwi5LqR5Y2XIiwxLCIiLCIiXSxbIumZleilvyIsIumZleilvyIsMSwiIiwiIl0sWyLnlJjogoMiLCLnlJjogoMiLDEsIiIsIiJdLFsi6Z2S5rW3Iiwi6Z2S5rW3IiwxLCIiLCIiXSxbIuWGheiSmeWPpCIsIuWGheiSmeWPpCIsMSwiIiwiIl0sWyLlub/opb8iLCLlub/opb8iLDEsIiIsIiJdLFsi6KW/6JePIiwi6KW/6JePIiwxLCIiLCIiXSxbIuWugeWkjyIsIuWugeWkjyIsMSwiIiwiIl0sWyLmlrDnloYiLCLmlrDnloYiLDEsIiIsIiJdLFsi6aaZ5rivIiwi6aaZ5rivIiwxLCIiLCIiXSxbIua+s+mXqCIsIua+s+mXqCIsMSwiIiwiIl0sWyLlj7Dmub4iLCLlj7Dmub4iLDEsIiIsIiJdXSwiU2VsZWN0ZWRWYWx1ZUFycmF5IjpbIuS4iua1tyJdfSwicDFfZGRsU2hpIjp7IkVuYWJsZWQiOnRydWUsIkZfSXRlbXMiOltbIi0xIiwi6YCJ5oup5biCIiwxLCIiLCIiXSxbIuS4iua1t+W4giIsIuS4iua1t+W4giIsMSwiIiwiIl1dLCJTZWxlY3RlZFZhbHVlQXJyYXkiOlsi5LiK5rW35biCIl19LCJwMV9kZGxYaWFuIjp7IkVuYWJsZWQiOnRydWUsIkZfSXRlbXMiOltbIi0xIiwi6YCJ5oup5Y6/5Yy6IiwxLCIiLCIiXSxbIum7hOa1puWMuiIsIum7hOa1puWMuiIsMSwiIiwiIl0sWyLljaLmub7ljLoiLCLljaLmub7ljLoiLDEsIiIsIiJdLFsi5b6Q5rGH5Yy6Iiwi5b6Q5rGH5Yy6IiwxLCIiLCIiXSxbIumVv+WugeWMuiIsIumVv+WugeWMuiIsMSwiIiwiIl0sWyLpnZnlronljLoiLCLpnZnlronljLoiLDEsIiIsIiJdLFsi5pmu6ZmA5Yy6Iiwi5pmu6ZmA5Yy6IiwxLCIiLCIiXSxbIuiZueWPo+WMuiIsIuiZueWPo+WMuiIsMSwiIiwiIl0sWyLmnajmtabljLoiLCLmnajmtabljLoiLDEsIiIsIiJdLFsi5a6d5bGx5Yy6Iiwi5a6d5bGx5Yy6IiwxLCIiLCIiXSxbIumXteihjOWMuiIsIumXteihjOWMuiIsMSwiIiwiIl0sWyLlmInlrprljLoiLCLlmInlrprljLoiLDEsIiIsIiJdLFsi5p2+5rGf5Yy6Iiwi5p2+5rGf5Yy6IiwxLCIiLCIiXSxbIumHkeWxseWMuiIsIumHkeWxseWMuiIsMSwiIiwiIl0sWyLpnZLmtabljLoiLCLpnZLmtabljLoiLDEsIiIsIiJdLFsi5aWJ6LSk5Yy6Iiwi5aWJ6LSk5Yy6IiwxLCIiLCIiXSxbIua1puS4nOaWsOWMuiIsIua1puS4nOaWsOWMuiIsMSwiIiwiIl0sWyLltIfmmI7ljLoiLCLltIfmmI7ljLoiLDEsIiIsIiJdXSwiU2VsZWN0ZWRWYWx1ZUFycmF5IjpbIuWuneWxseWMuiJdfSwicDFfRmVuZ1hEUURMIjp7IlNlbGVjdGVkVmFsdWUiOiLlkKYiLCJGX0l0ZW1zIjpbWyLmmK8iLCLmmK8iLDFdLFsi5ZCmIiwi5ZCmIiwxXV19LCJwMV9Ub25nWldETEgiOnsiU2VsZWN0ZWRWYWx1ZSI6IuWQpiIsIkZfSXRlbXMiOltbIuaYryIsIuaYryIsMV0sWyLlkKYiLCLlkKYiLDFdXX0sInAxX1hpYW5nWERaIjp7IlRleHQiOiLkuIrmtbflpKflraYifSwicDFfUXVlWkhaSkMiOnsiRl9JdGF_STATEVtcyI6W1si5pivIiwi5pivIiwxLCIiLCIiXSxbIuWQpiIsIuWQpiIsMSwiIiwiIl1dLCJTZWxlY3RlZFZhbHVlQXJyYXkiOlsi5ZCmIl19LCJwMV9EYW5nUkdMIjp7IlNlbGVjdGVkVmFsdWUiOiLlkKYiLCJGX0l0ZW1zIjpbWyLmmK8iLCLmmK8iLDFdLFsi5ZCmIiwi5ZCmIiwxXV19LCJwMV9HZUxTTSI6eyJIaWRkZW4iOnRydWUsIklGcmFtZUF0dHJpYnV0ZXMiOnt9fSwicDFfR2VMRlMiOnsiUmVxdWlyZWQiOmZhbHNlLCJIaWRkZW4iOnRydWUsIkZfSXRlbXMiOltbIuWxheWutumalOemuyIsIuWxheWutumalOemuyIsMV0sWyLpm4bkuK3pmpTnprsiLCLpm4bkuK3pmpTnprsiLDFdXSwiU2VsZWN0ZWRWYWx1ZSI6bnVsbH0sInAxX0dlTERaIjp7IkhpZGRlbiI6dHJ1ZX0sInAxX0NlbmdGV0giOnsiTGFiZWwiOiIyMDIw5bm0OeaciDI35pel5ZCO5piv5ZCm5Zyo5Lit6auY6aOO6Zmp5Zyw5Yy66YCX55WZ6L+HPHNwYW4gc3R5bGU9J2NvbG9yOnJlZDsnPu+8iOWkqea0peS4nOeWhua4r+WMuueesOa1t+i9qeWwj+WMuuOAgeWkqea0peaxieayveihl+OAgeWkqea0peS4reW/g+a4lOa4r+WGt+mTvueJqea1geWMukHljLrlkoxC5Yy644CB5rWm5Lic6JCl5YmN5p2R44CB5a6J5b6955yB6Zic6Ziz5biC6aKN5LiK5Y6/5oWO5Z+O6ZWH5byg5rSL5bCP5Yy644CB5rWm5Lic5ZGo5rWm6ZWH5piO5aSp5Y2O5Z+O5bCP5Yy644CB5rWm5Lic56Wd5qGl6ZWH5paw55Sf5bCP5Yy644CB5rWm5Lic5byg5rGf6ZWH6aG65ZKM6LevMTI25byE5bCP5Yy644CB5YaF6JKZ5Y+k5ruh5rSy6YeM5Lic5bGx6KGX6YGT5Yqe5LqL5aSE44CB5YaF6JKZ5Y+k5ruh5rSy6YeM5YyX5Yy66KGX6YGT77yJPC9zcGFuPiIsIkZfSXRlbXMiOltbIuaYryIsIuaYryIsMV0sWyLlkKYiLCLlkKYiLDFdXSwiU2VsZWN0ZWRWYWx1ZSI6IuWQpiJ9LCJwMV9DZW5nRldIX1JpUWkiOnsiSGlkZGVuIjp0cnVlfSwicDFfQ2VuZ0ZXSF9CZWlaaHUiOnsiSGlkZGVuIjp0cnVlfSwicDFfSmllQ2h1Ijp7IkxhYmVsIjoiMTHmnIgwOeaXpeiHszEx5pyIMjPml6XmmK/lkKbkuI7mnaXoh6rkuK3pq5jpo47pmanlnLDljLrlj5Hng63kurrlkZjlr4bliIfmjqXop6Y8c3BhbiBzdHlsZT0nY29sb3I6cmVkOyc+77yI5aSp5rSl5Lic55aG5riv5Yy6556w5rW36L2p5bCP5Yy644CB5aSp5rSl5rGJ5rK96KGX44CB5aSp5rSl5Lit5b+D5riU5riv5Ya36ZO+54mp5rWB5Yy6QeWMuuWSjELljLrjgIHmtabkuJzokKXliY3mnZHjgIHlronlvr3nnIHpmJzpmLPluILpoo3kuIrljr/mhY7ln47plYflvKDmtIvlsI/ljLrjgIHmtabkuJzlkajmtabplYfmmI7lpKnljY7ln47lsI/ljLrjgIHmtabkuJznpZ3moaXplYfmlrDnlJ/lsI/ljLrjgIHmtabkuJzlvKDmsZ/plYfpobrlkozot68xMjblvITlsI/ljLrjgIHlhoXokpnlj6Tmu6HmtLLph4zkuJzlsbHooZfpgZPlip7kuovlpITjgIHlhoXokpnlj6Tmu6HmtLLph4zljJfljLrooZfpgZPvvIk8L3NwYW4+IiwiU2VsZWN0ZWRWYWx1ZSI6IuWQpiIsIkZfSXRlbXMiOltbIuaYryIsIuaYryIsMV0sWyLlkKYiLCLlkKYiLDFdXX0sInAxX0ppZUNodV9SaVFpIjp7IkhpZGRlbiI6dHJ1ZX0sInAxX0ppZUNodV9CZWlaaHUiOnsiSGlkZGVuIjp0cnVlfSwicDFfVHVKV0giOnsiTGFiZWwiOiIxMeaciDA55pel6IezMTHmnIgyM+aXpeaYr+WQpuS5mOWdkOWFrOWFseS6pOmAmumAlOW+hOS4remrmOmjjumZqeWcsOWMujxzcGFuIHN0eWxlPSdjb2xvcjpyZWQ7Jz7vvIjlpKnmtKXkuJznlobmuK/ljLrnnrDmtbfovanlsI/ljLrjgIHlpKnmtKXmsYnmsr3ooZfjgIHlpKnmtKXkuK3lv4PmuJTmuK/lhrfpk77nianmtYHljLpB5Yy65ZKMQuWMuuOAgea1puS4nOiQpeWJjeadkeOAgeWuieW+veecgemYnOmYs+W4gumijeS4iuWOv+aFjuWfjumVh+W8oOa0i+Wwj+WMuuOAgea1puS4nOWRqOa1pumVh+aYjuWkqeWNjuWfjuWwj+WMuuOAgea1puS4nOelneahpemVh+aWsOeUn+Wwj+WMuuOAgea1puS4nOW8oOaxn+mVh+mhuuWSjOi3rzEyNuW8hOWwj+WMuuOAgeWGheiSmeWPpOa7oea0sumHjOS4nOWxseihl+mBk+WKnuS6i+WkhOOAgeWGheiSmeWPpOa7oea0sumHjOWMl+WMuuihl+mBk++8iTwvc3Bhbj4iLCJTZWxlY3RlZFZhbHVlIjoi5ZCmIiwiRl9JdGVtcyI6W1si5pivIiwi5pivIiwxXSxbIuWQpiIsIuWQpiIsMV1dfSwicDFfVHVKV0hfUmlRaSI6eyJIaWRkZW4iOnRydWV9LCJwMV9UdUpXSF9CZWlaaHUiOnsiSGlkZGVuIjp0cnVlfSwicDFfSmlhUmVuIjp7IkxhYmVsIjoiMTHmnIgwOeaXpeiHszEx5pyIMjPml6XlrrbkurrmmK/lkKbmnInlj5Hng63nrYnnl4fnirYifSwicDFfSmlhUmVuX0JlaVpodSI6eyJIaWRkZW4iOnRydWV9LCJwMV9TdWlTTSI6eyJTZWxlY3RlZFZhbHVlIjoi57u/6ImyIiwiRl9JdGVtcyI6W1si57qi6ImyIiwi57qi6ImyIiwxXSxbIum7hOiJsiIsIum7hOiJsiIsMV0sWyLnu7/oibIiLCLnu7/oibIiLDFdXX0sInAxX0x2TWExNERheXMiOnsiU2VsZWN0ZWRWYWx1ZSI6IuaYryIsIkZfSXRlbXMiOltbIuaYryIsIuaYryIsMV0sWyLlkKYiLCLlkKYiLDFdXX0sInAxIjp7IlRpdGxlIjoi5q+P5pel5Lik5oql77yI5LiK5Y2I77yJIiwiSUZyYW1lQXR0cmlidXRlcyI6e319fQ=='
    }, headers={
        'X-Requested-With': 'XMLHttpRequest',
        'X-FineUI-Ajax': 'true'
    }, allow_redirects=False)

    if any(i in r.text for i in ['提交成功', '历史信息不能修改', '现在还没到晚报时间', '只能填报当天或补填以前的信息']):
        print(f'{t} 提交成功')
        return True
    else:
        print(r.text)
        return False


with open('config.yaml', encoding='utf8') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)
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

                            if not report(sess, t):
                                user_login_status[user]['sess'] = None
                                user_login_status[user]['has_before'] = False
                                break
                            else:
                                user_login_status[user]['has_before'] = True

            t = get_time()
            if not report(sess, t):
                user_login_status[user]['sess'] = None

    time.sleep(60 * 10)
