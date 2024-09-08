import requests
import re
import time
import base64

# 从fofa获取IP地址的函数
def fetch_ips_from_fofa(query):
    try:
        # base64编码查询字符串
        query_base64 = base64.b64encode(query.encode('utf-8')).decode('utf-8')
        # 发送请求到 fofa 并获取结果
        response = requests.get(f"https://fofa.info/result?qbase64={query_base64}", timeout=10)
        # 正则表达式提取IP地址
        ips = re.findall(r'(?:[0-9]{1,3}\.){3}[0-9]{1,3}:[0-9]+', response.text)
        return ips
    except Exception as e:
        print(f"从fofa获取IP失败: {e}")
        return []

# 验证 URL 是否可以访问的函数
def validate_stream(url):
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True
        else:
            return False
    except Exception as e:
        print(f"验证失败: {url}, 错误信息: {e}")
        return False

# 测试 URL 响应速度的函数
def test_speed(url):
    try:
        start_time = time.time()
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            end_time = time.time()
            return end_time - start_time
        else:
            return float('inf')
    except Exception as e:
        print(f"测速失败: {url}, 错误信息: {e}")
        return float('inf')

# 更新组播地址列表
def update_channel_list(ips):
    with open("channels.txt", 'r', encoding='utf-8') as file:
        channelsx = file.readlines()
    
    results = []

    for ip in ips:
        for line in channelsx:
            try:
                name, url = line.strip().split(',')
                url = url.replace("http://8.8.8.8:8", f"http://{ip}")
                
                print(f"验证 URL: {url}")  # 调试信息
                
                if validate_stream(url):
                    speed = test_speed(url)
                    print(f"测速结果: {speed} 秒")  # 调试信息
                    results.append((name, url, speed))
                else:
                    print(f"验证不通过: {url}")  # 调试信息
            except ValueError:
                print(f"跳过格式错误的行: {line}")
                continue

    return results

# 主要流程

# 定义FOFA查询字符串
query = '"Rozhuk" && region="Beijing" && org="China Unicom Beijing Province Network"'

# 从fofa获取IP地址
ips = fetch_ips_from_fofa(query)

if not ips:
    print("未能获取到任何IP地址。")
else:
    # 更新组播地址列表并验证可用性
    results = update_channel_list(ips)

    # 检查验证通过的结果
    print(f"验证通过的结果: {results}")  # 调试信息

    if results:
        # 按速度排序并选择最快的3个
        fastest_channels = sorted(results, key=lambda x: x[2])[:3]

        # 检查排序后的最快频道
        print(f"最快的频道: {fastest_channels}")  # 调试信息

        # 将最快的3个频道写入文件
        with open("bjlt.txt", 'w', encoding='utf-8') as file:
            for name, url, _ in fastest_channels:
                file.write(f"{name},{url}\n")
                print(f"写入文件: {name},{url}")  # 调试信息
    else:
        print("没有找到任何可用的频道。")
