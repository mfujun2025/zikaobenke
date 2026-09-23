#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自考本科.com 站点构建后处理器。
- 清理 data-page-node-id 垃圾属性（P2-12）
- example.com 占位域名 -> 自考本科.com（punycode，保证 sitemap/canonical 合规）（P0-1）
- 删除 meta keywords（P2-13）
- 重写 title / description / og（P1-5）
- 补权威外链到页脚（P0-2）
- 补结构化数据 WebSite/Org/Breadcrumb/Article（P1-8/9）+ 面包屑
- 补更新日期信号（P0-4）+ 下一步内链模块（P1-7）
- 补长尾短语 FAQ（P1-6）
- 重建 nav / footer（统一外壳）
- P0-3 关键词修复（agencies / policy 的 H1+首段）
- 生成 sitemap.xml / robots.txt / CNAME
所有变换幂等（带标记守卫），可重复运行。
"""
import os, re, glob, json

ROOT = os.path.dirname(os.path.abspath(__file__))
# 技术 URL 用 punycode，保证机器可读（sitemap/canonical/og/robots 合规）
DOMAIN_PUNY = "xn--8pvy82b5pew4b.com"
SITE = "https://" + DOMAIN_PUNY
DATE = "2026-09-23"
SITE_NAME = "自考本科指南"
PUB_DATE = "2026-09-22"

NAV = [
    ('index.html', '首页'),
    ('recognition.html', '含金量'),
    ('comparison.html', '路径对比'),
    ('difficulty.html', '难度'),
    ('majors.html', '专业'),
    ('policy.html', '政策'),
    ('timeline.html', '拿证时间'),
    ('cost.html', '费用'),
    ('registration.html', '报名'),
    ('agencies.html', '避坑'),
    ('outline.html', '考试大纲'),
    ('textbooks.html', '教材'),
    ('news.html', '资讯'),
    ('faq.html', '问答'),
    ('about.html', '关于'),
]
NAV_LABEL = dict(NAV)
NAV_FILES = [f for f, _ in NAV]

# 每页元数据：标题/描述/面包屑/优先级/更新频率/下一步/标签
PAGES = {
    'index.html': dict(title='自考本科全指南：报名条件、含金量、难度、专业与费用拆解',
        desc='自考本科九类高频疑问一次拆开：国家承认吗、自考与成考怎么选、难不难、什么专业好考、多久拿证、花多少钱、在哪报名、助学点怎么查。附官方查证路径与自查清单。',
        crumb='首页', priority='1.0', freq='weekly', tag='九类疑问总览',
        next=['recognition.html','comparison.html','registration.html']),
    'recognition.html': dict(title='自考本科有用吗？国家承认吗？含金量分七个场景说清',
        desc='自考本科学历国家承认、学信网可查，但认可度分场景：考公、考研、考证、评职称、求职分别怎么看？哪些岗位明确不认？附三分钟自查方法与官方查证路径。',
        crumb='含金量与认可度', priority='0.9', freq='monthly', tag='国家承认吗、含金量',
        next=['difficulty.html','comparison.html','majors.html']),
    'comparison.html': dict(title='自考、成考、国开、统招怎么选？四条学历路径对比',
        desc='四条成人学历路径的入学门槛、考试难度、拿证时间、费用与认可度横向对照，附大自考与小自考的区别，以及按你现在的身份选路径的判断顺序。',
        crumb='路径对比', priority='0.9', freq='monthly', tag='自考成考国开怎么选',
        next=['difficulty.html','cost.html','timeline.html']),
    'difficulty.html': dict(title='自考本科难不难？通过率 10%–30% 的口径要说清',
        desc='自考通过率常被引用为 10%–30%，但那是报名人数与毕业人数之比，不是单科及格率。拆解 12–16 门课的真实负担、拖长周期的四个原因与六种提分办法。',
        crumb='难度与通过率', priority='0.8', freq='monthly', tag='难不难、考几门',
        next=['majors.html','timeline.html','recognition.html']),
    'majors.html': dict(title='自考本科什么专业好考？好就业、能考公的筛选顺序',
        desc='按「好考」「对口求职」「考公考研可用」三类目标分别给筛选逻辑，说明常见专业方向的课程特点与难度差异，附选专业的正确顺序与六个高频误区。',
        crumb='专业选择', priority='0.9', freq='monthly', tag='什么专业好考',
        next=['cost.html','timeline.html','policy.html']),
    'policy.html': dict(title='自考本科政策变化：停考专业与最后机会怎么辨别',
        desc='考试计划、开考目录、主考院校会调整，部分专业设停考过渡期。教你三分钟分辨真政策与销售话术，搞清已通过的成绩算不算数，并给出官方查证路径。',
        crumb='政策与改革', priority='0.9', freq='weekly', tag='停考与最后机会',
        next=['registration.html','timeline.html','agencies.html']),
    'timeline.html': dict(title='自考本科多久能拿证？「1.5 年毕业」是真的吗',
        desc='把毕业时间拆成考试次数、课程数量、及格率三个变量，给出你自己算周期的公式，说明 1.5 年成立需要什么条件，以及四段常被漏掉的流程时间。',
        crumb='拿证时间', priority='0.8', freq='monthly', tag='1.5年拿证是真的吗',
        next=['cost.html','registration.html','policy.html']),
    'cost.html': dict(title='自考本科要花多少钱？自学与助学两套账本拆解',
        desc='自学只有报考费与教材费，助学要加助学学费。本文把两套账本分开列项，说明费用差异为何巨大、缴费前必须确认的七件事，以及官方收费标准去哪查。',
        crumb='费用构成', priority='0.8', freq='monthly', tag='花多少钱',
        next=['agencies.html','registration.html','policy.html']),
    'registration.html': dict(title='自考本科在哪报名？官方入口、六步流程与时间节点',
        desc='自考唯一官方报名入口是考生所在省教育考试院官网。本文给出从新生注册到准考证的六步流程、报名时间规律、资格与材料要求，以及报名失败的六种常见原因。',
        crumb='报名入口与流程', priority='1.0', freq='weekly', tag='官方入口与流程',
        next=['agencies.html','policy.html','cost.html']),
    'agencies.html': dict(title='自考本科助学点靠谱吗？三步查正规备案与机构骗局',
        desc='机构不等于助学点。给出三步核查正规备案的方法、八种高危话术逐条拆解、培训贷风险与签约前必须落到纸面的条款，以及已经出问题后的处理路径。',
        crumb='助学点与避坑', priority='1.0', freq='monthly', tag='助学点怎么查',
        next=['registration.html','cost.html','policy.html']),
    'outline.html': dict(title='自考本科考试大纲怎么查、怎么读？官方入口与读法',
        desc='自考本科的考试大纲在哪查、长什么样、怎么读才有用：官方查询入口、大纲与教材的对应关系、怎么用大纲反推重点。附官方查证路径。',
        crumb='考试大纲', priority='0.7', freq='monthly', tag='大纲怎么查怎么读',
        next=['registration.html','textbooks.html','policy.html']),
    'textbooks.html': dict(title='自考本科教材怎么认正版、避开盗版？官方书目与核对方法',
        desc='自考本科教材怎么认正版、避开盗版：官方书目在哪查、版本年份怎么看、盗版风险与鉴别方法。附权威购书与核对路径。',
        crumb='教材与书目', priority='0.7', freq='monthly', tag='认正版避盗版',
        next=['outline.html','agencies.html','cost.html']),
    'news.html': dict(title='自考本科政策动态与资讯索引：去哪查、怎么判断',
        desc='自考本科的政策动态与资讯去哪查、怎么判断真假：官方公告入口、考试计划与开考目录的查看方法、识别营销话术。附官方查证路径。',
        crumb='资讯与动态', priority='0.6', freq='weekly', tag='政策动态索引',
        next=['policy.html','outline.html','registration.html']),
    'faq.html': dict(title='自考本科常见问题汇总：含金量、报名、费用、避坑',
        desc='自考本科高频问题汇总：国家承认吗、难不难、考几门、多少钱、怎么报名、助学点怎么查，逐条给出判断方法与官方查证路径。',
        crumb='常见问题', priority='0.8', freq='monthly', tag='高频问题汇总',
        next=['recognition.html','registration.html','agencies.html']),
    'about.html': dict(title='关于本站：内容定位、信息来源与免责声明',
        desc='关于自考本科指南：本站的内容定位、信息来源与更新方式，以及不与任何机构合作、不提供代报名的免责说明。',
        crumb='关于本站', priority='0.3', freq='yearly', tag='内容定位与免责',
        next=['index.html','faq.html','policy.html']),
}

# 长尾短语 FAQ 增补（P1-6）：引入精确短语，作为独立「相关问题」模块
FAQ_ADD = {
    'recognition.html': [
        ('自考本科毕业条件是什么？', '申请自考本科毕业，须在通过专业计划全部课程后，提交国家承认的专科及以上学历证书，并完成论文（部分专业）与毕业申请。具体课程与环节以你所在省考试计划为准。'),
        ('自考本科含金量高吗？', '含金量分场景：考研、考证、评职称、部分公考岗位均认可；要求全日制学历的岗位不认可。具体见本站「含金量与认可度」页按场景拆解。'),
    ],
    'comparison.html': [
        ('大自考和小自考的区别？', '大自考全部课程参加统考，费用低、自主性强；小自考部分课程由主考院校组织校考或过程性考核，通过率较高但需缴助学学费。两者毕业证均为自考学历，无含金量之分。'),
    ],
    'difficulty.html': [
        ('自考本科考几门？', '多数专业课程总数在 12 到 16 门之间，含公共课、专业核心课与选修课；具体以你所在省该专业的课程计划为准。'),
    ],
    'majors.html': [
        ('自考本科专业有哪些方向？', '常见方向含管理类、法学类、教育类、文学类、经济类、工学类等，各专业课程差异大。选专业应先用用途倒推，详见本站「专业选择」页。'),
    ],
    'cost.html': [
        ('自考本科多少钱？', '完全自学主要支出是每科报考费加教材费，全程通常在数千元以内；参加助学还要加助学学费，以主考院校官网公示标准为准，不要以销售口头报价为依据。'),
    ],
    'registration.html': [
        ('自考本科报名时间是什么时候？', '多数省份每年 4 月、10 月统考，报名通常在考前 2–3 个月；部分省份 1 月、7 月有增考。具体时间以你所在省教育考试院公告为准。'),
    ],
    'agencies.html': [
        ('自考助学点怎么查？', '登录所在省教育考试院官网查官方公布的助学机构名单，再到主考院校继续教育学院官网核对合作单位，机构名称须能与官方名单对应上。'),
    ],
    'timeline.html': [
        ('自考本科最快多久拿证？', '理论上每次报满并通过，最快 1.5–2 年考完全部课程；但受考试计划、课程安排、及格率影响，2.5–3 年更常见。'),
    ],
}

# P0-3 关键词修复（agencies / policy 的 H1 + 首段）
REPL = {
    'agencies.html': [
        ('助学点靠谱吗？核查只要三步，但能筛掉大部分风险',
         '自考本科助学点靠谱吗？核查只要三步，但能筛掉大部分风险'),
        ('「机构」「助学点」「招生中心」「官方合作」——这些词被混着用',
         '自考本科报名时，「机构」「助学点」「招生中心」「官方合作」——这些词被混着用'),
    ],
    'policy.html': [
        ('自考政策年年变，但变化的不是「自考要取消」',
         '自考本科政策年年变，但变化的不是「自考要取消」'),
        ('政策焦虑是每一年的增量变量，也是最容易被利用的情绪。',
         '自考本科的政策焦虑是每一年的增量变量，也是最容易被利用的情绪。'),
        ('「明年自考就取消了，今年最后一批」——自考制度不会以这种方式取消',
         '「明年自考本科就取消了，今年最后一批」——自考制度不会以这种方式取消'),
        ('「内部名额，交钱就能提前锁定」——自考没有这类名额机制。',
         '「内部名额，交钱就能提前锁定」——自考本科没有这类名额机制。'),
    ],
}

# ---- 关键词密度补足（P0-3 延伸）：正文长但主词出现不足 0.3%，按语义自然植入 ----
DENSITY = {
    'agencies.html': [
        ('应对：要求给出公告原文名称与发布时间，自己去省考试院官网核对，见政策与改革。',
         '应对：要求给出公告原文名称与发布时间，自己去省考试院官网核对自考本科政策，见政策与改革。'),
        ('应对：直接问「这个名额在官方系统的哪一步体现」，没有答案就是话术。',
         '应对：直接问「这个自考本科名额在官方系统的哪一步体现」，没有答案就是话术。'),
    ],
    'registration.html': [
        ('报名第一步不是填表，是确认网站。',
         '自考本科报名第一步不是填表，是确认网站。'),
        ('自考的时间节奏相对固定，但每年会微调',
         '自考本科的时间节奏相对固定，但每年会微调'),
        ('如果你选择的是助学形式（小自考）',
         '如果你选择的是自考本科助学形式（小自考）'),
    ],
    'cost.html': [
        ('大自考与小自考的成本结构不同。',
         '自考本科里，大自考与小自考的成本结构不同。'),
        ('不是。自考助学学费是主考院校或助学机构为考生提供教学辅导',
         '不是。自考本科助学的学费是主考院校或助学机构为考生提供教学辅导'),
    ],
    'comparison.html': [
        ('在自考、成考、国开三者之间，很多机构会强调「自考含金量最高」。',
         '在自考本科、成考、国开三者之间，很多机构会强调「自考含金量最高」。'),
    ],
    'majors.html': [
        ('策略：先定岗位方向，再反查这个方向招什么专业，最后在自考开考专业目录里找名称一致的。',
         '策略：先定岗位方向，再反查这个方向招什么专业，最后在自考本科开考专业目录里找名称一致的。'),
    ],
    'timeline.html': [
        ('节奏中断。工作变动、家庭事务导致停考半年，重启时知识点已经生疏。',
         '节奏中断。工作变动、家庭事务导致自考本科停考半年，重启时知识点已经生疏。'),
    ],
}

INFOGRAPHICS = {
    'difficulty.html': ('assets/fig-difficulty.svg', '自考本科课程构成与通过率口径'),
    'timeline.html': ('assets/fig-timeline.svg', '拿证时间的三个变量'),
    'comparison.html': ('assets/fig-comparison.svg', '四条学历路径对照'),
    'registration.html': ('assets/fig-registration.svg', '报名六步流程'),
}


# ---- 资讯文章登记（news/ 目录下的文章页）----
# slug   : 文件名，对应 news/<slug>.html
# title  : ≤30 全角字，口语问句形态，含目标长尾词
# desc   : ≤80 全角字
# date   : 发布日期（刷新正文时同步改这里与 dateModified）
# kw     : 目标长尾词（自检用）
# next   : 文末「下一步」链回的栏目页（锚文本用描述性文字，不用「点击查看」）
ARTICLES = [
    {
        'slug': 'exam-day-checklist',
        'title': '自考考试当天要注意什么？进场时间、必带物品与答题卡填法',
        'desc': '自考考试当天全流程拆解：几点进场、必带证件与文具、禁带物品、答题卡填涂与时间分配，考前一周照着核对即可。',
        'date': '2026-09-23',
        'kw': '自考考试当天',
        'next': [('registration.html', '自考本科报名入口怎么确认'),
                 ('timeline.html', '自考本科多久能拿证')],
    },
    {
        'slug': 'answer-skills',
        'title': '自考答题技巧有哪些？选择、名词解释、简答、论述怎么拿分',
        'desc': '按题型拆解答题策略：选择题排除法、名词解释公式、简答分点作答、论述总—分—总，以及绝不留空白的底线原则。',
        'date': '2026-09-23',
        'kw': '自考答题技巧',
        'next': [('difficulty.html', '自考本科到底难不难'),
                 ('registration.html', '自考本科报名入口怎么确认')],
    },
]

ART_DIR = 'news'


def gen_article_head(a):
    """文章页 <head>：元信息 + Article 结构化数据（补 E-E-A-T 时效与署名信号）"""
    url = '%s/%s/%s.html' % (SITE, ART_DIR, a['slug'])
    ld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": a['title'],
        "description": a['desc'],
        "datePublished": a['date'],
        "dateModified": a['date'],
        "author": {"@type": "Organization", "name": SITE_NAME + "编辑部"},
        "publisher": {"@type": "Organization", "name": SITE_NAME},
        "mainEntityOfPage": {"@type": "WebPage", "@id": url},
        "inLanguage": "zh-CN",
    }
    return (
        '<title>%s</title>\n'
        '<meta name="description" content="%s">\n'
        '<link rel="canonical" href="%s">\n'
        '<meta property="og:type" content="article">\n'
        '<meta property="og:title" content="%s">\n'
        '<meta property="og:description" content="%s">\n'
        '<meta property="og:url" content="%s">\n'
        '<meta property="og:image" content="%s/assets/og-cover.png">\n'
        '<meta property="og:site_name" content="%s">\n'
        '<meta name="twitter:card" content="summary_large_image">\n'
        '<link rel="apple-touch-icon" href="%s/assets/favicon-180.png">\n'
        '<script type="application/ld+json">%s</script>'
        % (a['title'], a['desc'], url, a['title'], a['desc'], url, SITE, SITE_NAME, SITE,
           json.dumps(ld, ensure_ascii=False))
    )


def transform_article(html, a):
    """文章页后处理：换 head、补导航/面包屑/署名日期/下一步/页脚"""
    # 清垃圾属性
    html = re.sub(r'\s*data-page-node-id="[^"]*"', '', html)
    html = html.replace('https://example.com', SITE)
    html = re.sub(r'<meta name="keywords"[^>]*>\s*', '', html)
    # head：先把本函数此前注入过的元信息全部清掉，再整段注入。
    # ⚠️ 这步是幂等的关键 —— 只删 title/description 的话，canonical / og / ld+json
    #    每跑一次就会多叠一份（实测跑 3 次变 3 份 JSON-LD）。
    html = re.sub(r'<title>.*?</title>', '', html, flags=re.S)
    html = re.sub(r'<meta name="description"[^>]*>\s*', '', html)
    html = re.sub(r'<link rel="canonical"[^>]*>\s*', '', html)
    html = re.sub(r'<meta property="og:[^>]*>\s*', '', html)
    html = re.sub(r'<meta name="twitter:[^>]*>\s*', '', html)
    html = re.sub(r'<link rel="apple-touch-icon"[^>]*>\s*', '', html)
    html = re.sub(r'<script type="application/ld\+json">.*?</script>\s*', '', html, flags=re.S)
    html = html.replace('</head>', gen_article_head(a) + '\n</head>')
    nav = '<nav class="nav" aria-label="主导航">' + ''.join(
        '<a href="../%s"%s>%s</a>' % (f, ' class="is-active"' if f == 'news.html' else '', lab)
        for f, lab in NAV) + '</nav>'
    html = re.sub(r'<nav class="nav"[^>]*>.*?</nav>', nav, html, flags=re.S)
    # 面包屑
    crumb = ('<div class="wrap"><nav class="crumb" aria-label="面包屑">'
             '<a href="../index.html">首页</a> › <a href="../news.html">资讯</a> › <span>%s</span>'
             '</nav></div>' % a['kw'])
    if 'class="crumb"' not in html:
        html = html.replace('<main>', crumb + '\n<main>')
    # 日期 + 署名（页面可见，补时效信号）
    byline = ('<p class="byline" style="font-size:13.5px;color:var(--ink-3);margin:0 0 18px">'
              '%s编辑部 · 更新于 %s</p>' % (SITE_NAME, a['date']))
    if 'class="byline"' not in html:
        html = re.sub(r'(</h1>)', r'\1\n' + byline, html, count=1)
    # 文末「下一步」内链
    if 'NEXT-MARK' not in html:
        cards = ''.join(
            '<a class="card" href="../%s"><h3>%s</h3></a>' % (f, t) for f, t in a['next'])
        sec = ('<section class="section"><div class="wrap"><div class="section-head">'
               '<h2>下一步该看什么</h2></div><div class="grid cols-2">%s</div>'
               '</div></section><!--NEXT-MARK-->' % cards)
        html = html.replace('</main>', sec + '\n</main>')
    # 页脚
    if 'site-footer' not in html:
        html = html.replace('</body>', gen_footer().replace('href="', 'href="../') + '\n</body>')
    return html


def gen_news_list():
    """news.html 列表页的文章卡片（按登记顺序倒序，新文在前）"""
    items = sorted(ARTICLES, key=lambda x: x['date'], reverse=True)
    return ''.join(
        '<a class="card" href="%s/%s.html"><h3>%s</h3>'
        '<p style="font-size:14px;color:var(--ink-2);margin:8px 0 0">%s</p>'
        '<p style="font-size:13px;color:var(--ink-3);margin:8px 0 0">更新于 %s</p></a>'
        % (ART_DIR, x['slug'], x['title'], x['desc'], x['date']) for x in items)


def gen_footer():
    decision = ''.join('<li><a href="%s">%s</a></li>' % (f, NAV_LABEL[f])
                       for f in ['recognition.html','comparison.html','difficulty.html','majors.html','policy.html','timeline.html','cost.html','registration.html','agencies.html'])
    info = ''.join('<li><a href="%s">%s</a></li>' % (f, NAV_LABEL[f])
                   for f in ['outline.html','textbooks.html','news.html','faq.html','about.html'])
    return ('''<footer class="site-footer"><!--FOOTER-MARK-->
  <div class="wrap">
    <div class="footer-grid">
      <div><h3>自考本科指南</h3><p style="margin:0;font-size:14.5px;line-height:1.8">围绕「自考本科」这个关键词，把常见疑问拆开讲透：能不能考、值不值得考、花多少钱、多久拿证、找谁报名不踩坑。</p></div>
      <div><h3>决策指南</h3><ul>__DECISION__</ul></div>
      <div><h3>资讯栏目</h3><ul>__INFO__</ul></div>
    </div>
    <div class="footer-note">
      <p>权威来源：<a href="https://www.neea.edu.cn" target="_blank" rel="noopener">教育部教育考试院</a> · <a href="https://www.chsi.com.cn" target="_blank" rel="noopener">学信网</a> · <a href="http://www.moe.gov.cn" target="_blank" rel="noopener">教育部</a></p>
      <p>政策、专业计划、收费标准以各省教育考试院与主考院校官方公告为准。本站不提供报名代办、助学招生与课程销售服务。</p>
      <p>© 2026 自考本科指南 · 内容更新于 __DATE__</p>
    </div>
  </div>
</footer>''').replace('__DECISION__', decision).replace('__INFO__', info).replace('__DATE__', DATE)


def transform(html, page):
    # 1 清理垃圾属性
    html = re.sub(r'\s*data-page-node-id="[^"]*"', '', html)
    # 2 域名替换
    html = html.replace('https://example.com', SITE)
    # 3 删除 meta keywords
    html = re.sub(r'<meta name="keywords"[^>]*>\s*', '', html)

    if page in PAGES:
        p = PAGES[page]
        # 4 标题
        html = re.sub(r'<title>.*?</title>', '<title>%s</title>' % p['title'], html, flags=re.S)
        # 5 描述
        html = re.sub(r'<meta name="description" content="[^"]*"[^>]*>',
                      '<meta name="description" content="%s">' % p['desc'], html)
        # 6 og:title / og:description 同步
        html = re.sub(r'<meta property="og:title" content="[^"]*"[^>]*>',
                      '<meta property="og:title" content="%s">' % p['title'], html)
        html = re.sub(r'<meta property="og:description" content="[^"]*"[^>]*>',
                      '<meta property="og:description" content="%s">' % p['desc'], html)
        # 7 og:image + twitter（守卫）
        if 'og:image' not in html:
            html = re.sub(r'(<meta property="og:description"[^>]*>)',
                r'\1\n<meta property="og:image" content="%s/assets/og-cover.png">\n'
                r'<meta property="og:image:width" content="1200">\n'
                r'<meta property="og:image:height" content="630">\n'
                r'<meta name="twitter:card" content="summary_large_image">\n'
                r'<meta name="twitter:image" content="%s/assets/og-cover.png">'
                % (SITE, SITE), html, count=1)
        # 7b apple-touch-icon（守卫）
        if 'apple-touch-icon' not in html:
            html = html.replace('<link rel="icon" href="favicon.svg" type="image/svg+xml">',
                '<link rel="icon" href="favicon.svg" type="image/svg+xml">\n<link rel="apple-touch-icon" href="assets/favicon-180.png">')
        # 8 WebSite + Organization（守卫）
        if 'SCHEMA-SITE' not in html:
            block = ('<script type="application/ld+json">\n{\n'
                     '  "@context":"https://schema.org",\n  "@graph":[\n'
                     '    {"@type":"WebSite","@id":"%s#website","url":"%s/","name":"%s","inLanguage":"zh-CN"},\n'
                     '    {"@type":"Organization","@id":"%s#organization","name":"%s","url":"%s/"}\n  ]\n}\n'
                     '</script><!--SCHEMA-SITE-->\n'
                     ) % (SITE, SITE, SITE_NAME, SITE, SITE_NAME, SITE)
            html = html.replace('</head>', block + '</head>')
        # 9 面包屑 + Article（守卫）
        if 'SCHEMA-PAGE' not in html:
            art = ('<script type="application/ld+json">\n{\n'
                   '  "@context":"https://schema.org","@type":"BreadcrumbList",\n'
                   '  "itemListElement":[\n'
                   '    {"@type":"ListItem","position":1,"name":"首页","item":"%s/"},\n'
                   '    {"@type":"ListItem","position":2,"name":"%s","item":"%s/%s"}\n  ]\n}\n</script>\n'
                   '<script type="application/ld+json">\n{\n'
                   '  "@context":"https://schema.org","@type":"Article",\n'
                   '  "headline":"%s","description":"%s","inLanguage":"zh-CN",\n'
                   '  "datePublished":"%s","dateModified":"%s",\n'
                   '  "author":{"@type":"Organization","name":"%s编辑部"},\n'
                   '  "publisher":{"@id":"%s#organization"},\n'
                   '  "mainEntityOfPage":{"@type":"WebPage","@id":"%s/%s"}\n}\n'
                   '</script><!--SCHEMA-PAGE-->\n'
                   ) % (SITE, p['crumb'], SITE, page, p['title'], p['desc'], PUB_DATE, DATE, SITE_NAME, SITE, SITE, page)
            html = html.replace('</head>', art + '</head>')
        # 10 重建 nav
        nav_html = '<nav class="nav" aria-label="主导航">' + ''.join(
            '<a href="%s"%s>%s</a>' % (f, ' class="is-active"' if f == page else '', lab)
            for f, lab in NAV) + '</nav>'
        html = re.sub(r'<nav class="nav"[^>]*>.*?</nav>', nav_html, html, flags=re.S)
        # 11 面包屑（非首页）
        if page != 'index.html' and 'CRUMB-MARK' not in html:
            crumb = '<div class="crumb"><!--CRUMB-MARK-->首页 <span>›</span> %s</div>' % p['crumb']
            html = re.sub(r'(<main[^>]*>)', r'\1\n' + crumb, html, count=1)
        # 12 长尾 FAQ 增补（守卫）
        if page in FAQ_ADD and 'FAQ-EXTRA' not in html and FAQ_ADD[page]:
            items = ''.join(
                '<details><summary>%s</summary><div class="fa-body"><p>%s</p></div></details>' % (q, a)
                for q, a in FAQ_ADD[page])
            sec = ('<section class="section is-soft"><div class="wrap">'
                   '<div class="section-head"><h2>相关问题</h2></div>'
                   '<div class="faq"><!--FAQ-EXTRA-->%s</div></div></section>' % items)
            html = html.replace('</main>', sec + '\n</main>')
        # 13 下一步内链模块（守卫）
        if 'NEXT-MARK' not in html:
            cards = ''.join(
                '<a class="card" href="%s"><div class="ct"><span class="num">→</span> %s</div><div class="cd">%s</div></a>'
                % (t, NAV_LABEL.get(t, ''), PAGES[t]['tag']) for t in p['next'])
            sec = ('<section class="related" id="next"><div class="wrap">'
                   '<div class="rt"><!--NEXT-MARK-->下一步该看什么</div>'
                   '<div class="grid cols-3">%s</div></div></section>' % cards)
            html = html.replace('</main>', sec + '\n</main>')
        # 14 信息图（守卫）—— 内联 SVG：零额外请求、不会加载失败、无尺寸推断误差 => CLS 恒为 0
        if page in INFOGRAPHICS and 'INFOGRAPHIC-MARK' not in html:
            src, cap = INFOGRAPHICS[page]
            svg_path = os.path.join(ROOT, src)
            svg = ''
            if os.path.exists(svg_path):
                with open(svg_path, 'r', encoding='utf-8') as f:
                    svg = f.read()
            # 去掉 XML 声明，改为响应式；加上 role/aria 让读屏可识别
            svg = svg.replace('<?xml version="1.0" encoding="UTF-8"?>', '').strip()
            svg = svg.replace('<svg ',
                              '<svg aria-label="%s" role="img" preserveAspectRatio="xMidYMid meet" '
                              'style="display:block;width:100%%;height:auto" ' % cap, 1)
            fig = ('<section class="section"><div class="wrap"><div class="section-head">'
                   '<h2>一图速览</h2><p>下方图示用于快速建立整体概念，具体数字以官方公告为准。</p></div>'
                   '<figure class="infographic" style="margin:0;border:1px solid var(--line);'
                   'border-radius:var(--radius);overflow:hidden;background:#fff">%s'
                   '<figcaption style="font-size:13.5px;color:var(--ink-3);padding:0 14px 12px">%s</figcaption>'
                   '</figure></div></section><!--INFOGRAPHIC-MARK-->' % (svg, cap))
            html = html.replace('</main>', fig + '\n</main>')
        # 15 P0-3 关键词修复（幂等：新串包含旧串，需防止重跑叠加）
        for old, new in REPL.get(page, []):
            if old in html and new not in html:
                html = html.replace(old, new)
        # 15b 关键词密度补足（同样幂等）
        for old, new in DENSITY.get(page, []):
            if old in html and new not in html:
                html = html.replace(old, new)
    # 页脚统一（守卫）
    if 'site-footer' not in html:
        html = html.replace('</body>', gen_footer() + '\n</body>')
    else:
        html = re.sub(r'<footer class="site-footer">.*?</footer>', gen_footer(), html, flags=re.S)
    return html


def gen_sitemap():
    urls = []
    for f in NAV_FILES:
        p = PAGES[f]
        loc = SITE + '/' if f == 'index.html' else SITE + '/' + f
        urls.append('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n'
                    '    <changefreq>%s</changefreq>\n    <priority>%s</priority>\n  </url>'
                    % (loc, DATE, p['freq'], p['priority']))
    # 资讯文章页自动追加（无需手工维护 sitemap）
    for a in ARTICLES:
        loc = '%s/%s/%s.html' % (SITE, ART_DIR, a['slug'])
        urls.append('  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n'
                    '    <changefreq>monthly</changefreq>\n    <priority>0.6</priority>\n  </url>'
                    % (loc, a['date']))
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + '\n'.join(urls) + '\n</urlset>\n')


def main():
    # 全量页面（含 B 层），404 仅做基础清理
    # ⚠️ 跳过名单：这些文件必须原样保留，build 一律不碰
    #   - baidu_verify_*.html 百度站点验证文件，内容是裸哈希，被塞进任何 HTML 都会导致验证失效
    SKIP = {'baidu_verify_codeva-VEue2u0Dge.html'}
    pages = [os.path.basename(p) for p in glob.glob(os.path.join(ROOT, '*.html'))]
    for page in sorted(pages):
        if page in SKIP:
            print('skip (原样保留):', page)
            continue
        path = os.path.join(ROOT, page)
        html = open(path, encoding='utf-8').read()
        if page == '404.html':
            html = re.sub(r'\s*data-page-node-id="[^"]*"', '', html)
            html = html.replace('https://example.com', SITE)
            html = re.sub(r'<meta name="keywords"[^>]*>\s*', '', html)
            html = re.sub(r'<nav class="nav"[^>]*>.*?</nav>',
                '<nav class="nav" aria-label="主导航">' + ''.join(
                    '<a href="%s"%s>%s</a>' % (f, ' class="is-active"' if f == page else '', lab) for f, lab in NAV) + '</nav>',
                html, flags=re.S)
        else:
            html = transform(html, page)
        open(path, 'w', encoding='utf-8').write(html)
        print('built:', page)

    # 资讯文章页（news/ 子目录）
    for a in ARTICLES:
        path = os.path.join(ROOT, ART_DIR, a['slug'] + '.html')
        if not os.path.exists(path):
            print('skip (缺正文):', ART_DIR + '/' + a['slug'] + '.html')
            continue
        html = open(path, encoding='utf-8').read()
        html = transform_article(html, a)
        open(path, 'w', encoding='utf-8').write(html)
        print('built:', ART_DIR + '/' + a['slug'] + '.html')

    # news.html 列表页自动追加文章卡片
    npath = os.path.join(ROOT, 'news.html')
    if os.path.exists(npath):
        nh = open(npath, encoding='utf-8').read()
        block = '<div class="grid cols-2">%s</div><!--NEWS-LIST-MARK-->' % gen_news_list()
        if 'NEWS-LIST-MARK' in nh:
            nh = re.sub(r'<div class="grid cols-2">.*?<!--NEWS-LIST-MARK-->', block, nh, flags=re.S)
        else:
            sec = ('<section class="section"><div class="wrap"><div class="section-head">'
                   '<h2>最新文章</h2></div>%s</div></section>' % block)
            nh = nh.replace('</main>', sec + '\n</main>')
        open(npath, 'w', encoding='utf-8').write(nh)
        print('built: news.html（文章列表 %d 条）' % len(ARTICLES))

    # sitemap / robots / CNAME
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(gen_sitemap())
    robots = ('User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n' % SITE)
    open(os.path.join(ROOT, 'robots.txt'), 'w', encoding='utf-8').write(robots)
    open(os.path.join(ROOT, 'CNAME'), 'w', encoding='utf-8').write(DOMAIN_PUNY + '\n')
    print('built: sitemap.xml / robots.txt / CNAME')


if __name__ == '__main__':
    main()
