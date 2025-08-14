#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NetHammer 白名单更新工具
定期更新受保护目标列表
"""

import json
import requests
import sys
from datetime import datetime

def update_china_gov_domains():
    """更新中国政府域名列表"""
    # 这里可以添加从官方API获取最新政府域名的逻辑
    # 目前使用静态列表
    return [
        "gov.cn", "www.gov.cn", "china.gov.cn",
        # 中央部委
        "mfa.gov.cn", "mod.gov.cn", "mps.gov.cn", "moj.gov.cn",
        "mof.gov.cn", "moe.gov.cn", "most.gov.cn", "miit.gov.cn",
        "mca.gov.cn", "mohrss.gov.cn", "mnr.gov.cn", "mee.gov.cn",
        "mohurd.gov.cn", "mot.gov.cn", "mwr.gov.cn", "moa.gov.cn",
        "mofcom.gov.cn", "nhc.gov.cn", "nrta.gov.cn", "sport.gov.cn",
        "nea.gov.cn", "safe.gov.cn", "pbc.gov.cn", "cbirc.gov.cn",
        "csrc.gov.cn", "cac.gov.cn", "samr.gov.cn", "nfra.gov.cn",
        # 省市政府
        "beijing.gov.cn", "shanghai.gov.cn", "tianjin.gov.cn", "chongqing.gov.cn",
        "guangdong.gov.cn", "jiangsu.gov.cn", "zhejiang.gov.cn", "shandong.gov.cn",
        "henan.gov.cn", "sichuan.gov.cn", "hubei.gov.cn", "hunan.gov.cn",
        "hebei.gov.cn", "shanxi.gov.cn", "liaoning.gov.cn", "jilin.gov.cn",
        "heilongjiang.gov.cn", "anhui.gov.cn", "fujian.gov.cn", "jiangxi.gov.cn",
        "guangxi.gov.cn", "hainan.gov.cn", "guizhou.gov.cn", "yunnan.gov.cn",
        "shaanxi.gov.cn", "gansu.gov.cn", "qinghai.gov.cn", "ningxia.gov.cn",
        "xinjiang.gov.cn", "tibet.gov.cn", "xizang.gov.cn"
    ]

def update_international_domains():
    """更新国际重要机构域名"""
    return {
        "us_government": [
            "gov", "mil", "edu", "whitehouse.gov", "state.gov",
            "defense.gov", "fbi.gov", "cia.gov", "nsa.gov", "dhs.gov",
            "treasury.gov", "justice.gov", "energy.gov", "nasa.gov",
            "epa.gov", "cdc.gov", "nih.gov", "usda.gov", "dot.gov"
        ],
        "international_orgs": [
            "un.org", "who.int", "unesco.org", "unicef.org",
            "nato.int", "europa.eu", "worldbank.org", "imf.org",
            "wto.org", "oecd.org", "g20.org", "asean.org"
        ],
        "other_governments": [
            "gov.uk", "gov.au", "gc.ca", "bundesregierung.de",
            "elysee.fr", "governo.it", "gov.jp", "kremlin.ru",
            "gov.in", "gov.br", "gov.za", "gov.sg"
        ]
    }

def create_updated_config():
    """创建更新的配置文件"""
    config = {
        "description": "NetHammer 受保护目标列表 - 禁止测试的重要机构和网站",
        "last_updated": datetime.now().strftime("%Y-%m-%d"),
        "version": "2.1",
        
        "china_government": {
            "description": "中国政府机构域名",
            "domains": update_china_gov_domains()
        },
        
        "china_institutions": {
            "description": "中国重要机构和事业单位",
            "domains": [
                "cas.cn", "cass.cn", "xinhuanet.com", "people.com.cn",
                "cctv.com", "cnr.cn", "chinanews.com", "gmw.cn",
                "ce.cn", "youth.cn", "legaldaily.com.cn"
            ]
        },
        
        "china_media_social": {
            "description": "中国主要媒体和社交平台",
            "domains": [
                "weibo.com", "weibo.cn", "sina.com.cn", "zhihu.com",
                "douban.com", "tieba.baidu.com", "bilibili.com",
                "douyin.com", "toutiao.com", "qq.com", "wechat.com",
                "weixin.qq.com", "baidu.com", "alibaba.com", "tencent.com",
                "jd.com", "taobao.com", "tmall.com", "alipay.com", "ant.group"
            ]
        },
        
        "education": {
            "description": "重要教育机构",
            "domains": [
                "tsinghua.edu.cn", "pku.edu.cn", "fudan.edu.cn", "sjtu.edu.cn",
                "zju.edu.cn", "nju.edu.cn", "ustc.edu.cn", "hit.edu.cn",
                "harvard.edu", "mit.edu", "stanford.edu", "yale.edu",
                "princeton.edu", "columbia.edu", "oxford.ac.uk", "cambridge.ac.uk"
            ]
        },
        
        "financial": {
            "description": "重要金融机构",
            "domains": [
                "federalreserve.gov", "ecb.europa.eu", "boj.or.jp",
                "bankofengland.co.uk", "bundesbank.de", "banque-france.fr",
                "swift.com", "visa.com", "mastercard.com", "paypal.com"
            ]
        },
        
        "critical_infrastructure": {
            "description": "关键基础设施关键词",
            "keywords": [
                "hospital", "emergency", "911", "110", "119", "120",
                "police", "fire", "ambulance", "medical", "health",
                "power", "electric", "electricity", "water", "gas", "nuclear",
                "airport", "railway", "subway", "metro", "bank", "financial",
                "school", "university", "government", "military", "defense",
                "critical", "infrastructure", "utility", "telecom"
            ]
        },
        
        "protected_ip_ranges": {
            "description": "受保护的IP地址段",
            "ranges": [
                "127.0.0.0/8",      # 本地回环
                "10.0.0.0/8",       # 私有网络A类
                "172.16.0.0/12",    # 私有网络B类
                "192.168.0.0/16",   # 私有网络C类
                "169.254.0.0/16",   # 链路本地
                "224.0.0.0/4",      # 多播地址
                "240.0.0.0/4"       # 保留地址
            ]
        }
    }
    
    # 添加国际域名
    international = update_international_domains()
    for category, domains in international.items():
        config[category] = {
            "description": f"国际{category}域名",
            "domains": domains
        }
    
    return config

def backup_current_config():
    """备份当前配置"""
    try:
        with open('protected_targets.json', 'r', encoding='utf-8') as f:
            current_config = json.load(f)
        
        backup_filename = f"protected_targets_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(backup_filename, 'w', encoding='utf-8') as f:
            json.dump(current_config, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 当前配置已备份到: {backup_filename}")
        return True
    except FileNotFoundError:
        print("ℹ️ 未找到现有配置文件，跳过备份")
        return True
    except Exception as e:
        print(f"❌ 备份失败: {e}")
        return False

def update_config():
    """更新配置文件"""
    try:
        # 备份现有配置
        if not backup_current_config():
            return False
        
        # 创建新配置
        new_config = create_updated_config()
        
        # 写入新配置
        with open('protected_targets.json', 'w', encoding='utf-8') as f:
            json.dump(new_config, f, ensure_ascii=False, indent=2)
        
        print("✅ 白名单配置已更新")
        
        # 统计信息
        total_domains = 0
        for category, data in new_config.items():
            if isinstance(data, dict) and 'domains' in data:
                total_domains += len(data['domains'])
        
        print(f"📊 保护统计:")
        print(f"   - 总计保护域名: {total_domains}")
        print(f"   - 关键词过滤: {len(new_config.get('critical_infrastructure', {}).get('keywords', []))}")
        print(f"   - IP段保护: {len(new_config.get('protected_ip_ranges', {}).get('ranges', []))}")
        
        return True
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

def test_filter():
    """测试过滤器功能"""
    print("\n🧪 测试白名单过滤器...")
    
    test_targets = [
        "gov.cn",           # 应该被阻止
        "weibo.com",        # 应该被阻止
        "127.0.0.1",        # 应该被阻止
        "192.168.1.1",      # 应该被阻止
        "example.com",      # 应该通过
        "test.local"        # 应该通过
    ]
    
    filter_system = WhitelistFilter()
    
    for target in test_targets:
        is_protected, message = filter_system.check_target(target)
        status = "🚫 阻止" if is_protected else "✅ 通过"
        print(f"   {target:15} -> {status}")

def main():
    """主函数"""
    print("NetHammer 白名单更新工具")
    print("=" * 30)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_filter()
        return
    
    print("正在更新白名单配置...")
    
    if update_config():
        print("\n✅ 更新完成！")
        test_filter()
    else:
        print("\n❌ 更新失败！")
        sys.exit(1)

if __name__ == "__main__":
    main()
