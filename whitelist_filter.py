#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer 白名单过滤系统
防止工具被恶意使用攻击重要机构和网站
"""

import re
import sys
import json
import ipaddress
from urllib.parse import urlparse

class WhitelistFilter:
    def __init__(self, config_file='protected_targets.json'):
        """初始化白名单过滤器"""
        self.config_file = config_file
        self.protected_config = self.load_config()

        # 从配置文件加载所有保护列表
        self.all_protected_domains = []
        self.critical_keywords = []
        self.protected_ip_ranges = []

        self._load_protected_lists()

    def load_config(self):
        """加载配置文件"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ 配置文件 {self.config_file} 不存在，使用默认保护列表")
            return self._get_default_config()
        except Exception as e:
            print(f"⚠️ 加载配置文件失败: {e}，使用默认保护列表")
            return self._get_default_config()

    def _get_default_config(self):
        """获取默认配置"""
        return {
            "china_government": {"domains": ["gov.cn"]},
            "us_government": {"domains": ["gov", "mil", "edu"]},
            "critical_infrastructure": {"keywords": ["hospital", "emergency", "police", "government"]},
            "protected_ip_ranges": {"ranges": ["127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"]}
        }

    def _load_protected_lists(self):
        """从配置加载所有保护列表"""
        # 加载所有域名
        for category, data in self.protected_config.items():
            if isinstance(data, dict) and 'domains' in data:
                self.all_protected_domains.extend(data['domains'])

        # 加载关键词
        if 'critical_infrastructure' in self.protected_config:
            keywords = self.protected_config['critical_infrastructure'].get('keywords', [])
            self.critical_keywords.extend(keywords)

        # 加载IP范围
        if 'protected_ip_ranges' in self.protected_config:
            ranges = self.protected_config['protected_ip_ranges'].get('ranges', [])
            self.protected_ip_ranges.extend(ranges)
        


    def is_protected_domain(self, target):
        """检查目标是否为受保护的域名"""
        if not target:
            return False

        # 解析URL获取域名
        if target.startswith(('http://', 'https://')):
            parsed = urlparse(target)
            domain = parsed.netloc.lower()
        else:
            domain = target.lower()

        # 移除端口号
        if ':' in domain:
            domain = domain.split(':')[0]

        # 精确匹配
        if domain in self.all_protected_domains:
            return True

        # 后缀匹配
        for protected in self.all_protected_domains:
            if domain.endswith('.' + protected) or domain == protected:
                return True

        # 关键词检查
        for keyword in self.critical_keywords:
            if keyword in domain:
                return True

        return False
    
    def is_protected_ip(self, ip_str):
        """检查IP是否为受保护的地址"""
        try:
            ip = ipaddress.ip_address(ip_str)

            # 检查配置的IP范围
            for network_str in self.protected_ip_ranges:
                try:
                    network = ipaddress.ip_network(network_str, strict=False)
                    if ip in network:
                        return True
                except:
                    continue

            # 检查特殊IP段
            if ip.is_private or ip.is_loopback or ip.is_link_local:
                return True

            return False
        except:
            return False
    
    def check_target(self, target):
        """综合检查目标是否受保护"""
        if not target:
            return True, "目标不能为空"
            
        # 检查域名
        if self.is_protected_domain(target):
            return True, f"目标 {target} 在保护列表中，禁止测试"
            
        # 尝试解析为IP
        try:
            # 如果是IP地址
            ipaddress.ip_address(target)
            if self.is_protected_ip(target):
                return True, f"IP地址 {target} 在保护范围内，禁止测试"
        except:
            pass
            
        return False, "目标检查通过"

def main():
    """命令行测试接口"""
    if len(sys.argv) != 2:
        print("使用方法: python3 whitelist_filter.py <目标>")
        sys.exit(1)
        
    target = sys.argv[1]
    filter_system = WhitelistFilter()
    
    is_protected, message = filter_system.check_target(target)
    
    if is_protected:
        print(f"❌ {message}")
        sys.exit(1)
    else:
        print(f"✅ {message}")
        sys.exit(0)

if __name__ == "__main__":
    main()
