#!/usr/bin/env python3
"""
统一采集脚本：从每日快照自动读取书籍ID，支持多分类并发采集
严格对齐项目现有 scrape_fanqie_ranks.py + fetch_top20_chapters.py 的实现模式

用法：python fetch_category_chapters.py [--categories 都市高武 都市脑洞] [--date 20260720] [--top 20] [--chapters 10]
"""

import argparse
import json
import os
import threading
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# 字体解码（与 scrape_fanqie_ranks.py 保持一致）
START_CODE = 58344  # 0xE3E8
CHAR_SEQUENCE = [
    "D", "在", "主", "特", "家", "军", "然", "表", "场", "4", "要", "只", "v", "和", "?", "6", "别", "还", "g", "现", "儿", "岁", "?", "?", "此", "象", "月", "3", "出", "战", "工", "相", "o", "男", "直", "失", "世", "F", "都", "平", "文", "什", "V", "O", "将", "真", "T", "那", "当", "?", "会", "立", "些", "u", "是", "十", "张", "学", "气", "大", "爱", "两", "命", "全", "后", "东", "性", "通", "被", "1", "它", "乐", "接", "而", "感", "车", "山", "公", "了", "常", "以", "何", "可", "话", "先", "p", "i", "叫", "轻", "M", "士", "w", "着", "变", "尔", "快", "l", "个", "说", "少", "色", "里", "安", "花", "远", "7", "难", "师", "放", "t", "报", "认", "面", "道", "S", "?", "克", "地", "度", "I", "好", "机", "U", "民", "写", "把", "万", "同", "水", "新", "没", "书", "电", "吃", "像", "斯", "5", "为", "y", "白", "几", "日", "教", "看", "但", "第", "加", "候", "作", "上", "拉", "住", "有", "法", "r", "事", "应", "位", "利", "你", "声", "身", "国", "问", "马", "女", "他", "Y", "比", "父", "x", "A", "H", "N", "s", "X", "边", "美", "对", "所", "金", "活", "回", "意", "到", "z", "从", "j", "知", "又", "内", "因", "点", "Q", "三", "定", "8", "R", "b", "正", "或", "夫", "向", "德", "听", "更", "?", "得", "告", "并", "本", "q", "过", "记", "L", "让", "打", "f", "人", "就", "者", "去", "原", "满", "体", "做", "经", "K", "走", "如", "孩", "c", "G", "给", "使", "物", "?", "最", "笑", "部", "?", "员", "等", "受", "k", "行", "一", "条", "果", "动", "光", "门", "头", "见", "往", "自", "解", "成", "处", "天", "能", "于", "名", "其", "发", "总", "母", "的", "死", "手", "入", "路", "进", "心", "来", "h", "时", "力", "多", "开", "已", "许", "d", "至", "由", "很", "界", "n", "小", "与", "Z", "想", "代", "么", "分", "生", "口", "再", "妈", "望", "次", "西", "风", "种", "带", "J", "?", "实", "情", "才", "这", "?", "E", "我", "神", "格", "长", "觉", "间", "年", "眼", "无", "不", "亲", "关", "结", "0", "友", "信", "下", "却", "重", "己", "老", "2", "音", "字", "m", "呢", "明", "之", "前", "高", "P", "B", "目", "太", "e", "9", "起", "稜", "她", "也", "W", "用", "方", "子", "英", "每", "理", "便", "四", "数", "期", "中", "C", "外", "样", "a", "海", "们", "任"
]


def decode_text(text):
    """字体解码（与主爬虫一致）"""
    if not text:
        return ""
    result = []
    for char in text:
        code = ord(char)
        idx = code - START_CODE
        if 0 <= idx < len(CHAR_SEQUENCE):
            result.append(CHAR_SEQUENCE[idx])
        else:
            result.append(char)
    return "".join(result)


def load_books_from_snapshot(category_name, date_str=None, top_n=20):
    """从每日快照JSON中读取指定分类的书籍ID"""
    data_dir = Path(__file__).parent / "data"

    if date_str:
        snapshot_file = data_dir / f"fanqie_male_new_ranks_{date_str}.json"
    else:
        snapshots = sorted(data_dir.glob("fanqie_male_new_ranks_*.json"), reverse=True)
        if not snapshots:
            raise FileNotFoundError("没有找到任何快照文件")
        snapshot_file = snapshots[0]

    print(f"[{category_name}] 读取快照: {snapshot_file.name}")
    with open(snapshot_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    for cat in data.get("categories", []):
        if cat["name"] == category_name:
            books = []
            for i, book in enumerate(cat["books"][:top_n]):
                url = book.get("url", "")
                book_id = url.split("/page/")[-1] if "/page/" in url else ""
                books.append({
                    "rank": i + 1,
                    "title": book["title"],
                    "bookId": book_id,
                    "author": book.get("author", ""),
                    "reads": book.get("reads", ""),
                })
            return books

    raise ValueError(f"快照中未找到分类: {category_name}")


def extract_chapters(page, book_id):
    """提取完整章节目录（对齐 fetch_top20_chapters.py 的实现）"""
    page.goto(f"https://fanqienovel.com/page/{book_id}", wait_until="load", timeout=15000)
    time.sleep(3)

    # 关闭弹窗（fetch_top20_chapters.py 的反爬策略）
    page.evaluate('document.querySelectorAll("button").forEach(function(b){if(b.innerText.includes("我知道了"))b.click()})')
    time.sleep(0.5)

    # 滚动加载更多章节
    for _ in range(3):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

    # 提取章节链接（对齐 fetch_top20_chapters.py 的JS逻辑，增加过滤）
    js = """(function(){var links=document.querySelectorAll('a[href*="/reader/"]');var chs=[];var seen={};links.forEach(function(a){var h=a.getAttribute('href')||'';var t=a.innerText.trim();if(t&&h.startsWith('/reader/')&&!seen[h]&&!t.startsWith('最近')&&(t.startsWith('第')||t.includes('章'))){seen[h]=1;chs.push({title:t,chapterId:h.replace('/reader/','')})}});return chs})()"""
    try:
        return page.evaluate(js) or []
    except Exception as e:
        print(f"  提取章节目录失败: {e}")
        return []


def extract_content(page, chapter_id):
    """提取章节正文（对齐 fetch_top20_chapters.py 的实现）"""
    page.goto(f"https://fanqienovel.com/reader/{chapter_id}", wait_until="load", timeout=15000)
    time.sleep(2)

    # 滚动触发懒加载
    for _ in range(3):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)

    js = """(function(){var sels=['.muye-reader-content','.reader-content','p'];for(var i=0;i<sels.length;i++){var els=document.querySelectorAll(sels[i]);if(els.length>0){var t='';els.forEach(function(e){var x=e.innerText.trim();if(x&&x.length>5)t+=x+'\\n\\n'});if(t.length>100)return t.trim()}}return ''})()"""
    try:
        return decode_text(page.evaluate(js))
    except Exception as e:
        print(f"  提取正文失败: {e}")
        return ""


def is_book_complete(book_dir, max_chapters):
    """检查书籍是否已完成采集（目录+正文文件齐全）"""
    chapters_file = os.path.join(book_dir, "chapters.json")
    if not os.path.exists(chapters_file):
        return False

    # 检查 chapters.json 是否有内容
    try:
        with open(chapters_file, 'r', encoding='utf-8') as f:
            chapters = json.load(f)
        if not chapters or len(chapters) == 0:
            return False
    except (json.JSONDecodeError, IOError):
        return False

    # 检查前N章正文文件是否齐全
    expected = min(max_chapters, len(chapters))
    for i in range(1, expected + 1):
        chapter_file = os.path.join(book_dir, f"chapter_{i}.txt")
        if not os.path.exists(chapter_file):
            return False
        # 文件存在但内容为空也算未完成
        if os.path.getsize(chapter_file) < 100:
            return False

    return True


def get_existing_book_ids(cat_dir):
    """扫描已有目录，通过meta.json或汇总文件提取已采集的bookId"""
    existing_ids = set()
    if not os.path.exists(cat_dir):
        return existing_ids

    for d in os.listdir(cat_dir):
        book_dir = os.path.join(cat_dir, d)
        if not os.path.isdir(book_dir):
            continue

        # 优先从meta.json读取bookId
        meta_file = os.path.join(book_dir, "meta.json")
        if os.path.exists(meta_file):
            try:
                with open(meta_file, 'r', encoding='utf-8') as fh:
                    meta = json.load(fh)
                if "bookId" in meta:
                    existing_ids.add(meta["bookId"])
                    continue
            except:
                pass

        # 从汇总文件读取bookId（目录级汇总）
        if d.startswith("Top"):
            for f in os.listdir(book_dir):
                if f.endswith(".json") and f not in ("chapters.json", "meta.json"):
                    try:
                        with open(os.path.join(book_dir, f), 'r', encoding='utf-8') as fh:
                            data = json.load(fh)
                        if isinstance(data, dict) and "bookId" in data:
                            existing_ids.add(data["bookId"])
                    except:
                        pass

    # 也检查分类级汇总文件
    for f in os.listdir(cat_dir):
        if f.endswith("_complete.json"):
            try:
                with open(os.path.join(cat_dir, f), 'r', encoding='utf-8') as fh:
                    data = json.load(fh)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "bookId" in item:
                            existing_ids.add(item["bookId"])
            except:
                pass

    return existing_ids


def fetch_category(category_name, books, output_base, max_chapters=10, max_content_chars=5000, force=False):
    """采集单个分类（每个线程独立的浏览器实例）"""
    cat_dir = os.path.join(output_base, category_name)
    os.makedirs(cat_dir, exist_ok=True)

    # 扫描已有bookId（基于bookId去重，避免排名变化导致重复采集）
    existing_ids = set() if force else get_existing_book_ids(cat_dir)
    if existing_ids:
        print(f"[{category_name}] 已有 {len(existing_ids)} 本书的bookId记录")

    # 过滤已完成的书籍（优先用bookId匹配，其次用目录名匹配）
    books_to_fetch = []
    for book in books:
        safe_title = book['title'][:25].replace('/', '_').replace('\\', '_')
        book_dir = os.path.join(cat_dir, f"Top{book['rank']}_{safe_title}")

        # bookId已在已有记录中，跳过
        if book['bookId'] in existing_ids:
            print(f"[{category_name}] [{book['rank']}/{len(books)}] ⏭️ bookId已存在，跳过: {book['title']}")
            continue

        # 目录存在且内容完整，跳过
        if is_book_complete(book_dir, max_chapters):
            print(f"[{category_name}] [{book['rank']}/{len(books)}] ⏭️ 目录已完整，跳过: {book['title']}")
            continue

        books_to_fetch.append(book)

    if not books_to_fetch:
        print(f"[{category_name}] 所有书籍已完成采集，无需重新抓取")
        return

    print(f"[{category_name}] 需要采集 {len(books_to_fetch)}/{len(books)} 本书")

    with sync_playwright() as p:
        # 对齐 scrape_fanqie_ranks.py 的浏览器配置
        if os.environ.get("GITHUB_ACTIONS"):
            browser = p.chromium.launch(headless=True)
        else:
            browser = p.chromium.launch(headless=True, channel="chrome")

        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        all_data = []

        for book in books_to_fetch:
            rank = book['rank']
            title = book['title']
            book_id = book['bookId']

            print(f"\n[{category_name}] [{rank}/{len(books)}] {title}")

            # 获取章节目录
            print(f"  获取章节目录...")
            chapters = extract_chapters(page, book_id)
            print(f"  找到 {len(chapters)} 章")

            # 获取前N章正文
            chapter_contents = []
            for i, ch in enumerate(chapters[:max_chapters]):
                print(f"  获取第{i+1}章: {ch['title']}")
                content = extract_content(page, ch['chapterId'])
                if content and len(content) > 100:
                    chapter_contents.append({
                        'chapter_num': i + 1,
                        'title': ch['title'],
                        'chapterId': ch['chapterId'],
                        'content': content[:max_content_chars]
                    })
                    print(f"    ✓ {len(content)}字")
                else:
                    print(f"    ✗ 获取失败")
                time.sleep(1)  # 防止请求过快

            book_data = {
                'rank': rank,
                'title': title,
                'bookId': book_id,
                'author': book.get('author', ''),
                'reads': book.get('reads', ''),
                'total_chapters': len(chapters),
                'chapters': chapters,
                f'first_{max_chapters}_chapters': chapter_contents
            }
            all_data.append(book_data)

            # 保存单本书（对齐 fetch_top20_chapters.py 的目录结构）
            safe_title = title[:25].replace('/', '_').replace('\\', '_')
            book_dir = os.path.join(cat_dir, f"Top{rank}_{safe_title}")
            os.makedirs(book_dir, exist_ok=True)

            with open(os.path.join(book_dir, "chapters.json"), 'w', encoding='utf-8') as f:
                json.dump(chapters, f, ensure_ascii=False, indent=2)

            # 保存bookId元数据（用于去重）
            with open(os.path.join(book_dir, "meta.json"), 'w', encoding='utf-8') as f:
                json.dump({"bookId": book_id, "rank": rank, "title": title}, f, ensure_ascii=False)

            for i, ch_data in enumerate(chapter_contents):
                with open(os.path.join(book_dir, f"chapter_{i+1}.txt"), 'w', encoding='utf-8') as f:
                    f.write(ch_data['content'])

            time.sleep(3)  # 书籍间隔，防封禁

        browser.close()

    # 保存汇总
    summary_file = os.path.join(cat_dir, f"{category_name}_top{len(books)}_complete.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n[{category_name}] ✅ 完成！汇总: {summary_file}")


def main():
    parser = argparse.ArgumentParser(description="番茄小说分类章节采集（对齐项目现有实现）")
    parser.add_argument('--categories', nargs='+', default=['都市高武', '都市脑洞'],
                        help='要采集的分类名称（默认: 都市高武 都市脑洞）')
    parser.add_argument('--date', default=None,
                        help='快照日期，格式YYYYMMDD（默认: 最新）')
    parser.add_argument('--top', type=int, default=20,
                        help='每个分类采集前N本书（默认: 20）')
    parser.add_argument('--chapters', type=int, default=10,
                        help='每本书采集前N章正文（默认: 10）')
    parser.add_argument('--output', default=None,
                        help='输出目录（默认: 项目data/目录）')
    parser.add_argument('--force', action='store_true',
                        help='强制重新采集已完成的书籍')
    args = parser.parse_args()

    output_base = args.output or os.path.join(Path(__file__).parent, "data", "拆文库")
    os.makedirs(output_base, exist_ok=True)

    # 从快照读取书籍列表
    category_books = {}
    for cat_name in args.categories:
        books = load_books_from_snapshot(cat_name, args.date, args.top)
        category_books[cat_name] = books
        print(f"[{cat_name}] 读取到 {len(books)} 本书")

    # 多分类并发（每个分类一个独立线程+独立浏览器实例）
    threads = []
    for cat_name, books in category_books.items():
        t = threading.Thread(
            target=fetch_category,
            args=(cat_name, books, output_base, args.chapters, 5000, args.force),
            name=f"fetch-{cat_name}"
        )
        threads.append(t)

    print(f"\n启动 {len(threads)} 个并发采集线程...")
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    print(f"\n✅ 全部完成！输出目录: {output_base}")


if __name__ == "__main__":
    main()
