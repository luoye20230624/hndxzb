import time
import os
import re
import base64
import datetime
import requests
import threading
from queue import Queue
from datetime import datetime


# 线程安全的队列，用于存储下载任务
task_queue = Queue()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

urls = ["Beijing"]
channelsx = [
   "CCTV-1 综合[高清],http://8.8.8.8:8/udp/udp/239.3.1.129:8008",
   "CCTV-2 财经[高清],http://8.8.8.8:8/udp/udp/239.3.1.60:8084",
   "CCTV-3 综艺[高清],http://8.8.8.8:8/udp/udp/239.3.1.172:8001",
   "CCTV-4 中文国际[高清],http://8.8.8.8:8/udp/udp/239.3.1.105:8092",
   "CCTV-4 中文国际 欧洲[高清],http://8.8.8.8:8/udp/udp/239.3.1.213:4220",
   "CCTV-4 中文国际 美洲[高清],http://8.8.8.8:8/udp/udp/239.3.1.214:4220",
   "CCTV-5 体育[高清],http://8.8.8.8:8/udp/udp/239.3.1.173:8001",
   "CCTV-5+ 体育赛事[高清],http://8.8.8.8:8/udp/udp/239.3.1.130:8004",
   "CCTV-6 电影[高清],http://8.8.8.8:8/udp/udp/239.3.1.174:8001",
   "CCTV-7 国防军事[高清],http://8.8.8.8:8/udp/udp/239.3.1.61:8104",
   "CCTV-8 电视剧[高清],http://8.8.8.8:8/udp/udp/239.3.1.175:8001",
   "CCTV-9 纪录[高清],http://8.8.8.8:8/udp/udp/239.3.1.62:8112",
   "CCTV-10 科教[高清],http://8.8.8.8:8/udp/udp/239.3.1.63:8116",
   "CCTV-11 戏曲[高清],http://8.8.8.8:8/udp/udp/239.3.1.152:8120",
   "CCTV-12 社会与法[高清],http://8.8.8.8:8/udp/udp/239.3.1.64:8124",
   "CCTV-13 新闻[高清],http://8.8.8.8:8/udp/udp/239.3.1.124:8128",
   "CCTV-14 少儿[高清],http://8.8.8.8:8/udp/udp/239.3.1.65:8132",
   "CCTV-15 音乐[高清],http://8.8.8.8:8/udp/udp/239.3.1.153:8136",
   "CCTV-16 奥林匹克[超清HDR],http://8.8.8.8:8/udp/udp/239.3.1.183:8001",
   "CCTV-16 奥林匹克[高清],http://8.8.8.8:8/udp/udp/239.3.1.184:8001",
   "CCTV-17 农业农村[高清],http://8.8.8.8:8/udp/udp/239.3.1.151:8144",
   "CCTV-4K 超高清[超清HDR],http://8.8.8.8:8/udp/udp/239.3.1.245:2000",
   "湖南卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.132:8012",
   "东方卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.136:8032",
   "浙江卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.137:8036",
   "江苏卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.135:8028",
   "深圳卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.134:8020",
   "广东卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.142:8048",
   "安徽卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.211:8064",
   "天津卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.141:1234",
   "重庆卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.122:8160",
   "山东卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.209:8052",
   "黑龙江卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.133:8016",
   "河北卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.148:8072",
   "辽宁卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.210:8056",
   "湖北卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.138:8044",
   "吉林卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.240:8172",
   "贵州卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.149:8076",
   "东南卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.156:8148",
   "江西卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.123:8164",
   "海南卫视,http://8.8.8.8:8/udp/udp/239.3.1.45:8304",
   "云南卫视,http://8.8.8.8:8/udp/udp/239.3.1.26:8108",
   "兵团卫视,http://8.8.8.8:8/udp/udp/239.3.1.144:4120",
   "厦门卫视,http://8.8.8.8:8/udp/udp/239.3.1.143:4120",
   "四川卫视,http://8.8.8.8:8/udp/udp/239.3.1.29:8288",
   "大湾区卫视,http://8.8.8.8:8/udp/udp/239.3.1.161:8001",
   "宁夏卫视,http://8.8.8.8:8/udp/udp/239.3.1.46:8124",
   "山西卫视,http://8.8.8.8:8/udp/udp/239.3.1.42:8172",
   "广西卫视,http://8.8.8.8:8/udp/udp/239.3.1.39:8300",
   "新疆卫视,http://8.8.8.8:8/udp/udp/239.3.1.48:8160",
   "河南卫视,http://8.8.8.8:8/udp/udp/239.3.1.27:8128",
   "甘肃卫视,http://8.8.8.8:8/udp/udp/239.3.1.49:8188",
   "西藏卫视,http://8.8.8.8:8/udp/udp/239.3.1.47:8164",
   "三沙卫视,http://8.8.8.8:8/udp/udp/239.3.1.155:4120",
   "陕西卫视,http://8.8.8.8:8/udp/udp/239.3.1.41:8140",
   "青海卫视,http://8.8.8.8:8/udp/udp/239.3.1.44:8184",
   "内蒙古卫视,http://8.8.8.8:8/udp/udp/239.3.1.43:8176",
   "BRTV北京卫视[高清],http://8.8.8.8:8/udp/udp/239.3.1.241:8000",
   "BRTV新闻[高清],http://8.8.8.8:8/udp/udp/239.3.1.159:8000",
   "BRTV影视[高清],http://8.8.8.8:8/udp/udp/239.3.1.158:8000",
   "BRTV文艺[高清],http://8.8.8.8:8/udp/udp/239.3.1.242:8000",
   "BRTV财经[高清],http://8.8.8.8:8/udp/udp/239.3.1.116:8000",
   "BRTV生活[高清],http://8.8.8.8:8/udp/udp/239.3.1.117:8000",
   "BRTV青年[高清],http://8.8.8.8:8/udp/udp/239.3.1.118:8000",
   "BRTV纪实科教[高清],http://8.8.8.8:8/udp/udp/239.3.1.115:8000",
   "BRTV卡酷少儿[高清],http://8.8.8.8:8/udp/udp/239.3.1.189:8000",
   "BRTV冬奥纪实[高清],http://8.8.8.8:8/udp/udp/239.3.1.243:8000",
   "BRTV冬奥纪实[超清HDR],http://8.8.8.8:8/udp/udp/239.3.1.120:8000",
   "BRTV冬奥纪实[超清],http://8.8.8.8:8/udp/udp/239.3.1.121:8000",
   "BRTV体育休闲[高清],http://8.8.8.8:8/udp/udp/239.3.1.243:8000",
   "BRTV国际频道[高清],http://8.8.8.8:8/udp/udp/239.3.1.235:8000",
   "爱上4K[超清],http://8.8.8.8:8/udp/udp/239.3.1.236:2000",
   "4K超清[超清],http://8.8.8.8:8/udp/udp/239.3.1.249:8001",
   "淘电影[高清],http://8.8.8.8:8/udp/udp/239.3.1.250:8001",
   "每日影院[高清],http://8.8.8.8:8/udp/udp/239.3.1.111:8001",
   "星影,http://8.8.8.8:8/udp/udp/239.3.1.94:4120",
   "动作影院,http://8.8.8.8:8/udp/udp/239.3.1.92:4120",
   "光影,http://8.8.8.8:8/udp/udp/239.3.1.84:4120",
   "喜剧影院,http://8.8.8.8:8/udp/udp/239.3.1.91:4120",
   "家庭影院,http://8.8.8.8:8/udp/udp/239.3.1.93:4120",
   "精选,http://8.8.8.8:8/udp/udp/239.3.1.74:4120",
   "经典电影,http://8.8.8.8:8/udp/udp/239.3.1.195:9024",
   "纪实人文[高清],http://8.8.8.8:8/udp/udp/239.3.1.212:8060",
   "金鹰纪实[高清],http://8.8.8.8:8/udp/udp/239.3.1.58:8156",
   "乐游[高清],http://8.8.8.8:8/udp/udp/239.3.1.207:8001",
   "风尚生活[高清],http://8.8.8.8:8/udp/udp/239.3.1.114:8001",
   "地理,http://8.8.8.8:8/udp/udp/239.3.1.71:4120",
   "淘剧场[高清],http://8.8.8.8:8/udp/udp/239.3.1.95:8001",
   "幸福剧场[高清],http://8.8.8.8:8/udp/udp/239.3.1.112:8001",
   "都市剧场[高清],http://8.8.8.8:8/udp/udp/239.3.1.203:8001",
   "淘娱乐[高清],http://8.8.8.8:8/udp/udp/239.3.1.100:8001",
   "幸福娱乐[高清],http://8.8.8.8:8/udp/udp/239.3.1.113:8001",
   "淘Baby[高清],http://8.8.8.8:8/udp/udp/239.3.1.238:8001",
   "萌宠TV[高清],http://8.8.8.8:8/udp/udp/239.3.1.102:8001",
   "动漫秀场[高清],http://8.8.8.8:8/udp/udp/239.3.1.202:8001",
   "中国交通[高清],http://8.8.8.8:8/udp/udp/239.3.1.188:8001",
   "朝阳融媒[高清],http://8.8.8.8:8/udp/udp/239.3.1.163:8001",
   "通州融媒[高清],http://8.8.8.8:8/udp/udp/239.3.1.221:8001",
   "密云电视台[高清],http://8.8.8.8:8/udp/udp/239.3.1.154:8001",
   "房山电视台[高清],http://8.8.8.8:8/udp/udp/239.3.1.96:8001",
   "延庆电视台,http://8.8.8.8:8/udp/udp/239.3.1.187:8001",
   "法治天地[高清],http://8.8.8.8:8/udp/udp/239.3.1.204:8001",
   "CGTN 新闻[高清],http://8.8.8.8:8/udp/udp/239.3.1.215:4220",
   "CGTN 记录[高清],http://8.8.8.8:8/udp/udp/239.3.1.216:4220",
   "CGTN 西班牙语[高清],http://8.8.8.8:8/udp/udp/239.3.1.217:4220",
   "CGTN 法语[高清],http://8.8.8.8:8/udp/udp/239.3.1.218:4220",
   "CGTN 阿拉伯语[高清],http://8.8.8.8:8/udp/udp/239.3.1.219:4220",
   "CGTN 俄语[高清],http://8.8.8.8:8/udp/udp/239.3.1.220:4220",
   "睛彩竞技[高清],http://8.8.8.8:8/udp/udp/239.3.1.125:8001",
   "睛彩篮球[高清],http://8.8.8.8:8/udp/udp/239.3.1.126:8001",
   "睛彩羽毛球[高清],http://8.8.8.8:8/udp/udp/239.3.1.127:8001",
   "睛彩广场舞[高清],http://8.8.8.8:8/udp/udp/239.3.1.128:8001",
   "魅力足球[高清],http://8.8.8.8:8/udp/udp/239.3.1.201:8001",
   "茶频道[高清],http://8.8.8.8:8/udp/udp/239.3.1.165:8001",
   "淘精彩[高清],http://8.8.8.8:8/udp/udp/239.3.1.178:8001",
   "快乐垂钓[高清],http://8.8.8.8:8/udp/udp/239.3.1.164:8001",
   "生活时尚[高清],http://8.8.8.8:8/udp/udp/239.3.1.206:8001",
   "游戏风云[高清],http://8.8.8.8:8/udp/udp/239.3.1.205:8001",
   "金色学堂[高清],http://8.8.8.8:8/udp/udp/239.3.1.208:8001",
   "CETV1[高清],http://8.8.8.8:8/udp/udp/239.3.1.57:8152",
   "CETV2,http://8.8.8.8:8/udp/udp/239.3.1.54:4120",
   "CETV3,http://8.8.8.8:8/udp/udp/239.3.1.55:4120",
   "CETV4,http://8.8.8.8:8/udp/udp/239.3.1.56:4120",
   "少儿动画,http://8.8.8.8:8/udp/udp/239.3.1.199:9000",
   "热播剧场,http://8.8.8.8:8/udp/udp/239.3.1.194:9020",
   "解密,http://8.8.8.8:8/udp/udp/239.3.1.75:4120",
   "军事,http://8.8.8.8:8/udp/udp/239.3.1.76:4120",
   "军旅剧场,http://8.8.8.8:8/udp/udp/239.3.1.68:4120",
   "动画,http://8.8.8.8:8/udp/udp/239.3.1.80:4120",
   "古装剧场,http://8.8.8.8:8/udp/udp/239.3.1.69:4120",
   "嘉佳卡通,http://8.8.8.8:8/udp/udp/239.3.1.147:9268",
   "国学,http://8.8.8.8:8/udp/udp/239.3.1.77:4120",
   "城市剧场,http://8.8.8.8:8/udp/udp/239.3.1.67:4120",
   "墨宝,http://8.8.8.8:8/udp/udp/239.3.1.83:4120",
   "好学生,http://8.8.8.8:8/udp/udp/239.3.1.81:4120",
   "山东教育,http://8.8.8.8:8/udp/udp/239.3.1.52:4120",
   "戏曲,http://8.8.8.8:8/udp/udp/239.3.1.78:4120",
   "早教,http://8.8.8.8:8/udp/udp/239.3.1.79:4120",
   "武侠剧场,http://8.8.8.8:8/udp/udp/239.3.1.90:4120",
   "武术,http://8.8.8.8:8/udp/udp/239.3.1.87:4120",
   "爱生活,http://8.8.8.8:8/udp/udp/239.3.1.86:4120",
   "美人,http://8.8.8.8:8/udp/udp/239.3.1.73:4120",
   "美妆,http://8.8.8.8:8/udp/udp/239.3.1.72:4120",
   "财富天下,http://8.8.8.8:8/udp/udp/239.3.1.53:9136",
   "足球,http://8.8.8.8:8/udp/udp/239.3.1.89:4120",
   "金鹰卡通,http://8.8.8.8:8/udp/udp/239.3.1.51:9252",
   "鉴赏,http://8.8.8.8:8/udp/udp/239.3.1.82:4120",
   "音乐现场,http://8.8.8.8:8/udp/udp/239.3.1.70:4120",
   "魅力时尚,http://8.8.8.8:8/udp/udp/239.3.1.196:9012",
]

results = []
channel = []
urls_all = []
resultsx = []
resultxs = []
error_channels = []

for url in urls:
    url_0 = str(base64.b64encode((f'server="HTTP core server by Rozhuk" && region="{url}" && org="China Unicom Beijing Province Network"').encode("utf-8")), "utf-8")
    url_64 = f'https://fofa.info/result?qbase64={url_0}'
    print(url_64)
    try:
        response = requests.get(url_64, headers=headers, timeout=15)
        page_content = response.text
        print(f" {url}  访问成功")
        pattern = r'href="(http://\d+\.\d+\.\d+\.\d+:\d+)"'
        page_urls = re.findall(pattern, page_content)
        for urlx in page_urls:
            try:
                response = requests.get(url=urlx + '/stat', timeout=1)
                response.raise_for_status()  # 返回状态码不是200异常
                page_content = response.text
                pattern = r'connections online'
                page_proctabl = re.findall(pattern, page_content)
                if page_proctabl:
                    urls_all.append(urlx)
                    print(f"{urlx} 可以访问")

            except requests.RequestException as e:
                pass
    except:
        print(f"{url_64} 访问失败")
        pass

urls_all = set(urls_all)  # 去重得到唯一的URL列表
for urlx in urls_all:
    channel = [f'{name},{url.replace("http://8.8.8.8:8", urlx)}' for name, url in
               [line.strip().split(',') for line in channelsx]]
    results.extend(channel)

results = sorted(results)
# with open("itv.txt", 'w', encoding='utf-8') as file:
#     for result in results:
#         file.write(result + "\n")
#         print(result)


# 定义工作线程函数
def worker():
    while True:
        result = task_queue.get()
        channel_name, channel_url = result.split(',', 1)
        try:
            response = requests.get(channel_url, stream=True, timeout=3)
            if response.status_code == 200:
                result = channel_name, channel_url
                resultsx.append(result)
                numberx = (len(resultsx) + len(error_channels)) / len(results) * 100
                print(
                    f"可用频道：{len(resultsx)} , 不可用频道：{len(error_channels)} 个 , 总频道：{len(results)} 个 ,总进度：{numberx:.2f} %。")
            else:
                error_channels.append(result)
                numberx = (len(resultsx) + len(error_channels)) / len(results) * 100
                print(
                    f"可用频道：{len(resultsx)} 个 , 不可用频道：{len(error_channels)} , 总频道：{len(results)} 个 ,总进度：{numberx:.2f} %。")
        except:
            error_channels.append(result)
            numberx = (len(resultsx) + len(error_channels)) / len(results) * 100
            print(
                f"可用频道：{len(resultsx)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(results)} 个 ,总进度：{numberx:.2f} %。")

        # 标记任务完成
        task_queue.task_done()


# 创建多个工作线程
num_threads = 20
for _ in range(num_threads):
    t = threading.Thread(target=worker, daemon=True)
    t.start()

# 添加下载任务到队列
for result in results:
    task_queue.put(result)

# 等待所有任务完成
task_queue.join()


def channel_key(channel_name):
    match = re.search(r'\d+', channel_name)
    if match:
        return int(match.group())
    else:
        return float('inf')  # 返回一个无穷大的数字作为关键字


for resulta in resultsx:
    channel_name, channel_url = resulta
    resultx = channel_name, channel_url
    resultxs.append(resultx)

# 对频道进行排序
resultxs.sort(key=lambda x: channel_key(x[0]))

result_counter = 10  # 每个频道需要的个数

with open("bjlt.txt", 'w', encoding='utf-8') as file:
    channel_counters = {}
    file.write('央视频道,#genre#\n')
    for result in resultxs:
        channel_name, channel_url = result
        if 'CCTV' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1
    channel_counters = {}
    file.write('\n卫视频道,#genre#\n')
    for result in resultxs:
        channel_name, channel_url = result
        if '卫视' in channel_name or '凤凰' in channel_name or 'CHC' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1


    # 写入更新日期时间
    now = datetime.now()
    file.write(f"\n更新时间,#genre#\n")
    file.write(f"{now.strftime("%Y-%m-%d")},url\n")
    file.write(f"{now.strftime("%H:%M:%S")},url\n")

print(f"电视频道成功写入bjlt.txt")
