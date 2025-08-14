#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer 反射器管理工具
管理和切换不同的反射器列表
"""

import os
import shutil
from datetime import datetime

class ReflectorManager:
    def __init__(self):
        self.reflector_files = {
            'dns': {
                'verified': 'reflector_lists/dns_servers.txt',
                'large': 'reflector_lists/large_dns_servers.txt',
                'target': 'dns_list.txt'
            },
            'ntp': {
                'updated': 'scan_filter_attack/ntp_scan_filter/ntp/ntpamp.txt',
                'target': 'ntp_list.txt'
            }
        }
    
    def log(self, message):
        """日志输出"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
    
    def check_files(self):
        """检查反射器文件状态"""
        print("📋 反射器文件状态检查")
        print("=" * 50)
        
        for protocol, files in self.reflector_files.items():
            print(f"\n🔍 {protocol.upper()} 反射器:")
            
            for file_type, file_path in files.items():
                if file_type == 'target':
                    continue
                    
                if os.path.exists(file_path):
                    try:
                        with open(file_path, 'r') as f:
                            lines = len([line for line in f if line.strip() and not line.startswith('#')])
                        print(f"  ✅ {file_type}: {file_path} ({lines} 个服务器)")
                    except Exception as e:
                        print(f"  ❌ {file_type}: {file_path} (读取失败: {e})")
                else:
                    print(f"  ❌ {file_type}: {file_path} (文件不存在)")
    
    def switch_dns_reflectors(self, mode='verified'):
        """切换DNS反射器列表"""
        dns_files = self.reflector_files['dns']
        
        if mode == 'verified':
            source_file = dns_files['verified']
            description = "已验证的DNS反射器"
        elif mode == 'large':
            source_file = dns_files['large']
            description = "完整的DNS反射器列表"
        else:
            print(f"❌ 未知模式: {mode}")
            return False
        
        if not os.path.exists(source_file):
            print(f"❌ 源文件不存在: {source_file}")
            return False
        
        try:
            # 备份现有文件
            target_file = dns_files['target']
            if os.path.exists(target_file):
                backup_file = f"{target_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy(target_file, backup_file)
                self.log(f"📦 已备份现有文件到: {backup_file}")
            
            # 复制新文件
            shutil.copy(source_file, target_file)
            
            # 统计数量
            with open(target_file, 'r') as f:
                count = len([line for line in f if line.strip() and not line.startswith('#')])
            
            self.log(f"✅ 已切换到{description} ({count} 个服务器)")
            return True
            
        except Exception as e:
            print(f"❌ 切换失败: {e}")
            return False
    
    def switch_ntp_reflectors(self):
        """切换NTP反射器列表"""
        ntp_files = self.reflector_files['ntp']
        source_file = ntp_files['updated']
        target_file = ntp_files['target']
        
        if not os.path.exists(source_file):
            print(f"❌ NTP反射器文件不存在: {source_file}")
            return False
        
        try:
            # 备份现有文件
            if os.path.exists(target_file):
                backup_file = f"{target_file}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                shutil.copy(target_file, backup_file)
                self.log(f"📦 已备份现有文件到: {backup_file}")
            
            # 复制新文件
            shutil.copy(source_file, target_file)
            
            # 统计数量
            with open(target_file, 'r') as f:
                count = len([line for line in f if line.strip() and not line.startswith('#')])
            
            self.log(f"✅ 已切换到更新的NTP反射器 ({count} 个服务器)")
            return True
            
        except Exception as e:
            print(f"❌ 切换失败: {e}")
            return False
    
    def optimize_reflectors(self):
        """优化反射器列表 (去重、排序)"""
        print("🔧 优化反射器列表...")
        
        for protocol, files in self.reflector_files.items():
            target_file = files['target']
            
            if not os.path.exists(target_file):
                continue
            
            try:
                # 读取并去重
                with open(target_file, 'r') as f:
                    lines = f.readlines()
                
                # 提取有效IP
                ips = set()
                comments = []
                
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    elif line.startswith('#'):
                        comments.append(line)
                    else:
                        # 提取IP地址 (可能包含端口或其他信息)
                        ip = line.split()[0]
                        if self.is_valid_ip(ip):
                            ips.add(ip)
                
                # 排序并写回
                sorted_ips = sorted(ips)
                
                with open(target_file, 'w') as f:
                    # 写入注释
                    f.write(f"# NetHammer {protocol.upper()} 反射器列表\n")
                    f.write(f"# 优化时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"# 总数: {len(sorted_ips)} 个服务器\n")
                    f.write("#\n")
                    
                    # 写入原有注释
                    for comment in comments:
                        f.write(f"{comment}\n")
                    
                    if comments:
                        f.write("#\n")
                    
                    # 写入IP列表
                    for ip in sorted_ips:
                        f.write(f"{ip}\n")
                
                self.log(f"✅ {protocol.upper()} 反射器已优化: {len(sorted_ips)} 个服务器")
                
            except Exception as e:
                print(f"❌ 优化 {protocol} 反射器失败: {e}")
    
    def is_valid_ip(self, ip):
        """简单的IP地址验证"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not (0 <= int(part) <= 255):
                    return False
            return True
        except:
            return False
    
    def show_stats(self):
        """显示反射器统计信息"""
        print("\n📊 反射器统计信息")
        print("=" * 30)
        
        total_reflectors = 0
        
        for protocol, files in self.reflector_files.items():
            target_file = files['target']
            
            if os.path.exists(target_file):
                try:
                    with open(target_file, 'r') as f:
                        count = len([line for line in f if line.strip() and not line.startswith('#')])
                    print(f"{protocol.upper():>8}: {count:>6} 个反射器")
                    total_reflectors += count
                except:
                    print(f"{protocol.upper():>8}: {'错误':>6}")
            else:
                print(f"{protocol.upper():>8}: {'未配置':>6}")
        
        print("-" * 30)
        print(f"{'总计':>8}: {total_reflectors:>6} 个反射器")

def main():
    """主函数"""
    manager = ReflectorManager()
    
    print("NetHammer 反射器管理工具")
    print("=" * 40)
    
    while True:
        print("\n📋 可用操作:")
        print("1. 检查反射器文件状态")
        print("2. 切换到验证的DNS反射器 (推荐)")
        print("3. 切换到完整DNS反射器列表")
        print("4. 切换到更新的NTP反射器")
        print("5. 优化反射器列表")
        print("6. 显示统计信息")
        print("0. 退出")
        
        try:
            choice = input("\n请选择操作 (0-6): ").strip()
            
            if choice == '0':
                print("👋 再见!")
                break
            elif choice == '1':
                manager.check_files()
            elif choice == '2':
                manager.switch_dns_reflectors('verified')
            elif choice == '3':
                manager.switch_dns_reflectors('large')
            elif choice == '4':
                manager.switch_ntp_reflectors()
            elif choice == '5':
                manager.optimize_reflectors()
            elif choice == '6':
                manager.show_stats()
            else:
                print("❌ 无效选择，请重试")
                
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，退出")
            break
        except Exception as e:
            print(f"❌ 操作失败: {e}")

if __name__ == "__main__":
    main()
