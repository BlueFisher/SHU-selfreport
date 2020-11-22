# 上海大学在校生每日两报自动打卡

程序为python脚本文件，修改配置文件相关信息，设置后台运行脚本，脚本会根据配置文件信息自动进行每日两报。

此版本为精简代码，并加入了一键补报功能。

## 用法

在 `config.yaml` 中设置所有需要打卡的学号密码

**本程序自带一键补报功能**，如需补报，定位到 `main.py` 第9行

```python
NEED_BEFORE = True  # 如需补报则置为True，否则False
MONTHS = [10, 11]  # 补报的月份，默认10月、11月
```

4. 启动程序：

```bash
# 针对Linux，启动程序，后台运行，输出结果导出shu_report.log
nohup python -u main.py > shu_report.log 2>&1 &
```

## 依赖

- python3
- 依赖：
  - pyyaml
  - beautifulsoup4
  - requests