import time
import os
import re
import base64
import datetime
import requests
import cv2  # OpenCV库，用于视频流检测
import numpy as np
import threading
from queue import Queue
from datetime import datetime

# 线程安全的队列，用于存储下载任务
task_queue = Queue()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}

urls = ["changsha", "zhuzhou", "xiangtan", "hengyang", "shaoyang", "yueyang", "changde", "zhangjiajie", "yiyang",
        "chenzhou", "yongzhou", "huaihua", "loudi"]
channelsx = [
    "湖南卫视,http://8.8.8.8:8/udp/239.76.245.115:1234", "湖南经视,http://8.8.8.8:8/udp/239.76.245.116:1234",
    "湖南都市,http://8.8.8.8:8/udp/239.76.245.117:1234", "湖南电视剧,http://8.8.8.8:8/udp/239.76.245.118:1234",
    "湖南电影,http://8.8.8.8:8/udp/239.76.245.119:1234", "湖南娱乐,http://8.8.8.8:8/udp/239.76.245.121:1234",
    "湖南国际,http://8.8.8.8:8/udp/239.76.245.124:1234", "湖南公共,http://8.8.8.8:8/udp/239.76.245.123:1234",
    "CCTV1,http://8.8.8.8:8/udp/239.76.245.51:1234", "CCTV1,http://8.8.8.8:8/udp/239.76.246.151:1234",
    "CCTV2,http://8.8.8.8:8/udp/239.76.246.152:1234", "CCTV3,http://8.8.8.8:8/udp/239.76.246.153:1234",
    "CCTV4,http://8.8.8.8:8/udp/239.76.245.195:1234", "CCTV4,http://8.8.8.8:8/udp/239.76.246.154:1234",
    "CCTV5,http://8.8.8.8:8/udp/239.76.246.155:1234", "CCTV5+,http://8.8.8.8:8/udp/239.76.246.168:1234",
    "CCTV6,http://8.8.8.8:8/udp/239.76.246.156:1234", "CCTV7,http://8.8.8.8:8/udp/239.76.246.157:1234",
    "CCTV8,http://8.8.8.8:8/udp/239.76.246.158:1234", "CCTV9,http://8.8.8.8:8/udp/239.76.246.159:1234",
    "CCTV10,http://8.8.8.8:8/udp/239.76.246.160:1234", "CCTV11,http://8.8.8.8:8/udp/239.76.245.251:1234",
    "CCTV12,http://8.8.8.8:8/udp/239.76.246.162:1234", "CCTV13,http://8.8.8.8:8/udp/239.76.246.93:1234",
    "CCTV14,http://8.8.8.8:8/udp/239.76.246.164:1234", "CCTV15,http://8.8.8.8:8/udp/239.76.245.252:1234",
    "CCTV16,http://8.8.8.8:8/udp/239.76.246.98:1234", "CCTV17,http://8.8.8.8:8/udp/239.76.245.238:1234",
    "CCTV 4K,http://8.8.8.8:8/udp/239.76.254.101:9000", "CCTV16 4k,http://8.8.8.8:8/udp/239.76.246.224:1234",
    "CCTV16 4k,http://8.8.8.8:8/udp/239.76.246.230:1234", "体育,http://8.8.8.8:8/udp/239.76.246.136:1234",
    "金鹰卡通,http://8.8.8.8:8/udp/239.76.245.120:1234", "金鹰纪实,http://8.8.8.8:8/udp/239.76.245.122:1234",
    "快乐垂钓,http://8.8.8.8:8/udp/239.76.245.127:1234", "湖南教育,http://8.8.8.8:8/udp/239.76.245.233:1234",
    "茶频道,http://8.8.8.8:8/udp/239.76.245.239:1234", "广东卫视,http://8.8.8.8:8/udp/239.76.245.189:1234",
    "东南卫视,http://8.8.8.8:8/udp/239.76.245.190:1234", "安徽卫视,http://8.8.8.8:8/udp/239.76.245.196:1234",
    "辽宁卫视,http://8.8.8.8:8/udp/239.76.245.197:1234", "江西卫视,http://8.8.8.8:8/udp/239.76.245.225:1234",
    "河北卫视,http://8.8.8.8:8/udp/239.76.245.199:1234", "贵州卫视,http://8.8.8.8:8/udp/239.76.245.198:1234",
    "江苏卫视,http://8.8.8.8:8/udp/239.76.246.181:1234", "东方卫视,http://8.8.8.8:8/udp/239.76.246.186:1234",
    "浙江卫视,http://8.8.8.8:8/udp/239.76.246.182:1234", "北京卫视,http://8.8.8.8:8/udp/239.76.246.184:1234",
    "天津卫视,http://8.8.8.8:8/udp/239.76.246.185:1234", "深圳卫视,http://8.8.8.8:8/udp/239.76.246.188:1234",
    "湖北卫视,http://8.8.8.8:8/udp/239.76.246.193:1234", "山东卫视,http://8.8.8.8:8/udp/239.76.246.195:1234",
    "黑龙江卫视,http://8.8.8.8:8/udp/239.76.246.200:1234", "吉林卫视,http://8.8.8.8:8/udp/239.76.246.201:1234",
    "河南卫视,http://8.8.8.8:8/udp/239.76.246.202:1234", "海南卫视,http://8.8.8.8:8/udp/239.76.246.203:1234",
    "四川卫视,http://8.8.8.8:8/udp/239.76.246.91:1234", "重庆卫视,http://8.8.8.8:8/udp/239.76.246.92:1234",
    "甘肃卫视,http://8.8.8.8:8/udp/239.76.246.94:1234", "中国教育,http://8.8.8.8:8/udp/239.76.245.192:1234",
    "长沙女姓,http://8.8.8.8:8/udp/239.76.245.23:1234", "长沙影视,http://8.8.8.8:8/udp/239.76.245.204:1234",
    "湘西综合,http://8.8.8.8:8/udp/239.76.245.208:1234", "湘西综合,http://8.8.8.8:8/udp/239.76.245.209:1234",
    "河南梨园,http://8.8.8.8:8/udp/239.76.245.179:1234", "武术世界,http://8.8.8.8:8/udp/239.76.245.181:1234",
    "张家界,http://8.8.8.8:8/udp/239.76.245.235:1234", "张家界综合,http://8.8.8.8:8/udp/239.76.245.234:1234",
    "CHC动作电影,http://8.8.8.8:8/udp/239.76.245.243:1234", "CHC高清电影,http://8.8.8.8:8/udp/239.76.245.242:1234",
    "CHC家庭影院,http://8.8.8.8:8/udp/239.76.245.241:1234", "快乐垂钓,http://8.8.8.8:8/udp/239.76.246.5:1234",
    "凤凰资讯,http://8.8.8.8:8/udp/239.76.246.8:1234", "凤凰中文,http://8.8.8.8:8/udp/239.76.246.7:1234",
    "湖南卫视,http://8.8.8.8:8/udp/239.76.246.101:1234", "湖南卫视,http://8.8.8.8:8/udp/239.76.246.100:1234",
    "湖南经视,http://8.8.8.8:8/udp/239.76.246.103:1234", "湖南国际,http://8.8.8.8:8/udp/239.76.246.102:1234",
    "湖南都市,http://8.8.8.8:8/udp/239.76.246.104:1234", "湖南娱乐,http://8.8.8.8:8/udp/239.76.246.105:1234",
    "湖南电影,http://8.8.8.8:8/udp/239.76.246.106:1234", "湖南公共,http://8.8.8.8:8/udp/239.76.246.109:1234",
    "湖南电视剧,http://8.8.8.8:8/udp/239.76.246.108:1234", "金鹰卡通,http://8.8.8.8:8/udp/239.76.246.107:1234",
    "金鹰纪实,http://8.8.8.8:8/udp/239.76.246.110:1234", "长沙政法,http://8.8.8.8:8/udp/239.76.246.122:1234",
    "长沙新闻,http://8.8.8.8:8/udp/239.76.246.121:1234", "健康电视,http://8.8.8.8:8/udp/239.76.246.127:1234",
    "欢笑剧场4K,http://8.8.8.8:8/udp/239.76.246.130:1234", "都市剧场,http://8.8.8.8:8/udp/239.76.246.215:1234",
    "极速汽车,http://8.8.8.8:8/udp/239.76.246.133:1234", "动漫秀场,http://8.8.8.8:8/udp/239.76.246.131:1234",
    "游戏风云,http://8.8.8.8:8/udp/239.76.246.132:1234", "凤凰中文,http://8.8.8.8:8/udp/239.76.246.134:1234",
    "凤凰中文,http://8.8.8.8:8/udp/239.76.253.135:9000", "凤凰资讯,http://8.8.8.8:8/udp/239.76.253.134:9000",
    "凤凰资讯,http://8.8.8.8:8/udp/239.76.246.135:1234", "体育,http://8.8.8.8:8/udp/239.76.253.136:9000",
    "全纪实,http://8.8.8.8:8/udp/239.76.246.137:1234", "法治天地,http://8.8.8.8:8/udp/239.76.246.138:1234",
    "生活时尚,http://8.8.8.8:8/udp/239.76.246.223:1234", "浏阳新闻,http://8.8.8.8:8/udp/239.76.248.6:1234",
    "常德综合,http://8.8.8.8:8/udp/239.76.248.10:1234", "常德公共,http://8.8.8.8:8/udp/239.76.248.11:1234",
    "衡阳综合,http://8.8.8.8:8/udp/239.76.248.13:1234", "衡阳公共,http://8.8.8.8:8/udp/239.76.248.14:1234",
    "娄底综合,http://8.8.8.8:8/udp/239.76.248.18:1234", "娄底公共,http://8.8.8.8:8/udp/239.76.248.19:1234",
    "张家界综合,http://8.8.8.8:8/udp/239.76.252.234:9000", "张家界,http://8.8.8.8:8/udp/239.76.252.235:9000",
    "邵阳新闻,http://8.8.8.8:8/udp/239.76.248.23:1234", "永州新闻,http://8.8.8.8:8/udp/239.76.248.57:1234",
    "怀化综合,http://8.8.8.8:8/udp/239.76.255.12:9000", "金色夕阳,http://8.8.8.8:8/udp/239.76.254.43:9000",
    "CCTV第一剧场,http://8.8.8.8:8/udp/239.76.254.49:9000", "CCTV风云足球,http://8.8.8.8:8/udp/239.76.254.52:9000",
    "CCTV风云音乐,http://8.8.8.8:8/udp/239.76.254.51:9000", "CCTV风云剧场,http://8.8.8.8:8/udp/239.76.254.50:9000",
    "CCTV女姓时尚,http://8.8.8.8:8/udp/239.76.254.55:9000", "CCTV央视文化精品,http://8.8.8.8:8/udp/239.76.254.56:9000",
    "CCTV世界地理,http://8.8.8.8:8/udp/239.76.254.57:9000", "CCTV兵器科技,http://8.8.8.8:8/udp/239.76.254.59:9000",
    "CCTV央视台球,http://8.8.8.8:8/udp/239.76.254.58:9000", "CCTV怀旧剧场,http://8.8.8.8:8/udp/239.76.254.53:9000",
    "CCTV电视指南,http://8.8.8.8:8/udp/239.76.254.61:9000", "CCTV央视高尔夫,http://8.8.8.8:8/udp/239.76.254.62:9000",
    "北京少儿,http://8.8.8.8:8/udp/239.76.254.81:9000", "快乐垂钓,http://8.8.8.8:8/udp/239.76.253.5:9000",
    "湖南卫视,http://8.8.8.8:8/udp/239.76.253.101:9000", "湖南国际,http://8.8.8.8:8/udp/239.76.253.102:9000",
    "湖南卫视,http://8.8.8.8:8/udp/239.76.253.100:9000", "湖南经视,http://8.8.8.8:8/udp/239.76.253.103:9000",
    "湖南都市,http://8.8.8.8:8/udp/239.76.253.104:9000", "湖南娱乐,http://8.8.8.8:8/udp/239.76.253.105:9000",
    "湖南电影,http://8.8.8.8:8/udp/239.76.253.106:9000", "湖南电视剧,http://8.8.8.8:8/udp/239.76.253.108:9000",
    "金鹰卡通,http://8.8.8.8:8/udp/239.76.253.107:9000", "湖南公共,http://8.8.8.8:8/udp/239.76.253.109:9000",
    "金鹰纪实,http://8.8.8.8:8/udp/239.76.253.110:9000", "长沙新闻,http://8.8.8.8:8/udp/239.76.253.121:9000",
    "长沙政法,http://8.8.8.8:8/udp/239.76.253.122:9000", "欢笑剧场4K,http://8.8.8.8:8/udp/239.76.253.130:9000",
    "极速汽车,http://8.8.8.8:8/udp/239.76.253.133:9000", "动漫秀场,http://8.8.8.8:8/udp/239.76.253.131:9000",
    "凤凰中文,http://8.8.8.8:8/udp/239.76.253.135:9000", "凤凰资讯,http://8.8.8.8:8/udp/239.76.253.134:9000",
    "体育,http://8.8.8.8:8/udp/239.76.253.136:9000", "全纪实,http://8.8.8.8:8/udp/239.76.253.137:9000",
    "金色学堂,http://8.8.8.8:8/udp/239.76.253.139:9000", "法治天地,http://8.8.8.8:8/udp/239.76.253.138:9000",
    "CCTV1,http://8.8.8.8:8/udp/239.76.253.151:9000", "CCTV2,http://8.8.8.8:8/udp/239.76.253.152:9000",
    "CCTV3,http://8.8.8.8:8/udp/239.76.253.153:9000", "CCTV4,http://8.8.8.8:8/udp/239.76.253.154:9000",
    "CCTV5,http://8.8.8.8:8/udp/239.76.253.155:9000", "CCTV5+,http://8.8.8.8:8/udp/239.76.253.168:9000",
    "CCTV6,http://8.8.8.8:8/udp/239.76.253.156:9000", "CCTV7,http://8.8.8.8:8/udp/239.76.253.157:9000",
    "CCTV8,http://8.8.8.8:8/udp/239.76.253.158:9000", "CCTV9,http://8.8.8.8:8/udp/239.76.253.159:9000",
    "CCTV10,http://8.8.8.8:8/udp/239.76.253.160:9000", "CCTV12,http://8.8.8.8:8/udp/239.76.253.162:9000",
    "CCTV13,http://8.8.8.8:8/udp/239.76.253.93:9000", "CCTV14,http://8.8.8.8:8/udp/239.76.253.164:9000",
    "CCTV16,http://8.8.8.8:8/udp/239.76.253.98:9000", "CCTV16 4K,http://8.8.8.8:8/udp/239.76.253.214:9000",
    "CCTV16 4K,http://8.8.8.8:8/udp/239.76.254.200:9000", "CCTV16 4K,http://8.8.8.8:8/udp/239.76.253.224:9000",
    "CCTV16 4K,http://8.8.8.8:8/udp/239.76.253.230:9000", "江苏卫视,http://8.8.8.8:8/udp/239.76.253.181:9000",
    "浙江卫视,http://8.8.8.8:8/udp/239.76.253.182:9000", "北京卫视,http://8.8.8.8:8/udp/239.76.253.184:9000",
    "天津卫视,http://8.8.8.8:8/udp/239.76.253.185:9000", "东方卫视,http://8.8.8.8:8/udp/239.76.253.186:9000",
    "深圳卫视,http://8.8.8.8:8/udp/239.76.253.188:9000", "湖北卫视,http://8.8.8.8:8/udp/239.76.253.193:9000",
    "山东卫视,http://8.8.8.8:8/udp/239.76.253.195:9000", "黑龙江卫视,http://8.8.8.8:8/udp/239.76.253.200:9000",
    "吉林卫视,http://8.8.8.8:8/udp/239.76.253.201:9000", "河南卫视,http://8.8.8.8:8/udp/239.76.253.202:9000",
    "海南卫视,http://8.8.8.8:8/udp/239.76.253.203:9000", "四川卫视,http://8.8.8.8:8/udp/239.76.253.91:9000",
    "重庆卫视,http://8.8.8.8:8/udp/239.76.253.92:9000", "广西卫视,http://8.8.8.8:8/udp/239.76.254.54:9000",
    "陕西卫视,http://8.8.8.8:8/udp/239.76.254.76:9000", "云南卫视,http://8.8.8.8:8/udp/239.76.254.60:9000",
    "青海卫视,http://8.8.8.8:8/udp/239.76.254.132:9000", "甘肃卫视,http://8.8.8.8:8/udp/239.76.253.94:9000",
    "都市剧场,http://8.8.8.8:8/udp/239.76.253.215:9000", "生活时尚,http://8.8.8.8:8/udp/239.76.253.223:9000",
    "长沙女姓,http://8.8.8.8:8/udp/239.76.252.23:9000", "湖南卫视,http://8.8.8.8:8/udp/239.76.252.115:9000",
    "湖南经视,http://8.8.8.8:8/udp/239.76.252.116:9000", "湖南电视剧,http://8.8.8.8:8/udp/239.76.252.118:9000",
    "湖南电影,http://8.8.8.8:8/udp/239.76.252.119:9000", "金鹰卡通,http://8.8.8.8:8/udp/239.76.252.120:9000",
    "湖南公共,http://8.8.8.8:8/udp/239.76.252.123:9000", "湖南娱乐,http://8.8.8.8:8/udp/239.76.252.121:9000",
    "金鹰纪实,http://8.8.8.8:8/udp/239.76.252.122:9000", "湖南国际,http://8.8.8.8:8/udp/239.76.252.124:9000",
    "湖南都市,http://8.8.8.8:8/udp/239.76.252.117:9000", "快乐垂钓,http://8.8.8.8:8/udp/239.76.252.127:9000",
    "河南梨园,http://8.8.8.8:8/udp/239.76.252.179:9000", "文物宝库,http://8.8.8.8:8/udp/239.76.252.180:9000",
    "武术世界,http://8.8.8.8:8/udp/239.76.252.181:9000", "广东卫视,http://8.8.8.8:8/udp/239.76.252.189:9000",
    "东南卫视,http://8.8.8.8:8/udp/239.76.252.190:9000", "中国教育,http://8.8.8.8:8/udp/239.76.252.192:9000",
    "安徽卫视,http://8.8.8.8:8/udp/239.76.252.196:9000", "辽宁卫视,http://8.8.8.8:8/udp/239.76.252.197:9000",
    "河北卫视,http://8.8.8.8:8/udp/239.76.252.199:9000", "贵州卫视,http://8.8.8.8:8/udp/239.76.252.198:9000",
    "长沙影视,http://8.8.8.8:8/udp/239.76.252.204:9000", "湘西综合,http://8.8.8.8:8/udp/239.76.252.208:9000",
    "湘西公共,http://8.8.8.8:8/udp/239.76.252.209:9000", "湘西公共,http://8.8.8.8:8/udp/239.76.252.210:9000",
    "湖南教育,http://8.8.8.8:8/udp/239.76.252.233:9000", "浏阳新闻,http://8.8.8.8:8/udp/239.76.255.6:9000",
    "湘西公共,http://8.8.8.8:8/udp/239.76.252.209:9000", "湘西公共,http://8.8.8.8:8/udp/239.76.252.210:9000",
    "湘西综合,http://8.8.8.8:8/udp/239.76.252.208:9000", "湘西综合,http://8.8.8.8:8/udp/239.76.245.208:1234",
    "衡阳公共,http://8.8.8.8:8/udp/239.76.255.14:9000", "衡阳综合,http://8.8.8.8:8/udp/239.76.255.13:9000",
    "衡阳县电视台,http://8.8.8.8:8/udp/239.76.255.26:9000", "邵阳公共,http://8.8.8.8:8/udp/239.76.255.22:9000",
    "邵阳综合,http://8.8.8.8:8/udp/239.76.255.21:9000", "娄底教育,http://8.8.8.8:8/udp/239.76.255.20:9000",
    "娄底综合,http://8.8.8.8:8/udp/239.76.255.18:9000", "娄底公共,http://8.8.8.8:8/udp/239.76.255.19:9000",
    "郴州综合,http://8.8.8.8:8/udp/239.76.253.75:9000", "张家界综合,http://8.8.8.8:8/udp/239.76.252.234:9000",
    "张家界公共,http://8.8.8.8:8/udp/239.76.252.235:9000", "怀化综合,http://8.8.8.8:8/udp/239.76.255.12:9000",
    "常德综合,http://8.8.8.8:8/udp/239.76.255.10:9000", "常德公共,http://8.8.8.8:8/udp/239.76.255.11:9000",
    "永州综合,http://8.8.8.8:8/udp/239.76.255.23:9000", "溆浦综合,http://8.8.8.8:8/udp/239.76.255.25:9000",
    "武冈综合,http://8.8.8.8:8/udp/239.76.255.29:9000", "新化,http://8.8.8.8:8/udp/239.76.255.31:9000",
    "津市,http://8.8.8.8:8/udp/239.76.255.30:9000", "桂东融媒,http://8.8.8.8:8/udp/239.76.253.231:9000",
    "道县综合,http://8.8.8.8:8/udp/239.76.255.28:9000", "永州公共,http://8.8.8.8:8/udp/239.76.255.24:9000",
    "株洲公共,http://8.8.8.8:8/udp/239.76.252.236:9000", "株洲综合,http://8.8.8.8:8/udp/239.76.255.1:9000",
    "湘潭公共,http://8.8.8.8:8/udp/239.76.255.5:9000", "湘潭综合,http://8.8.8.8:8/udp/239.76.255.4:9000",
    "益阳公共,http://8.8.8.8:8/udp/239.76.255.16:9000", "益阳综合,http://8.8.8.8:8/udp/239.76.255.15:9000",
    "岳阳综合,http://8.8.8.8:8/udp/239.76.255.7:9000", "岳阳科教,http://8.8.8.8:8/udp/239.76.255.9:9000",
    "岳阳公共,http://8.8.8.8:8/udp/239.76.255.8:9000",
]

results = []
channel = []
urls_all = []
resultsx = []
resultxs = []
error_channels = []

for url in urls:
    url_0 = str(base64.b64encode((f'"Rozhuk" && city="{url}" && org="Chinanet"').encode("utf-8")), "utf-8")
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
        if result is None:
            break  # 终止线程的信号

        channel_name, channel_url = result.split(',', 1)
        try:
            # 尝试用 OpenCV 打开视频流
            cap = cv2.VideoCapture(channel_url)
            
            # 等待一段时间以确保视频流可以开始
            if not cap.isOpened():
                raise Exception("无法打开视频流")
            
            # 尝试读取视频流的第一帧
            ret, frame = cap.read()
            if not ret:
                raise Exception("无法读取视频流")

            # 如果成功读取到帧，说明视频流有效
            result = channel_name, channel_url
            resultsx.append(result)
            cap.release()
            
            numberx = (len(resultsx) + len(error_channels)) / len(results) * 100
            print(f"可用频道：{len(resultsx)} , 不可用频道：{len(error_channels)} 个 , 总频道：{len(results)} 个 , 总进度：{numberx:.2f} %。")
        
        except Exception as e:
            # 如果出现任何错误，记录到错误频道列表中
            error_channels.append(result)
            numberx = (len(resultsx) + len(error_channels)) / len(results) * 100
            print(f"可用频道：{len(resultsx)} 个 , 不可用频道：{len(error_channels)} 个 , 总频道：{len(results)} 个 , 总进度：{numberx:.2f} %。")

        finally:
            # 确保任务完成标记被调用
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

with open("iptv_list.txt", 'w', encoding='utf-8') as file:
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
    channel_counters = {}
    file.write('\n湖南频道,#genre#\n')
    for result in resultxs:
        channel_name, channel_url = result
        if '湖南' in channel_name or '长沙' in channel_name or '金鹰' in channel_name or '娄底' in channel_name or '常德' \
                in channel_name or '张家界' in channel_name or '怀化' in channel_name or '浏阳' in channel_name or '湘西' \
                in channel_name or '衡阳' in channel_name or '邵阳' in channel_name or '郴州' in channel_name or '岳阳' in channel_name or '溆浦' \
                in channel_name or '武冈' in channel_name or '新化' in channel_name or '津市' in channel_name or '桂东' in channel_name \
                or '道县' in channel_name or '永州' in channel_name or '株洲' in channel_name or '湘潭' in channel_name or '益阳' in channel_name:
            if channel_name in channel_counters:
                if channel_counters[channel_name] >= result_counter:
                    continue
                else:
                    file.write(f"{channel_name},{channel_url}\n")
                    channel_counters[channel_name] += 1
            else:
                file.write(f"{channel_name},{channel_url}\n")
                channel_counters[channel_name] = 1

# TXT转M3U
import datetime
def txt_to_m3u(input_file, output_file):
    # 读取txt文件内容
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    # 打开m3u文件并写入内容
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=8)
    current_time = now.strftime("%m-%d %H:%M")
    with open(output_file, 'w', encoding='utf-8') as f:  
        f.write('#EXTM3U x-tvg-url="https://live.fanmingming.com/e.xml" catchup="append" catchup-source="?playseek=${(b)yyyyMMddHHmmss}-${(e)yyyyMMddHHmmss}"\n')
        f.write(f'#EXTINF:-1 group-title="更新时间{current_time}",湖南卫视\n')    
        f.write(f'http://222.243.28.152:9901/tsfile/live/0128_1.m3u8\n')    
        # 初始化genre变量
        genre = ''
        # 遍历txt文件内容
        for line in lines:
            line = line.strip()
            if "," in line:  # 防止文件里面缺失","号报错
                channel_name, channel_url = line.split(',', 1)
                if channel_url == '#genre#':
                    genre = channel_name
                    print(genre)
                else:
                    # 将频道信息写入m3u文件
                    f.write(f'#EXTINF:-1 tvg-id="{channel_name}" tvg-name="{channel_name}" tvg-logo="https://live.fanmingming.com/tv/{channel_name}.png" group-title="{genre}",{channel_name}\n')
                    f.write(f'{channel_url}\n')

# 将txt文件转换为m3u文件
txt_to_m3u('iptv_list.txt', 'iptv_list.m3u')
