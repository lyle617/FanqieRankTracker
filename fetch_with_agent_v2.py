#!/usr/bin/env python3
"""使用浏览器agent抓取番茄小说Top20前10章正文"""

import os, json, time, subprocess, base64

OUTPUT_DIR = "/Users/gqlin/Documents/tomato/拆文库/都市高武Top20_原文"

# 字体解码
START_CODE = 58344
CHARS = list("D在主特家军然表场4要只v和?6别还g现儿岁??此象月3出战工相o男直失世F都平文什V O将真T那当?会立些u是十张学气大爱两命全后东性通被1它乐接而感车山公了常以何可话先pi叫轻M士w着变尔快l个说少色里安花远7难师放t报认面道S?克地度I好机U民写把万同水新没书电吃像斯5为y白几日教看但第加候作上拉住有法r事应位利你声身国问马女他Y比父xAHNsX边美对所金活回意到z从j知又内因点Q三定8Rb正或夫向德听更?得告并本q过记L让打f人就者去原满体做经K走如孩cG给使物?最笑部?员等受k行一条果动光门头见解成处于名其发总母的死手入路进心来h时力多开已许d至由很界n小与Z想代么分生口再妈望次西风种带J?实情才这?E我神格长觉间年眼无不亲关结0友信下却重己老2音字m呢明之前高PB目太e9起稜她也W用方子英每理便四数期中C外样a海们任")

def decode(text):
    if not text: return ""
    return "".join(CHARS[ord(c)-START_CODE] if 0<=ord(c)-START_CODE<len(CHARS) else c for c in text)

def run_cmd(cmd):
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout.strip()
    except:
        return ""

def eval_b64(js_code):
    """使用base64编码执行JS"""
    b64 = base64.b64encode(js_code.encode()).decode()
    return run_cmd(f'agent-browser --cdp 9222 eval -b "{b64}"')

TOP20 = [
    (1, "我都宇宙之主了，你们还在地球？", "7644040936980220953"),
    (2, "我才三岁，怎么会是灭世级灾厄", "7639494219232463897"),
    (3, "我，亿万天赋，天才不过见我门槛", "7633410676018400281"),
    (4, "打我一巴掌全世界都受到同等伤害", "7646982686409493566"),
    (5, "全球奇物降临，只有我有探宝雷达", "7641941944406379545"),
    (6, "晚年大帝，被妹妹召唤国运求生？", "7652308382908419096"),
    (7, "天幕让你当废物班长你独断万古？", "7635060797172878361"),
    (8, "无限复活，被院长姐姐上交国家", "7643848283697204248"),
    (9, "国术：从被武警搜山击毙开始见神", "7647892624631680025"),
    (10, "高武：长枪黑炎镇妖魔", "7644545496853253144"),
    (11, "高考正写作文，变身剑仙一剑开天", "7644262106589580312"),
    (12, "什么叫包养的五个校花都成最强了", "7634637857885277208"),
    (13, "重生烛龙，我成了最强学院守护兽", "7644796552564722750"),
    (14, "高武：开局摆烂的我被老婆绑架了", "7643389856965479448"),
    (15, "假面骑士的我，还是抱错的真少爷", "7652299898301205528"),
    (16, "我一正经邪神，只接受合法献祭", "7646325715121474584"),
    (17, "全面觉醒：一个F是垃圾，三个我", "7638160189346040894"),
    (18, "帝国：谁把这个老六招进来的！", "7641938910922165273"),
    (19, "本体SSS级，镜像也是SSS级", "7650374971725728792"),
    (20, "高武：不好了！真少爷是个修仙的", "7645554869385825304"),
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

for rank, title, book_id in TOP20:
    print(f"\n{'='*60}")
    print(f"[{rank}/20] {title}")
    print(f"{'='*60}")
    
    safe_title = title[:25].replace('/', '_')
    book_dir = os.path.join(OUTPUT_DIR, f"Top{rank}_{safe_title}")
    os.makedirs(book_dir, exist_ok=True)
    
    # 打开详情页
    print("  获取章节目录...")
    run_cmd(f'agent-browser --cdp 9222 open "https://fanqienovel.com/page/{book_id}"')
    time.sleep(3)
    
    # 提取章节（使用base64避免转义问题）
    chapters_js = """JSON.stringify(Array.from(document.querySelectorAll('a[href*="/reader/"]')).filter(a=>{var t=a.innerText.trim();return t&&(t.startsWith('第')||t.includes('章'))}).map(a=>({title:a.innerText.trim(),id:a.getAttribute('href').replace('/reader/','')})).slice(0,10))"""
    
    raw = eval_b64(chapters_js)
    try:
        chapters = json.loads(raw) if raw else []
    except:
        chapters = []
    
    print(f"  找到 {len(chapters)} 章")
    
    # 保存章节目录
    with open(os.path.join(book_dir, "chapters.json"), 'w', encoding='utf-8') as f:
        json.dump(chapters, f, ensure_ascii=False, indent=2)
    
    # 抓取每章正文
    for i, ch in enumerate(chapters[:10]):
        ch_id = ch['id']
        ch_title = ch['title']
        print(f"  第{i+1}章: {ch_title[:25]}...", end=" ")
        
        # 打开阅读页
        run_cmd(f'agent-browser --cdp 9222 open "https://fanqienovel.com/reader/{ch_id}"')
        time.sleep(2)
        
        # 滚动加载
        run_cmd('agent-browser --cdp 9222 eval "window.scrollTo(0, document.body.scrollHeight)"')
        time.sleep(1)
        
        # 提取正文（使用base64）
        content_js = """(function(){var els=document.querySelectorAll('p');var t='';els.forEach(function(e){var x=e.innerText.trim();if(x&&x.length>5)t+=x+'\\n\\n'});return t.substring(0,20000)})()"""
        raw_content = eval_b64(content_js)
        
        # 解码
        content = decode(raw_content) if raw_content else ""
        
        if content and len(content) > 100:
            with open(os.path.join(book_dir, f"chapter_{i+1}.txt"), 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ ({len(content)}字)")
        else:
            print("✗")
        
        time.sleep(2)
    
    time.sleep(3)

print(f"\n✅ 全部完成！数据保存在: {OUTPUT_DIR}")
