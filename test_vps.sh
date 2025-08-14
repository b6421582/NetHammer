#!/bin/bash
# NetHammer VPS兼容性测试脚本
# 测试VPS是否支持NetHammer所需的功能

echo "NetHammer VPS兼容性测试"
echo "======================="
echo "测试时间: $(date)"
echo "系统信息: $(uname -a)"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果统计
PASS=0
FAIL=0
WARN=0

# 测试函数
test_item() {
    local name="$1"
    local command="$2"
    local required="$3"
    
    printf "%-40s" "$name"
    
    if eval "$command" >/dev/null 2>&1; then
        echo -e "${GREEN}[PASS]${NC}"
        ((PASS++))
        return 0
    else
        if [ "$required" = "required" ]; then
            echo -e "${RED}[FAIL]${NC}"
            ((FAIL++))
        else
            echo -e "${YELLOW}[WARN]${NC}"
            ((WARN++))
        fi
        return 1
    fi
}

echo "🔍 基础环境检查"
echo "----------------------------------------"

# 检查root权限
test_item "Root权限检查" "[ \$(id -u) -eq 0 ]" "required"

# 检查操作系统
test_item "Linux系统检查" "[ \$(uname -s) = 'Linux' ]" "required"

# 检查基础命令
test_item "GCC编译器" "which gcc" "required"
test_item "Python3" "which python3" "required"
test_item "Make工具" "which make" "optional"

echo ""
echo "🌐 网络功能检查"
echo "----------------------------------------"

# 检查网络连接
test_item "外网连接" "ping -c 1 8.8.8.8" "required"
test_item "DNS解析" "nslookup google.com" "required"

# 检查原始Socket支持
test_item "原始Socket支持" "python3 -c 'import socket; s=socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP); s.close()'" "required"

# 检查端口绑定
test_item "端口绑定测试" "python3 -c 'import socket; s=socket.socket(); s.bind((\"\", 0)); s.close()'" "required"

echo ""
echo "📦 依赖库检查"
echo "----------------------------------------"

# 检查开发库
test_item "libpcap开发库" "ldconfig -p | grep libpcap" "required"
test_item "pthread库" "ldconfig -p | grep pthread" "required"

# 检查Python库
test_item "Python socket模块" "python3 -c 'import socket'" "required"
test_item "Python threading模块" "python3 -c 'import threading'" "required"
test_item "Python subprocess模块" "python3 -c 'import subprocess'" "required"

echo ""
echo "⚡ 性能检查"
echo "----------------------------------------"

# CPU核心数
CPU_CORES=$(nproc)
test_item "CPU核心数 (>= 2)" "[ $CPU_CORES -ge 2 ]" "optional"
echo "   检测到 $CPU_CORES 个CPU核心"

# 内存检查
MEMORY_GB=$(free -g | awk '/^Mem:/{print $2}')
test_item "内存容量 (>= 1GB)" "[ $MEMORY_GB -ge 1 ]" "required"
echo "   检测到 ${MEMORY_GB}GB 内存"

# 磁盘空间
DISK_GB=$(df / | awk 'NR==2{print int($4/1024/1024)}')
test_item "磁盘空间 (>= 1GB)" "[ $DISK_GB -ge 1 ]" "required"
echo "   可用磁盘空间: ${DISK_GB}GB"

echo ""
echo "🔧 系统配置检查"
echo "----------------------------------------"

# 检查文件描述符限制
ULIMIT_N=$(ulimit -n)
test_item "文件描述符限制 (>= 1024)" "[ $ULIMIT_N -ge 1024 ]" "optional"
echo "   当前限制: $ULIMIT_N"

# 检查进程限制
ULIMIT_U=$(ulimit -u)
test_item "进程数限制 (>= 1024)" "[ $ULIMIT_U -ge 1024 ]" "optional"
echo "   当前限制: $ULIMIT_U"

echo ""
echo "🏢 VPS提供商检测"
echo "----------------------------------------"

# 检测VPS提供商
if curl -s --max-time 5 http://169.254.169.254/latest/meta-data/ >/dev/null 2>&1; then
    echo "检测到: Amazon AWS EC2"
elif curl -s --max-time 5 http://169.254.169.254/metadata/v1/ >/dev/null 2>&1; then
    echo "检测到: DigitalOcean"
elif [ -f /sys/class/dmi/id/sys_vendor ] && grep -qi "Google" /sys/class/dmi/id/sys_vendor; then
    echo "检测到: Google Cloud Platform"
elif [ -f /sys/class/dmi/id/sys_vendor ] && grep -qi "Microsoft" /sys/class/dmi/id/sys_vendor; then
    echo "检测到: Microsoft Azure"
else
    echo "检测到: 其他VPS提供商或物理服务器"
fi

# 网络质量测试
echo ""
echo "📊 网络质量测试"
echo "----------------------------------------"

echo "延迟测试:"
for target in "8.8.8.8" "1.1.1.1" "114.114.114.114"; do
    latency=$(ping -c 3 $target 2>/dev/null | tail -1 | awk -F '/' '{print $5}')
    if [ -n "$latency" ]; then
        echo "  $target: ${latency}ms"
    else
        echo "  $target: 超时"
    fi
done

echo ""
echo "📋 测试结果汇总"
echo "========================================"
echo -e "通过: ${GREEN}$PASS${NC} 项"
echo -e "警告: ${YELLOW}$WARN${NC} 项"
echo -e "失败: ${RED}$FAIL${NC} 项"
echo ""

# 给出建议
if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}✅ 恭喜！您的VPS完全兼容NetHammer${NC}"
    echo "可以安全地运行所有NetHammer功能"
    echo ""
    echo "🚀 快速开始:"
    echo "git clone https://github.com/b6421582/NetHammer.git"
    echo "cd NetHammer"
    echo "bash compile_tools.sh"
elif [ $FAIL -le 2 ]; then
    echo -e "${YELLOW}⚠️  您的VPS基本兼容NetHammer，但有一些问题需要解决${NC}"
    echo ""
    echo "🔧 建议修复:"
    if ! which gcc >/dev/null 2>&1; then
        echo "- 安装GCC: apt install gcc 或 yum install gcc"
    fi
    if ! ldconfig -p | grep libpcap >/dev/null 2>&1; then
        echo "- 安装libpcap: apt install libpcap-dev 或 yum install libpcap-devel"
    fi
else
    echo -e "${RED}❌ 您的VPS不兼容NetHammer${NC}"
    echo "建议更换VPS提供商或升级配置"
    echo ""
    echo "🏆 推荐VPS提供商:"
    echo "- OVH (完全支持原始Socket)"
    echo "- Hetzner (性价比高)"
    echo "- Contabo (配置强大)"
fi

echo ""
echo "📞 需要帮助？"
echo "GitHub: https://github.com/b6421582/NetHammer/issues"
echo "========================================"
