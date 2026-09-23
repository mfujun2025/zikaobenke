#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度搜索资源平台 —— sitemap 主动推送脚本（普通收录 API）

用途：把站内 URL 主动推给百度，比等蜘蛛自己爬快得多（官方称可缩短到分钟级）。
前置：需要在百度搜索资源平台拿到「准入密钥 token」。

用法：
    python baidu_push.py <token>
    python baidu_push.py <token> --all        # 推送 sitemap 里的全部 URL（默认）
    python baidu_push.py <token> --url https://xn--8pvy82b5pew4b.com/policy.html

token 从哪来：
    百度搜索资源平台 -> 左侧「普通收录」-> API 提交 -> 准入密钥
    （站点必须先完成「站点验证」，见交付说明文档第四节）
"""
import sys, json, ssl, re, os, urllib.request, urllib.error

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
    # 百度限制：一次最多 2000 条；用 \n 分隔
    body = "\n".join(urls).encode("utf-8")
    url = API % (SITE, token)
    req = urllib.request.Request(url, data=body, method="POST",
        headers={"Content-Type": "text/plain", "User-Agent": "curl/8.0"})
    try:
        with op.open(req, timeout=30) as r:
            resp = json.loads(r.read().decode() or "{}")
            print("推送成功")
            print(json.dumps(resp, ensure_ascii=False, indent=2))
            if "success" in resp:
                print(f"\n  本次成功推送 {resp['success']} 条")
            if "remain" in resp:
                print(f"  今日剩余配额 {resp['remain']} 条")
            if "not_valid" in resp:
                print(f"  ⚠️ 无效 URL {len(resp['not_valid'])} 条")
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode()[:500]}")
    except Exception as e:
        print(f"失败: {e!r}")


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
