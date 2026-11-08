#!/usr/bin/env python3
"""抓取都市高武Top20前10章正文（含字体解码+反爬）"""

import json, os, time
from playwright.sync_api import sync_playwright

# 字体解码（FanqieRankTracker方案）
START_CODE = 58344
CHAR_SEQUENCE = ["D","在","主","特","家","军","然","表","场","4","要","只","v","和","?","6","别","还","g","现","儿","岁","?","?","此","象","月","3","出","战","工","相","o","男","直","失","世","F","都","平","文","什","V","O","将","真","T","那","当","?","会","立","些","u","是","十","张","学","气","大","爱","两","命","全","后","东","性","通","被","1","它","乐","接","而","感","车","山","公","了","常","以","何","可","话","先","p","i","叫","轻","M","士","w","着","变","尔","快","l","个","说","少","色","里","安","花","远","7","难","师","放","t","报","认","面","道","S","?","克","地","度","I","好","机","U","民","写","把","万","同","水","新","没","书","电","吃","像","斯","5","为","y","白","几","日","教","看","但","第","加","候","作","上","拉","住","有","法","r","事","应","位","利","你","声","身","国","问","马","女","他","Y","比","父","x","A","H","N","s","X","边","美","对","所","金","活","回","意","到","z","从","j","知","又","内","因","点","Q","三","定","8","R","b","正","或","夫","向","德","听","更","?","得","告","并","本","q","过","记","L","让","打","f","人","就","者","去","原","满","体","做","经","K","走","如","孩","c","G","给","使","物","?","最","笑","部","?","员","等","受","k","行","一","条","果","动","光","门","头","见","往","自","解","成","处","天","能","于","名","其","发","总","母","的","死","手","入","路","进","心","来","h","时","力","多","开","已","许","d","至","由","很","界","n","小","与","Z","想","代","么","分","生","口","再","妈","望","次","西","风","种","带","J","?","实","情","才","这","?","E","我","神","格","长","觉","间","年","眼","无","不","亲","关","结","0","友","信","下","却","重","己","老","2","音","字","m","呢","明","之","前","高","P","B","目","太","e","9","起","稜","她","也","W","用","方","子","英","每","理","便","四","数","期","中","C","外","样","a","海","们","任"]

def decode_text(text):
    if not text: return ""
    return "".join(CHAR_SEQUENCE[ord(c)-START_CODE] if 0<=ord(c)-START_CODE<len(CHAR_SEQUENCE) else c for c in text)

TOP20 = [
    {"rank":1,"title":"我都宇宙之主了，你们还在地球？","bookId":"7644040936980220953"},
    {"rank":2,"title":"我才三岁，怎么会是灭世级灾厄","bookId":"7639494219232463897"},
    {"rank":3,"title":"我，亿万天赋，天才不过见我门槛","bookId":"7633410676018400281"},
    {"rank":4,"title":"打我一巴掌全世界都受到同等伤害","bookId":"7646982686409493566"},
    {"rank":5,"title":"全球奇物降临，只有我有探宝雷达","bookId":"7641941944406379545"},
    {"rank":6,"title":"晚年大帝，被妹妹召唤国运求生？","bookId":"7652308382908419096"},
    {"rank":7,"title":"天幕让你当废物班长你独断万古？","bookId":"7635060797172878361"},
    {"rank":8,"title":"无限复活，被院长姐姐上交国家","bookId":"7643848283697204248"},
    {"rank":9,"title":"国术：从被武警搜山击毙开始见神","bookId":"7647892624631680025"},
    {"rank":10,"title":"高武：长枪黑炎镇妖魔","bookId":"7644545496853253144"},
    {"rank":11,"title":"高考正写作文，变身剑仙一剑开天","bookId":"7644262106589580312"},
    {"rank":12,"title":"什么叫包养的五个校花都成最强了","bookId":"7634637857885277208"},
    {"rank":13,"title":"重生烛龙，我成了最强学院守护兽","bookId":"7644796552564722750"},
    {"rank":14,"title":"高武：开局摆烂的我被老婆绑架了","bookId":"7643389856965479448"},
    {"rank":15,"title":"假面骑士的我，还是抱错的真少爷","bookId":"7652299898301205528"},
    {"rank":16,"title":"我一正经邪神，只接受合法献祭","bookId":"7646325715121474584"},
    {"rank":17,"title":"全面觉醒：一个F是垃圾，三个我","bookId":"7638160189346040894"},
    {"rank":18,"title":"帝国：谁把这个老六招进来的！","bookId":"7641938910922165273"},
    {"rank":19,"title":"本体SSS级，镜像也是SSS级","bookId":"7650374971725728792"},
    {"rank":20,"title":"高武：不好了！真少爷是个修仙的","bookId":"7645554869385825304"},
]

OUTPUT_DIR = "/Users/gqlin/Documents/tomato/拆文库/都市高武Top20_原文"

def extract_chapters(page, book_id):
    page.goto(f"https://fanqienovel.com/page/{book_id}", wait_until="load", timeout=15000)
    time.sleep(3)
    page.evaluate('document.querySelectorAll("button").forEach(function(b){if(b.innerText.includes("我知道了"))b.click()})')
    time.sleep(0.5)
    js = """(function(){var links=document.querySelectorAll('a[href*="/reader/"]');var chs=[];var seen={};links.forEach(function(a){var h=a.getAttribute('href')||'';var t=a.innerText.trim();if(t&&h.startsWith('/reader/')&&!seen[h]&&(t.startsWith('第')||t.includes('章'))){seen[h]=1;chs.push({title:t,chapterId:h.replace('/reader/','')})}});return chs})()"""
    try: return page.evaluate(js) or []
    except: return []

def extract_content(page, chapter_id):
    page.goto(f"https://fanqienovel.com/reader/{chapter_id}", wait_until="load", timeout=15000)
    time.sleep(2)
    for _ in range(3):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(1)
    js = """(function(){var sels=['.muye-reader-content','.reader-content','p'];for(var i=0;i<sels.length;i++){var els=document.querySelectorAll(sels[i]);if(els.length>0){var t='';els.forEach(function(e){var x=e.innerText.trim();if(x&&x.length>5)t+=x+'\\n\\n'});if(t.length>100)return t.trim()}}return ''})()"""
    try: return decode_text(page.evaluate(js))
    except: return ""

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, channel="chrome")
        ctx = browser.new_context(user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        page = ctx.new_page()
        for book in TOP20:
            r, title, bid = book['rank'], book['title'], book['bookId']
            print(f"\n[{r}/20] {title}")
            d = os.path.join(OUTPUT_DIR, f"Top{r}_{title[:25].replace('/','_')}")
            os.makedirs(d, exist_ok=True)
            chs = extract_chapters(page, bid)
            print(f"  目录: {len(chs)}章")
            json.dump(chs, open(os.path.join(d,"chapters.json"),"w",encoding="utf-8"), ensure_ascii=False, indent=2)
            for i,ch in enumerate(chs[:10]):
                c = extract_content(page, ch['chapterId'])
                if c and len(c)>100:
                    open(os.path.join(d,f"chapter_{i+1}.txt"),"w",encoding="utf-8").write(c)
                    print(f"  第{i+1}章: ✓ ({len(c)}字)")
                else:
                    print(f"  第{i+1}章: ✗")
                time.sleep(2)
            time.sleep(5)
        browser.close()
    print(f"\n✅ 完成！{OUTPUT_DIR}")

if __name__=="__main__": main()
