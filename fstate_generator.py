import base64
import datetime as dt
import json
import os
import re
import sys


def _generate_fstate_base64(fstate):
    fstate_json = json.dumps(fstate, ensure_ascii=False)
    fstate_bytes = fstate_json.encode("utf-8")
    return base64.b64encode(fstate_bytes).decode()


def generate_fstate_day(BaoSRQ, ShiFSH, ShiFZX, ddlSheng, ddlShi, ddlXian, XiangXDZ, ShiFZJ,
                        XingCM):
    with open(os.path.abspath(os.path.dirname(sys.argv[0])) + '/fstate_day.json', encoding='utf8') as f:
        fstate = json.loads(f.read())

    fstate['p1_BaoSRQ']['Text'] = BaoSRQ
    fstate['p1_ShiFSH']['SelectedValue'] = ShiFSH
    fstate['p1_ShiFZX']['SelectedValue'] = ShiFZX
    fstate['p1_ddlSheng']['F_Items'] = [[ddlSheng, ddlSheng, 1, '', '']]
    fstate['p1_ddlSheng']['SelectedValueArray'] = [ddlSheng]
    fstate['p1_ddlShi']['F_Items'] = [[ddlShi, ddlShi, 1, '', '']]
    fstate['p1_ddlShi']['SelectedValueArray'] = [ddlShi]
    fstate['p1_ddlXian']['F_Items'] = [[ddlXian, ddlXian, 1, '', '']]
    fstate['p1_ddlXian']['SelectedValueArray'] = [ddlXian]
    fstate['p1_XiangXDZ']['Text'] = XiangXDZ
    fstate['p1_ShiFZJ']['SelectedValue'] = ShiFZJ
    fstate['p1_pImages_HFimgXingCM']['Text'] = XingCM

    fstate_base64 = _generate_fstate_base64(fstate)
    t = len(fstate_base64) // 2
    fstate_base64 = fstate_base64[:t] + 'F_STATE' + fstate_base64[t:]

    return fstate_base64


def _html_to_json(html):
    return json.loads(html[html.find('=') + 1:])


def get_last_report(sess, t):
    print('#正在获取前一天的填报信息...')
    ShiFSH = '在上海（校内）'
    ShiFZX = '是'
    ddlSheng = '上海'
    ddlShi = '上海市'
    ddlXian = '宝山区'
    XiangXDZ = '上海大学1'
    ShiFZJ = '是'

    t = t - dt.timedelta(days=1)
    r = sess.get(f'https://selfreport.shu.edu.cn/ViewDayReport.aspx?day={t.year}-{t.month}-{t.day}')
    t = re.findall(r'^.*//\]', r.text, re.MULTILINE)[0]
    htmls = t.split(';var ')
    for i, h in enumerate(htmls):
        try:
            if 'ShiFSH' in h:
                print('-ShiFSH-')
                ShiFSH = _html_to_json(htmls[i - 1])['Text']
                print(ShiFSH)
            if 'ShiFZX' in h:
                print('-ShiFZX-')
                ShiFZX = _html_to_json(htmls[i - 1])['SelectedValue']
                print(ShiFZX)
            if 'ddlSheng' in h:
                print('-ddlSheng-')
                ddlSheng = _html_to_json(htmls[i - 1])['SelectedValueArray'][0]
                print(ddlSheng)
            if 'ddlShi' in h:
                print('-ddlShi-')
                ddlShi = _html_to_json(htmls[i - 1])['SelectedValueArray'][0]
                print(ddlShi)
            if 'ddlXian' in h:
                print('-ddlXian-')
                ddlXian = _html_to_json(htmls[i - 1])['SelectedValueArray'][0]
                print(ddlXian)
            if 'XiangXDZ' in h:
                print('-XiangXDZ-')
                XiangXDZ = _html_to_json(htmls[i - 1])['Text']
                print(XiangXDZ)
            if 'ShiFZJ' in h:
                print('-ShiFZJ-')
                ShiFZJ = _html_to_json(htmls[i - 1])['SelectedValue']
                print(ShiFZJ)
        except:
            print('获取前一天日报有错误', htmls[i - 1])

    return ShiFSH, ShiFZX, ddlSheng, ddlShi, ddlXian, XiangXDZ, ShiFZJ


def get_img_value(sess):
    print('#正在获取行程码信息...')

    XingCM = 'cYskH72v3ZA='

    r = sess.get(f'https://selfreport.shu.edu.cn/DayReport.aspx')
    t = re.findall(r'^.*//\]', r.text, re.MULTILINE)[0]
    htmls = t.split(';var ')
    for i, h in enumerate(htmls):
        try:
            if 'p1$pImages$HFimgXingCM' in h:
                XingCM = _html_to_json(htmls[i - 1])['Text']
        except:
            print('获取行程码有错误，使用默认行程码', htmls[i - 1])

    return XingCM


if __name__ == '__main__':
    print(generate_fstate_day())
