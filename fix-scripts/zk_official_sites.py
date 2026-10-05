#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
官方自考网站清单
老孟整理的全国31省市自学考试官网汇总
"""

# 国家平台
NATIONAL = {
    "neea": {
        "name": "中国教育考试网（教育部教育考试院）",
        "base": "https://www.neea.edu.cn/",
        "zikao": "https://zikao.neea.edu.cn/",
        "note": "考试大纲、教材动态、新书速递、常见问题 — 不做报名和查分"
    }
}

# 各省官网
PROVINCES = {
    # 华北
    "北京": {
        "base": "https://www.bjeea.cn/",
        "zikao": "https://zikao.bjeea.cn/",
        "region": "华北"
    },
    "天津": {
        "base": "http://www.zhaokao.net/",
        "region": "华北"
    },
    "河北": {
        "base": "http://www.hebeea.edu.cn/",
        "region": "华北"
    },
    "山西": {
        "base": "http://www.sxkszx.cn/",
        "region": "华北"
    },
    "内蒙古": {
        "base": "https://www.nm.zsks.cn/",
        "region": "华北"
    },
    # 东北
    "辽宁": {
        "base": "http://www.lnzsks.com/",
        "region": "东北"
    },
    "吉林": {
        "base": "http://www.jleea.com.cn/",
        "region": "东北"
    },
    "黑龙江": {
        "base": "https://www.lzk.hl.cn/",
        "region": "东北"
    },
    # 华东
    "上海": {
        "base": "https://www.shmeea.edu.cn/",
        "zikao_bm": "https://zkbm.shmeea.edu.cn/",
        "zikao_service": "https://ste.shmeea.edu.cn/",
        "region": "华东"
    },
    "江苏": {
        "base": "https://www.jseea.cn/",
        "region": "华东"
    },
    "浙江": {
        "base": "https://www.zjzs.net/",
        "zikao": "https://zk.zjzs.net/",
        "region": "华东"
    },
    "安徽": {
        "base": "https://www.ahzsks.cn/",
        "region": "华东"
    },
    "福建": {
        "base": "https://www.eeafj.cn/",
        "region": "华东"
    },
    "江西": {
        "base": "http://www.jxeea.cn/",
        "region": "华东"
    },
    "山东": {
        "base": "http://www.sdzk.cn/",
        "region": "华东"
    },
    # 华中
    "河南": {
        "base": "http://www.heao.com.cn/",
        "region": "华中"
    },
    "湖北": {
        "base": "http://www.hbea.edu.cn/",
        "region": "华中"
    },
    "湖南": {
        "base": "https://www.hneeb.cn/",
        "region": "华中"
    },
    # 华南
    "广东": {
        "base": "https://eea.gd.gov.cn/",
        "zikao": "https://www.eeagd.edu.cn/selfec/",
        "region": "华南"
    },
    "广西": {
        "base": "http://www.gxeea.cn/",
        "region": "华南"
    },
    "海南": {
        "base": "http://ea.hainan.gov.cn/",
        "region": "华南"
    },
    # 西南
    "重庆": {
        "base": "http://www.cqksy.cn/",
        "region": "西南"
    },
    "四川": {
        "base": "https://www.sceea.cn/",
        "zikao": "https://zk.sceea.cn/",
        "region": "西南"
    },
    "贵州": {
        "base": "http://zsksy.guizhou.gov.cn/",
        "region": "西南"
    },
    "云南": {
        "base": "https://www.ynzs.cn/",
        "region": "西南"
    },
    "西藏": {
        "base": "http://zsks.edu.xizang.gov.cn/",
        "region": "西南"
    },
    # 西北
    "陕西": {
        "base": "http://www.sneea.cn/",
        "region": "西北"
    },
    "甘肃": {
        "base": "https://www.ganseea.cn/",
        "region": "西北"
    },
    "青海": {
        "base": "http://www.qhjyks.com/",
        "region": "西北"
    },
    "宁夏": {
        "base": "https://www.nxjyks.cn/",
        "region": "西北"
    },
    "新疆": {
        "base": "http://www.xjzk.gov.cn/",
        "region": "西北"
    }
}

# 重点省份（优先抓取，信息更丰富）
KEY_PROVINCES = ["北京", "上海", "广东", "江苏", "浙江", "山东", "四川", "湖北", "河南", "河北"]

def get_all_urls():
    """获取所有抓取目标URL"""
    urls = []

    # 国家平台
    urls.append(("全国", "neea", NATIONAL["neea"]["zikao"], "考试大纲/教材动态"))

    # 各省官网
    for prov, info in PROVINCES.items():
        base = info.get("base", "")
        zikao = info.get("zikao", "")
        urls.append((prov, prov, base, "首页"))
        if zikao and zikao != base:
            urls.append((prov, prov, zikao, "自考系统"))
        for key in ["zikao_bm", "zikao_service"]:
            url = info.get(key, "")
            if url:
                urls.append((prov, prov, url, info.get(key.replace("_bm","").replace("_service",""), "入口")))

    return urls

if __name__ == "__main__":
    print("=" * 60)
    print("自考官网清单 - 全国31省市")
    print("=" * 60)
    print(f"\n国家平台: {len(NATIONAL)} 个")
    print(f"省份: {len(PROVINCES)} 个")
    print(f"重点省份: {', '.join(KEY_PROVINCES)}")
    print("\n完整URL列表:")
    for prov, code, url, note in get_all_urls():
        print(f"  [{prov}] {note}: {url}")
