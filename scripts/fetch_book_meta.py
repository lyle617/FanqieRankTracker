#!/usr/bin/env python3
"""抓取书目页元数据+章节目录（明文），输出 json。"""
import json, re, sys, time, urllib.request

def fetch(url, referer="https://fanqienovel.com/"):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": referer,
    })
    return urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "ignore")

def clean_title(t):
    t = t.replace("完整版在线免费阅读_", " ").replace("小说_番茄小说官网", "").replace("_番茄小说官网", "")
    # keep longest segment
    parts = re.split(r"[_\s]+", t.strip())
    return max(parts, key=len) if parts else t.strip()

def get_book(book_id):
    html = fetch(f"https://fanqienovel.com/page/{book_id}")
    m = re.search(r"<title>([^<]*)</title>", html)
    title = clean_title(m.group(1)) if m else ""
    rc = re.search(r'"readCount":\s*"?(\d+)', html)
    wn = re.search(r'"wordNumber":\s*"?(\d+)', html)
    st = re.search(r'"status":\s*"?(\d+)', html)
    ct = re.search(r'"chapterTotal":\s*"?(\d+)', html)
    # author
    au = re.search(r'"author":\s*"([^"]{1,30})"', html)
    # chapter list
    chaps = []
    i = html.find('"chapterListWithVolume":')
    if i >= 0:
        try:
            obj, _ = json.JSONDecoder().raw_decode(html[i + len('"chapterListWithVolume":'):])
            for v in obj:
                vname = v[0].get("volume_name", "") if v else ""
                for c in v:
                    chaps.append({"v": vname, "t": c.get("title", ""), "id": c.get("itemId", "")})
        except Exception as e:
            print("chap parse err", book_id, e, file=sys.stderr)
    return {
        "bookId": book_id,
        "title": title,
        "author": au.group(1) if au else "",
        "readCount": int(rc.group(1)) if rc else None,
        "wordNumber": int(wn.group(1)) if wn else None,
        "status": st.group(1) if st else None,
        "chapterTotal": int(ct.group(1)) if ct else None,
        "chapters": chaps,
    }

if __name__ == "__main__":
    ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]
    out = []
    for i, bid in enumerate(ids):
        try:
            b = get_book(bid)
            out.append(b)
            print(f"[{i+1}/{len(ids)}] {b['title'][:30]} 字数{b['wordNumber']} 在读{b['readCount']} status{b['status']} 章{b['chapterTotal']}", file=sys.stderr)
        except Exception as e:
            print(f"[{i+1}] ERR {bid} {e}", file=sys.stderr)
        time.sleep(0.8)
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), ensure_ascii=False, indent=1)
