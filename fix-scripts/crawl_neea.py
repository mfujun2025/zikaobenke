#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
crawl_neea.py
从教育部教育考试院（neea.edu.cn）和自考官网（zikao.neea.edu.cn）
抓取最新自考相关公告，输出 raw_neea.json。
"""
import json, re, sys, os
from urllib.request import Request, urlopen
from html.parser import HTMLParser

TARGETS = [
    ("https://www.neea.edu.cn/html1/category/1508/151-1.htm", "neea-公示公告"),
    ("https://zikao.neea.edu.cn/html1/category/1508/151-1.htm", "zikao-公示公告"),
    ("https://zikao.neea.edu.cn/html1/category/16093/615-1.htm", "zikao-考试资讯"),
    ("https://zikao.neea.edu.cn/html1/category/1508/1403-1.htm", "zikao-考试大纲"),
]

SKIP_KW = ['高考', '考研', '教资', 'CET', '四六级', '计算机等级', '托福', '雅思',
            'GRE', 'GMAT', '中小学', '教师资格', '学业水平', '同等学力',
            '科研成果', '科研规划', '科研课题', '科研项目', '成交公告', '短信通信',
            '教材出版', '新书速递', '查处', '销毁', '英国文化教育协会']
MUST_KW = ['自考', '自学考试', '考试计划', '开考', '停考', '报名', '免考',
            '毕业', '实践', '论文', '大纲', '教材目录', '延期', '诚信', '报考']


class LinkCollector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            d = dict(attrs)
            href = d.get('href', '')
            text = d.get('title') or ''
            if href and ('report' in href or '/html1/' in href):
                self.links.append((text, href))


def fetch_page(url):
    try:
        req = Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml',
        })
        with urlopen(req, timeout=15) as r:
            return r.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f"  [WARN] {url[:50]} -> {e}", file=sys.stderr)
        return None


def extract_items(html, label):
    parser = LinkCollector()
    parser.feed(html)
    items = []
    for title, href in parser.links:
        title = title.strip()
        if not title:
            continue
        if any(kw in title for kw in SKIP_KW):
            continue
        if not any(kw in title for kw in MUST_KW):
            continue
        m = re.search(r'20(2[4-9]|[3-9]\d)', title)
        if m:
            yr = int(m.group()[2:4])
            if yr < 25:
                continue
        items.append({'title': title, 'url': href, 'source': label})
    return items


def main():
    all_items = []
    seen = set()
    for url, label in TARGETS:
        print(f"Fetching {label}...")
        html = fetch_page(url)
        if not html:
            continue
        items = extract_items(html, label)
        for it in items:
            if it['url'] not in seen:
                seen.add(it['url'])
                all_items.append(it)
        print(f"  -> {len(items)} items")

    all_items.sort(key=lambda x: x['title'], reverse=True)
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'raw_neea.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(all_items, f, ensure_ascii=False, indent=2)
    print(f"\nTotal {len(all_items)} items -> {out}")
    for it in all_items[:10]:
        print(f"  {it['title'][:60]}  ({it['source']})")


if __name__ == '__main__':
    main()
