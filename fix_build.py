#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""修复 build.py：删除重复条目，补充缺失的 15 篇文章"""

import re

# 读取 build.py
with open('build.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file has {len(lines)} lines")

# 找出需要删除的重复条目（第 348-481 行，索引 347-480）
# 这些是 zk-四川-1 到 zk-全国-15 的重复
delete_start = 347  # 0-indexed, line 348
delete_end = 481    # 0-indexed, line 481 (inclusive end for slicing)

# 先检查这些行是否确实是重复的
print("\nLines to delete (348-481):")
for i in range(delete_start, min(delete_end + 1, len(lines))):
    print(f"{i+1}: {lines[i].rstrip()[:80]}")

# 删除重复条目
new_lines = lines[:delete_start] + lines[delete_end:]

print(f"\nAfter deletion: {len(new_lines)} lines (removed {len(lines) - len(new_lines)} lines)")

# 现在在第 347 行后插入缺失的 15 篇文章
# 缺失的文章：zk-上海-3, zk-全国-1, zk-北京-2, zk-四川-8, zk-安徽-13, zk-山东-7, zk-广东-4, zk-江苏-5, zk-河北-11, zk-河南-9, zk-浙江-6, zk-湖北-10, zk-福建-14, zk-辽宁-12, zk-陕西-15

missing_articles = '''
    {
        'slug': 'zk-全国-1',
        'title': '自考2026年下半年高等教育自学考试时间确定｜全国教育考试院公告',
        'desc': '全国教育考试院发布：2026年下半年高等教育自学考试定于10月24日至25日举行。各省报名、准考证打印时间相继公布，考生需关注本省考试院通知。',
        'date': '2026-10-06',
        'kw': '2026年下半年自考时间',
        'next': [['registration.html', '自考本科报名入口怎么确认'], ['timeline.html', '自考本科多久能拿证']],
    },

    {
        'slug': 'zk-北京-2',
        'title': '自考北京2026年下半年自考报名通知｜新生注册8月30日起',
        'desc': '北京教育考试院发布：2026年下半年北京市自学考试笔试课程报考通知。新考生8月30日-9月3日注册，9月9日-11日缴费；在籍考生8月30日-9月11日直接报考缴费。',
        'date': '2026-08-30',
        'kw': '北京2026年下半年自考报名',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-上海-3',
        'title': '自考上海2026年下半年自学考试报名公告｜9月1日-6日报考',
        'desc': '上海市教育考试院发布：2026年下半年高等教育自学考试（第89次）报名公告。首次考生7月6日-8日注册，7月10日前完成报考；在籍考生9月1日9:00至9月6日12:00网上报考。',
        'date': '2026-09-01',
        'kw': '上海2026年下半年自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-广东-4',
        'title': '自考广东2026年10月自学考试网上报名报考须知',
        'desc': '广东省教育考试院发布：2026年10月高等教育自学考试网上报名报考须知。考生需在规定时间内完成网上报考和缴费，逾期不予受理。',
        'date': '2026-09-01',
        'kw': '广东2026年10月自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-江苏-5',
        'title': '自考江苏2026年10月自学考试网上报名通告｜9月1日-5日报考',
        'desc': '江苏省教育考试院发布：2026年10月高等教育自学考试网上报名通告。首次考生需在规定时间注册，在籍考生9月1日9:00至5日17:00网上报考。',
        'date': '2026-09-01',
        'kw': '江苏2026年10月自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-浙江-6',
        'title': '自考浙江2026年10月自学考试报名公告｜首考生7月6日-8日注册',
        'desc': '浙江省教育考试院发布：2026年10月高等教育自学考试报名公告。首次考生7月6日-8日注册，7月10日前完成报考；在籍考生按规定时间网上报考。',
        'date': '2026-07-06',
        'kw': '浙江2026年10月自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-山东-7',
        'title': '自考山东2026年10月自学考试报名工作通知｜6月18日-24日报名',
        'desc': '山东省教育考试院发布：2026年10月高等教育自学考试报名工作通知。首次考生需在6月18日-24日办理注册，在籍考生按规定时间报考。',
        'date': '2026-06-18',
        'kw': '山东2026年10月自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-四川-8',
        'title': '自考四川2026年下半年自学考试新生注册及课程报考通告',
        'desc': '四川省教育考试院发布：2026年下半年高等教育自学考试新生注册及课程报考通告。首次考生需在规定时间内注册，在籍考生网上报考。',
        'date': '2026-09-01',
        'kw': '四川2026年下半年自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-河北-11',
        'title': '自考河北2026年下半年高等教育自学考试报考须知',
        'desc': '河北省教育考试院发布：2026年下半年高等教育自学考试报考须知。首次考生需在规定时间内注册，在籍考生网上报考缴费。',
        'date': '2026-09-01',
        'kw': '河北2026年下半年自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-河南-9',
        'title': '自考河南2026年下半年自学考试报名安排｜9月1日-3日网上报名',
        'desc': '河南省教育考试院发布：2026年下半年高等教育自学考试报名安排。首次考生9月1日9:00-3日18:00网上注册，在籍考生同期网上报考。',
        'date': '2026-09-01',
        'kw': '河南2026年下半年自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-湖北-10',
        'title': '自考湖北2026年10月自学考试网上报名须知｜8月24日-28日报名',
        'desc': '湖北省教育考试院发布：2026年10月高等教育自学考试网上报名须知。首次考生需在规定时间内注册，在籍考生8月24日至28日网上报考。',
        'date': '2026-08-24',
        'kw': '湖北2026年10月自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-安徽-13',
        'title': '自考安徽2026年下半年自学考试报名通告',
        'desc': '安徽省教育考试院发布：2026年下半年高等教育自学考试报名通告。首次考生需在规定时间内注册，在籍考生网上报考缴费。',
        'date': '2026-09-01',
        'kw': '安徽2026年下半年自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-福建-14',
        'title': '自考福建2026年下半年自学考试报名安排',
        'desc': '福建省教育考试院发布：2026年下半年高等教育自学考试报名安排。首次考生需在规定时间内注册，在籍考生网上报考。',
        'date': '2026-09-01',
        'kw': '福建2026年下半年自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-辽宁-12',
        'title': '自考辽宁2026年10月自学考试报名公告',
        'desc': '辽宁省教育考试院发布：2026年10月高等教育自学考试报名公告。首次考生需在规定时间内注册，在籍考生网上报考缴费。',
        'date': '2026-09-01',
        'kw': '辽宁2026年10月自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },

    {
        'slug': 'zk-陕西-15',
        'title': '自考陕西2026年下半年自学考试报名公告',
        'desc': '陕西省教育考试院发布：2026年下半年高等教育自学考试报名公告。首次考生需在规定时间内注册，在籍考生网上报考缴费。',
        'date': '2026-09-01',
        'kw': '陕西2026年下半年自学考试',
        'next': [['registration.html', '自考本科报名入口怎么确认']],
    },
'''

# 在第 347 行后插入（索引 347 对应 line 348，但我们想在 line 347 后，即索引 347 前插入）
insert_pos = 347  # 在第 347 行后插入（0-indexed）
new_lines = new_lines[:insert_pos] + [missing_articles + '\n'] + new_lines[insert_pos:]

print(f"\nAfter insertion: {len(new_lines)} lines (added {len(new_lines) - len(lines)} lines)")

# 写回文件
with open('build.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("\nbuild.py updated successfully!")

# 验证
import os
files = set(f.replace('.html', '') for f in os.listdir('news') if f.startswith('zk-'))
with open('build.py', 'r', encoding='utf-8') as f:
    c = f.read()
slugs = set(re.findall(r"'slug': 'zk-([^']+)',", c))

print(f"\nVerification:")
print(f"  Files on disk: {len(files)}")
print(f"  Slugs in build.py: {len(slugs)}")
missing = files - slugs
if missing:
    print(f"  Missing from build.py: {sorted(missing)}")
else:
    print(f"  All files registered in build.py!")
extra = slugs - files
if extra:
    print(f"  Extra slugs in build.py (no file): {sorted(extra)}")
