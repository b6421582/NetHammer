#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer 反射器列表更新工具
更新NTP、DNS、SSDP等反射攻击的反射器列表
"""

import requests
import socket
import threading
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import json
from datetime import datetime

class ReflectorUpdater:
    def __init__(self):
        self.valid_ntp_servers = []
        self.valid_dns_servers = []
        self.valid_ssdp_servers = []
        self.timeout = 3
        self.max_workers = 50
        
    def log(self, message):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def test_ntp_server(self, ip):
        """测试NTP服务器是否可用"""
        try:
            # NTP查询包 (简化版本)
            ntp_packet = b'\x1b' + b'\x00' * 47
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            sock.sendto(ntp_packet, (ip, 123))
            response, addr = sock.recvfrom(1024)
            sock.close()
            
            # 检查响应长度 (NTP响应通常是48字节)
            if len(response) >= 48:
                return True
                
        except Exception:
            pass
        return False
    
    def test_dns_server(self, ip):
        """测试DNS服务器是否可用"""
        try:
            # DNS查询包 (查询google.com的A记录)
            dns_packet = (
                b'\x12\x34'  # Transaction ID
                b'\x01\x00'  # Flags (standard query)
                b'\x00\x01'  # Questions: 1
                b'\x00\x00'  # Answer RRs: 0
                b'\x00\x00'  # Authority RRs: 0
                b'\x00\x00'  # Additional RRs: 0
                b'\x06google\x03com\x00'  # Query: google.com
                b'\x00\x01'  # Type: A
                b'\x00\x01'  # Class: IN
            )
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(self.timeout)
            
            sock.sendto(dns_packet, (ip, 53))
            response, addr = sock.recvfrom(1024)
            sock.close()
            
            # 检查响应 (DNS响应至少12字节)
            if len(response) >= 12:
                return True
                
        except Exception:
            pass
        return False
    
    def get_public_ntp_servers(self):
        """获取公共NTP服务器列表"""
        ntp_servers = [
            # 全球公共NTP服务器
            "pool.ntp.org", "0.pool.ntp.org", "1.pool.ntp.org", "2.pool.ntp.org", "3.pool.ntp.org",
            "time.nist.gov", "time-a.nist.gov", "time-b.nist.gov", "time-c.nist.gov", "time-d.nist.gov",
            "time.google.com", "time1.google.com", "time2.google.com", "time3.google.com", "time4.google.com",
            "time.cloudflare.com", "time.apple.com", "time.windows.com",
            
            # 亚洲NTP服务器
            "asia.pool.ntp.org", "cn.pool.ntp.org", "jp.pool.ntp.org", "kr.pool.ntp.org",
            "ntp.aliyun.com", "ntp1.aliyun.com", "ntp2.aliyun.com", "ntp3.aliyun.com",
            "time.pool.aliyun.com", "ntp.tencent.com", "ntp.baidu.com",
            
            # 欧洲NTP服务器
            "europe.pool.ntp.org", "de.pool.ntp.org", "uk.pool.ntp.org", "fr.pool.ntp.org",
            
            # 北美NTP服务器
            "north-america.pool.ntp.org", "us.pool.ntp.org", "ca.pool.ntp.org",
        ]
        
        # 解析域名为IP
        ip_list = []
        for server in ntp_servers:
            try:
                ip = socket.gethostbyname(server)
                if ip not in ip_list:
                    ip_list.append(ip)
            except Exception:
                continue
                
        return ip_list
    
    def get_public_dns_servers(self):
        """获取公共DNS服务器列表"""
        return [
            # 主要公共DNS
            "8.8.8.8", "8.8.4.4", "8.8.8.4", "8.8.4.8",  # Google
            "1.1.1.1", "1.0.0.1", "1.1.1.2", "1.0.0.2",  # Cloudflare
            "208.67.222.222", "208.67.220.220", "208.67.222.220", "208.67.220.222",  # OpenDNS
            "9.9.9.9", "149.112.112.112", "9.9.9.10", "149.112.112.10",  # Quad9

            # 国内DNS
            "114.114.114.114", "114.114.115.115", "114.114.114.115", "114.114.115.114",  # 114DNS
            "223.5.5.5", "223.6.6.6", "223.5.5.6", "223.6.6.5",  # 阿里DNS
            "119.29.29.29", "182.254.116.116", "119.28.28.28", "182.254.118.118",  # 腾讯DNS
            "180.76.76.76", "180.76.76.77",  # 百度DNS

            # 其他公共DNS
            "77.88.8.8", "77.88.8.1", "77.88.8.88", "77.88.8.2",  # Yandex
            "156.154.70.1", "156.154.71.1", "156.154.70.5", "156.154.71.5",  # Neustar
            "8.26.56.26", "8.20.247.20", "8.26.56.27", "8.20.247.21",  # Comodo

            # 更多国际DNS
            "4.2.2.1", "4.2.2.2", "4.2.2.3", "4.2.2.4", "4.2.2.5", "4.2.2.6",  # Level3
            "64.6.64.6", "64.6.65.6",  # Verisign
            "84.200.69.80", "84.200.70.40",  # DNS.WATCH
            "8.8.8.1", "8.8.4.1", "8.8.8.2", "8.8.4.2",  # Google备用
            "1.1.1.3", "1.0.0.3", "1.1.1.4", "1.0.0.4",  # Cloudflare备用

            # 各国DNS服务器
            "168.95.1.1", "168.95.192.1",  # 台湾
            "203.80.96.10", "203.80.96.9",  # 香港
            "202.96.209.133", "202.96.209.5",  # 中国电信
            "221.5.88.88", "221.6.4.66",  # 中国联通
            "112.124.47.27", "114.215.126.16",  # 其他中国DNS

            # 欧洲DNS
            "194.242.2.2", "194.242.2.3",  # Mullvad
            "80.80.80.80", "80.80.81.81",  # Freenom
            "37.235.1.174", "37.235.1.177",  # FreeDNS
            "89.233.43.71", "91.239.100.100",  # 欧洲其他

            # 美洲DNS
            "199.85.126.10", "199.85.127.10",  # Norton
            "185.228.168.9", "185.228.169.9",  # CleanBrowsing
            "76.76.19.19", "76.223.100.101",  # Alternate DNS
            "198.101.242.72", "23.253.163.53",  # 美国其他
        ]
    
    def scan_ip_range_for_ntp(self, base_ip, count=100):
        """扫描IP段寻找NTP服务器"""
        ip_parts = base_ip.split('.')
        base = '.'.join(ip_parts[:3])
        
        ips_to_test = []
        for i in range(1, min(255, count + 1)):
            ips_to_test.append(f"{base}.{i}")
        
        return ips_to_test
    
    def update_ntp_reflectors(self):
        """更新NTP反射器列表"""
        self.log("🔄 开始更新NTP反射器列表...")
        
        # 获取候选IP列表
        candidate_ips = set()
        
        # 1. 公共NTP服务器
        public_ntps = self.get_public_ntp_servers()
        candidate_ips.update(public_ntps)
        self.log(f"📋 获得 {len(public_ntps)} 个公共NTP服务器")
        
        # 2. 扫描一些常见网段
        common_ranges = [
            "8.8.8", "1.1.1", "208.67.222", "114.114.114",
            "223.5.5", "119.29.29", "180.76.76"
        ]
        
        for range_base in common_ranges:
            range_ips = self.scan_ip_range_for_ntp(f"{range_base}.1", 50)
            candidate_ips.update(range_ips)
        
        self.log(f"📊 总计候选IP: {len(candidate_ips)} 个")
        
        # 3. 并发测试
        valid_servers = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ip = {executor.submit(self.test_ntp_server, ip): ip for ip in candidate_ips}
            
            completed = 0
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                completed += 1
                
                if completed % 50 == 0:
                    self.log(f"⏳ 已测试 {completed}/{len(candidate_ips)} 个IP...")
                
                try:
                    if future.result():
                        valid_servers.append(ip)
                        self.log(f"✅ 发现有效NTP服务器: {ip}")
                except Exception:
                    pass
        
        self.log(f"🎯 找到 {len(valid_servers)} 个有效NTP反射器")
        return valid_servers
    
    def scan_ip_range_for_dns(self, base_ip, count=254):
        """扫描IP段寻找DNS服务器"""
        ip_parts = base_ip.split('.')
        base = '.'.join(ip_parts[:3])

        ips_to_test = []
        for i in range(1, min(255, count + 1)):
            ips_to_test.append(f"{base}.{i}")

        return ips_to_test

    def update_dns_reflectors(self):
        """更新DNS反射器列表"""
        self.log("🔄 开始更新DNS反射器列表...")

        # 获取候选IP列表
        candidate_ips = set()

        # 1. 公共DNS服务器
        public_dns = self.get_public_dns_servers()
        candidate_ips.update(public_dns)
        self.log(f"📋 获得 {len(public_dns)} 个公共DNS服务器")

        # 2. 扫描常见DNS服务器网段
        common_dns_ranges = [
            "8.8.8", "8.8.4", "1.1.1", "1.0.0",  # Google, Cloudflare
            "208.67.222", "208.67.220",  # OpenDNS
            "114.114.114", "114.114.115",  # 114DNS
            "223.5.5", "223.6.6",  # 阿里DNS
            "119.29.29", "182.254.116",  # 腾讯DNS
            "4.2.2", "64.6.64", "64.6.65",  # Level3, Verisign
            "77.88.8", "156.154.70", "156.154.71",  # Yandex, Neustar
        ]

        for range_base in common_dns_ranges:
            range_ips = self.scan_ip_range_for_dns(f"{range_base}.1", 100)
            candidate_ips.update(range_ips)

        # 3. 添加一些随机的公共IP段 (很多ISP在这些段提供DNS)
        random_ranges = [
            "202.96.209", "202.96.128", "202.102.224", "202.102.227",  # 中国电信
            "221.5.88", "221.6.4", "210.2.4", "61.139.2",  # 中国联通
            "218.30.19", "218.85.157", "218.104.111", "61.134.1",  # 其他中国ISP
            "168.95.1", "168.95.192", "203.74.205", "139.175.252",  # 台湾
            "203.80.96", "202.45.84", "202.14.67", "202.181.7",  # 香港
        ]

        for range_base in random_ranges:
            range_ips = self.scan_ip_range_for_dns(f"{range_base}.1", 50)
            candidate_ips.update(range_ips)

        self.log(f"📊 总计候选IP: {len(candidate_ips)} 个")

        # 4. 并发测试
        valid_servers = []
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_ip = {executor.submit(self.test_dns_server, ip): ip for ip in candidate_ips}

            completed = 0
            for future in as_completed(future_to_ip):
                ip = future_to_ip[future]
                completed += 1

                if completed % 100 == 0:
                    self.log(f"⏳ 已测试 {completed}/{len(candidate_ips)} 个IP...")

                try:
                    if future.result():
                        valid_servers.append(ip)
                        self.log(f"✅ 发现有效DNS服务器: {ip}")
                except Exception:
                    pass

        self.log(f"🎯 找到 {len(valid_servers)} 个有效DNS反射器")
        return valid_servers
    
    def save_reflectors(self, reflector_type, servers):
        """保存反射器列表到文件"""
        if reflector_type == "ntp":
            file_path = "scan_filter_attack/ntp_scan_filter/ntp/ntpamp.txt"
        elif reflector_type == "dns":
            file_path = "reflector_lists/dns_servers.txt"
        else:
            return False
        
        # 确保目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # 备份原文件
        if os.path.exists(file_path):
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            os.rename(file_path, backup_path)
            self.log(f"📦 原文件已备份到: {backup_path}")
        
        # 写入新文件
        with open(file_path, 'w') as f:
            for server in servers:
                f.write(f"{server}\n")
        
        self.log(f"💾 已保存 {len(servers)} 个{reflector_type.upper()}反射器到: {file_path}")
        return True
    
    def create_reflector_info(self):
        """创建反射器信息文件"""
        info = {
            "description": "NetHammer 反射器列表信息",
            "last_updated": datetime.now().isoformat(),
            "reflector_types": {
                "ntp": {
                    "description": "NTP时间服务器反射器",
                    "port": 123,
                    "protocol": "UDP",
                    "amplification_factor": "2-10x"
                },
                "dns": {
                    "description": "DNS域名服务器反射器", 
                    "port": 53,
                    "protocol": "UDP",
                    "amplification_factor": "28-54x"
                },
                "ssdp": {
                    "description": "SSDP UPnP设备反射器",
                    "port": 1900,
                    "protocol": "UDP", 
                    "amplification_factor": "30-40x"
                }
            }
        }
        
        with open("reflector_info.json", 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        
        self.log("📋 反射器信息文件已创建: reflector_info.json")

def main():
    """主函数"""
    print("NetHammer 反射器列表更新工具")
    print("=" * 40)
    
    updater = ReflectorUpdater()
    
    try:
        # 更新NTP反射器
        ntp_servers = updater.update_ntp_reflectors()
        if ntp_servers:
            updater.save_reflectors("ntp", ntp_servers)
        
        print()
        
        # 更新DNS反射器
        dns_servers = updater.update_dns_reflectors()
        if dns_servers:
            updater.save_reflectors("dns", dns_servers)
        
        # 创建信息文件
        updater.create_reflector_info()
        
        print("\n" + "=" * 40)
        print("✅ 反射器列表更新完成!")
        print(f"📊 NTP反射器: {len(ntp_servers)} 个")
        print(f"📊 DNS反射器: {len(dns_servers)} 个")
        print("\n⚠️ 重要提醒:")
        print("- 反射器列表仅用于授权的安全测试")
        print("- 请确保遵守相关法律法规")
        print("- 建议定期更新反射器列表")
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断更新")
    except Exception as e:
        print(f"❌ 更新失败: {e}")

if __name__ == "__main__":
    main()
