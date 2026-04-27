import re
import os
from datetime import datetime

# --- 配置区域 ---
CONFIG_PATH = '/etc/XrayR/config.yml'
PEAK_LIMIT = 35    # 高峰期限速 (Mbps)
NORMAL_LIMIT = 100 # 闲时限速 (Mbps)
PEAK_HOURS = range(19, 24) # 19:00 到 23:59

def get_target_limit():
    """根据当前时间判断目标限速"""
    current_hour = datetime.now().hour
    if current_hour in PEAK_HOURS:
        return PEAK_LIMIT
    return NORMAL_LIMIT

def update_xrayr_config():
    target_limit = get_target_limit()
    print(f"当前时间: {datetime.now().strftime('%H:%M')}, 目标限速值: {target_limit}Mbps")

    try:
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_lines = []
        changed = False
        
        # 匹配模式：SpeedLimit 后面跟着数字，确保不是注释行
        # 这里使用正则匹配，保持 6 个空格的缩进
        pattern = r'^\s*SpeedLimit:\s*(\d+)'
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                current_val = int(match.group(1))
                # 只有当当前值和目标值不一致时才修改
                if current_val != target_limit:
                    new_lines.append(f'      SpeedLimit: {target_limit} # Auto Updated\n')
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
            print("当前配置已是目标限速，无需修改。")

    except Exception as e:
        print(f"执行出错: {e}")

if __name__ == "__main__":
    update_xrayr_config()
