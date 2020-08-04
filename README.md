# 上海大学在校生每日两报自动打卡

程序为python脚本文件，修改配置文件相关信息，设置后台运行脚本，脚本会根据配置文件信息自动进行每日两报。

## 特点

- 可在`setting_config.yaml`自定义打卡时间、报送体温。

- 如果配置了邮件服务器的话会在填报失败的情况下发邮件提醒。

  设置原因：由于学校每日两报服务器数据库有一定概率出问题，实际提交成功，但服务器返回的是失败信息。

- 可在`setting_config.yaml`自定义填报成功是否进行邮件提醒。

- 程序运行中修改 `report_config.yaml` 可以在下一次提交时生效。

- 邮件服务器不是必须的，根据需要修改。

- 邮件smtp服务器更改为使用SSL协议端口号，可以适应阿里云服务器等默认关闭25端口的服务器。

## 用法
1. 修改 `report_config.yaml`

   ```yaml
   # 邮件提醒服务设置，如果不需要， 将email下的字段设置为null即可
   email:
     from: "12345@qq.com"                    # 发送邮件的地址
     username: "12345@qq.com"	       # 登陆邮箱的账号
     password: "QQmima"	                   # smtp服务授权码，请进入邮箱设置进行查看
     smtp: "smtp.qq.com"						 # smtp服务器
     port: 465                                                  # smtp服务器SSL协议端口号，大多数邮箱默认为465
   
   users:
     - id: "user1"	                                           # 学号
       pwd: "pwd"	                                        # 密码
       email_to: "user1@qq.com"	      # 接受报送成功邮件的邮箱地址
     - id: "user2"
       pwd: "pwd"
       email_to: "user2@qq.com"
     - id: "user3"
       pwd: "pwd"
       email_to: "user3@qq.com"
   ```
   
2. 修改`setting_config.yaml`

   ```yaml
   # 设置“每日一报”填报成功是否发送邮件
   # true：发送
   # false：不发送
   send_email: false
   
   # 早上申报时间,建议填写7点或8点，依据自己需要填写
   morning_hour: 7
   
   # 晚上申报时间，建议填写20点
   night_hour: 20
   
   # 申报的时间区间
   # 如morning_hour和night_hour填写为7和20，minute填为10，则会在7:10-7:11、20:10-20:11进行填报
   minute: 10
   
   # 温度
   # 如填写36.3，则会在36.3-0.2， 36.3+0.2之间选择随机数填报
   temperature: 36.3
   ```

3. 测试（可选）

   - 测试填写的所有账号密码是否正确，如果填写错误，程序会报错。

     - TODO：账号与密码错误会导致程序卡出，所以设计了这个功能用于防止运行时出错，没学网页内容分析，最近也没有时间学，希望有大神解决。

     ```python
     python main.py -r
     ```

   - 测试邮箱服务是否可使用

     ```python
     python main.py -e -a xxx@xx.com					# xxx@xx.com为接收测试邮件的账号
     ```

4. 启动程序：

   ```python
   # 针对启动后不关的Linux服务器，如阿里云服务器，启动程序，后台运行，输出结果导出shu_report.log中
   # 如使用个人电脑设置开机自启动，请自行搜索网上教程
   nohup python main.py > shu_report.log 2>&1 & 		  
   ```

## 要求

- python3
- 依赖：
  - pyyaml
  - beautifulsoup4
  - requests