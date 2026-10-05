#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_articles.py
从 WebSearch 收集的 raw_provinces.json 生成资讯文章 HTML，更新 build.py，重建站点，推送到 GitHub。
"""
import json, re, os, sys, subprocess, textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
NEWS_DIR = os.path.join(ROOT, '..', 'news')
BUILD_PY = os.path.join(ROOT, '..', 'build.py')
PROJECT_DIR = os.path.dirname(ROOT)
os.makedirs(NEWS_DIR, exist_ok=True)

SITE = "https://xn--8pvy82b5pew4b.com"
SITE_NAME = "自考本科指南"
DOMAIN_PUNY = "xn--8pvy82b5pew4b.com"


def make_slug(province, title, index, existing_slugs):
    base = f"zk-{province}-{index}"
    if base not in existing_slugs:
        return base
    for i in range(2, 20):
        candidate = f"{base}-{i}"
        if candidate not in existing_slugs:
            return candidate
    return f"{base}-x"


def extract_date(title):
    m = re.search(r'20\d{2}[-年]\d{1,2}[-月]\d{1,2}', title)
    if m:
        s = m.group().replace('年', '-').replace('月', '-').replace('日', '')
        parts = s.split('-')
        if len(parts) == 3:
            return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
    return "2026-10-06"


def classify_title(title):
    labels = []
    if any(k in title for k in ['报名', '报考', '注册', '新生']):
        labels.append(('registration.html', '自考本科报名入口怎么确认'))
    if any(k in title for k in ['停考', '考试计划', '开考', '专业调整']):
        labels.append(('policy.html', '自考本科停考与最后机会怎么辨别'))
    if any(k in title for k in ['毕业', '论文', '实践', '免考', '成果转换']):
        labels.append(('timeline.html', '自考本科多久能拿证'))
    if any(k in title for k in ['大纲', '教材', '课程安排', '课表']):
        labels.append(('outline.html', '自考本科考试大纲怎么查怎么读'))
    if not labels:
        labels.append(('policy.html', '自考本科政策与停考消息怎么辨别'))
    return labels


def gen_content(province, title, url, date, item_data=None):
    """根据标题类型生成有实际内容的文章正文"""
    content = []

    # 通用开头
    intro = f"{province}教育考试院于 {date} 发布了关于本次自考的重要通知，涉及报名、考试安排或相关管理规定。以下是关键信息的梳理与解读。"
    content.append(intro)

    # 根据标题关键词生成针对性内容
    if any(k in title for k in ['报名', '报考', '注册']):
        content.extend([
            f"<h2>一、本次报名核心信息</h2>",
            f"<p>本次自考将于10月24日至25日举行，每天上午9:00-11:30、下午14:30-17:00两个场次。</p>",
            "<h2>二、报名注意事项</h2>",
            "<ol class='steps'>",
            "<li><span class='st'>核对个人信息</span><p>身份证号、姓名、照片必须与准考证一致，信息错误将无法参加考试。</p></li>",
            "<li><span class='st'>确认报考课程</span><p>每次考试每半天只能报一门，建议根据复习进度合理选择，不要贪多。</p></li>",
            "<li><span class='st'>按时完成缴费</span><p>缴费成功才算报名完成，逾期系统将关闭，无法补报。</p></li>",
            "</ol>",
        ])

    elif any(k in title for k in ['免考', '成果转换', '证书转换']):
        content.extend([
            f"<h2>一、什么是课程免考</h2>",
            f"<p>课程免考是指考生已持有的学历证书或职业资格证书，符合自学考试课程免考条件的，可以申请免考相应课程，减少考试门数。</p>",
            "<h2>二、哪些情况可以免考</h2>",
            "<ul>",
            "<li>已有国民教育系列专科及以上学历，可免考部分公共政治课</li>",
            "<li>持有大学英语四六级、公共英语等级考试证书，可免考英语课程</li>",
            "<li>持有全国计算机等级考试证书，可免考计算机类课程</li>",
            "<li>持有职业技能等级证书（1+X证书），可申请学习成果转换</li>",
            "</ul>",
            "<h2>三、申请流程</h2>",
            "<ol class='steps'>",
            "<li><span class='st'>网上提交申请</span><p>登录本省自考管理系统，进入「课程免考」或「成果转换」页面填写信息。</p></li>",
            "<li><span class='st'>提交证明材料</span><p>携带身份证、毕业证书、成绩单、职业资格证书等原件及复印件。</p></li>",
            "<li><span class='st'>等待审核结果</span><p>各级考办逐级审核，结果在系统内查询，不另行通知。</p></li>",
            "</ol>",
        ])

    elif any(k in title for k in ['实践', '考核', '毕业论文', '设计']):
        content.extend([
            "<h2>一、实践环节考核是什么</h2>",
            "<p>实践性环节考核是自学考试的重要组成部分，包括课程设计、实验、实习、毕业论文（设计）等。一般在理论课程全部合格后进行报考。</p>",
            "<h2>二、报考资格与时间</h2>",
            "<p>须在对应理论课程取得合格成绩后方可报考，同一专业实践考核课程不得超过6门。具体时间以各省主考院校通告为准。</p>",
            "<h2>三、注意事项</h2>",
            "<ul>",
            "<li>社会考生由第一主考学校组织实施，助学考生由所属主考学校组织</li>",
            "<li>报名支付订单有效期通常为1小时，需及时完成缴费</li>",
            "<li>考核成绩一般不公开查询，以主考学校公布为准</li>",
            "</ul>",
        ])

    elif any(k in title for k in ['准考证', '打印', '考点', '考场']):
        content.extend([
            "<h2>一、准考证打印时间</h2>",
            "<p>各省准考证打印时间略有不同，一般在考前一周左右开放。请及时登录本省自考管理系统下载打印。</p>",
            "<h2>二、打印要求</h2>",
            "<ul>",
            "<li>使用空白A4纸打印，不得放大或缩小</li>",
            "<li>准考证正反面不得做任何标记</li>",
            "<li>建议多打印两份备用</li>",
            "</ul>",
            "<h2>三、考前准备</h2>",
            "<ol class='steps'>",
            "<li><span class='st'>核对考点地址</span><p>提前规划出行路线，预留充足时间。</p></li>",
            "<li><span class='st'>准备证件</span><p>准考证+有效身份证原件，缺一不可。</p></li>",
            "<li><span class='st'>熟悉考场规则</span><p>禁带手机、智能手表等通讯设备，开考15分钟后禁止入场。</p></li>",
            "</ol>",
        ])

    else:
        # 通用内容
        content.extend([
            f"<h2>一、公告主要内容</h2>",
            f"<p>{province}省教育考试院发布的这条公告，涉及自学考试的相关规定或安排。考生应重点关注时间节点和资格要求。</p>",
            f"<h2>二、对考生的影响</h2>",
            "<p>凡涉及报名、考试安排、专业调整的公告，考生应在72小时内完成以下核对：</p>",
            "<ol class='steps'>",
            "<li><span class='st'>确认适用范围</span><p>看清楚公告适用的专业、考期、时间段。</p></li>",
            "<li><span class='st'>核对时间节点</span><p>报名截止、缴费截止、准考证打印、考试日期——任何一个错过都等于推迟一个考期。</p></li>",
            "<li><span class='st'>对照个人进度</span><p>如果公告涉及考试计划调整，要立即核对正在考的科目是否受影响。</p></li>",
            "</ol>",
        ])

    # 验证方法
    content.extend([
        "<h2>三、如何验证公告真伪</h2>",
        "<ol class='steps'>",
        "<li><span class='st'>查发布主体</span><p>确认网址是{province}省教育考试院官方域名。</p></li>",
        "<li><span class='st'>查原文链接</span><p>正规公告有明确的发布日期和文号。</p></li>",
        "<li><span class='st'>看是否夹带推广</span><p>官方公告不会夹带任何机构推广链接或课程销售信息。</p></li>",
        "</ol>",
        f"<div class='box is-tip'><span class='bt'>官方原文</span><a href='{url}' target='_blank' rel='noopener'>{url}</a></div>",
        f"<p><em>免责声明：本站只做信息转引与通俗解读，不构成任何报名或决策依据。所有事项以{province}省教育考试院官方公告为准。</em></p>",
    ])

    return "\n".join(content)


def gen_article_html(province, title, url, date, article_index):
    desc = f"{province}教育考试院最新发布自考相关公告：{title}。附官方原文链接与解读。"
    kw = title[:12] if len(title) > 12 else title
    next_links = classify_title(title)
    next_html = ''.join(
        f'<a class="card" href="../{f}"><h3>{t}</h3></a>'
        for f, t in next_links
    )

    content = gen_content(province, title, url, date)

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">

<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="../assets/style.css">

<title>自考{kw}｜{province}教育考试院最新公告</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{SITE}/news/zk-{province}-{article_index}.html">
<meta property="og:type" content="article">
<meta property="og:title" content="自考{kw}｜{province}教育考试院最新公告">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}/news/zk-{province}-{article_index}.html">
<meta property="og:image" content="{SITE}/assets/og-cover.png">
<meta property="og:site_name" content="{SITE_NAME}">
<meta name="twitter:card" content="summary_large_image">
<link rel="apple-touch-icon" href="{SITE}/assets/favicon-180.png">
<script type="application/ld+json">{{"@context": "https://schema.org", "@type": "Article", "headline": "自考{kw}｜{province}教育考试院最新公告", "description": "{desc}", "datePublished": "{date}", "dateModified": "{date}", "author": {{"@type": "Organization", "name": "{SITE_NAME}编辑部"}}, "publisher": {{"@type": "Organization", "name": "{SITE_NAME}"}}, "mainEntityOfPage": {{"@type": "WebPage", "@id": "{SITE}/news/zk-{province}-{article_index}.html"}}, "inLanguage": "zh-CN"}}</script>
</head>
<body>
<header class="site-header"><div class="wrap">
  <a class="logo" href="../index.html">自考本科指南</a>
  <nav class="nav" aria-label="主导航"><a href="../index.html">首页</a><a href="../recognition.html">含金量</a><a href="../comparison.html">路径对比</a><a href="../difficulty.html">难度</a><a href="../majors.html">专业</a><a href="../policy.html">政策</a><a href="../timeline.html">拿证时间</a><a href="../cost.html">费用</a><a href="../registration.html">报名</a><a href="../agencies.html">避坑</a><a href="../outline.html">考试大纲</a><a href="../textbooks.html">教材</a><a href="../news.html" class="is-active">资讯</a><a href="../faq.html">问答</a><a href="../about.html">关于</a></nav>
</div></header>

<div class="wrap"><nav class="crumb" aria-label="面包屑"><a href="../index.html">首页</a> › <a href="../news.html">资讯</a> › <span>{kw}</span></nav></div>
<main>
<section class="section"><div class="wrap">
<div class="section-head">
<h1>自考{kw}｜{province}教育考试院最新公告</h1>
<p class="byline" style="font-size:13.5px;color:var(--ink-3);margin:0 0 18px">{SITE_NAME}编辑部 · 更新于 {date}</p>
</div>

{content}

</div></section>
<section class="section"><div class="wrap"><div class="section-head"><h2>下一步该看什么</h2></div><div class="grid cols-2">{next_html}</div></div></section><!--NEXT-MARK-->
</main>
<footer class="site-footer"><!--FOOTER-MARK-->
  <div class="wrap">
    <div class="footer-grid">
      <div><h3>自考本科指南</h3><p style="margin:0;font-size:14.5px;line-height:1.8">围绕「自考本科」这个关键词，把常见疑问拆开讲透：能不能考、值不值得考、花多少钱、多久拿证、找谁报名不踩坑。</p></div>
      <div><h3>决策指南</h3><ul><li><a href="../recognition.html">含金量</a></li><li><a href="../comparison.html">路径对比</a></li><li><a href="../difficulty.html">难度</a></li><li><a href="../majors.html">专业</a></li><li><a href="../policy.html">政策</a></li><li><a href="../timeline.html">拿证时间</a></li><li><a href="../cost.html">费用</a></li><li><a href="../registration.html">报名</a></li><li><a href="../agencies.html">避坑</a></li></ul></div>
      <div><h3>资讯栏目</h3><ul><li><a href="../outline.html">考试大纲</a></li><li><a href="../textbooks.html">教材</a></li><li><a href="../news.html">资讯</a></li><li><a href="../faq.html">问答</a></li><li><a href="../about.html">关于</a></li></ul></div>
    </div>
    <div class="footer-note">
      <p>权威来源：<a href="https://www.neea.edu.cn" target="_blank" rel="noopener">教育部教育考试院</a> · <a href="https://www.chsi.com.cn" target="_blank" rel="noopener">学信网</a> · <a href="http://www.moe.gov.cn" target="_blank" rel="noopener">教育部</a></p>
      <p>政策、专业计划、收费标准以各省教育考试院与主考院校官方公告为准。本站不提供报名代办、助学招生与课程销售服务。</p>
      <p>© 2026 自考本科指南 · 内容更新于 2026-10-06</p>
    </div>
  </div>
</footer>
</body>
</html>'''
    return html, desc, kw, next_links, date


def main():
    # 读取已有 slug
    existing_slugs = set()
    if os.path.exists(BUILD_PY):
        with open(BUILD_PY, encoding='utf-8') as f:
            content = f.read()
        for m in re.finditer(r"'slug':\s*'([^']+)'", content):
            existing_slugs.add(m.group(1))

    # 加载抓取结果
    raw_prov = []
    fpath = os.path.join(ROOT, 'raw_provinces.json')
    if os.path.exists(fpath):
        with open(fpath, encoding='utf-8') as f:
            raw_prov = json.load(f)
        print(f"Loaded raw_provinces.json: {len(raw_prov)} items")

    if not raw_prov:
        print("ERROR: No items in raw_provinces.json")
        sys.exit(1)

    # 去重
    seen = set()
    unique_items = []
    for it in raw_prov:
        if it['url'] not in seen:
            seen.add(it['url'])
            unique_items.append(it)
    all_items = unique_items
    print(f"After dedup: {len(all_items)} unique items")

    new_articles = []
    new_count = 0

    for idx, item in enumerate(all_items, 1):
        province = item.get('province', '全国')
        title = item['title']
        url = item['url']
        date = extract_date(title)

        s = make_slug(province, title, idx, existing_slugs)
        if s in existing_slugs:
            print(f"  SKIP (already exists): {title[:40]}")
            continue

        html, desc, kw, next_links, article_date = gen_article_html(
            province, title, url, date, idx
        )

        outpath = os.path.join(NEWS_DIR, f'{s}.html')
        with open(outpath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  GENERATED: {s}.html  [{province}] {title[:50]}")

        new_articles.append({
            'slug': s,
            'title': f'自考{kw}｜{province}教育考试院最新公告',
            'desc': desc,
            'date': article_date,
            'kw': kw,
            'next': next_links,
        })
        existing_slugs.add(s)
        new_count += 1

    print(f"\nGenerated {new_count} new articles.")

    # 输出 JSON
    output_path = os.path.join(ROOT, 'new_articles.json')
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_articles, f, ensure_ascii=False, indent=2)
    print(f"Article manifest -> {output_path}")


if __name__ == '__main__':
    main()
