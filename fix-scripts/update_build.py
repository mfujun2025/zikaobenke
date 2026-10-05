#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
update_build.py
读取 new_articles.json，把新文章追加到 build.py 的 ARTICLES 列表中。
"""
import json, re, os

ROOT = os.path.dirname(os.path.abspath(__file__))
BUILD_PY = os.path.join(ROOT, '..', 'build.py')
NEW_ARTICLES = os.path.join(ROOT, 'new_articles.json')


def main():
    if not os.path.exists(NEW_ARTICLES):
        print("ERROR: new_articles.json not found. Run generate_articles.py first.")
        return

    with open(NEW_ARTICLES, encoding='utf-8') as f:
        new_articles = json.load(f)

    if not new_articles:
        print("No new articles to add.")
        return

    with open(BUILD_PY, encoding='utf-8') as f:
        content = f.read()

    # 找到 ARTICLES 列表的结束位置（最后一个 ]）
    # 格式：ARTICLES = [\n    {...},\n    {...},\n]
    # 我们要在最后一个 } 后面、] 前面插入新条目

    # 先找到 ARTICLES = [ 的位置
    art_match = re.search(r"ARTICLES\s*=\s*\[", content)
    if not art_match:
        print("ERROR: Could not find ARTICLES list in build.py")
        return

    # 从 ARTICLES = [ 开始，找到最后一个 }, 然后下一个 ]
    start = art_match.end()
    # 找最后一个 '}' 后面跟着 ',' 或 '\n' 的位置
    # 用简单策略：找到最后一个 ']' 在 ARTICLES 块中的位置
    # 实际上 ARTICLES 块就是内容末尾附近，从 start 往后找平衡的 ]
    brace_depth = 0
    bracket_depth = 0
    last_item_end = start
    i = start
    in_string = False
    escape_next = False
    while i < len(content):
        c = content[i]
        if escape_next:
            escape_next = False
            i += 1
            continue
        if c == '\\':
            escape_next = True
            i += 1
            continue
        if c == '"' and not in_string:
            in_string = True
        elif c == '"' and in_string:
            in_string = False
        if in_string:
            i += 1
            continue
        if c == '{':
            brace_depth += 1
        elif c == '}':
            brace_depth -= 1
            if brace_depth == 0:
                last_item_end = i + 1
        elif c == '[':
            bracket_depth += 1
        elif c == ']':
            bracket_depth -= 1
            if bracket_depth == 0:
                # 找到了 ARTICLES 列表的结尾
                break
        i += 1

    # 在 last_item_end 和 ']' 之间插入新条目
    insert_pos = last_item_end

    # 构建新条目
    new_entries = []
    for a in new_articles:
        entry = (
            "    {\n"
            f"        'slug': '{a['slug']}',\n"
            f"        'title': {json.dumps(a['title'], ensure_ascii=False)},\n"
            f"        'desc': {json.dumps(a['desc'], ensure_ascii=False)},\n"
            f"        'date': '{a['date']}',\n"
            f"        'kw': {json.dumps(a['kw'], ensure_ascii=False)},\n"
            f"        'next': {json.dumps(a['next'], ensure_ascii=False)},\n"
            "    },\n"
        )
        new_entries.append(entry)

    new_block = '\n'.join(new_entries)

    # 插入
    new_content = content[:insert_pos] + '\n' + new_block + content[insert_pos:]

    with open(BUILD_PY, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"Updated build.py: added {len(new_articles)} articles.")
    print("Run python build.py to regenerate all pages.")


if __name__ == '__main__':
    main()
