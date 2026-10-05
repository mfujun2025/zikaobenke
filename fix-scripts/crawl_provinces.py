#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawl_provinces.py
抓取各省教育考试院自考栏目最新公告，输出 raw_provinces.json。
"""
import json, re, sys, os
from urllib.request import Request, urlopen

SKIP_KW = ['高考', '考研', '教资', 'CET', '四六级', '托福', '雅思',
            'GRE', '计算机', '中小学', '教师资格', '科研', '成交', '招标',
            '普通话', '护士', '会计师']
MUST_KW = ['自考', '自学考试', '考试计划', '开考', '停考', '报名', '免考',
            '毕业', '实践', '论文', '大纲', '延期', '诚信', '报考']

PROV_ZK_URLS = [
    ("北京",   "https://www.bjeea.cn/html/zkzsd/index.html"),
    ("上海",   "https://www.shmeea.edu.cn/page/02000/200.html"),
    ("广东",   "https://eea.gd.gov.cn/xxgk/zfkawj/content/post_4328694.html"),
    ("江苏",   "https://www.jse.edu.cn/zk/index.shtml"),
    ("浙江",   "https://www.zjzs.net/zk/index.html"),
    ("山东",   "https://www.zk.dxpzxx.com"),
    ("四川",   "https://www.sceea.cn/html/zikaozigonggao.html"),
    ("湖北",   "https://www.hbea.edu.cn/zk.html"),
    ("河南",   "https://www.heeag.com/zk/index.html"),
    ("河北",   "https://www.hebeea.edu.cn/zk/index.html"),
]


def fetch(url, label=""):
    try:
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
        })
        with urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  [WARN] {label}: {e}", file=sys.stderr)
        return None


def extract_items(html, province):
    items = []
    for m in re.finditer(
        r'<a[^>]+href=["\']([^"\']+)["\'][^>]*>(?:<[^>]*>)?([^<]*(?:<[^>]*>[^<]*)*)?</a>',
        html
    ):
        href = m.group(1).strip()
        title_raw = m.group(2).strip()
        # 清理嵌套标签
        title = re.sub(r'<[^>]+>', '', title_raw).strip()
        if not href or not title:
            continue
        if '/html1/' not in href and 'report' not in href:
            continue
        if any(kw in title for kw in SKIP_KW):
            continue
        if not any(kw in title for kw in MUST_KW):
            continue
        dm = re.search(r'20(2[5-9]|[3-9]\d)', title)
        if dm:
            yr = int(dm.group()[2:4])
            if yr < 25:
                continue
        items.append({'title': title, 'url': href, 'province': province})
    return items


def main():
    all_items = []
    seen = set()

    for province, url in PROV_ZK_URLS:
        print(f"Fetching {province}...")
        html = fetch(url, province)
        if not html:
            continue
        items = extract_items(html, province)
        for it in items:
            if it['url'] not in seen:
                seen.add(it['url'])
                all_items.append(it)
        print(f"  -> {len(items)} items")

    # 也抓 zikao.neea.edu.cn
    print("Fetching zikao.neea.edu.cn 考试资讯...")
    html = fetch("https://zikao.neea.edu.cn/html1/category/16093/615-1.htm", "zikao资讯")
    if html:
        items = extract_items(html, "全国")
        for it in items:
            if it['url'] not in seen:
                seen.add(it['url'])
                all_items.append(it)
        print(f"  -> {len(items)} items")

    all_items.sort(key=lambda x: x['title'], reverse=True)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw_provinces.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"\nTotal {len(all_items)} items -> {out}")
    for it in all_items[:15]:
        print(f"  [{it.get('province','')}] {it['title'][:60]}")


if __name__ == '__main__':
    main()
