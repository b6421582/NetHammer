#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer 安全启动器
在执行任何测试前进行多重安全检查
"""

import sys
import os
from whitelist_filter import WhitelistFilter

def show_safety_warning():
    """显示安全警告"""
    print("""
🛡️ NetHammer 安全启动器
========================

⚠️  重要安全提醒:
1. 本工具仅供授权的网络安全测试使用
2. 使用前必须获得目标系统的明确书面授权
3. 违法使用后果由用户自行承担
4. 内置白名单系统将阻止对重要机构的测试

🚫 受保护的目标包括:
- 政府机构 (.gov.cn, .gov, .mil)
- 教育机构 (.edu.cn, .edu)
- 医疗机构 (hospital, medical, health)
- 金融机构 (bank, financial)
- 社交媒体平台 (微博, 知乎, bilibili等)
- 国际组织 (UN, WHO, NATO等)
- 关键基础设施

📋 合法使用场景:
✅ 企业内部安全测试
✅ 授权渗透测试
✅ 学术研究 (受控环境)
✅ 安全培训演示
✅ 产品安全测试

❌ 禁止使用场景:
❌ 未授权测试
❌ 恶意攻击
❌ 商业竞争
❌ 个人恩怨
❌ 非法牟利

========================
""")

def get_user_confirmation():
    """获取用户确认"""
    print("请确认您的使用目的 (输入对应数字):")
    print("1. 企业内部安全测试")
    print("2. 授权渗透测试")
    print("3. 学术研究")
    print("4. 安全培训")
    print("5. 产品测试")
    print("0. 退出")
    
    try:
        choice = input("\n请选择 (1-5): ").strip()
        if choice == '0':
            print("已退出")
            return False
        elif choice in ['1', '2', '3', '4', '5']:
            purposes = {
                '1': '企业内部安全测试',
                '2': '授权渗透测试', 
                '3': '学术研究',
                '4': '安全培训',
                '5': '产品测试'
            }
            print(f"\n✅ 已确认使用目的: {purposes[choice]}")
            
            # 二次确认
            confirm = input("请输入 'YES' 确认您已获得相关授权: ").strip().upper()
            if confirm == 'YES':
                print("✅ 授权确认完成")
                return True
            else:
                print("❌ 未确认授权，已退出")
                return False
        else:
            print("❌ 无效选择，已退出")
            return False
    except KeyboardInterrupt:
        print("\n\n用户取消操作")
        return False

def check_target_safety(target):
    """检查目标安全性"""
    filter_system = WhitelistFilter()
    is_protected, message = filter_system.check_target(target)
    
    if is_protected:
        print(f"\n🚫 {message}")
        print("🛡️ 为了网络安全，NetHammer拒绝执行此测试")
        return False
    else:
        print(f"\n✅ 目标安全检查通过: {target}")
        return True

def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("python3 safe_launch.py <目标> [其他参数...]")
        print("\n示例:")
        print("python3 safe_launch.py 192.168.1.100 -m dns -c 100 -t 300")
        sys.exit(1)
    
    target = sys.argv[1]
    
    # 显示安全警告
    show_safety_warning()
    
    # 获取用户确认
    if not get_user_confirmation():
        sys.exit(1)
    
    # 检查目标安全性
    if not check_target_safety(target):
        sys.exit(1)
    
    # 如果所有检查都通过，启动NetHammer
    print("\n🚀 启动NetHammer...")
    print("=" * 50)
    
    # 构建命令
    cmd = ['python3', 'quick_attack.py'] + sys.argv[1:]
    
    try:
        os.execvp('python3', cmd)
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
