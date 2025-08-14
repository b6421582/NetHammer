#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer GUI 可视化界面
连接服务器提交测试指令的图形化界面
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import requests
import json
import threading
import time
from datetime import datetime
import sys

class NetHammerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("NetHammer 2025 - 网络压力测试工具")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # 设置图标和样式
        self.setup_styles()
        
        # 服务器连接状态
        self.server_connected = False
        self.server_url = "http://127.0.0.1:8080"  # 默认本地服务器
        
        # 测试状态
        self.testing = False
        self.test_thread = None
        
        # 创建界面
        self.create_widgets()
        
    def setup_styles(self):
        """设置界面样式"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 自定义颜色
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground='#2c3e50')
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground='#34495e')
        style.configure('Status.TLabel', font=('Arial', 10), foreground='#27ae60')
        style.configure('Error.TLabel', font=('Arial', 10), foreground='#e74c3c')
        
    def create_widgets(self):
        """创建界面组件"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="NetHammer 2025 - 专业网络压力测试", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 服务器连接区域
        self.create_server_section(main_frame)
        
        # 测试配置区域
        self.create_config_section(main_frame)
        
        # 控制按钮区域
        self.create_control_section(main_frame)
        
        # 日志显示区域
        self.create_log_section(main_frame)
        
        # 状态栏
        self.create_status_bar(main_frame)
        
    def create_server_section(self, parent):
        """创建服务器连接区域"""
        server_frame = ttk.LabelFrame(parent, text="🌐 服务器连接", padding="10")
        server_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        server_frame.columnconfigure(1, weight=1)
        
        # 服务器地址
        ttk.Label(server_frame, text="服务器地址:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.server_entry = ttk.Entry(server_frame, width=40)
        self.server_entry.insert(0, self.server_url)
        self.server_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # 连接按钮
        self.connect_btn = ttk.Button(server_frame, text="连接", command=self.connect_server)
        self.connect_btn.grid(row=0, column=2)
        
        # 连接状态
        self.connection_status = ttk.Label(server_frame, text="❌ 未连接", style='Error.TLabel')
        self.connection_status.grid(row=0, column=3, padx=(10, 0))
        
    def create_config_section(self, parent):
        """创建测试配置区域"""
        config_frame = ttk.LabelFrame(parent, text="⚙️ 测试配置", padding="10")
        config_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(3, weight=1)
        
        # 目标地址
        ttk.Label(config_frame, text="目标地址:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.target_entry = ttk.Entry(config_frame, width=25)
        self.target_entry.insert(0, "192.168.1.100")
        self.target_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 20))
        
        # 端口
        ttk.Label(config_frame, text="端口:").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.port_entry = ttk.Entry(config_frame, width=10)
        self.port_entry.insert(0, "80")
        self.port_entry.grid(row=0, column=3, sticky=tk.W)
        
        # 测试方法
        ttk.Label(config_frame, text="测试方法:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.method_combo = ttk.Combobox(config_frame, width=22, state="readonly")
        self.method_combo['values'] = [
            'http2', 'cldap', 'coap', 'dns', 'ntp', 'ssdp', 'snmp',
            'syn', 'ack', 'udp', 'fin', 'rst', 'psh', 'http', 'rudy',
            'multi', 'combo'
        ]
        self.method_combo.set('dns')
        self.method_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=(10, 0))
        
        # 线程数
        ttk.Label(config_frame, text="线程数:").grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.threads_entry = ttk.Entry(config_frame, width=10)
        self.threads_entry.insert(0, "100")
        self.threads_entry.grid(row=1, column=3, sticky=tk.W, pady=(10, 0))
        
        # 持续时间
        ttk.Label(config_frame, text="持续时间(秒):").grid(row=2, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.duration_entry = ttk.Entry(config_frame, width=25)
        self.duration_entry.insert(0, "300")
        self.duration_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(0, 20), pady=(10, 0))
        
        # 高性能模式选项 - 使用自定义按钮样式
        advanced_frame = ttk.Frame(config_frame)
        advanced_frame.grid(row=2, column=2, columnspan=2, sticky=tk.W, pady=(10, 0))

        self.advanced_var = tk.BooleanVar()

        # 创建自定义的勾选按钮
        self.advanced_btn = tk.Button(
            advanced_frame,
            text="☐",
            font=("Arial", 12),
            width=3,
            height=1,
            relief="flat",
            bg="#f0f0f0",
            command=self.on_advanced_toggle
        )
        self.advanced_btn.pack(side=tk.LEFT)

        self.advanced_label = ttk.Label(advanced_frame, text="高性能模式 (最大化测试效果)")
        self.advanced_label.pack(side=tk.LEFT, padx=(5, 0))
        
    def create_control_section(self, parent):
        """创建控制按钮区域"""
        control_frame = ttk.Frame(parent)
        control_frame.grid(row=3, column=0, columnspan=3, pady=(0, 10))
        
        # 开始测试按钮
        self.start_btn = ttk.Button(control_frame, text="🚀 开始测试", command=self.start_test, state='disabled')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 停止测试按钮
        self.stop_btn = ttk.Button(control_frame, text="⏹️ 停止测试", command=self.stop_test, state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 清空日志按钮
        clear_btn = ttk.Button(control_frame, text="🗑️ 清空日志", command=self.clear_log)
        clear_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # 安全检查按钮
        check_btn = ttk.Button(control_frame, text="🛡️ 安全检查", command=self.safety_check)
        check_btn.pack(side=tk.LEFT)
        
    def create_log_section(self, parent):
        """创建日志显示区域"""
        log_frame = ttk.LabelFrame(parent, text="📋 测试日志", padding="5")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # 日志文本框
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # 添加欢迎信息
        self.log("NetHammer 2025 GUI 已启动")
        self.log("📋 请先连接服务器，然后配置测试参数")
        self.log("⚠️ 请确保已获得目标系统的明确授权")
        
    def create_status_bar(self, parent):
        """创建状态栏"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(1, weight=1)
        
        # 状态信息
        self.status_label = ttk.Label(status_frame, text="请合法测试", style='Status.TLabel')
        self.status_label.grid(row=0, column=0, sticky=tk.W)
        
        # 时间显示
        self.time_label = ttk.Label(status_frame, text="")
        self.time_label.grid(row=0, column=2, sticky=tk.E)
        
        # 更新时间
        self.update_time()
        
    def log(self, message):
        """添加日志信息"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        
    def clear_log(self):
        """清空日志"""
        self.log_text.delete(1.0, tk.END)
        self.log("📋 日志已清空")
        
    def update_time(self):
        """更新时间显示"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=current_time)
        self.root.after(1000, self.update_time)

    def on_advanced_toggle(self):
        """高性能模式切换回调"""
        # 切换状态
        self.advanced_var.set(not self.advanced_var.get())

        if self.advanced_var.get():
            # 启用高性能模式
            self.advanced_btn.config(text="✅", bg="#d5f4e6", fg="#27ae60")
            self.advanced_label.config(text="高性能模式 (已启用)", foreground='#27ae60')
            self.log("⚡ 高性能模式已启用 - 将使用最大线程数和优化参数")
        else:
            # 禁用高性能模式
            self.advanced_btn.config(text="☐", bg="#f0f0f0", fg="#000000")
            self.advanced_label.config(text="高性能模式 (最大化测试效果)", foreground='#34495e')
            self.log("📊 高性能模式已禁用 - 使用标准参数")
        
    def connect_server(self):
        """连接服务器"""
        self.server_url = self.server_entry.get().strip()
        if not self.server_url:
            messagebox.showerror("错误", "请输入服务器地址")
            return
            
        self.log(f"🔄 正在连接服务器: {self.server_url}")
        
        try:
            # 测试连接
            response = requests.get(f"{self.server_url}/status", timeout=5)
            if response.status_code == 200:
                self.server_connected = True
                self.connection_status.config(text="✅ 已连接", style='Status.TLabel')
                self.start_btn.config(state='normal')
                self.log("✅ 服务器连接成功")
                self.status_label.config(text="服务器已连接，请合法测试")
            else:
                raise Exception(f"服务器响应错误: {response.status_code}")
                
        except Exception as e:
            self.server_connected = False
            self.connection_status.config(text="❌ 连接失败", style='Error.TLabel')
            self.start_btn.config(state='disabled')
            self.log(f"❌ 服务器连接失败: {str(e)}")
            messagebox.showerror("连接失败", f"无法连接到服务器:\n{str(e)}")
            
    def safety_check(self):
        """安全检查"""
        target = self.target_entry.get().strip()
        if not target:
            messagebox.showwarning("警告", "请输入目标地址")
            return
            
        self.log(f"🛡️ 正在进行安全检查: {target}")
        
        try:
            # 调用白名单检查
            from whitelist_filter import WhitelistFilter
            filter_system = WhitelistFilter()
            is_protected, message = filter_system.check_target(target)
            
            if is_protected:
                self.log(f"🚫 安全检查失败: {message}")
                messagebox.showerror("安全检查失败", f"目标受保护:\n{message}")
            else:
                self.log(f"✅ 安全检查通过: {target}")
                messagebox.showinfo("安全检查通过", f"目标可以进行测试:\n{target}")
                
        except ImportError:
            self.log("⚠️ 白名单模块未找到，跳过安全检查")
            messagebox.showwarning("警告", "白名单模块未找到\n请确保 whitelist_filter.py 存在")
        except Exception as e:
            self.log(f"❌ 安全检查出错: {str(e)}")
            messagebox.showerror("检查出错", f"安全检查失败:\n{str(e)}")
            
    def start_test(self):
        """开始测试"""
        if not self.server_connected:
            messagebox.showerror("错误", "请先连接服务器")
            return
            
        # 获取配置
        target = self.target_entry.get().strip()
        port = self.port_entry.get().strip()
        method = self.method_combo.get()
        threads = self.threads_entry.get().strip()
        duration = self.duration_entry.get().strip()
        
        # 验证输入
        if not all([target, port, method, threads, duration]):
            messagebox.showerror("错误", "请填写完整的测试配置")
            return
            
        try:
            port = int(port)
            threads = int(threads)
            duration = int(duration)
        except ValueError:
            messagebox.showerror("错误", "端口、线程数和持续时间必须是数字")
            return
            
        # 确认测试
        confirm = messagebox.askyesno(
            "确认测试", 
            f"即将开始测试:\n\n"
            f"目标: {target}:{port}\n"
            f"方法: {method}\n"
            f"线程: {threads}\n"
            f"时间: {duration}秒\n\n"
            f"请确认已获得目标授权!"
        )
        
        if not confirm:
            return
            
        # 开始测试
        self.testing = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self.status_label.config(text="测试进行中...")
        
        # 创建测试线程
        self.test_thread = threading.Thread(target=self.run_test, args=(target, port, method, threads, duration))
        self.test_thread.daemon = True
        self.test_thread.start()
        
    def run_test(self, target, port, method, threads, duration):
        """运行测试"""
        try:
            self.log(f"🚀 开始测试: {target}:{port}")
            self.log(f"📊 配置: {method} | {threads}线程 | {duration}秒")
            
            # 构建测试请求
            test_data = {
                'target': target,
                'port': port,
                'method': method,
                'threads': threads,
                'duration': duration,
                'high_performance': self.advanced_var.get()
            }
            
            # 发送测试请求
            response = requests.post(f"{self.server_url}/start_test", json=test_data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"✅ 测试启动成功: {result.get('message', '无消息')}")
                
                # 监控测试状态
                self.monitor_test()
                
            else:
                self.log(f"❌ 测试启动失败: HTTP {response.status_code}")
                
        except Exception as e:
            self.log(f"❌ 测试执行出错: {str(e)}")
        finally:
            self.testing = False
            self.root.after(0, self.test_finished)
            
    def monitor_test(self):
        """监控测试状态"""
        start_time = time.time()
        duration = int(self.duration_entry.get())
        
        while self.testing and (time.time() - start_time) < duration:
            try:
                # 获取测试状态
                response = requests.get(f"{self.server_url}/test_status", timeout=5)
                if response.status_code == 200:
                    status = response.json()
                    elapsed = int(time.time() - start_time)
                    remaining = max(0, duration - elapsed)
                    
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"测试中... 已用时:{elapsed}s 剩余:{remaining}s"
                    ))
                    
            except Exception as e:
                self.log(f"⚠️ 状态监控出错: {str(e)}")
                
            time.sleep(2)
            
        self.log("✅ 测试完成")
        
    def stop_test(self):
        """停止测试"""
        if not self.testing:
            return
            
        try:
            response = requests.post(f"{self.server_url}/stop_test", timeout=5)
            if response.status_code == 200:
                self.log("⏹️ 测试已停止")
            else:
                self.log("⚠️ 停止测试请求失败")
        except Exception as e:
            self.log(f"❌ 停止测试出错: {str(e)}")
            
        self.testing = False
        self.test_finished()
        
    def test_finished(self):
        """测试结束处理"""
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self.status_label.config(text="测试完成，请合法使用")

def main():
    """主函数"""
    root = tk.Tk()
    app = NetHammerGUI(root)
    
    try:
        root.mainloop()
    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(0)

if __name__ == "__main__":
    main()
