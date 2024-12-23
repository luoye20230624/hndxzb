import os
import re
import time
import requests
import threading
from queue import Queue
from threading import Thread
from datetime import datetime
from datetime import timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed


def should_run():
    time_file_path = 'update_time.txt'

    # 如果时间文件不存在，说明需要执行
    if not os.path.exists(time_file_path):
        return True

    # 读取时间文件的内容
    with open(time_file_path, 'r') as file:
        last_run_time_str = file.read().strip()
        last_run_time = datetime.strptime(last_run_time_str, '%Y-%m-%d %H:%M:%S')

    # 获取当前时间
    current_time = datetime.now()

    # 判断当前时间与上次执行时间的差异是否大于等于两天
    if current_time - last_run_time >= timedelta(days=0):
        return True

    return False


def update_run_time():
    time_file_path = 'update_time.txt'
    current_time = datetime.now()
    with open(time_file_path, 'w') as file:
        file.write(current_time.strftime('%Y-%m-%d %H:%M:%S'))


def check_ip(ip, port):
    try:
        url = f"http://{ip}:{port}/stat"
        response = requests.get(url, timeout=1)  # 设置超时为1秒
        if response.status_code == 200 and 'Multi stream daemon' in response.text:
            print(f"扫描到有效ip: {ip}:{port}")
            return f"{ip}:{port}"
    except requests.RequestException:
        return None
    return None


def generate_ips(ip_part, option):
    a, b, c, d = map(int, ip_part.split('.'))
    if option == 0:
        return [f"{a}.{b}.{c}.{d}" for d in range(1, 256)]
    else:
        return [f"{a}.{b}.{c}.{d}" for c in range(0, 256) for d in range(0, 256)]


def save_to_file(foldername, filename, valid_ips):
    if not os.path.exists(foldername):
        os.makedirs(foldername)

    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"{current_date}_{filename}"

    filepath = os.path.join(foldername, filename)

    with open(filepath, 'w') as f:
        for ip in valid_ips:
            f.write(f"{ip}\n")


def read_config(config_path):
    configs = []
    try:
        with open(config_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(',')
                    ip_port = parts[0].strip()  # 去除IP:端口部分前后的空格
                    if len(parts) == 2:
                        option = int(parts[1].strip())  # 去除扫描类型部分前后的空格，并转换为整数
                    else:
                        option = 0  # 默认为0
                    if ':' in ip_port:
                        ip, port = ip_port.split(':')
                        configs.append((ip, port, option))
                    else:
                        print(f"配置文件中的 IP:端口 格式错误: {line}")
    except FileNotFoundError:
        print(f"配置文件 '{config_path}' 不存在。")
        return []
    except ValueError as e:
        print(f"配置文件格式错误: {e}")
        return []
    except Exception as e:
        print(f"读取配置文件出错: {e}")
        return []
    return configs


def replace_ip_in_channels(ip, channels):
    return [channel.replace("udp://", f"http://{ip}/udp/") for channel in channels]


# 定义一个集合，用于存储唯一的 IP 地址及端口组合
unique_ip_ports = set()

# 读取配置文件
if should_run():
    update_run_time()
    config_path = 'config.txt'
    configs = read_config(config_path)

    # 使用集合去除配置文件内重复的 IP 地址及端口
    unique_configs = []
    for ip_part, port, option in configs:
        ip_port = f"{ip_part}:{port}"
        if ip_port not in unique_ip_ports:
            unique_ip_ports.add(ip_port)
            unique_configs.append((ip_part, port, option))

    # 执行 IP 扫描
    all_valid_ips = []
    for ip_part, port, option in unique_configs:
        print(f"开始扫描 地址: {ip_part}, 端口: {port}, 类型: {option} （默认类型为0扫描D段，类型为1时扫描C,D段）")
        ips_to_check = generate_ips(ip_part, option)

        valid_ips = []
        total_ips = len(ips_to_check)
        checked_count = [0]


        def update_status(checked_count):
            while checked_count[0] < total_ips:
                print(f"扫描数量: {checked_count[0]}, 有效数量: {len(valid_ips)}")
                time.sleep(10)


        # 启动状态更新线程
        status_thread = threading.Thread(target=update_status, args=(checked_count,))
        status_thread.start()

        max_workers = 10 if option == 0 else 100  # 扫描IP线程数量
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_ip = {executor.submit(check_ip, ip, port): ip for ip in ips_to_check}
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                result = future.result()
                if result is not None:
                    valid_ips.append(result)
                checked_count[0] += 1

        # 等待状态线程结束
        status_thread.join()
        all_valid_ips.extend(valid_ips)

    save_to_file('ip', 'ip.txt', all_valid_ips)

    for ip in all_valid_ips:
        print(ip)

    # 替换组播ID并写入文件
    # 读取湖南_电信.txt文件中的频道列表
    with open('zubo/湖南_电信.txt', 'r', encoding='utf-8') as f:
        channels = f.readlines()

    # 将所有替换后的频道列表写入湖南_组播.txt文件中
    with open('湖南_组播.txt', 'w', encoding='utf-8') as f:
        for ip in all_valid_ips:
            replaced_channels = replace_ip_in_channels(ip, channels)
            for channel in replaced_channels:
                f.write(f"{channel}")
            f.write("\n")

    print(f"共扫描获取到有效IP {len(all_valid_ips)} 个，已全部匹配到湖南_组播.txt文件中。\n")

# 开始对组播源频道列表进行下载速度检测
# 定义一个全局队列，用于存储需要测速的频道信息
speed_test_queue = Queue()

# 用于存储测速结果的列表
speed_results = []


# 读取iptv_list.txt文件中的所有频道，并将它们添加到队列中
def load_channels_to_speed_test():
    with open('湖南_组播.txt', 'r', encoding='utf-8') as file:
        for line in file:
            channel_info = line.strip().split(',')
            if len(channel_info) >= 2:  # 假设至少有名称和URL
                name, url = channel_info[:2]  # 只取名称和URL
                speed_test_queue.put((name, url))


# 执行下载速度测试
def download_speed_test():
    while not speed_test_queue.empty():
        channel = speed_test_queue.get()
        name, url = channel
        download_time = 5  # 设置下载时间为 5 秒
        chunk_size = 1024  # 设置下载数据块大小为 1024 字节

        try:
            start_time = time.time()
            response = requests.get(url, stream=True, timeout=download_time)
            response.raise_for_status()
            size = 0
            for chunk in response.iter_content(chunk_size=chunk_size):
                size += len(chunk)
                if time.time() - start_time >= download_time:
                    break
            download_time = time.time() - start_time
            download_rate = round(size / download_time / 1024 / 1024, 2)
        except requests.RequestException as e:
            print(f"请求异常: {e}")
            download_rate = 0

        print(f"{name},{url}, {download_rate} MB/s")
        speed_test_queue.task_done()
        speed_results.append((download_rate, name, url))


# 创建并启动线程
def start_speed_test_threads(num_threads):
    threads = []
    for _ in range(num_threads):
        thread = Thread(target=download_speed_test)
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()


load_channels_to_speed_test()
start_speed_test_threads(10)  # 测试下载速度线程数
speed_results.sort(reverse=True)

# 写入分类排序后的频道信息
with open("speed.txt", 'w', encoding='utf-8') as file:
    for result in speed_results:
        download_rate, channel_name, channel_url = result
        if download_rate >= 0.01:  # 只写入下载速度大于或等于 0.2 MB/s 的频道
            file.write(f"{channel_name},{channel_url},{download_rate}\n")

# 对经过下载速度检测后的所有组播频道列表进行分组排序
# 从测速后的文件中读取频道列表
with open('speed.txt', 'r', encoding='utf-8') as file:
    channels = []
    for line in file:
        line = line.strip()
        if line:
            parts = line.split(',')
            if len(parts) == 3:
                name, url, speed = parts
                channels.append((name, url, speed))


def natural_key(string):
    return [int(text) if text.isdigit() else text.lower() for text in re.split(r'(\d+)', string)]


def group_and_sort_channels(channels):
    groups = {
        '央视频道,#genre#': [],
        '卫视频道,#genre#': [],
        '湖南频道,#genre#': [],
        '其他频道,#genre#': []
    }

    for name, url, speed in channels:
        if 'cctv' in name.lower():
            groups['央视频道,#genre#'].append((name, url, speed))
        elif '卫视' in name or '凤凰' in name or '翡翠' in name or 'CHC' in name:
            groups['卫视频道,#genre#'].append((name, url, speed))
        elif ('湖南' in name or '金鹰' in name or '长沙' in name or '娄底' in name or '岳阳' in name or '张家界' in name
              or '常德' in name or '怀化' in name or '新化' in name or '株洲' in name or '桂东' in name or '武冈' in name
              or '永州' in name or '津市' in name or '浏阳' in name or '湘潭' in name or '湘西' in name or '溆浦' in name
              or '益阳' in name or '衡阳' in name or '道县' in name or '邵阳' in name or '郴州' in name or '双峰' in name
              or '东安' in name or '中方' in name or '会同' in name or '双牌' in name or '城步' in name or '宁乡' in name
              or '宁远' in name or '岳麓' in name or '新田' in name or '桃源' in name or '江华' in name or '江永' in name
              or '汨罗' in name or '洪江' in name or '涟源' in name or '湘江' in name or '祁阳' in name or '芷江' in name
              or '蓝山' in name or '辰溪' in name or '通道' in name or '靖州' in name or '麻阳' in name):
            groups['湖南频道,#genre#'].append((name, url, speed))
        else:
            groups['其他频道,#genre#'].append((name, url, speed))

        # 对每组进行排序
        for group in groups.values():
            group.sort(key=lambda x: (natural_key(x[0]), -float(x[2]) if x[2] is not None else float('-inf')))

    # 筛选相同名称的频道，只保存10个
    filtered_groups = {}
    overflow_groups = {}

    for group_name, channel_list in groups.items():
        seen_names = {}
        filtered_list = []
        overflow_list = []

        for channel in channel_list:
            name = channel[0]
            if name not in seen_names:
                seen_names[name] = 0

            if seen_names[name] < 10:
                filtered_list.append(channel)
                seen_names[name] += 1
            else:
                overflow_list.append(channel)

        filtered_groups[group_name] = filtered_list
        overflow_groups[group_name] = overflow_list

    #  获取当前时间
    now = datetime.now()
    update_time_line = f"更新时间,#genre#\n{now.strftime('%Y-%m-%d %H:%M:%S')},url\n"
    with open('iptv_list.txt', 'w', encoding='utf-8') as file:
        file.write(update_time_line)
        total_channels = 0  # 用于统计频道总数
        for group_name, channel_list in filtered_groups.items():
            file.write(f"{group_name}:\n")
            print(f"{group_name}:")  # 打印分组名称
            for name, url, speed in channel_list:
                # if speed >= 0.3:  # 只写入下载速度大于或等于 0.3 MB/s 的频道
                file.write(f"{name},{url}\n")
                print(f"  {name},{url},{speed}")  # 打印频道信息
                total_channels += 1  # 统计写入文件内的频道总数
            file.write("\n")
            print()  # 打印空行分隔组

    # # 保存频道数量超过10个的频道列表到新文件
    # with open('Filtered_iptv.txt', 'w', encoding='utf-8') as file:
    #     for group_name, channel_list in overflow_groups.items():
    #         if channel_list:  # 只写入非空组
    #             file.write(f"{group_name}\n")
    #             for name, url, speed in channel_list:
    #                 file.write(f"{name},{url}\n")
    #             file.write("\n")  # 打印空行分隔组
    print(f"\n经过测速分类排序后的频道列表数量为: {total_channels} 个，已全部写入iptv_list.txt文件中。")
    return groups

grouped_channels = group_and_sort_channels(channels)

# os.remove("湖南_组播.txt")
# os.remove("speed.txt")
# os.remove("ip.txt")

#  获取远程直播源文件
# url = "http://aktv.top/live.txt"
# r = requests.get(url)
# open('AKTV.txt', 'wb').write(r.content)

# 合并所有的txt文件
file_contents = []
file_paths = ["iptv_list.txt", "AKTV.txt", "hnyd.txt"]  # 替换为实际的文件路径列表
for file_path in file_paths:
    with open(file_path, 'r', encoding="utf-8") as file:
        content = file.read()
        file_contents.append(content)

# 写入合并后的txt文件
with open("iptv_list.txt", "w", encoding="utf-8") as output:
    output.write('\n'.join(file_contents))
