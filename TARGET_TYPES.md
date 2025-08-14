# NetHammer 目标类型说明

## 📋 测试方法与目标类型对应表

### 🌐 需要域名的方法 (应用层攻击)

这些方法需要域名，因为它们工作在应用层，需要进行DNS解析或HTTP请求：

| 方法 | 目标类型 | 端口 | 说明 |
|------|----------|------|------|
| **http2** | 域名 | 443/80 | HTTP/2 Rapid Reset攻击，需要建立HTTP/2连接 |
| **http** | 域名 | 80/443 | HTTP洪水攻击，需要发送HTTP请求 |
| **rudy** | 域名 | 80/443 | 慢速POST攻击，需要HTTP协议 |

**示例:**
```bash
# ✅ 正确 - 使用域名
python3 quick_attack.py test.local -p 443 -m http2 -c 200 -t 600
python3 quick_attack.py example.local -p 80 -m http -c 150 -t 300

# ❌ 错误 - 不要对这些方法使用IP
# python3 quick_attack.py 192.168.1.100 -m http2  # 这样不会工作
```

### 🔢 支持IP地址的方法 (网络层攻击)

这些方法工作在网络层或传输层，可以直接使用IP地址：

| 方法 | 目标类型 | 端口 | 说明 |
|------|----------|------|------|
| **syn** | IP/域名 | 任意 | SYN洪水攻击，TCP层攻击 |
| **ack** | IP/域名 | 任意 | ACK洪水攻击，TCP层攻击 |
| **udp** | IP/域名 | 任意 | UDP洪水攻击，UDP层攻击 |
| **fin** | IP/域名 | 任意 | FIN洪水攻击，TCP层攻击 |
| **rst** | IP/域名 | 任意 | RST洪水攻击，TCP层攻击 |
| **psh** | IP/域名 | 任意 | PSH洪水攻击，TCP层攻击 |

**示例:**
```bash
# ✅ 推荐 - 使用IP地址
python3 quick_attack.py 192.168.1.100 -m syn -c 300 -t 600
python3 quick_attack.py 192.168.1.100 -m udp -c 200 -t 300

# ✅ 也可以 - 使用域名 (会自动解析为IP)
python3 quick_attack.py test.local -m syn -c 300 -t 600
```

### 🔄 反射放大攻击 (特殊情况)

这些方法使用第三方服务器进行反射攻击，目标可以是IP或域名：

| 方法 | 目标类型 | 端口 | 说明 |
|------|----------|------|------|
| **dns** | IP/域名 | 53 | DNS反射攻击，使用DNS服务器放大 |
| **ntp** | IP/域名 | 123 | NTP反射攻击，使用NTP服务器放大 |
| **ssdp** | IP/域名 | 1900 | SSDP反射攻击，使用UPnP设备放大 |
| **cldap** | IP/域名 | 389 | CLDAP反射攻击，使用LDAP服务器放大 |
| **coap** | IP/域名 | 5683 | CoAP反射攻击，使用IoT设备放大 |
| **snmp** | IP/域名 | 161 | SNMP反射攻击，使用SNMP设备放大 |
| **netbios** | IP/域名 | 137 | NetBIOS反射攻击 |

**示例:**
```bash
# ✅ 推荐 - 使用IP地址 (更直接)
python3 quick_attack.py 192.168.1.100 -m dns -c 100 -t 600
python3 quick_attack.py 192.168.1.100 -m cldap -c 80 -t 900

# ✅ 也可以 - 使用域名
python3 quick_attack.py test.local -m dns -c 100 -t 600
```

### 🎯 高级专用方法

| 方法 | 目标类型 | 说明 |
|------|----------|------|
| **arme** | IP/域名 | 高级TCP攻击 |
| **dominate** | IP/域名 | 多协议组合攻击 |
| **essyn** | IP/域名 | 增强SYN攻击 |
| **trigemini** | IP/域名 | 三重协议攻击 |
| **vse** | IP/域名 | 游戏服务器专用 |

## 🔧 实际使用建议

### 📝 选择目标类型的原则

1. **测试Web服务** → 使用域名
   ```bash
   python3 quick_attack.py your-test-site.local -m http2
   ```

2. **测试网络设备** → 使用IP地址
   ```bash
   python3 quick_attack.py 192.168.1.1 -m syn
   ```

3. **测试服务器性能** → 根据服务类型选择
   ```bash
   # Web服务器
   python3 quick_attack.py web.test.local -m http2
   
   # 数据库服务器
   python3 quick_attack.py 192.168.1.100 -p 3306 -m syn
   ```

### ⚠️ 重要提醒

- **域名示例**: 请使用 `test.local`, `example.local` 等测试域名
- **IP示例**: 请使用 `192.168.x.x`, `10.x.x.x` 等私有IP
- **生产环境**: 确保获得明确授权后再进行任何测试
- **白名单保护**: 工具会自动阻止对重要机构的测试

### 🛡️ 安全启动示例

```bash
# 安全启动 - 自动进行目标类型检查
python3 safe_launch.py test.local -m http2 -c 200 -t 600
python3 safe_launch.py 192.168.1.100 -m syn -c 300 -t 600
```
