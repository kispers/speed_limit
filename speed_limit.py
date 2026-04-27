cat << 'EOF' > install_speed_limit.sh
#!/bin/bash

# --- 变量配置 ---
PY_SCRIPT_PATH="/root/speed_limit.py"
LOG_PATH="/var/log/xrayr_auto.log"
CRON_JOB="*/30 * * * * /usr/bin/python3 $PY_SCRIPT_PATH >> $LOG_PATH 2>&1"

echo "1. 正在安装依赖..."
apt-get update && apt-get install -y python3-pip
# 备注：原代码使用了正则处理，不需要 ruamel.yaml，但为了兼容性保留安装
pip3 install ruamel.yaml --break-system-packages || pip3 install ruamel.yaml

echo "2. 正在创建 Python 脚本..."
cat << 'PYEOF' > $PY_SCRIPT_PATH
import re
import os
from datetime import datetime

# --- 配置区域 ---
CONFIG_PATH = '/etc/XrayR/config.yml'
PEAK_LIMIT = 35    # 高峰期限速 (Mbps)
NORMAL_LIMIT = 100 # 闲时限速 (Mbps)
PEAK_HOURS = range(19, 24) # 19:00 到 23:59

def get_target_limit():
    current_hour = datetime.now().hour
    return PEAK_LIMIT if current_hour in PEAK_HOURS else NORMAL_LIMIT

def update_xrayr_config():
    target_limit = get_target_limit()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M')}] 目标限速: {target_limit}Mbps")

    if not os.path.exists(CONFIG_PATH):
        print(f"错误: 找不到配置文件 {CONFIG_PATH}")
        return

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        changed = False
        pattern = r'^(\s*SpeedLimit:\s*)(\d+)'
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                prefix = match.group(1)
                current_val = int(match.group(2))
                if current_val != target_limit:
                    new_lines.append(f"{prefix}{target_limit} # Auto Updated\n")
                    changed = True
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)

        if changed:
            with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
                f.writelines(new_lines)
            print("配置已更新，正在重启 XrayR...")
            os.system('systemctl restart XrayR')
        else:
            print("限速值未变，跳过更新。")

    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    update_xrayr_config()
PYEOF

echo "3. 正在设置定时任务 (每30分钟执行一次)..."
(crontab -l 2>/dev/null | grep -v "$PY_SCRIPT_PATH"; echo "$CRON_JOB") | crontab -

echo "4. 初始化运行测试..."
python3 $PY_SCRIPT_PATH

echo "------------------------------------------------"
echo "✅ 部署完成！"
echo "脚本路径: $PY_SCRIPT_PATH"
echo "日志路径: $LOG_PATH"
echo "提示: 如果你的 XrayR 配置文件路径不是 /etc/XrayR/config.yml，请手动修改脚本。"
EOF

# 给脚本权限并执行
chmod +x install_speed_limit.sh
./install_speed_limit.sh
