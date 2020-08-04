# -- coding: utf-8 --

import time
import os
import random

from selfreport.base import report, send_mail, get_time, write_log, read_file_as_str
from utils.config_utils import load_config


def test_report(report_config_path):
    users = load_config(report_config_path)['users']
    print("测试每日一报：")
    for user in users:
        t = get_time()
        is_successful = report(t, user['id'], user['pwd'], 36.2)
        if is_successful:
            print(
                t.strftime('%Y-%m-%d %H:%M:%S'),
                "{} 提交成功".format(
                    user['id']))
        else:
            print(
                t.strftime('%Y-%m-%d %H:%M:%S'),
                "{} 提交失败".format(
                    user['id']))


def test_send_email(addressee, report_config_path):
    if addressee is None:
        print("邮件发送测试错误：请使用参数'--account'或'-a'输入收件邮箱")

    sender_config = load_config(report_config_path)['email']

    if send_mail(sender_config, [addressee], "每日两报测试邮件", "邮件提醒功能设置正常"):
        print("邮件提醒功能测试成功")
    else:
        print("邮件提醒功能测试失败，可能为密钥错误或者您输入的邮箱错误！")


def get_log_file_path(log_path):
    t = get_time()
    return os.path.join(log_path, '{}_{}.log'.format(t.month, t.day))


def get_status(is_true):
    return "成功" if is_true else "失败"


def get_report_name(t, morning_hour):
    return "晨报" if t.hour == morning_hour else "晚报"


def get_report_message(is_successful, t, now, user_id, morning_hour):
    return (now.strftime('%Y-%m-%d %H:%M:%S') +
            " {} {} {}".format(user_id, get_report_name(t, morning_hour), get_status(is_successful)))


def get_send_email_log_message(is_send, is_successful, now, user_id):
    return (now.strftime('%Y-%m-%d %H:%M:%S') +
            " {} 发送【报送{}】邮件 {}".format(
                user_id, get_status(is_successful), get_status(is_send)))


def write_report_log(is_successful, t, now, user_id, morning_hour, log_file_path):
    write_log(get_report_message(is_successful, t, now, user_id, morning_hour), log_file_path)


def get_subject(is_successful, t, morning_hour):
    return "{}月{}日{}提交{}".format(
        t.month, t.day, get_report_name(t, morning_hour), get_status(is_successful))


def send_report_email(is_successful, email, email_to,
                      t, now, user_id, setting_config):
    if is_successful:
        if setting_config['send_email']:
            return send_mail(email, email_to, get_subject(is_successful, t, setting_config['morning_hour']),
                             get_report_message(is_successful, t, now, user_id, setting_config['morning_hour']))
        else:
            return None
    else:
        return send_mail(email, email_to, get_subject(is_successful, t, setting_config['morning_hour']),
                         get_report_message(is_successful, t, now, user_id, setting_config['morning_hour']))


def write_send_email_log(is_send, is_successful, now, user_id, log_file_path):
    if is_send is not None:
        write_log(
            get_send_email_log_message(is_send, is_successful, now, user_id),
            log_file_path)


def auto_report(report_config_path, setting_config_path, log_path):
    if not os.path.isfile(report_config_path):
        raise TypeError(report_config_path + " does not exist")

    if not os.path.isfile(setting_config_path):
        raise TypeError(setting_config_path + " does not exist")

    if not os.path.isdir(log_path):
        raise TypeError(log_path + " does not exist")

    report_config = load_config(report_config_path)
    report_setting = load_config(setting_config_path)['report_setting']
    manager_setting = load_config(setting_config_path)['manager_setting']

    while True:
        t = get_time()

        if t.hour == report_setting["morning_hour"] or t.hour == report_setting['night_hour']:
            if t.minute in [report_setting['minute'],
                            report_setting['minute'] + 1]:
                log_file_path = get_log_file_path(log_path)

                for user in report_config['users']:
                    is_successful = report(
                        t, user['id'], user['pwd'], report_setting['temperature'])

                    now = get_time()
                    write_report_log(
                        is_successful, t, now, user['id'], report_setting['morning_hour'], log_file_path)
                    is_send = send_report_email(
                        is_successful, report_config['email'], [
                            user['email_to']], t, now, user['id'], report_setting)
                    write_send_email_log(is_send, is_successful, now, user['id'], log_file_path)

                    # 如果有多个账号需要提交，不让程序在短时间内多次提交
                    time.sleep(int(random.uniform(3, 6)))

        if manager_setting['send_email']:
            if t.hour == manager_setting['hours'] and t.minute == manager_setting['minute']:
                send_mail(report_config['email'], [manager_setting['email_to']], "{}月{}日 日志".format(t.month, t.day),
                          read_file_as_str(get_log_file_path(log_path)))

            time.sleep(61)

        time.sleep(60)