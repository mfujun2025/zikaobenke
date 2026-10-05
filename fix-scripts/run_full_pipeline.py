#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_full_pipeline.py
一键运行：抓取 -> 生成文章 -> 更新 build.py -> 重建站点 -> push
"""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(ROOT)
PYTHON = sys.executable


def run(cmd, desc=""):
    print(f"\n{'='*60}")
    print(f"> {desc or cmd}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, shell=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print(f"FAILED with exit code {result.returncode}")
        return False
    return True


def main():
    # Step 1: 抓取
    print("\n📥 STEP 1: 抓取公告数据...")
    if not run(f'"{PYTHON}" crawl_neea.py', "抓取教育部考试网公告"):
        print("⚠️  neea 抓取失败，继续...")
    if not run(f'"{PYTHON}" crawl_provinces.py', "抓取各省考试院公告"):
        print("⚠️  省份抓取失败，继续...")

    # Step 2: 生成文章
    print("\n📝 STEP 2: 生成资讯文章...")
    if not run(f'"{PYTHON}" generate_articles.py', "生成新文章 HTML"):
        print("❌ 文章生成失败，终止。")
        return

    # Step 3: 更新 build.py
    print("\n🔧 STEP 3: 更新 build.py ARTICLES 列表...")
    if not run(f'"{PYTHON}" update_build.py', "追加新文章到 build.py"):
        print("❌ build.py 更新失败，终止。")
        return

    # Step 4: 重建站点
    print("\n🏗️  STEP 4: 重建站点...")
    build_cmd = f'cd "{REPO_ROOT}" && "{PYTHON}" build.py'
    result = subprocess.run(build_cmd, shell=True, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print(result.stderr, file=sys.stderr)
    if result.returncode != 0:
        print("❌ build.py 执行失败")
        return
    print("✅ 站点重建完成")

    # Step 5: commit & push
    print("\n🚀 STEP 5: 提交并推送...")
    commit_msg = "feat(news): 新增各省自考公告资讯文章"
    cmds = [
        f'cd "{REPO_ROOT}" && GIT_TERMINAL_PROMPT=0 git -c credential.helper= -c credential.helper=store add news/',
        f'cd "{REPO_ROOT}" && GIT_TERMINAL_PROMPT=0 git -c credential.helper= -c credential.helper=store add fix-scripts/ new_articles.json raw_*.json 2>/dev/null || true',
        f'cd "{REPO_ROOT}" && GIT_TERMINAL_PROMPT=0 git -c credential.helper= -c credential.helper=store add build.py',
        f'cd "{REPO_ROOT}" && GIT_TERMINAL_PROMPT=0 git -c credential.helper= -c credential.helper=store commit -m "{commit_msg}"',
        f'cd "{REPO_ROOT}" && GIT_TERMINAL_PROMPT=0 git -c credential.helper= -c credential.helper=store push origin main',
    ]
    for cmd in cmds:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(r.stdout.strip())
        if r.stderr:
            print(r.stderr.strip(), file=sys.stderr)
        if r.returncode != 0 and "nothing to commit" not in r.stdout.lower():
            print(f"  ⚠️  non-zero exit: {r.returncode}")

    print("\n✅ Pipeline complete!")
    print(f"   新增文章数: {len(__import__('json').load(open(os.path.join(ROOT, 'new_articles.json'), encoding='utf-8'))) if os.path.exists(os.path.join(ROOT, 'new_articles.json')) else 0}")
    print("   仓库: https://github.com/mfujun2025/zikaobenke")


if __name__ == '__main__':
    main()
