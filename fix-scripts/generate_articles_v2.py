#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_articles_v2.py
从 raw_provinces_v2.json（真实官网数据）生成资讯文章 HTML，更新 build.py，重建站点，推送 GitHub。
"""
import json
import os
import re
import sys
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent.parent
NEWS_DIR = WORK_DIR / "news"
BUILD_PY = WORK_DIR / "build.py"
RAW_FILE = WORK_DIR / "fix-scripts" / "raw_provinces_v2.json"
OUTPUT_JSON = WORK_DIR / "fix-scripts" / "new_articles_v2.json"


def load_raw():
    with open(RAW_FILE, encoding="utf-8") as f:
        return json.load(f)


def existing_slugs():
    """获取已存在的 slug 列表"""
    slugs = set()
    if NEWS_DIR.exists():
        for fp in NEWS_DIR.glob("*.html"):
            m = re.match(r"^(zk-[^-]+)-(\d+)\.html$", fp.name)
            if m:
                slugs.add(fp.stem)
    # 也读 build.py 的 ARTICLES
    if BUILD_PY.exists():
        code = BUILD_PY.read_text(encoding="utf-8")
        for m in re.finditer(r"'slug':\s*'([^']+)'", code):
            slugs.add(m.group(1))
    return slugs


def make_slug(province, title, index, existing):
    base = f"zk-{province}-{index}"
    if base not in existing:
        return base
    for i in range(100):
        candidate = f"{base}-{i+1}"
        if candidate not in existing:
            return candidate
    return f"zk-{province}-{index}"


def gen_article_html(item, article_index):
    province = item["province"]
    title = item["title"]
    url = item["url"]
    date = item["date"]
    source = item.get("source", "")
    fee = item.get("fee", "")
    exam_dates = item.get("exam_dates", "")
    apply_start = item.get("apply_start", "")
    apply_end = item.get("apply_end", "")
    note = item.get("note", "")

    # 判断文章类型
    if "报名" in title and ("注册" in title or "报考" in title):
        article_type = "报名"
    elif "免考" in title or "免考" in title:
        article_type = "免考"
    elif "实践" in title or "实践环节" in title:
        article_type = "实践考核"
    elif "成绩" in title or "查询" in title:
        article_type = "成绩查询"
    elif "打印" in title or "准考证" in title:
        article_type = "准考证打印"
    elif "通知" in title or "公告" in title:
        article_type = "官方通知"
    else:
        article_type = "资讯"

    # 生成解读内容
    sections = gen_content_sections(item, article_type)

    sections_html = "\n".join(sections)

    # next 链接（内链）
    next_links = classify_next_links(article_type, province)

    next_html_parts = []
    for target_slug, target_title in next_links:
        next_html_parts.append(
            f'<li><a href="/news/{target_slug}.html">{target_title}</a></li>'
        )
    next_html = "\n".join(next_html_parts) if next_html_parts else '<li>暂无相关内链</li>'

    # 结构化数据
    jsonld = f'''{{
      "@context": "https://schema.org",
      "@type": "NewsArticle",
      "headline": "{title}",
      "datePublished": "{date}",
      "dateModified": "{date}",
      "author": {{
        "@type": "Organization",
        "name": "自考本科.com"
      }},
      "publisher": {{
        "@type": "Organization",
        "name": "自考本科.com",
        "url": "https://xn--8pvy82b5pew4b.com/"
      }},
      "description": "{item.get('note', title[:60])}",
      "about": [{{"@type": "thing", "name": "高等教育自学考试"}}, {{"@type": "thing", "name": "{province}自考"}}]
    }}'''

    kw = f"自考,{province}自考,{date}自考"
    if article_type == "报名":
        kw += ",自考报名"
    elif article_type == "免考":
        kw += ",自考免考"

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} - 自考本科.com</title>
<meta name="description" content="{item.get('note', title[:80])}">
<meta name="keywords" content="{kw}">
<link rel="canonical" href="https://xn--8pvy82b5pew4b.com/news/zk-{province.lower()}-{article_index}.html">
<script type="application/ld+json">{jsonld}</script>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,"Noto Sans SC",sans-serif;background:#f5f7fa;color:#1a1a1a;line-height:1.8}}
  a{{color:#1a73e8;text-decoration:none}}
  a:hover{{text-decoration:underline}}
  .container{{max-width:800px;margin:0 auto;padding:20px}}
  .breadcrumb{{font-size:14px;color:#666;margin-bottom:16px}}
  .breadcrumb a{{color:#1a73e8}}
  h1{{font-size:24px;font-weight:700;margin-bottom:12px;line-height:1.4}}
  .meta{{font-size:14px;color:#888;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid #e8e8e8}}
  .meta span{{margin-right:16px}}
  .lead{{font-size:16px;color:#333;margin-bottom:24px;padding:16px;background:#fff;border-radius:8px;border-left:4px solid #1a73e8}}
  .article-body h2{{font-size:18px;font-weight:600;margin:24px 0 12px;color:#1a1a1a}}
  .article-body p{{margin-bottom:12px;color:#333}}
  .article-body ul,.article-body ol{{margin:12px 0 12px 20px}}
  .article-body li{{margin-bottom:8px}}
  .info-table{{width:100%;border-collapse:collapse;margin:16px 0;font-size:14px}}
  .info-table th,.info-table td{{border:1px solid #e0e0e0;padding:10px 12px;text-align:left}}
  .info-table th{{background:#f0f4ff;font-weight:600}}
  .info-table tr:nth-child(even){{background:#fafbfc}}
  .warning-box{{background:#fff8e1;border-left:4px solid #ffa000;padding:12px 16px;margin:16px 0;border-radius:0 8px 8px 0}}
  .tip-box{{background:#e8f5e9;border-left:4px solid #43a047;padding:12px 16px;margin:16px 0;border-radius:0 8px 8px 0}}
  .next-links{{background:#fff;padding:20px;border-radius:8px;margin-top:32px;border:1px solid #e8e8e8}}
  .next-links h3{{font-size:16px;margin-bottom:12px}}
  .next-links ul{{list-style:none;margin:0;padding:0}}
  .next-links li{{padding:8px 0;border-bottom:1px solid #f0f0f0}}
  .next-links li:last-child{{border-bottom:none}}
  .source-box{{font-size:13px;color:#888;margin-top:24px;padding-top:16px;border-top:1px solid #e8e8e8}}
</style>
</head>
<body>
<div class="container">
  <div class="breadcrumb">
    <a href="/">首页</a> &gt; <a href="/news.html">自考资讯</a> &gt; <span>{title[:30]}...</span>
  </div>

  <h1>{title}</h1>

  <div class="meta">
    <span>📅 {date}</span>
    <span>📍 {province}</span>
    <span>📌 {article_type}</span>
  </div>

  <div class="lead">
    {item.get('note', f'{province}教育考试院最新发布自考相关公告，涉及报名时间、考试安排、费用标准等重要信息，考生请及时关注官方渠道获取准确资讯。')}
  </div>

  <div class="article-body">
{sections_html}
  </div>

  <div class="source-box">
    <strong>信息来源：</strong><a href="{url}" target="_blank" rel="noopener noreferrer">{source or url}</a>
    <br><strong>官方入口：</strong>{item.get('source', '各省教育考试院官网')}
  </div>

  <div class="next-links">
    <h3>📖 推荐阅读</h3>
    <ul>
{next_html}
    </ul>
  </div>
</div>
</body>
</html>'''
    return html


def gen_content_sections(item, article_type):
    """根据文章类型生成有针对性的解读内容"""
    province = item["province"]
    title = item["title"]
    fee = item.get("fee", "")
    exam_dates = item.get("exam_dates", "")
    apply_start = item.get("apply_start", "")
    apply_end = item.get("apply_end", "")
    reg_start = item.get("reg_start", "")
    reg_end = item.get("reg_end", "")
    pay_start = item.get("pay_start", "")
    pay_end = item.get("pay_end", "")
    print_start = item.get("print_start", "")
    results = item.get("results", "")
    note = item.get("note", "")

    if article_type == "报名":
        return [
            f'<h2>一、{province}自考报名时间节点</h2>',
            f'<p>根据{province}教育考试院最新公告，2026年下半年自学考试将于{exam_dates or "10月下旬"}举行。本次报名关键环节如下：</p>',
            '<ul>',
            f'<li><span class="st">网上报名时间</span><p>{apply_start or "请关注官方公告"} — {apply_end or "请关注官方公告"}</p></li>',
            f'<li><span class="st">新生注册时间</span><p>{reg_start or apply_start or "同上"} — {reg_end or apply_end or "同上"}</p></li>',
            f'<li><span class="st">网上缴费时间</span><p>{pay_start or apply_start or "同上"} — {pay_end or apply_end or "同上"}</p></li>',
            '</ul>',
            '<div class="warning-box">',
            '<strong>⚠️ 重要提醒：</strong>各省份报名时间节点不同，务必以本省教育考试院官方公告为准。错过报名需等待下次考期（通常为间隔半年）。',
            '</div>',
            f'<h2>二、报名费用标准</h2>',
            f'<p>本次自考报名费用为<strong>{fee or "按省规定"}</strong>，具体金额以报名系统显示为准。</p>',
            '<h2>三、报名注意事项</h2>',
            '<ol>',
            '<li><strong>官方渠道</strong>：务必通过各省教育考试院官网报名，勿信第三方代报。</li>',
            '<li><strong>材料准备</strong>：身份证、证件照、手机号等提前备好，部分省份要求手持身份证照。</li>',
            '<li><strong>缴费确认</strong>：报考后必须完成缴费，仅选科不缴费视为无效报考。</li>',
            '<li><strong>时间节点</strong>：报名系统有严格截止时间，建议提前操作避免拥堵。</li>',
            '</ol>',
            '<div class="tip-box">',
            '<strong>💡 备考建议：</strong>报名完成后即可开始备考，结合考试计划选择每次报考科目数量（一般2-4门为宜）。',
            '</div>',
        ]

    elif article_type == "官方通知":
        return [
            f'<h2>一、公告核心内容</h2>',
            f'<p>{province}教育考试院发布通知，明确了2026年下半年自学考试的相关安排。考试定于<strong>{exam_dates or "10月下旬"}</strong>举行。</p>',
            '<h2>二、关键时间节点</h2>',
            '<table class="info-table">',
            '<tr><th>事项</th><th>时间</th></tr>',
            f'<tr><td>考试时间</td><td>{exam_dates or "10月24-25日"}</td></tr>',
            f'<tr><td>报名时间</td><td>{apply_start or apply_end or "以官方公告为准"}</td></tr>',
            f'<tr><td>缴费时间</td><td>{pay_start or pay_end or "以官方公告为准"}</td></tr>',
            f'<tr><td>准考证打印</td><td>{print_start or "考前一周"}</td></tr>',
            f'<tr><td>成绩公布</td><td>{results or "考后约1个月"}</td></tr>',
            '</table>',
            '<h2>三、重要说明</h2>',
            f'<p>{note or "具体安排请以官方公告为准，考生应密切关注所在省份教育考试院官网通知。"}</p>',
            '<div class="warning-box">',
            '<strong>⚠️ 提示：</strong>各省份自考报名时间、考试安排存在差异，请务必以本省教育考试院官方发布的信息为准。',
            '</div>',
        ]

    elif article_type == "免考":
        return [
            f'<h2>一、免考申请条件</h2>',
            '<p>符合以下条件之一的考生可申请课程免考：</p>',
            '<ul>',
            '<li>已取得国民教育系列学历，且课程设置名称、代码相同或相近的</li>',
            '<li>取得全国英语等级考试（PETS）、大学英语四六级（CET）等证书，可申请外语类课程免考</li',
            '<li>取得计算机等级证书，可申请计算机类课程免考</li',
            '<li>其他符合各省教育考试院规定的免考情形</li>',
            '</ul>',
            '<h2>二、办理流程</h2>',
            '<ol>',
            '<li><strong>网上提交申请</strong>：登录本省自考管理系统，进入"课程免考"或"成果转换"页面填写信息。</li>',
            '<li><strong>提交证明材料</strong>：携带身份证、毕业证书、成绩单、职业资格证书等原件及复印件。</li>',
            '<li><strong>等待审核结果</strong>：各级考办逐级审核，结果在系统内查询，不另行通知。</li>',
            '</ol>',
            '<div class="tip-box">',
            '<strong>💡 注意：</strong>免考申请通常在报名同期进行，错过需等待下次申请窗口。实践课程、毕业论文一般不可免考。',
            '</div>',
        ]

    else:
        # 通用模板
        return [
            f'<h2>一、公告概述</h2>',
            f'<p>{province}教育考试院发布关于2026年下半年高等教育自学考试的最新通知，涉及报名、考试、成绩等重要事项。</p>',
            f'<h2>二、考试时间</h2>',
            f'<p>本次考试定于<strong>{exam_dates or "2026年10月24日至25日"}</strong>举行，具体科目时间安排以准考证为准。</p>',
            '<h2>三、备考建议</h2>',
            '<ul>',
            '<li><strong>教材对齐</strong>：严格按省考试院当次公布的使用教材版本备考，旧版易漏新考点。</li>',
            '<li><strong>大纲领路</strong>：以课程大纲的"考核要求"为纲，区分识记、领会、简单应用与综合应用层级。</li>',
            '<li><strong>真题驱动</strong>：近三至五年真题反映命题侧重，按题型归纳高频考点。</li>',
            '</ul>',
            '<div class="warning-box">',
            '<strong>⚠️ 提示：</strong>具体安排请以各省教育考试院官方公告为准，本文仅供参考。',
            '</div>',
        ]


def classify_next_links(article_type, province):
    """根据文章类型和省份推荐内链"""
    internal_links = [
        ("zk-全国-14", "全国自考2026年下半年考试安排"),
        ("zk-全国-15", "全国自学考试时间及考场规则"),
    ]

    province_links = {
        "北京": [("zk-北京-1", "北京自考2026年下半年报名通知")],
        "上海": [("zk-上海-1", "上海自考2026年下半年报名公告")],
        "广东": [("zk-广东-1", "广东自考2026年10月网上报名须知")],
        "江苏": [("zk-江苏-1", "江苏自考2026年10月报名通告")],
        "浙江": [("zk-浙江-1", "浙江自考2026年10月报名公告")],
        "山东": [("zk-山东-1", "山东自考2026年10月报名工作通知")],
        "四川": [("zk-四川-1", "四川自考2026年下半年新生注册及课程报考通告")],
        "河南": [("zk-河南-1", "河南自考2026年下半年报名安排")],
        "湖北": [("zk-湖北-1", "湖北自考2026年10月网上报名须知")],
    }

    links = list(internal_links)
    links.extend(province_links.get(province, []))
    return links


def main():
    print("📥 读取原始数据...")
    items = load_raw()
    print(f"   共 {len(items)} 条数据")

    print("📋 检查已有文章...")
    existing = existing_slugs()
    print(f"   已有 {len(existing)} 个 slug")

    print("📝 生成文章 HTML...")
    new_articles = []
    existing_count = len(list(NEWS_DIR.glob("zk-*.html")))

    for idx, item in enumerate(items, start=1):
        slug = make_slug(item["province"], item["title"], idx, existing)
        html = gen_article_html(item, idx + existing_count)
        filepath = NEWS_DIR / f"{slug}.html"
        filepath.write_text(html, encoding="utf-8")
        new_articles.append({
            "slug": slug,
            "title": item["title"],
            "province": item["province"],
            "date": item["date"],
            "source": item.get("source", ""),
            "url": item["url"],
        })
        print(f"   ✓ {slug}")

    print(f"\n✅ 生成 {len(new_articles)} 篇新文章")

    # 输出清单
    OUTPUT_JSON.write_text(json.dumps(new_articles, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"📄 清单已保存到: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
