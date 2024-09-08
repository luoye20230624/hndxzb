import requests
import re

# Fofa API 配置
FOFA_API_URL = "https://fofa.info/api/v1/search/all"
FOFA_API_TOKEN = "your_fofa_api_token_here"  # 替换为你的 Fofa API token

# 组播视频流的频道文件
CHANNELS = {
    "CCTV-1 综合[高清]": "http://8.8.8.8:8/udp/239.3.1.129:8008",
    "CCTV-2 财经[高清]": "http://8.8.8.8:8/udp/239.3.1.60:8084",
    # ... 其他频道
}

# 搜索条件
QUERY = 'server="HTTP core server by Rozhuk" && region="Beijing" && org="China Unicom Beijing Province Network"'

def get_ip_addresses():
    """从 Fofa 获取符合条件的 IP 地址。"""
    headers = {
        'Authorization': f'Bearer {FOFA_API_TOKEN}'
    }
    params = {
        'qbase64': QUERY.encode('base64').strip(),
        'fields': 'host',
        'size': 100
    }
    response = requests.get(FOFA_API_URL, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
    ip_addresses = [item['host'] for item in data['results']]
    return ip_addresses

def check_multicast_stream(ip_address, channel_url):
    """检查指定 IP 地址的组播视频流。"""
    try:
        response = requests.get(channel_url.replace('8.8.8.8', ip_address), timeout=10)
        return response.status_code == 200
    except requests.RequestException:
        return False

def main():
    ip_addresses = get_ip_addresses()
    with open('bjlt.txt', 'w') as file:
        for ip in ip_addresses:
            for channel_name, channel_url in CHANNELS.items():
                if check_multicast_stream(ip, channel_url):
                    file.write(f'{ip} - {channel_name} - {channel_url}\n')
                    print
