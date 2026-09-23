# 自考本科.com

参照国家级自考官方信息源的信息架构，围绕关键词「自考本科」做的中文资讯站。

- 站点域名：自考本科.com（xn--8pvy82b5pew4b.com）
- 托管：GitHub Pages（main 分支根目录）
- 生产内容：仓库根目录的静态 HTML
- 构建脚本：`build.py`（Python 后处理式构建，幂等，可重跑）

## 内容口径

政策 / 收费 / 机构资质类内容只写「去哪查、怎么判断」，不写具体省份、院校、机构名与金额；
避坑内容只给核查方法，不评价任何具体机构；每页保留免责声明。
外链仅指向国家级权威源（neea.edu.cn / chsi.com.cn / moe.gov.cn）。

## 重建

```bash
python build.py
```

会就地重写 15 个页面并生成 sitemap.xml / robots.txt / CNAME。
