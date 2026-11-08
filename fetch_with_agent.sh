#!/bin/bash
# 使用浏览器agent抓取番茄小说Top20前10章正文

OUTPUT_DIR="/Users/gqlin/Documents/tomato/拆文库/都市高武Top20_原文"
mkdir -p "$OUTPUT_DIR"

# 字体解码函数
decode_text() {
    echo "$1" | python3 -c "
import sys
START_CODE = 58344
CHARS = ['D','在','主','特','家','军','然','表','场','4','要','只','v','和','?','6','别','还','g','现','儿','岁','?','?','此','象','月','3','出','战','工','相','o','男','直','失','世','F','都','平','文','什','V','O','将','真','T','那','当','?','会','立','些','u','是','十','张','学','气','大','爱','两','命','全','后','东','性','通','被','1','它','乐','接','而','感','车','山','公','了','常','以','何','可','话','先','p','i','叫','轻','M','士','w','着','变','尔','快','l','个','说','少','色','里','安','花','远','7','难','师','放','t','报','认','面','道','S','?','克','地','度','I','好','机','U','民','写','把','万','同','水','新','没','书','电','吃','像','斯','5','为','y','白','几','日','教','看','但','第','加','候','作','上','拉','住','有','法','r','事','应','位','利','你','声','身','国','问','马','女','他','Y','比','父','x','A','H','N','s','X','边','美','对','所','金','活','回','意','到','z','从','j','知','又','内','因','点','Q','三','定','8','R','b','正','或','夫','向','德','听','更','?','得','告','并','本','q','过','记','L','让','打','f','人','就','者','去','原','满','体','做','经','K','走','如','孩','c','G','给','使','物','?','最','笑','部','?','员','等','受','k','行','一','条','果','动','光','门','头','见','往','自','解','成','处','天','能','于','名','其','发','总','母','的','死','手','入','路','进','心','来','h','时','力','多','开','已','许','d','至','由','很','界','n','小','与','Z','想','代','么','分','生','口','再','妈','望','次','西','风','种','带','J','?','实','情','才','这','?','E','我','神','格','长','觉','间','年','眼','无','不','亲','关','结','0','友','信','下','却','重','己','老','2','音','字','m','呢','明','之','前','高','P','B','目','太','e','9','起','稜','她','也','W','用','方','子','英','每','理','便','四','数','期','中','C','外','样','a','海','们','任']
text = sys.stdin.read().strip()
result = []
for c in text:
    idx = ord(c) - 58344
    if 0 <= idx < len(CHARS):
        result.append(CHARS[idx])
    else:
        result.append(c)
print(''.join(result))
"
}

# Top20书籍列表
declare -A BOOKS
BOOKS[1]="7644040936980220953|我都宇宙之主了，你们还在地球？"
BOOKS[2]="7639494219232463897|我才三岁，怎么会是灭世级灾厄"
BOOKS[3]="7633410676018400281|我，亿万天赋，天才不过见我门槛"
BOOKS[4]="7646982686409493566|打我一巴掌全世界都受到同等伤害"
BOOKS[5]="7641941944406379545|全球奇物降临，只有我有探宝雷达"
BOOKS[6]="7652308382908419096|晚年大帝，被妹妹召唤国运求生？"
BOOKS[7]="7635060797172878361|天幕让你当废物班长你独断万古？"
BOOKS[8]="7643848283697204248|无限复活，被院长姐姐上交国家"
BOOKS[9]="7647892624631680025|国术：从被武警搜山击毙开始见神"
BOOKS[10]="7644545496853253144|高武：长枪黑炎镇妖魔"
BOOKS[11]="7644262106589580312|高考正写作文，变身剑仙一剑开天"
BOOKS[12]="7634637857885277208|什么叫包养的五个校花都成最强了"
BOOKS[13]="7644796552564722750|重生烛龙，我成了最强学院守护兽"
BOOKS[14]="7643389856965479448|高武：开局摆烂的我被老婆绑架了"
BOOKS[15]="7652299898301205528|假面骑士的我，还是抱错的真少爷"
BOOKS[16]="7646325715121474584|我一正经邪神，只接受合法献祭"
BOOKS[17]="7638160189346040894|全面觉醒：一个F是垃圾，三个我"
BOOKS[18]="7641938910922165273|帝国：谁把这个老六招进来的！"
BOOKS[19]="7650374971725728792|本体SSS级，镜像也是SSS级"
BOOKS[20]="7645554869385825304|高武：不好了！真少爷是个修仙的"

for rank in $(seq 1 20); do
    IFS='|' read -r book_id title <<< "${BOOKS[$rank]}"
    echo ""
    echo "============================================"
    echo "[$rank/20] $title"
    echo "============================================"
    
    BOOK_DIR="$OUTPUT_DIR/Top${rank}_${title:0:25}"
    mkdir -p "$BOOK_DIR"
    
    # 获取章节目录
    echo "  获取章节目录..."
    agent-browser --cdp 9222 open "https://fanqienovel.com/page/$book_id" > /dev/null 2>&1
    sleep 3
    
    # 提取章节链接
    CHAPTERS=$(agent-browser --cdp 9222 eval "
        var links = document.querySelectorAll('a[href*=\"/reader/\"]');
        var chs = [];
        var seen = {};
        links.forEach(function(a) {
            var h = a.getAttribute('href') || '';
            var t = a.innerText.trim();
            if (t && h.startsWith('/reader/') && !seen[h] && (t.startsWith('第') || t.includes('章'))) {
                seen[h] = 1;
                chs.push(t + '|' + h.replace('/reader/', ''));
            }
        });
        chs.slice(0, 10).join('\\n');
    " 2>/dev/null)
    
    echo "$CHAPTERS" > "$BOOK_DIR/chapters.txt"
    CHAPTER_COUNT=$(echo "$CHAPTERS" | wc -l)
    echo "  目录: ${CHAPTER_COUNT}章"
    
    # 抓取前10章正文
    CHAPTER_NUM=0
    echo "$CHAPTERS" | while IFS='|' read -r ch_title ch_id; do
        CHAPTER_NUM=$((CHAPTER_NUM + 1))
        if [ $CHAPTER_NUM -gt 10 ]; then break; fi
        
        echo -n "  第${CHAPTER_NUM}章: ${ch_title:0:20}..."
        
        agent-browser --cdp 9222 open "https://fanqienovel.com/reader/$ch_id" > /dev/null 2>&1
        sleep 2
        
        # 滚动加载
        agent-browser --cdp 9222 eval "window.scrollTo(0, document.body.scrollHeight)" > /dev/null 2>&1
        sleep 1
        
        # 提取正文
        RAW=$(agent-browser --cdp 9222 eval "
            var els = document.querySelectorAll('p');
            var t = '';
            els.forEach(function(e) { var x = e.innerText.trim(); if (x && x.length > 5) t += x + '\\n\\n'; });
            t.substring(0, 15000);
        " 2>/dev/null)
        
        # 解码并保存
        echo "$RAW" | decode_text > "$BOOK_DIR/chapter_${CHAPTER_NUM}.txt"
        
        SIZE=$(wc -c < "$BOOK_DIR/chapter_${CHAPTER_NUM}.txt")
        echo " ✓ (${SIZE}字节)"
        
        sleep 2
    done
    
    sleep 3
done

echo ""
echo "✅ 全部完成！数据保存在: $OUTPUT_DIR"
