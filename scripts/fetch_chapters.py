#!/usr/bin/env python3
"""抓取番茄章节正文并解码（charset 两模式），输出 md 文件。"""
import json, re, sys, time, urllib.request

charsets = json.load(open('/Users/gqlin/Documents/workspace/fanqienovel-downloader/src/charset.json'))

def decode(content, mode=0):
    code = [58344, 58715]
    table = charsets[mode]
    out = []
    for ch in content:
        u = ord(ch)
        if code[0] <= u <= code[1]:
            bias = u - code[0]
            if 0 <= bias < len(table) and table[bias] != '?':
                out.append(table[bias])
            else:
                out.append(ch)
        else:
            out.append(ch)
    return ''.join(out)

def fetch(url):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://fanqienovel.com/",
    })
    return urllib.request.urlopen(req, timeout=25).read().decode('utf-8', 'ignore')

def get_chapter(item_id):
    html = fetch(f"https://fanqienovel.com/reader/{item_id}")
    m = re.search(r'<div class="muye-reader-content[^"]*"[^>]*>(.*?)</div>', html, re.S)
    if not m:
        return None, None
    txt = re.sub(r'<[^>]+>', '\n', m.group(1))
    txt = re.sub(r'\n{2,}', '\n', txt).strip()
    d0 = decode(txt, 0)
    # count leftover shifted chars; if many, try mode 1
    left = sum(1 for ch in d0 if 58344 <= ord(ch) <= 58715)
    if left > 20:
        d1 = decode(txt, 1)
        left1 = sum(1 for ch in d1 if 58344 <= ord(ch) <= 58715)
        if left1 < left:
            return d1, left1
    return d0, left

def main(specs, outdir):
    import os
    os.makedirs(outdir, exist_ok=True)
    for book_id, label, sel in specs:
        meta = [b for b in json.load(open('/tmp/book_meta10.json')) if b['bookId'] == book_id][0]
        chs = []
        for want in sel:
            for c in meta['chapters']:
                if c['t'].startswith(want):
                    chs.append(c)
                    break
        for c in chs:
            content, leftover = get_chapter(c['id'])
            fn = f"{outdir}/{label}_{c['t'].split(' ')[0]}_{c['id']}.md"
            with open(fn, 'w', encoding='utf-8') as f:
                f.write(f"# {meta['title']} {c['t']}\n\n")
                f.write(content or "[空]")
            print(f"{label} {c['t']} -> {len(content or '')}字 leftover={leftover}", file=sys.stderr)
            time.sleep(0.8)

if __name__ == '__main__':
    import pickle
    specs = json.load(open(sys.argv[1]))
    main(specs, sys.argv[2])
