#!/bin/bash
# NetHammer 快速编译脚本 - 仅编译核心攻击工具

echo "NetHammer 快速编译器 (核心工具)"
echo "================================"

# 创建目录
mkdir -p attack_tools
mkdir -p logs

echo "🚀 快速编译核心攻击工具..."

# 核心工具列表
declare -A core_tools=(
    ["http2_rapid_reset"]="http2_rapid_reset_attack.c"
    ["cldap_amplification"]="cldap_amplification_attack.c"
    ["coap_amplification"]="coap_amplification_attack.c"
    ["DNS"]="dns_reflection_attack.c"
    ["ssdp"]="ssdp_amplification_attack.c"
    ["syn"]="syn_flood_attack.c"
    ["ack"]="ack_flood_attack.c"
    ["udp"]="udp_flood_attack.c"
    ["http"]="http_flood_attack.c"
    ["rudy"]="rudy_slow_attack.c"
)

compiled=0
failed=0

for tool in "${!core_tools[@]}"; do
    source_file="source_code/${core_tools[$tool]}"
    if [ -f "$source_file" ]; then
        echo "编译 $tool..."
        if gcc -o "attack_tools/$tool" "$source_file" -lpthread -lpcap 2>/dev/null; then
            echo "✅ $tool 编译成功"
            ((compiled++))
        else
            echo "❌ $tool 编译失败"
            ((failed++))
        fi
    else
        echo "⚠️  源文件不存在: $source_file"
        ((failed++))
    fi
done

# 设置执行权限
chmod +x attack_tools/* 2>/dev/null
chmod +x *.py 2>/dev/null

echo ""
echo "📊 编译结果:"
echo "   - 成功: $compiled 个工具"
echo "   - 失败: $failed 个工具"
echo "   - 总计: $((compiled + failed)) 个工具"

if [ $compiled -gt 0 ]; then
    echo ""
    echo "🎉 快速编译完成！可用工具:"
    ls -1 attack_tools/ 2>/dev/null | sed 's/^/   - /'
    
    echo ""
    echo "🚀 快速使用:"
    echo "   sudo python3 quick_attack.py <目标IP>"
    echo "   sudo python3 quick_attack.py <目标IP> -m http2"
fi

echo ""
echo "💡 提示: 使用 'bash compile_tools.sh' 编译所有工具"
echo "⚠️  仅用于授权测试！"
