#!/bin/bash

# 远程下载 Python 脚本并保存到 /root
curl -s -o /root/speed_limit.py https://raw.githubusercontent.com/kispers/speed_limit/master/speed_limit.py

# 安装依赖
apt-get update && apt-get install -y python3-pip
pip3 install ruamel.yaml --break-system-packages || pip3 install ruamel.yaml

# 设置定时任务
PY_SCRIPT="/root/speed_limit.py"
LOG_PATH="/var/log/xrayr_auto.log"
CRON_JOB="*/30 * * * * /usr/bin/python3 $PY_SCRIPT >> $LOG_PATH 2>&1"

(crontab -l 2>/dev/null | grep -v "$PY_SCRIPT"; echo "$CRON_JOB") | crontab -

# 初次执行
python3 /root/speed_limit.py

echo "部署完成！"
