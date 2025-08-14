#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer GUI 启动脚本
自动启动服务器和GUI界面
"""

import subprocess
import time
import sys
import os
import threading
import signal

def check_dependencies():
    """检查依赖"""
    required_modules = ['tkinter', 'requests', 'flask']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        print("❌ 缺少依赖模块:")
        for module in missing:
            print(f"   - {module}")
        print("\n📦 请安装缺少的模块:")
        print("pip install requests flask")
        if 'tkinter' in missing:
            print("sudo apt install python3-tk  # Ubuntu/Debian")
            print("# 或者使用系统包管理器安装 tkinter")
        return False
    
    return True

def start_server():
    """启动服务器"""
    print("🚀 启动 NetHammer 服务器...")
    try:
        server_process = subprocess.Popen([
            sys.executable, 'NetHammer_Server.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # 等待服务器启动
        time.sleep(3)
        
        # 检查服务器是否启动成功
        if server_process.poll() is None:
            print("✅ 服务器启动成功")
            return server_process
        else:
            stdout, stderr = server_process.communicate()
            print("❌ 服务器启动失败:")
            print(stderr.decode())
            return None
            
    except Exception as e:
        print(f"❌ 启动服务器失败: {e}")
        return None

def start_gui():
    """启动GUI"""
    print("🖥️ 启动 NetHammer GUI...")
    try:
        gui_process = subprocess.Popen([
            sys.executable, 'NetHammer_GUI.py'
        ])
        return gui_process
    except Exception as e:
        print(f"❌ 启动GUI失败: {e}")
        return None

def main():
    """主函数"""
    print("🛡️ NetHammer 2025 GUI 启动器")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查必要文件
    required_files = ['NetHammer_Server.py', 'NetHammer_GUI.py', 'quick_attack.py']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print("❌ 缺少必要文件:")
        for file in missing_files:
            print(f"   - {file}")
        sys.exit(1)
    
    server_process = None
    gui_process = None
    
    try:
        # 启动服务器
        server_process = start_server()
        if not server_process:
            print("❌ 无法启动服务器，退出")
            sys.exit(1)
        
        # 启动GUI
        gui_process = start_gui()
        if not gui_process:
            print("❌ 无法启动GUI")
            if server_process:
                server_process.terminate()
            sys.exit(1)
        
        print("✅ NetHammer GUI 系统启动完成!")
        print("📋 使用说明:")
        print("   1. 在GUI中连接服务器 (默认: http://127.0.0.1:8080)")
        print("   2. 配置测试参数")
        print("   3. 点击'安全检查'验证目标")
        print("   4. 点击'开始测试'执行测试")
        print("\n⚠️ 重要提醒:")
        print("   - 请确保已获得目标系统的明确授权")
        print("   - 工具内置白名单保护系统")
        print("   - 仅用于合法的安全测试目的")
        print("\n按 Ctrl+C 退出...")
        
        # 等待GUI进程结束
        gui_process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 用户中断，正在关闭...")
    except Exception as e:
        print(f"❌ 运行出错: {e}")
    finally:
        # 清理进程
        if gui_process and gui_process.poll() is None:
            print("🧹 关闭GUI...")
            gui_process.terminate()
            
        if server_process and server_process.poll() is None:
            print("🧹 关闭服务器...")
            server_process.terminate()
            time.sleep(1)
            if server_process.poll() is None:
                server_process.kill()
        
        print("✅ 清理完成")

if __name__ == "__main__":
    main()
