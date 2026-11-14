---
name: xiaohongshu-post-extraction
description: "Use when reading a Xiaohongshu or xhslink post."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos]
metadata:
  hermes:
    tags: [Xiaohongshu, XHS, Scraping, Vision]
    category: web
---

# Xiaohongshu (小红书) post extraction

Extract the full text and long-form images of an XHS post from a share link with
no login. XHS pages render client-side, but the whole post payload is embedded in
the HTML.

## Procedure

① **Resolve the short link with GET, never HEAD.** `curl -I` returns **404** even
when the link is live. Use a mobile UA and follow redirects; the final URL carries
the mandatory `xsec_token`:

```bash
UA='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1'
curl -sL --max-time 30 -A "$UA" -o /tmp/xhs.html \
  -w '%{http_code} %{url_effective} %{size_download}\n' 'http://xhslink.com/o/XXXX'
```

② **Parse `__INITIAL_STATE__` — it is not valid JSON.** It contains bare
`undefined` tokens (e.g. `"jsAssetsList":undefined`), so `json.loads` throws
`Expecting value`. Sanitize first:

```python
import re, json
s = open('/tmp/xhs.html', encoding='utf-8', errors='ignore').read()
i = s.index('__INITIAL_STATE__=')
raw = s[i + len('__INITIAL_STATE__='):s.index('</script>', i)]
data = json.loads(re.sub(r'\bundefined\b', 'null', raw))
note = data['noteData']['data']['noteData']   # title, desc, imageList, interactInfo, time, user
```

Useful fields: `title`, `desc`, `tagList`, `interactInfo` (likedCount /
collectedCount / commentCount / shareCount), `time` (ms epoch), `user.nickName`,
`imageList[].url` / `width` / `height`. `data['noteData']['data']` keys to expect:
`noteData`, `routeQuery`, `config`, `errorNoteData`, `normalNotePreloadData`.

③ **Long-form posts put the body in the images.** If `desc` ends with
"详见图片", the argument lives in `imageList`, usually 1080×1920 infographic pages.
Download with `https://` (the payload hands out `http://`) **plus the referer and
UA**, or the CDN returns 403:

```bash
curl -s --max-time 60 -A "$UA" -e 'https://www.xiaohongshu.com/' -o 00.jpg '<url>'
```

④ **Read images one per `vision_analyze` call.** Batching several images into a
single turn makes the runtime drop all but the last — the results come back as
`[screenshot removed to save context]` and you have not actually seen them.
One image, one call, is what actually renders. Note the small page counter baked
into the corner (e.g. `09 / 11`); when a post ships a separate cover, the file
index is offset by one from the page number, so read the counter, don't assume it.

⑤ **Trace the numbers.** These posts are curated digests of Chinese tech media.
Grep the poster's figures back to the primary piece before repeating them — the
same numbers (download declines, ARPU, retention) circulate through 36氪 / 虎嗅 /
人人都是产品经理 / 新浪财经 with slight variations, and transcription errors
compound. Recompute any ratio the article states yourself.

## Pitfalls

- `curl -I` on xhslink = 404. It is not a dead link.
- Dropping `xsec_token` from the resolved URL breaks the fetch; always use
  `%{url_effective}` output, not a hand-trimmed URL.
- `json.loads` on the raw state block always fails on `undefined`.
- `http://` image URLs from `imageList` need upgrading to `https://` **and** a
  referer header.
- **36kr.com refuses curl** with a 火山引擎 "正在进行安全检测" interstitial (~60
  bytes of text). Use a mirror instead: `woshipm.com/ai/<id>.html`,
  `m.huxiu.com/article/<id>.html`, `163.com` reposts, or `finance.sina.com.cn`.
  `m.21jingji.com` and `post.smzdm.com` fetch fine.
- There is no local OCR (no tesseract, no paddleocr, no easyocr) on this box —
  vision is the only path through the images.
- `noteData` can be empty for a non-share navigation; the share-link route
  (`xsec_source=app_share`) is the one that returns content anonymously.
