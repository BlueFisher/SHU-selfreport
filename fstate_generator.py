import base64
import datetime as dt
import json
import random
import re
from pathlib import Path
import os
import sys

def _generate_fstate_base64(fstate):
    fstate_json = json.dumps(fstate, ensure_ascii=False)
    fstate_bytes = fstate_json.encode("utf-8")
    return base64.b64encode(fstate_bytes).decode()


def generate_fstate_day(BaoSRQ, ShiFSH, ShiFZX, ddlSheng, ddlShi, ddlXian, XiangXDZ, ShiFZJ):
    with open(os.path.abspath(os.path.dirname(sys.argv[0]))+'/fstate_day.json', encoding='utf8') as f:
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

    fstate_base64 = _generate_fstate_base64(fstate)
    t = len(fstate_base64) // 2
    fstate_base64 = fstate_base64[:t] + 'F_STATE' + fstate_base64[t:]

    return fstate_base64


def generate_fstate_halfday(BaoSRQ):
    with open(Path(__file__).resolve().parent.joinpath('fstate_halfday.json'), encoding='utf8') as f:
        fstate = json.loads(f.read())

    fstate['p1_BaoSRQ']['Text'] = BaoSRQ

    fstate_base64 = _generate_fstate_base64(fstate)

    return fstate_base64


def _html_to_json(html):
    return json.loads(html[html.find('=') + 1:])


# 随机生成地址
def get_random_address():
    address = [chr(random.randint(0x4e00, 0x9fbf)) for _ in range(3)]
    address = ''.join(address) + '路'
    address += str(random.randint(1, 999)) + '号'
    address += str(random.randint(1, 20)) + '0' + str(random.randint(1, 9)) + '室'
    return address


def get_last_report(sess, t):
    ShiFSH = '是'
    ShiFZX = '否'
    ddlSheng = '上海'
    ddlShi = '上海市'
    ddlXian = '宝山区'
    XiangXDZ = get_random_address()
    ShiFZJ = '是'

    t = t - dt.timedelta(days=1)
    r = sess.get(f'https://selfreport.shu.edu.cn/ViewDayReport.aspx?day={t.year}-{t.month}-{t.day}')
    t = re.findall(r'^.*//\]', r.text, re.MULTILINE)[0]
    htmls = t.split(';var ')
    for i, h in enumerate(htmls):
        if 'ShiFSH' in h:
            ShiFSH = _html_to_json(htmls[i - 1])['SelectedValue']
        if 'ShiFZX' in h:
            ShiFZX = _html_to_json(htmls[i - 1])['SelectedValue']
        if 'ddlSheng' in h:
            ddlSheng = _html_to_json(htmls[i - 1])['SelectedValueArray'][0]
        if 'ddlShi' in h:
            ddlShi = _html_to_json(htmls[i - 1])['SelectedValueArray'][0]
        if 'ddlXian' in h:
            ddlXian = _html_to_json(htmls[i - 1])['SelectedValueArray'][0]
        if 'XiangXDZ' in h:
            XiangXDZ = _html_to_json(htmls[i - 1])['Text']
        if 'ShiFZJ' in h:
            ShiFZJ = _html_to_json(htmls[i - 1])['SelectedValue']

    return ShiFSH, ShiFZX, ddlSheng, ddlShi, ddlXian, XiangXDZ, ShiFZJ


if __name__ == '__main__':
    print(generate_fstate_day())
    print(generate_fstate_halfday())
