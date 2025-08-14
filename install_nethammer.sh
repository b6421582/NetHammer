#!/bin/bash
# NetHammer 一键安装脚本
# 支持 Ubuntu/Debian/CentOS

set -e

echo "========================================"
echo "    NetHammer 一键安装脚本 v1.0"
echo "========================================"

# 检查root权限
if [ "$EUID" -ne 0 ]; then
    echo "❌ 需要root权限运行此脚本"
    echo "请使用: sudo bash install_nethammer.sh"
    exit 1
fi

# 检测系统类型
if [ -f /etc/debian_version ]; then
    OS="debian"
    echo "✅ 检测到 Debian/Ubuntu 系统"
elif [ -f /etc/redhat-release ]; then
    OS="redhat"
    echo "✅ 检测到 CentOS/RHEL 系统"
else
    echo "❌ 不支持的操作系统"
    exit 1
fi

# 更新系统
echo "📦 更新系统包..."
if [ "$OS" = "debian" ]; then
    apt update -y
    apt upgrade -y
elif [ "$OS" = "redhat" ]; then
    yum update -y
fi

# 安装基础依赖
echo "📦 安装基础依赖..."
if [ "$OS" = "debian" ]; then
    apt install -y \
        gcc \
        g++ \
        make \
        build-essential \
        libpcap-dev \
        python3 \
        python3-pip \
        git \
        wget \
        curl \
        screen \
        htop \
        net-tools \
        dstat
elif [ "$OS" = "redhat" ]; then
    yum groupinstall -y "Development Tools"
    yum install -y \
        gcc \
        gcc-c++ \
        make \
        libpcap-devel \
        python3 \
        python3-pip \
        git \
        wget \
        curl \
        screen \
        htop \
        net-tools
fi

# 安装Python依赖
echo "🐍 安装Python依赖..."
pip3 install --upgrade pip
pip3 install requests argparse

# 创建工作目录
echo "📁 创建工作目录..."
mkdir -p /opt/nethammer
cd /opt/nethammer

# 创建子目录
mkdir -p {attack_tools,source_code,scan_filter_attack,reflector_lists,logs}

echo "✅ 基础环境安装完成"
echo ""
echo "📋 下一步操作:"
echo "1. 将您的攻击脚本文件上传到 /opt/nethammer/"
echo "2. 运行编译脚本: bash compile_tools.sh"
echo "3. 开始攻击: python3 quick_attack.py <目标IP>"
echo ""
echo "📤 文件上传方法:"
echo "   scp -r attack_tools/ root@$(hostname -I | awk '{print $1}'):/opt/nethammer/"
echo "   scp -r source_code/ root@$(hostname -I | awk '{print $1}'):/opt/nethammer/"
echo "   scp *.py root@$(hostname -I | awk '{print $1}'):/opt/nethammer/"
echo ""

# 创建快速部署脚本
cat > /opt/nethammer/deploy.sh << 'EOF'
#!/bin/bash
# NetHammer 快速部署脚本

echo "NetHammer 快速部署"
echo "=================="

# 检查文件是否存在
if [ ! -d "source_code" ]; then
    echo "❌ 未找到source_code目录"
    echo "请先上传所有文件到当前目录"
    exit 1
fi

# 编译攻击工具
echo "🔨 编译攻击工具..."
bash compile_tools.sh

# 生成反射器列表
echo "📋 生成反射器列表..."
python3 create_reflector_database.py

# 设置权限
chmod +x attack_tools/*
chmod +x *.py

echo "✅ 部署完成！"
echo ""
echo "🚀 使用方法:"
echo "   python3 quick_attack.py <目标IP>"
echo "   python3 NetHammer_Master_Controller.py --target <目标IP> --auto"
echo ""
echo "⚠️  仅用于授权测试！"
EOF

chmod +x /opt/nethammer/deploy.sh

# 创建系统优化脚本
cat > /opt/nethammer/optimize_system.sh << 'EOF'
#!/bin/bash
# 系统网络优化脚本

echo "优化系统网络参数..."

# 网络参数优化
cat >> /etc/sysctl.conf << 'SYSCTL_EOF'
# NetHammer 网络优化
net.core.rmem_max = 134217728
net.core.wmem_max = 134217728
net.ipv4.tcp_rmem = 4096 87380 134217728
net.ipv4.tcp_wmem = 4096 65536 134217728
net.core.netdev_max_backlog = 30000
net.core.netdev_budget = 600
net.ipv4.ip_forward = 1
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 65535
net.ipv4.tcp_syncookies = 1
net.ipv4.tcp_tw_reuse = 1
net.ipv4.tcp_fin_timeout = 30
fs.file-max = 1048576
SYSCTL_EOF

# 应用参数
sysctl -p

# 文件描述符限制
cat >> /etc/security/limits.conf << 'LIMITS_EOF'
* soft nofile 1048576
* hard nofile 1048576
* soft nproc 1048576
* hard nproc 1048576
LIMITS_EOF

echo "✅ 系统优化完成"
echo "建议重启系统使所有参数生效: reboot"
EOF

chmod +x /opt/nethammer/optimize_system.sh

echo "🎯 安装完成！"
echo ""
echo "📍 当前位置: /opt/nethammer"
echo "🔧 运行系统优化: bash optimize_system.sh"
echo "📤 上传文件后运行: bash deploy.sh"
