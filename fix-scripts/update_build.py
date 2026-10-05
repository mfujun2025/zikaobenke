#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_build.py
更新 build.py 的 ARTICLES 列表，添加新的有实质内容的文章。
"""
import re
from pathlib import Path

WORK_DIR = Path(__file__).resolve().parent.parent
BUILD_PY = WORK_DIR / "build.py"
NEWS_DIR = WORK_DIR / "news"

# 新增文章的元数据
NEW_ARTICLES = [
    {
        "slug": "zk-四川-4",
        "title": "2026年下半年四川省高等教育自学考试新生注册及课程报考通告",
        "desc": "四川省教育考试院发布：2026年下半年四川自考新生注册及课程报考通告。社会型专业9月1-3日注册，9月7-10日报考缴费，考试10月24-25日。",
        "date": "2026-08-08",
        "kw": "四川自考报名,四川自学考试,四川教育考试院",
        "next": [["zk-四川-5.html", "四川自考课程免试申请通告"]],
    },
    {
        "slug": "zk-四川-5",
        "title": "四川省教育考试院关于申请2026年下半年高等教育自学考试课程免试的通告",
        "desc": "四川省教育考试院发布：2026年下半年四川自考课程免试申请通告。9月17-21日申请，免试审定费8元/科，附各市州咨询电话。",
        "date": "2026-09-08",
        "kw": "四川自考免考,四川自学考试免试,四川自考课程转换",
        "next": [["zk-四川-4.html", "四川自考新生注册及课程报考通告"]],
    },
    {
        "slug": "zk-北京-6",
        "title": "关于北京市2026年下半年自学考试笔试课程报考相关事项的通知",
        "desc": "北京教育考试院发布：2026年下半年北京自考报考通知。新生8月30日-9月3日注册，9月9-11日缴费；在籍考生8月30日-9月11日报考。",
        "date": "2026-07-08",
        "kw": "北京自考报名,北京自学考试,北京教育考试院",
        "next": [["zk-全国-1.html", "全国自考2026年下半年考试时间确定"]],
    },
    {
        "slug": "zk-上海-7",
        "title": "上海市2026年下半年高等教育自学考试（第89次）报名公告",
        "desc": "上海市教育考试院发布：2026年下半年上海自考报名公告。9月1日-6日报考，考试10月24-25日，护理学专升本需现场审核。",
        "date": "2026-09-01",
        "kw": "上海自考报名,上海自学考试,上海市教育考试院",
        "next": [["zk-全国-1.html", "全国自考2026年下半年考试时间确定"]],
    },
    {
        "slug": "zk-广东-8",
        "title": "广东省2026年10月高等教育自学考试网上报名报考须知",
        "desc": "广东省教育考试院发布：2026年10月广东自考网上报名报考须知。新生预报名8月25-28日，正式报名至28日；课程报考9月1-4日。",
        "date": "2026-08-25",
        "kw": "广东自考报名,广东自学考试,广东省教育考试院",
        "next": [["zk-全国-1.html", "全国自考2026年下半年考试时间确定"]],
    },
    {
        "slug": "zk-江苏-9",
        "title": "江苏省2026年10月高等教育自学考试网上报名通告",
        "desc": "江苏省教育考试院发布：2026年10月江苏自考网上报名通告。9月1日-5日报考，每日22:00至次日8:00系统维护，护理学/药学需现场审核。",
        "date": "2026-09-01",
        "kw": "江苏自考报名,江苏自学考试,江苏省教育考试院",
        "next": [["zk-全国-1.html", "全国自考2026年下半年考试时间确定"]],
    },
    {
        "slug": "zk-浙江-10",
        "title": "浙江省2026年10月高等教育自学考试报名公告",
        "desc": "浙江省教育考试院发布：2026年10月浙江自考报名公告。首考生7月6日-8日注册，续考生直接报考，费用50元/科次。",
        "date": "2026-07-06",
        "kw": "浙江自考报名,浙江自学考试,浙江省教育考试院",
        "next": [["zk-全国-1.html", "全国自考2026年下半年考试时间确定"]],
    },
    {
        "slug": "zk-山东-11",
        "title": "山东省2026年10月高等教育自学考试报名工作通知",
        "desc": "山东省教育招生考试院发布：2026年10月山东自考报名工作通知。6月18日-24日报名，新考生18-21日注册，全程网上办理。",
        "date": "2026-06-18",
        "kw": "山东自考报名,山东自学考试,山东省教育招生考试院",
        "next": [["zk-全国-1.html", "全国自考2026年下半年考试时间确定"]],
    },
    {
        "slug": "zk-河南-12",
        "title": "河南省2026年下半年高等教育自学考试报名安排",
        "desc": "河南省教育考试院发布：2026年下半年河南自考报名安排。9月1日-3日网上报名，转考申请仅限8月31日一天。",
        "date": "2026-09-01",
        "kw": "河南自考报名,河南自学考试,河南省教育考试院",
        "next": [["zk-全国-1.html", "全国自考2026年下半年考试时间确定"]],
    },
    {
        "slug": "zk-湖北-13",
        "title": "湖北省2026年10月高等教育自学考试网上报名须知",
        "desc": "湖北省教育考试院发布：2026年10月湖北自考网上报名须知。8月24日-28日报名，考试为期3天（含周五）。",
        "date": "2026-08-24",
        "kw": "湖北自考报名,湖北自学考试,湖北省教育考试院",
        "next": [["zk-全国-1.html", "全国自考2026年下半年考试时间确定"]],
    },
]


def update_build_py():
    """更新 build.py 的 ARTICLES 列表"""
    code = BUILD_PY.read_text(encoding='utf-8')

    # 找到 ARTICLES 列表的结束位置
    articles_start = code.find("ARTICLES = [")
    if articles_start == -1:
        print("❌ 未找到 ARTICLES 列表")
        return

    # 找到列表结束位置（第1个 ']' 在 ARTICLES 之后）
    list_start = code.find("[", articles_start)
    bracket_count = 1
    i = list_start + 1
    while i < len(code) and bracket_count > 0:
        if code[i] == '[':
            bracket_count += 1
        elif code[i] == ']':
            bracket_count -= 1
        i += 1
    articles_end = i - 1

    # 提取现有 ARTICLES 内容
    existing_articles = code[articles_start:articles_end+1]

    # 检查是否已存在这些 slug
    existing_slugs = set()
    for m in re.finditer(r"'slug':\s*'([^']+)'", existing_articles):
        existing_slugs.add(m.group(1))

    # 过滤掉已存在的
    new_entries = []
    for article in NEW_ARTICLES:
        if article['slug'] not in existing_slugs:
            new_entries.append(article)
        else:
            print(f"  ⏭ 跳过已存在: {article['slug']}")

    if not new_entries:
        print("✅ 所有新文章已存在，无需更新")
        return

    print(f"📝 将添加 {len(new_entries)} 篇新文章到 ARTICLES 列表")

    # 生成新的 ARTICLES 条目
    entries_to_add = []
    for article in new_entries:
        entry = f'''    {{
        'slug': '{article['slug']}',
        'title': '{article['title']}',
        'desc': '{article['desc']}',
        'date': '{article['date']}',
        'kw': "{article['kw']}",
        'next': {article['next']},
    }},'''
        entries_to_add.append(entry)

    # 在 ARTICLES 列表结束前插入新条目
    new_code = (
        code[:articles_end] +
        "\n" + "\n".join(entries_to_add) +
        code[articles_end:]
    )

    # 写回文件
    BUILD_PY.write_text(new_code, encoding='utf-8')
    print(f"✅ 已更新 build.py，添加了 {len(new_entries)} 篇新文章")


def main():
    print("🔧 更新 build.py...")
    update_build_py()


if __name__ == "__main__":
    main()
