#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度搜索资源平台 —— sitemap 主动推送脚本（普通收录 API）

用途：把站内 URL 主动推给百度，比等蜘蛛自己爬快得多（官方称可缩短到分钟级）。
前置：需要在百度搜索资源平台拿到「准入密钥 token」。

用法：
    python baidu_push.py <token>              # 推送 sitemap 里的全部 URL
    python baidu_push.py <token> --url <URL>  # 只推指定 URL（可跟多个）

token 从哪来：
    百度搜索资源平台 -> 左侧「普通收录」-> API 提交 -> 准入密钥
    （站点必须先完成「站点验证」）

⚠️ 配额（2026-09-23 实测）：
    新站每日配额仅 **10 条**，且返回 400 {"message":"over quota"} 表示配额用尽。
    脚本已按 8 条一批切分，遇配额耗尽会自动停手并提示剩余数量，
    剩下的次日再跑即可（配额每日重置）。
"""
import sys, json, ssl, re, os, time, urllib.request, urllib.error

SITE = "https://xn--8pvy82b5pew4b.com"
SITEMAP = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sitemap.xml")
API = "http://data.zz.baidu.com/urls?site=%s&token=%s"

ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
op = urllib.request.build_opener(urllib.request.ProxyHandler({}), urllib.request.HTTPSHandler(context=ctx))


def load_urls_from_sitemap(path=SITEMAP):
    if not os.path.exists(path):
        print(f"找不到 sitemap: {path}")
        return []
    with open(path, encoding="utf-8") as f:
        return re.findall(r"<loc>(.*?)</loc>", f.read())


def push(token, urls):
    if not urls:
        print("没有要推送的 URL"); return
    # 百度限制：一次最多 2000 条。但新站每日配额很小（实测仅 10 条/天），
    # 所以按小批量切分，遇 remain=0 立即停手，剩下的留给明天。
    BATCH = 8
    total_ok = 0
    pending = list(urls)
    while pending:
        batch, pending = pending[:BATCH], pending[BATCH:]
        body = "\n".join(batch).encode("utf-8")
        url = API % (SITE, token)
        req = urllib.request.Request(url, data=body, method="POST",
            headers={"Content-Type": "text/plain", "User-Agent": "curl/8.0"})
        try:
            with op.open(req, timeout=30) as r:
                resp = json.loads(r.read().decode() or "{}")
        except urllib.error.HTTPError as e:
            raw = e.read().decode()
            if "over quota" in raw:
                print(f"\n⚠️ 今日配额已用尽。本次共成功推送 {total_ok} 条，"
                      f"剩余 {len(batch) + len(pending)} 条请明天再推。")
                return
            print(f"HTTP {e.code}: {raw[:300]}")
            if e.code == 401:
                print("  → token 无效，去平台重新复制「准入密钥」")
            return
        except Exception as e:
            print(f"失败: {e!r}"); return

        ok = resp.get("success", 0)
        total_ok += ok
        print(f"  本批 {len(batch)} 条 → 成功 {ok}，剩余配额 {resp.get('remain', '?')}")
        if resp.get("not_valid"):
            print(f"  ⚠️ 无效 URL {len(resp['not_valid'])} 条: {resp['not_valid']}")
        if resp.get("remain", 0) <= 0 and pending:
            print(f"\n⚠️ 今日配额已用尽。共成功 {total_ok} 条，"
                  f"剩余 {len(pending)} 条请明天再推。")
            return
        time.sleep(1)
    print(f"\n完成：本次共成功推送 {total_ok} 条")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    token = sys.argv[1]
    if "--url" in sys.argv:
        i = sys.argv.index("--url")
        urls = sys.argv[i + 1:]
    else:
        urls = load_urls_from_sitemap()
        print(f"从 sitemap 载入 {len(urls)} 条 URL")
    push(token, urls)
