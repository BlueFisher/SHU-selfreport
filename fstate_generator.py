import base64
import datetime as dt
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont


def _generate_fstate_base64(fstate):
    fstate_json = json.dumps(fstate, ensure_ascii=False)
    fstate_bytes = fstate_json.encode("utf-8")
    return base64.b64encode(fstate_bytes).decode()


def generate_fstate_day(BaoSRQ, ShiFSH, JinXXQ, ShiFZX, XiaoQu,
                        ddlSheng, ddlShi, ddlXian, ddlJieDao, XiangXDZ, ShiFZJ,
                        SuiSM, XingCM):
    with open('fstate_day.json', encoding='utf8') as f:
        fstate = json.loads(f.read())

    fstate['p1_BaoSRQ']['Text'] = BaoSRQ
    fstate['p1_P_GuoNei_ShiFSH']['SelectedValue'] = ShiFSH
    fstate['p1_P_GuoNei_JinXXQ']['SelectedValueArray'][0] = JinXXQ
    fstate['p1_P_GuoNei_ShiFZX']['SelectedValue'] = ShiFZX
    fstate['p1_P_GuoNei_XiaoQu']['SelectedValue'] = XiaoQu
    fstate['p1_ddlSheng']['F_Items'] = [[ddlSheng, ddlSheng, 1, '', '']]
    fstate['p1_ddlSheng']['SelectedValueArray'] = [ddlSheng]
    fstate['p1_ddlShi']['F_Items'] = [[ddlShi, ddlShi, 1, '', '']]
    fstate['p1_ddlShi']['SelectedValueArray'] = [ddlShi]
    fstate['p1_ddlXian']['F_Items'] = [[ddlXian, ddlXian, 1, '', '']]
    fstate['p1_ddlXian']['SelectedValueArray'] = [ddlXian]
    fstate['p1_ddlJieDao']['F_Items'] = [[ddlJieDao, ddlJieDao, 1, '', '']]
    fstate['p1_ddlJieDao']['SelectedValueArray'] = [ddlJieDao]
    fstate['p1_XiangXDZ']['Text'] = XiangXDZ
    fstate['p1_ShiFZJ']['SelectedValue'] = ShiFZJ
    # fstate['p1_P_GuoNei_pImages_HFimgSuiSM']['Text'] = SuiSM
    # fstate['p1_P_GuoNei_pImages_HFimgXingCM']['Text'] = XingCM

    fstate_base64 = _generate_fstate_base64(fstate)
    t = len(fstate_base64) // 2
    fstate_base64 = fstate_base64[:t] + 'F_STATE' + fstate_base64[t:]

    return fstate_base64


def _html_to_json(html):
    return json.loads(html[html.find('=') + 1:])


def get_ShouJHM(sess):
    print('#正在获取个人信息...')
    ShouJHM = '111111111'

    r = sess.get(f'https://selfreport.shu.edu.cn/PersonInfo.aspx')
    t = re.findall(r'^.*//\]', r.text, re.MULTILINE)[0]
    htmls = t.split(';var ')
    for i, h in enumerate(htmls):
        try:
            if 'ShouJHM' in h:
                print('-ShouJHM-')
                ShouJHM = _html_to_json(htmls[i - 1])['Text']
        except:
            print('获取个人信息有错误', htmls[i - 1])

    return ShouJHM


def get_last_report(sess, t):
    print('#正在获取前一天的填报信息...')
    ShiFSH = '在上海（校内）'
    JinXXQ = '宝山'
    ShiFZX = '是'
    XiaoQu = '宝山'
    ddlSheng = '上海'
    ddlShi = '上海市'
    ddlXian = '宝山区'
    ddlJieDao = '大场镇'
    XiangXDZ = '上海大学'
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
            if 'JinXXQ' in h:
                print('-JinXXQ-')
                JinXXQ = _html_to_json(htmls[i - 1])['Text']
                print(JinXXQ)
            if 'ShiFZX' in h:
                print('-ShiFZX-')
                ShiFZX = _html_to_json(htmls[i - 1])['SelectedValue']
                print(ShiFZX)
            if 'XiaoQu' in h:
                print('-XiaoQu-')
                XiaoQu = _html_to_json(htmls[i - 1])['Text']
                print(XiaoQu)
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
            if 'ddlJieDao' in h:
                print('-ddlJieDao-')
                ddlJieDao = _html_to_json(htmls[i - 1])['SelectedValueArray'][0]
                if ddlJieDao == '-1':
                    ddlJieDao = '大场镇'
                print(ddlJieDao)
            if 'XiangXDZ' in h:
                print('-XiangXDZ-')
                XiangXDZ = _html_to_json(htmls[i - 1])['Text']
                print(f'###{XiangXDZ[-2:]}')
            if 'ShiFZJ' in h:
                print('-ShiFZJ-')
                ShiFZJ = _html_to_json(htmls[i - 1])['SelectedValue']
                print(ShiFZJ)
        except:
            print('获取前一天日报有错误', htmls[i - 1], htmls[i])
    
    return ShiFSH, JinXXQ, ShiFZX, XiaoQu, ddlSheng, ddlShi, ddlXian, ddlJieDao, XiangXDZ, ShiFZJ


def _draw_XingCM(ShouJHM: str, t):
    
    work_path = Path(__file__).resolve().parent
    image = Image.open(str(work_path / 'xingcm.jpg'))

    font1 = ImageFont.truetype(str(work_path / 'yahei.ttf'), 30)
    font2 = ImageFont.truetype(str(work_path / 'yahei.ttf'), 36)

    draw = ImageDraw.Draw(image)
    draw.text((414, 380), f'{ShouJHM[:3]}****{ShouJHM[-4:]}的动态行程卡', font=font1, fill=(39, 39, 39), anchor='mm')
    draw.text((414, 460), '更新于：' + t.strftime('%Y-%m-%d %H:%M:%S'), font=font2, fill=(143, 142, 147), anchor='mm')
    img_path = str(Path(__file__).resolve().parent.joinpath('xingcm_a.jpg'))
    image.save(img_path, 'jpeg')

    return img_path


def upload_img(sess, view_state, is_SuiSM, ShouJHM, t):
    img_path = _draw_XingCM(ShouJHM, t)

    target = 'p1$P_GuoNei$pImages$fileSuiSM' if is_SuiSM else 'p1$P_GuoNei$pImages$fileXingCM'
    with open(img_path, 'rb') as f:
        r = sess.post('https://selfreport.shu.edu.cn/DayReport.aspx', data={
            '__EVENTTARGET': target,
            '__VIEWSTATE': view_state
        }, files={
            target: f
        }, headers={
            'X-Requested-With': 'XMLHttpRequest',
            'X-FineUI-Ajax': 'true'
        }, allow_redirects=False)

    ret = re.search(r'Text&quot;:&quot;(.*?)&quot;}\)', r.text)
    if ret is None:
        return None
    else:
        return ret.group(1)


def get_img_value(sess, ShouJHM, t):
    print('#正在获取随申码、行程码信息...')

    SuiSM = 'cYskH72v3ZA='
    XingCM = 'cYskH72v3ZA='

    r = sess.get(f'https://selfreport.shu.edu.cn/DayReport.aspx')

    soup = BeautifulSoup(r.text, 'html.parser')
    view_state = soup.find('input', attrs={'name': '__VIEWSTATE'})
    view_state = view_state['value']

    ret = re.findall(r'^.*//\]', r.text, re.MULTILINE)[0]
    htmls = ret.split(';var ')
    for i, h in enumerate(htmls):
        if 'p1_P_GuoNei_pImages_fileSuiSM' in h:
            try:
                SuiSM = _html_to_json(htmls[i - 1])['Text']
            except:
                print('没有获取到已提交随申码，开始自动上传')
                code = upload_img(sess, view_state, True, ShouJHM, t)
                if code is None:
                    print('上传随申码失败，使用默认随申码')
                else:
                    SuiSM = code

        if 'p1_P_GuoNei_pImages_fileXingCM' in h:
            try:
                XingCM = _html_to_json(htmls[i - 1])['Text']
            except:
                print('没有获取到已提交行程码，开始自动上传')
                code = upload_img(sess, view_state, False, ShouJHM, t)
                if code is None:
                    print('上传行程码失败，使用默认行程码')
                else:
                    XingCM = code

    return SuiSM, XingCM
