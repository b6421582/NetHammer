# NetHammer 反射器列表说明

## 📋 什么是反射器？

**反射器**是指能够响应特定协议请求并返回放大响应的服务器。在网络压力测试中，反射攻击利用这些服务器来放大测试流量。

## 🗂️ 反射器文件结构

```
scan_filter_attack/
├── ntp_scan_filter/ntp/
│   └── ntpamp.txt              # NTP反射器列表 (需要更新)
├── memcached_scan_filter/      # Memcached反射器相关
├── ssdp_scan_filter/           # SSDP反射器相关
└── zmap_udp_probes/           # 各种UDP协议探测包
```

## 🔍 各类反射器详解

### 1. NTP反射器 (ntpamp.txt)

**文件**: `scan_filter_attack/ntp_scan_filter/ntp/ntpamp.txt`

**作用**: 
- 存储可用的NTP时间服务器IP地址
- 用于NTP反射放大攻击
- 放大倍数: 2-10倍

**问题**: 
- ❌ 文件中的IP大多是10年前的，很多已失效
- ❌ 需要定期更新以保持有效性

**示例内容**:
```
208.100.11.200    # 可能已失效
175.137.208.253   # 可能已失效
8.8.8.8          # Google NTP (通常有效)
1.1.1.1          # Cloudflare NTP (通常有效)
```

### 2. DNS反射器

**作用**:
- 利用DNS服务器进行反射放大
- 放大倍数: 28-54倍 (效果最好)
- 查询大型DNS记录获得放大效果

**常用DNS服务器**:
```
8.8.8.8          # Google DNS
1.1.1.1          # Cloudflare DNS
114.114.114.114  # 114 DNS
223.5.5.5        # 阿里DNS
```

### 3. SSDP反射器

**文件**: `scan_filter_attack/ssdp_scan_filter/`

**作用**:
- 利用UPnP设备进行SSDP反射
- 放大倍数: 30-40倍
- 主要针对家用路由器、智能设备

### 4. Memcached反射器

**文件**: `scan_filter_attack/memcached_scan_filter/`

**作用**:
- 利用Memcached缓存服务器
- 放大倍数: 10,000-51,000倍 (最强)
- 2018年曾被大量滥用，现在大多已修复

## 🔄 更新反射器列表

### 自动更新工具

```bash
# 运行反射器更新工具
python3 update_reflectors.py
```

**功能**:
- ✅ 自动扫描和测试NTP服务器
- ✅ 验证DNS服务器可用性
- ✅ 备份原有列表
- ✅ 生成新的有效反射器列表

### 手动更新

1. **备份原文件**:
   ```bash
   cp scan_filter_attack/ntp_scan_filter/ntp/ntpamp.txt ntpamp.txt.backup
   ```

2. **添加新的有效IP**:
   ```bash
   # 测试NTP服务器是否响应
   ntpdate -q 服务器IP
   
   # 如果响应正常，添加到列表
   echo "服务器IP" >> scan_filter_attack/ntp_scan_filter/ntp/ntpamp.txt
   ```

## 📊 反射器效果对比

| 协议 | 默认端口 | 放大倍数 | 可用性 | 推荐度 |
|------|----------|----------|--------|--------|
| **DNS** | 53 | 28-54x | 高 | ⭐⭐⭐⭐⭐ |
| **SSDP** | 1900 | 30-40x | 中 | ⭐⭐⭐⭐ |
| **NTP** | 123 | 2-10x | 中 | ⭐⭐⭐ |
| **SNMP** | 161 | 6-10x | 低 | ⭐⭐ |
| **Memcached** | 11211 | 10,000x+ | 极低 | ⭐ |

## 🛡️ 安全使用指南

### ✅ 合法使用

- **授权测试**: 仅对获得授权的目标进行测试
- **内网测试**: 优先在内网环境中测试
- **控制强度**: 避免对公共服务器造成过大负载
- **及时停止**: 测试完成后立即停止

### ❌ 禁止行为

- **未授权攻击**: 对未授权目标进行攻击
- **恶意放大**: 利用反射器进行恶意DDoS攻击
- **滥用公共服务**: 过度使用公共NTP/DNS服务器
- **商业攻击**: 用于商业竞争或报复

## 🔧 反射器维护

### 定期检查

```bash
# 检查NTP反射器有效性
for ip in $(cat scan_filter_attack/ntp_scan_filter/ntp/ntpamp.txt); do
    timeout 3 ntpdate -q $ip && echo "$ip - 有效" || echo "$ip - 失效"
done
```

### 清理无效IP

```bash
# 创建新的有效列表
> ntpamp_new.txt
for ip in $(cat ntpamp.txt); do
    if timeout 3 ntpdate -q $ip >/dev/null 2>&1; then
        echo $ip >> ntpamp_new.txt
    fi
done
```

### 添加新发现的反射器

```bash
# 扫描新的NTP服务器
nmap -sU -p 123 --script ntp-monlist 网段/24
```

## 📈 使用统计

当前反射器列表状态:
- **NTP反射器**: 2120个 (大部分需要更新)
- **DNS反射器**: 需要创建
- **SSDP反射器**: 需要扫描更新
- **最后更新**: 需要更新

## 🚀 推荐更新频率

- **NTP列表**: 每月更新
- **DNS列表**: 每季度检查
- **SSDP列表**: 每半年扫描
- **紧急更新**: 发现大量失效时立即更新

---

**⚠️ 重要提醒**: 反射器列表仅用于合法的网络安全测试，请确保遵守相关法律法规！
