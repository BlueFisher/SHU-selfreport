# 上海大学在校生每日两报自动打卡

在配置文件 `config.yaml` 中修改学号密码，挂在服务器上即可。

对于在校同学早上7点晚上20点10-11分左右会自动打卡，目前设置每次报送体温在35.2℃~36.9℃之间随机。由于服务器数据库有一定概率出问题，实际提交成功，但服务器返回的是失败信息，如果配置了邮件服务器的话会在失败的情况下发邮件提醒（成功时不发）。

程序运行中修改 `config.yaml` 可以在下一次提交时生效。

邮件服务器不是必须的，根据需要修改。

## 用法：
1. 修改 `config.yaml`

   ```yaml
   email:	# 如果不需要接受邮件报送提醒服务，emial下字段设置为null即可
     from: "12345@qq.com" # 发送邮件的地址
     username: "12345@qq.com"	# 登陆邮箱的账号
     password: "QQmima"	# 邮箱密码
     smtp: "smtp.qq.com"	# smtp服务
   
   users:
     - id: "user1"	# 学号
       pwd: "pwd"	# 密码
       email_to: "user1@qq.com"	# 接受报送成功邮件的邮箱地址
     - id: "user2"
       pwd: "pwd"
       email_to: "user2@qq.com"
     - id: "user3"
       pwd: "pwd"
       email_to: "user3@qq.com"
   ```


2. 启动程序
```shell
nohup python -u main.py > shu_report.log 2>&1 &
或指定配置文件位置
nohup python -u main.py -c config.yaml > shu_report.log 2>&1 &
```

## 依赖：

- pyyaml
- beautifulsoup4
- requests