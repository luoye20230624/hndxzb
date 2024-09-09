import requests
import json
import time

# 配置FOFA API
FOFA_EMAIL = "your_email@example.com"
FOFA_KEY = "your_fofa_api_key"
FOFA_SEARCH_URL = "https://fofa.info/api/v1/search/all"

# 搜索关键词
query = 'server="HTTP core server by Rozhuk" && region="Beijing" && org="China Unicom Beijing Province Network"'

# 发起FOFA查询
def get_fofa_results(query):
    params = {
        "email": FOFA_EMAIL,
        "key": FOFA_KEY,
        "qbase64": base64.b64encode(query.encode()).decode(),
        "size": 1000
    }
    response = requests.get(FOFA_SEARCH_URL, params=params)
    if response.status_code == 200:
        return response.json()["results"]
    else:
        print(f"FOFA查询失败，状态码: {response.status_code}")
        return []

# 检查URL是否可访问
def check_url(url):
    try:
        response = requests.get(url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

# 检查组播视频流是否可用
def check_multicast_stream(ip, port):
    stream_url = f"http://{ip}:{port}/udp/239.3.1.129:8008"
    return check_url(stream_url)

# 处理FOFA结果
def process_results(results):
    with open("bjlt.txt", "w") as file:
        for result in results:
            ip_port = result[0]
            ip, port = ip_port.split(":")
            
            # 检查组播状态页面
            status_url = f"http://{ip}:{port}/stat"
            if check_url(status_url):
                # 检查组播视频流
                if check_multicast_stream(ip, port):
                    # 替换原始频道文件中的IP地址
                    file.write(f"http://{ip}:{port}/udp/239.3.1.129:8008\n")
                    print(f"IP {ip} 组播流验证成功")
                else:
                    print(f"IP {ip} 组播流验证失败")
            else:
                print(f"IP {ip} 组播状态页面不可访问")

# 主函数
def main():
    results = get_fofa_results(query)
    process_results(results)

if __name__ == "__main__":
    main()
