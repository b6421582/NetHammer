#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer 反射器状态检查工具
显示当前反射器文件的使用情况
"""

import os
from datetime import datetime

def check_file_info(file_path):
    """检查文件信息"""
    if not os.path.exists(file_path):
        return {"exists": False}
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        
        # 统计有效IP数量
        valid_ips = 0
        comments = 0
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            elif line.startswith('#'):
                comments += 1
            else:
                # 简单验证IP格式
                ip = line.split()[0]
                if is_valid_ip(ip):
                    valid_ips += 1
        
        # 获取文件大小和修改时间
        stat = os.stat(file_path)
        size = stat.st_size
        mtime = datetime.fromtimestamp(stat.st_mtime)
        
        return {
            "exists": True,
            "size": size,
            "total_lines": len(lines),
            "valid_ips": valid_ips,
            "comments": comments,
            "modified": mtime
        }
    except Exception as e:
        return {"exists": True, "error": str(e)}

def is_valid_ip(ip):
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

def format_size(size):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} TB"

def main():
    """主函数"""
    print("NetHammer 反射器状态检查")
    print("=" * 50)
    
    # 定义要检查的文件
    files_to_check = {
        "🎯 当前使用的反射器文件 (根目录)": {
            "dns_list.txt": "DNS反射器 (攻击工具调用)",
            "ntp_list.txt": "NTP反射器 (攻击工具调用)",
        },
        "📁 源反射器文件 (目录中)": {
            "reflector_lists/dns_servers.txt": "验证的DNS反射器",
            "reflector_lists/large_dns_servers.txt": "完整DNS反射器列表",
            "scan_filter_attack/ntp_scan_filter/ntp/ntpamp.txt": "更新的NTP反射器",
        },
        "🗑️ 可能的冗余文件": {
            "scan_filter_attack/ntp_scan_filter/ntp/ntpamp.txt.backup_20250814_183522": "NTP备份文件",
        }
    }
    
    total_active_reflectors = 0
    
    for category, files in files_to_check.items():
        print(f"\n{category}")
        print("-" * 40)
        
        for file_path, description in files.items():
            info = check_file_info(file_path)
            
            if not info["exists"]:
                print(f"❌ {description}")
                print(f"   文件: {file_path}")
                print(f"   状态: 不存在")
            elif "error" in info:
                print(f"⚠️ {description}")
                print(f"   文件: {file_path}")
                print(f"   状态: 读取错误 - {info['error']}")
            else:
                status = "✅" if "当前使用" in category else "📁"
                print(f"{status} {description}")
                print(f"   文件: {file_path}")
                print(f"   大小: {format_size(info['size'])}")
                print(f"   反射器数量: {info['valid_ips']} 个")
                print(f"   总行数: {info['total_lines']} 行")
                print(f"   注释行: {info['comments']} 行")
                print(f"   修改时间: {info['modified'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                # 统计当前使用的反射器
                if "当前使用" in category:
                    total_active_reflectors += info['valid_ips']
    
    print(f"\n📊 总计")
    print("-" * 20)
    print(f"当前激活的反射器: {total_active_reflectors} 个")
    
    # 检查调用关系
    print(f"\n🔗 调用关系说明")
    print("-" * 30)
    print("NetHammer攻击脚本调用流程:")
    print("1. quick_attack.py → dns_list.txt (DNS攻击)")
    print("2. quick_attack.py → ntp_list.txt (NTP攻击)")
    print("3. 源文件通过 manage_reflectors.py 复制到根目录")
    print("4. 攻击工具直接读取根目录的 *_list.txt 文件")
    
    print(f"\n⚠️ 重要提醒")
    print("-" * 20)
    print("• 修改源文件后需要运行 manage_reflectors.py 来更新")
    print("• 删除根目录的 *_list.txt 会导致攻击失败")
    print("• 备份文件可以安全删除以节省空间")

if __name__ == "__main__":
    main()
