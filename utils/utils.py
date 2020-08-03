# -- coding: utf-8 --

import time
import random

from selfreport.base import report, send_mail, get_time
from utils.config_utils import load_config


def test_report(report_config_path):
    users = load_config(report_config_path)['users']
    print("测试每日一报：")
    for user in users:
        t = get_time()
        is_successful = report(t, user['id'], user['pwd'], 36.2)
        if is_successful:
            print(t.strftime('%Y-%m-%d %H:%M:%S'), "{} 提交成功".format(user['id']))
        else:
            print(t.strftime('%Y-%m-%d %H:%M:%S'), "{} 提交失败".format(user['id']))


def test_send_email(addressee, report_config_path):
    sender_config = load_config(report_config_path)['email']

    if send_mail(sender_config, [addressee], "每日一报测试邮件", "每日一报邮件提醒功能正常开启"):
        print("邮件提醒功能测试成功")
    else:
        print("邮件提醒功能测试失败，可能为密钥错误或者您输入的邮箱错误！")


def auto_report(report_config_path, setting_config_path):
    report_config = load_config(report_config_path)
    setting_config = load_config(setting_config_path)
    
    while True:
        t = get_time()

        if t.hour == setting_config["morning_hour"] or t.hour == setting_config['night_hour']:
            if t.minute in [setting_config['minute'], setting_config['minute'] + 1]:
                for user in report_config['users']:
                    is_successful = report(t, user['id'], user['pwd'], setting_config['temperature'])

                    print('report', user['id'])
                    now = get_time()
                    if is_successful:
                        print(now.strftime('%Y-%m-%d %H:%M:%S'), '提交成功')
                        if setting_config['send_email']:
                            is_send = send_mail(report_config['email'], [user['email_to']],
                                                "{}月{}日每日一报提交成功".format(t.month, t.day),
                                                t.strftime('%Y-%m-%d %H:%M:%S') + "{}的每日一报提交成功".format(user['id']))
                            if not is_send:
                                print("发送每日一报成功邮件给{}失败!如您已对邮件发送模块进行测试，则可能为该发送对象的邮件错误。".format(user['id']))
                    else:
                        print(now.strftime('%Y-%m-%d %H:%M:%S'), '提交失败')
                        is_send = send_mail(report_config['email'], [user['email_to']],
                                            "{}月{}日每日一报提交失败".format(t.month, t.day),
                                            t.strftime('%Y-%m-%d %H:%M:%S') + "{}的每日一报提交失败".format(user['id']))
                        if not is_send:
                            print("发送每日一报失败邮件给{}失败!如您已对邮件发送模块进行测试，则可能为该发送对象的邮件错误。".format(user['id']))

                    # 如果有多个账号需要提交，不让程序在短时间内多次提交
                    time.sleep(int(random.uniform(5, 10)))

                time.sleep(60)

        time.sleep(60)
