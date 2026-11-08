#!/usr/bin/env python3
"""抓取番茄小说top10的章节目录和前10章正文"""

import os
import json
import time
from datetime import datetime
from playwright.sync_api import sync_playwright

# 字体解码
START_CODE = 58344
CHAR_SEQUENCE = [
    "D", "在", "主", "特", "家", "军", "然", "表", "场", "4", "要", "只", "v", "和", "?", "6", "别", "还", "g", "现", "儿", "岁", "?", "?", "此", "象", "月", "3", "出", "战", "工", "相", "o", "男", "直", "失", "世", "F", "都", "平", "文", "什", "V", "O", "将", "真", "T", "那", "当", "?", "会", "立", "些", "u", "是", "十", "张", "学", "气", "大", "爱", "两", "命", "全", "后", "东", "性", "通", "被", "1", "它", "乐", "接", "而", "感", "车", "山", "公", "了", "常", "以", "何", "可", "话", "先", "p", "i", "叫", "轻", "M", "士", "w", "着", "变", "尔", "快", "l", "个", "说", "少", "色", "里", "安", "花", "远", "7", "难", "师", "放", "t", "报", "认", "面", "道", "S", "?", "克", "地", "度", "I", "好", "机", "U", "民", "写", "把", "万", "同", "水", "新", "没", "书", "电", "吃", "像", "斯", "5", "为", "y", "白", "几", "日", "教", "看", "但", "第", "加", "候", "作", "上", "拉", "住", "有", "法", "r", "事", "应", "位", "利", "你", "声", "身", "国", "问", "马", "女", "他", "Y", "比", "父", "x", "A", "H", "N", "s", "X", "边", "美", "对", "所", "金", "活", "回", "意", "到", "z", "从", "j", "知", "又", "内", "因", "点", "Q", "三", "定", "8", "R", "b", "正", "或", "夫", "向", "德", "听", "更", "?", "得", "告", "并", "本", "q", "过", "记", "L", "让", "打", "f", "人", "就", "者", "去", "原", "满", "体", "做", "经", "K", "走", "如", "孩", "c", "G", "给", "使", "物", "?", "最", "笑", "部", "?", "员", "等", "受", "k", "行", "一", "条", "果", "动", "光", "门", "头", "见", "往", "自", "解", "成", "处", "天", "能", "于", "名", "其", "发", "总", "母", "的", "死", "手", "入", "路", "进", "心", "来", "h", "时", "力", "多", "开", "已", "许", "d", "至", "由", "很", "界", "n", "小", "与", "Z", "想", "代", "么", "分", "生", "口", "再", "妈", "望", "次", "西", "风", "种", "带", "J", "?", "实", "情", "才", "这", "?", "E", "我", "神", "格", "长", "觉", "间", "年", "眼", "无", "不", "亲", "关", "结", "0", "友", "信", "下", "却", "重", "己", "老", "2", "音", "字", "m", "呢", "明", "之", "前", "高", "P", "B", "目", "太", "e", "9", "起", "稜", "她", "也", "W", "用", "方", "子", "英", "每", "理", "便", "四", "数", "期", "中", "C", "外", "样", "a", "海", "们", "任"
]

def decode_text(text):
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

# Top10书籍
TOP10 = [
    {"rank": 1, "title": "什么叫高考满分，但人失踪了？", "bookId": "7647411499236871230"},
    {"rank": 2, "title": "上恋综后，和清冷设计师爆火全网", "bookId": "7641906591557487640"},
    {"rank": 3, "title": "我一写网文的，你让我混娱乐圈？", "bookId": "7571820285721054233"},
    {"rank": 4, "title": "顶级博导，重生成为研一规培生", "bookId": "7350265138160602136"},
    {"rank": 5, "title": "神豪系统找替班，我成刀枪炮了！", "bookId": "7621098193832381502"},
    {"rank": 6, "title": "饰演封于修，女友神仙姐姐", "bookId": "7646355030403992638"},
    {"rank": 7, "title": "嘴比脑子快，我上跑男笑疯全网", "bookId": "7645746742557690904"},
    {"rank": 8, "title": "直播研发丧尸病毒，吓坏全国网友", "bookId": "7589310661251828760"},
    {"rank": 9, "title": "高考被撞昏迷，醒来我成文坛领袖", "bookId": "7636981770428107800"},
    {"rank": 10, "title": "医院太卷，我去部队当兵王了！", "bookId": "7637577352167312446"},
]

OUTPUT_DIR = "/Users/gqlin/Documents/tomato/拆文库/都市脑洞新书榜_原文"

def extract_chapters(page, book_id):
    """提取章节目录"""
    url = f"https://fanqienovel.com/page/{book_id}"
    page.goto(url, wait_until="load", timeout=15000)
    time.sleep(2)
    
    # 提取章节目录
    chapters_js = """
    () => {
        const links = document.querySelectorAll('a[href*="/reader/"]');
        const chapters = [];
        links.forEach(link => {
            const href = link.getAttribute('href');
            const text = link.innerText.trim();
            if (text && href) {
                const match = href.match(/\\/reader\\/\\d+\\/(\\d+)/);
                if (match) {
                    chapters.push({
                        title: text,
                        chapterId: match[1],
                        url: 'https://fanqienovel.com' + href
                    });
                }
            }
        });
        return chapters;
    }
    """
    
    try:
        chapters = page.evaluate(chapters_js)
        return chapters
    except Exception as e:
        print(f"  提取章节目录失败: {e}")
        return []

def extract_chapter_content(page, book_id, chapter_id):
    """提取章节正文"""
    url = f"https://fanqienovel.com/reader/{book_id}/{chapter_id}"
    page.goto(url, wait_until="load", timeout=15000)
    time.sleep(2)
    
    # 提取正文
    content_js = """
    () => {
        // 尝试多种选择器
        const selectors = [
            '.muye-reader-content',
            '.reader-content',
            '[class*="content"]',
            'article',
            '.text',
            'p'
        ];
        
        for (const selector of selectors) {
            const elements = document.querySelectorAll(selector);
            if (elements.length > 0) {
                let text = '';
                elements.forEach(el => {
                    const t = el.innerText.trim();
                    if (t && t.length > 10) {
                        text += t + '\\n\\n';
                    }
                });
                if (text.length > 100) {
                    return text.trim();
                }
            }
        }
        
        // 兜底：获取body文本
        return document.body.innerText;
    }
    """
    
    try:
        content = page.evaluate(content_js)
        return decode_text(content)
    except Exception as e:
        print(f"  提取正文失败: {e}")
        return ""

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        all_data = []
        
        for book in TOP10:
            rank = book['rank']
            title = book['title']
            book_id = book['bookId']
            
            print(f"\n[{rank}/10] 处理: {title}")
            
            # 获取章节目录
            print(f"  获取章节目录...")
            chapters = extract_chapters(page, book_id)
            print(f"  找到 {len(chapters)} 章")
            
            # 获取前10章正文
            chapter_contents = []
            for i, chapter in enumerate(chapters[:10]):
                print(f"  获取第{i+1}章: {chapter['title']}")
                content = extract_chapter_content(page, book_id, chapter['chapterId'])
                chapter_contents.append({
                    'chapter_num': i + 1,
                    'title': chapter['title'],
                    'chapterId': chapter['chapterId'],
                    'content': content[:5000]  # 限制每章最多5000字
                })
                time.sleep(1)  # 防止请求过快
            
            book_data = {
                'rank': rank,
                'title': title,
                'bookId': book_id,
                'total_chapters': len(chapters),
                'chapters': chapters,
                'first_10_chapters': chapter_contents
            }
            all_data.append(book_data)
            
            # 保存单本书的数据
            filename = f"Top{rank}_{title[:20]}.json"
            filepath = os.path.join(OUTPUT_DIR, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(book_data, f, ensure_ascii=False, indent=2)
            print(f"  已保存: {filepath}")
            
            time.sleep(2)  # 防止请求过快
        
        browser.close()
    
    # 保存汇总数据
    summary_file = os.path.join(OUTPUT_DIR, "top10_complete_data.json")
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ 全部完成！汇总数据: {summary_file}")

if __name__ == "__main__":
    main()
