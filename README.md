# 上海大学每日一报自动打卡

在配置文件 `config.yaml` 中修改学号密码，挂在服务器上即可。

对于在校同学早上7点晚上20点10-11分左右会自动打卡。由于服务器数据库有一定概率出问题，实际提交成功，但服务器返回的是失败信息，如果配置了邮件服务器的话会在失败的情况下发邮件提醒（成功时不发）。

程序运行中修改 `config.yaml` 可以在下一次提交时生效。

邮件服务器不是必须的，根据需要修改。

## 用法：
1. 修改 `config.yaml`

2. 启动程序
```shell
nohup python -u main.py > shu_report.log 2>&1 &
或指定配置文件位置
nohup python -u main.py -c config.yaml > shu_report.log 2>&1 &
```

