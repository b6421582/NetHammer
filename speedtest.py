#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的网络速度测试工具
用于NetHammer VPS性能评估
"""

import time
import urllib.request
import urllib.error
import sys
import threading

def format_bytes(bytes_val):
    """格式化字节数"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.2f} TB"

def format_speed(bytes_per_sec):
    """格式化速度"""
    return format_bytes(bytes_per_sec) + "/s"

def test_download_speed(url, timeout=30):
    """测试下载速度"""
    try:
        print(f"正在测试下载速度: {url}")
        start_time = time.time()
        
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = response.read()
            
        end_time = time.time()
        duration = end_time - start_time
        size = len(data)
        speed = size / duration
        
        print(f"文件大小: {format_bytes(size)}")
        print(f"下载时间: {duration:.2f} 秒")
        print(f"下载速度: {format_speed(speed)}")
        
        return speed
    except Exception as e:
        print(f"下载测试失败: {e}")
        return 0

def test_latency(host, count=5):
    """测试延迟 (简单HTTP请求)"""
    print(f"\n正在测试延迟: {host}")
    latencies = []
    
    for i in range(count):
        try:
            start_time = time.time()
            urllib.request.urlopen(f"http://{host}", timeout=10)
            end_time = time.time()
            latency = (end_time - start_time) * 1000  # 转换为毫秒
            latencies.append(latency)
            print(f"请求 {i+1}: {latency:.2f} ms")
        except Exception as e:
            print(f"请求 {i+1}: 超时")
    
    if latencies:
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        
        print(f"平均延迟: {avg_latency:.2f} ms")
        print(f"最小延迟: {min_latency:.2f} ms")
        print(f"最大延迟: {max_latency:.2f} ms")
        
        return avg_latency
    return 0

def main():
    print("NetHammer 网络速度测试")
    print("=" * 40)
    
    # 测试服务器列表 (2025年8月可用 - 多个不同服务器)
    test_servers = [
        {
            'name': 'CacheFly CDN',
            'download_url': 'http://cachefly.cachefly.net/10mb.test',
            'latency_host': 'cachefly.cachefly.net'
        },
        {
            'name': 'ThinkBroadband UK',
            'download_url': 'http://ipv4.download.thinkbroadband.com/10MB.zip',
            'latency_host': 'ipv4.download.thinkbroadband.com'
        },
        {
            'name': 'DownloadTestFile',
            'download_url': 'https://downloadtestfile.com/10mb',
            'latency_host': 'downloadtestfile.com'
        },
        {
            'name': 'OpenSpeedTest',
            'download_url': 'https://openspeedtest.com/download/random4000x4000.jpg',
            'latency_host': 'openspeedtest.com'
        },
        {
            'name': 'GitHub Archive',
            'download_url': 'https://github.com/b6421582/NetHammer/archive/refs/heads/main.zip',
            'latency_host': 'github.com'
        }
    ]
    
    results = []
    
    for server in test_servers:
        print(f"\n🌍 测试服务器: {server['name']}")
        print("-" * 30)
        
        # 测试延迟
        latency = test_latency(server['latency_host'], 3)
        
        # 测试下载速度
        speed = test_download_speed(server['download_url'])
        
        results.append({
            'name': server['name'],
            'latency': latency,
            'speed': speed
        })
        
        time.sleep(1)  # 间隔1秒
    
    # 显示汇总结果
    print("\n" + "=" * 50)
    print("📊 测试结果汇总")
    print("=" * 50)
    
    for result in results:
        print(f"{result['name']:12} | "
              f"延迟: {result['latency']:6.1f}ms | "
              f"速度: {format_speed(result['speed'])}")
    
    # 找出最佳服务器
    if results:
        best_server = min(results, key=lambda x: x['latency'] if x['latency'] > 0 else float('inf'))
        fastest_server = max(results, key=lambda x: x['speed'])
        
        print(f"\n🏆 最低延迟: {best_server['name']} ({best_server['latency']:.1f}ms)")
        print(f"🚀 最快速度: {fastest_server['name']} ({format_speed(fastest_server['speed'])})")
    
    # VPS性能评估
    print(f"\n📋 VPS性能评估")
    print("-" * 20)
    
    avg_speed = sum(r['speed'] for r in results) / len(results) if results else 0
    avg_latency = sum(r['latency'] for r in results if r['latency'] > 0) / len([r for r in results if r['latency'] > 0]) if results else 0
    
    print(f"平均下载速度: {format_speed(avg_speed)}")
    print(f"平均延迟: {avg_latency:.1f}ms")
    
    # 给出建议
    if avg_speed > 100 * 1024 * 1024:  # 100MB/s
        print("✅ 网络性能优秀，适合高强度测试")
    elif avg_speed > 50 * 1024 * 1024:  # 50MB/s
        print("✅ 网络性能良好，适合中等强度测试")
    elif avg_speed > 10 * 1024 * 1024:  # 10MB/s
        print("⚠️  网络性能一般，建议降低并发数")
    else:
        print("❌ 网络性能较差，可能影响测试效果")
    
    if avg_latency < 50:
        print("✅ 延迟优秀")
    elif avg_latency < 100:
        print("✅ 延迟良好") 
    elif avg_latency < 200:
        print("⚠️  延迟一般")
    else:
        print("❌ 延迟较高")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中出现错误: {e}")
        sys.exit(1)
