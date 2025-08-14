#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer 数据包分析工具
分析PKT和TPL文件的内容和用途
"""

import os
import struct
from datetime import datetime

class PacketAnalyzer:
    def __init__(self):
        self.packet_dir = "scan_filter_attack/zmap_udp_probes"
        
    def analyze_upnp_packet(self, data):
        """分析UPnP SSDP数据包"""
        try:
            text = data.decode('utf-8', errors='ignore')
            lines = text.split('\r\n')
            
            info = {
                "protocol": "SSDP/UPnP",
                "method": lines[0] if lines else "Unknown",
                "headers": {},
                "purpose": "UPnP设备发现和反射攻击"
            }
            
            for line in lines[1:]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    info["headers"][key.strip()] = value.strip()
            
            return info
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_dns_packet(self, data):
        """分析DNS数据包"""
        try:
            if len(data) < 12:
                return {"error": "数据包太短"}
            
            # DNS头部解析
            header = struct.unpack('!HHHHHH', data[:12])
            transaction_id = header[0]
            flags = header[1]
            questions = header[2]
            answers = header[3]
            authority = header[4]
            additional = header[5]
            
            # 解析查询部分
            query_name = ""
            pos = 12
            while pos < len(data) and data[pos] != 0:
                length = data[pos]
                if length == 0:
                    break
                pos += 1
                if pos + length <= len(data):
                    query_name += data[pos:pos+length].decode('ascii', errors='ignore') + "."
                    pos += length
                else:
                    break
            
            if pos + 4 <= len(data):
                query_type = struct.unpack('!H', data[pos+1:pos+3])[0]
                query_class = struct.unpack('!H', data[pos+3:pos+5])[0]
            else:
                query_type = query_class = 0
            
            type_names = {1: "A", 2: "NS", 5: "CNAME", 6: "SOA", 12: "PTR", 15: "MX", 16: "TXT", 28: "AAAA"}
            
            info = {
                "protocol": "DNS",
                "transaction_id": f"0x{transaction_id:04X}",
                "flags": f"0x{flags:04X}",
                "questions": questions,
                "query_name": query_name.rstrip('.'),
                "query_type": type_names.get(query_type, f"Type {query_type}"),
                "query_class": "IN" if query_class == 1 else f"Class {query_class}",
                "purpose": "DNS查询，用于DNS反射攻击"
            }
            
            return info
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_ntp_packet(self, data):
        """分析NTP数据包"""
        try:
            if len(data) < 48:
                return {"error": "NTP数据包长度不足"}
            
            # NTP头部解析
            first_byte = data[0]
            li = (first_byte >> 6) & 0x3
            vn = (first_byte >> 3) & 0x7
            mode = first_byte & 0x7
            
            stratum = data[1]
            poll = data[2]
            precision = struct.unpack('!b', data[3:4])[0]
            
            mode_names = {0: "Reserved", 1: "Symmetric Active", 2: "Symmetric Passive", 
                         3: "Client", 4: "Server", 5: "Broadcast", 6: "Control", 7: "Private"}
            
            info = {
                "protocol": "NTP",
                "version": vn,
                "mode": mode_names.get(mode, f"Mode {mode}"),
                "stratum": stratum,
                "poll_interval": f"2^{poll} seconds" if poll > 0 else "Unknown",
                "precision": f"2^{precision} seconds",
                "purpose": "NTP时间查询，用于NTP反射攻击"
            }
            
            return info
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_snmp_packet(self, data):
        """分析SNMP数据包"""
        try:
            # 简单的SNMP ASN.1解析
            if len(data) < 10:
                return {"error": "SNMP数据包太短"}
            
            # SNMP通常以0x30开始 (SEQUENCE)
            if data[0] != 0x30:
                return {"error": "不是有效的SNMP数据包"}
            
            info = {
                "protocol": "SNMP",
                "asn1_type": f"0x{data[0]:02X} (SEQUENCE)",
                "length": data[1] if data[1] < 0x80 else "长格式",
                "purpose": "SNMP查询，用于SNMP反射攻击"
            }
            
            # 尝试找到community string
            pos = 2
            if pos < len(data) and data[pos] == 0x02:  # INTEGER (version)
                pos += 2 + data[pos + 1]  # 跳过version
                if pos < len(data) and data[pos] == 0x04:  # OCTET STRING (community)
                    comm_len = data[pos + 1]
                    if pos + 2 + comm_len <= len(data):
                        community = data[pos + 2:pos + 2 + comm_len].decode('ascii', errors='ignore')
                        info["community"] = community
            
            return info
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_packet_file(self, filename):
        """分析单个数据包文件"""
        filepath = os.path.join(self.packet_dir, filename)
        
        if not os.path.exists(filepath):
            return {"error": "文件不存在"}
        
        try:
            with open(filepath, 'rb') as f:
                data = f.read()
            
            file_info = {
                "filename": filename,
                "size": len(data),
                "hex_preview": ' '.join(f'{b:02X}' for b in data[:32])
            }
            
            # 根据文件名判断协议类型
            if 'upnp' in filename.lower() or '1900' in filename:
                packet_info = self.analyze_upnp_packet(data)
            elif 'dns' in filename.lower() or '53' in filename:
                packet_info = self.analyze_dns_packet(data)
            elif 'ntp' in filename.lower() or '123' in filename:
                packet_info = self.analyze_ntp_packet(data)
            elif 'snmp' in filename.lower() or '161' in filename:
                packet_info = self.analyze_snmp_packet(data)
            else:
                packet_info = {"protocol": "Unknown", "purpose": "未知协议数据包"}
            
            return {**file_info, **packet_info}
            
        except Exception as e:
            return {"error": str(e)}
    
    def analyze_all_packets(self):
        """分析所有数据包文件"""
        if not os.path.exists(self.packet_dir):
            print(f"❌ 目录不存在: {self.packet_dir}")
            return
        
        print("NetHammer 数据包分析报告")
        print("=" * 50)
        print(f"📁 分析目录: {self.packet_dir}")
        print(f"🕒 分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        pkt_files = [f for f in os.listdir(self.packet_dir) if f.endswith('.pkt')]
        tpl_files = [f for f in os.listdir(self.packet_dir) if f.endswith('.tpl')]
        
        if not pkt_files and not tpl_files:
            print("❌ 未找到PKT或TPL文件")
            return
        
        # 分析PKT文件
        if pkt_files:
            print("📦 PKT文件分析")
            print("-" * 30)
            
            for filename in sorted(pkt_files):
                info = self.analyze_packet_file(filename)
                
                print(f"\n🔍 {filename}")
                if "error" in info:
                    print(f"   ❌ 错误: {info['error']}")
                else:
                    print(f"   📊 大小: {info['size']} 字节")
                    print(f"   🌐 协议: {info.get('protocol', 'Unknown')}")
                    print(f"   🎯 用途: {info.get('purpose', 'Unknown')}")
                    
                    # 协议特定信息
                    if info.get('protocol') == 'SSDP/UPnP':
                        print(f"   📝 方法: {info.get('method', 'Unknown')}")
                        if 'headers' in info:
                            for key, value in info['headers'].items():
                                print(f"   📋 {key}: {value}")
                    
                    elif info.get('protocol') == 'DNS':
                        print(f"   🔢 事务ID: {info.get('transaction_id', 'Unknown')}")
                        print(f"   ❓ 查询: {info.get('query_name', 'Unknown')}")
                        print(f"   📝 类型: {info.get('query_type', 'Unknown')}")
                    
                    elif info.get('protocol') == 'NTP':
                        print(f"   📅 版本: {info.get('version', 'Unknown')}")
                        print(f"   🔧 模式: {info.get('mode', 'Unknown')}")
                        print(f"   📊 层级: {info.get('stratum', 'Unknown')}")
                    
                    elif info.get('protocol') == 'SNMP':
                        print(f"   🔑 Community: {info.get('community', 'Unknown')}")
                    
                    print(f"   🔢 十六进制: {info.get('hex_preview', '')}")
        
        # 分析TPL文件
        if tpl_files:
            print(f"\n\n📝 TPL文件分析")
            print("-" * 30)
            
            for filename in sorted(tpl_files):
                filepath = os.path.join(self.packet_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    print(f"\n📄 {filename}")
                    print(f"   📊 大小: {len(content)} 字符")
                    
                    # 检测协议类型
                    if 'SIP' in content.upper():
                        print(f"   🌐 协议: SIP")
                        print(f"   🎯 用途: SIP服务器扫描和攻击")
                    elif 'HTTP' in content.upper():
                        print(f"   🌐 协议: HTTP")
                        print(f"   🎯 用途: HTTP服务器测试")
                    else:
                        print(f"   🌐 协议: Unknown")
                    
                    # 显示前几行
                    lines = content.split('\n')[:3]
                    for i, line in enumerate(lines):
                        if line.strip():
                            print(f"   📝 第{i+1}行: {line.strip()[:60]}...")
                
                except Exception as e:
                    print(f"   ❌ 读取错误: {e}")
        
        print(f"\n📊 总结")
        print("-" * 20)
        print(f"PKT文件: {len(pkt_files)} 个")
        print(f"TPL文件: {len(tpl_files)} 个")
        print(f"总计: {len(pkt_files) + len(tpl_files)} 个数据包文件")

def main():
    """主函数"""
    analyzer = PacketAnalyzer()
    analyzer.analyze_all_packets()

if __name__ == "__main__":
    main()
