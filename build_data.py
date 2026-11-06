#!/usr/bin/env python3
"""Parse HowToCook markdown into recipes.js (loaded by index.html).
Usage: python3 build_data.py <path-to-HowToCook-repo> [out.js]
Edit aliases.json / basics.json and re-run to tune matching."""
import sys, os, re, json, collections

HERE = os.path.dirname(os.path.abspath(__file__))
CATS = {"aquatic":"水产","breakfast":"早餐","condiment":"调味料","dessert":"甜品","drink":"饮品",
        "meat_dish":"荤菜","semi-finished":"半成品","soup":"汤与粥","staple":"主食","vegetable_dish":"素菜"}

alias_src = json.load(open(os.path.join(HERE,"aliases.json"),encoding="utf-8"))
alias_src.pop("_comment",None)
ALIAS = {}
for canon, d in alias_src.items():
    ALIAS[canon] = canon
    for a in d["aliases"]: ALIAS[a] = canon
BASICS = json.load(open(os.path.join(HERE,"basics.json"),encoding="utf-8"))

TOOL_RE = re.compile(r'(锅|灶|烤箱|微波炉|料理机|搅拌|榨汁机|机$|模具|碗|盘|盆|筷|刀|砧板|纱布|保鲜膜|锡纸|容器|瓶|勺|铲|筛|杯|秤|称|炉|烤架|竹签|牙签|电饭煲|蒸笼|漏|袋|器$|罐|锤|擀面杖|夹|垫|布$|纸$|煲)')
JUNK = {"原料","工具","必备","注","备注","原料和工具","可选"}
FOOD_WHITELIST = {"锅巴","刀鱼"}

def section(text, name):
    m = re.search(r'^##\s*'+name+r'[^\n]*\n(.*?)(?=^##\s|\Z)', text, re.S|re.M)
    return m.group(1).strip() if m else ""

def bullets(block):
    return [m.group(1).strip() for l in block.splitlines() if (m:=re.match(r'^\s*[\*\-\+]\s+(.*\S)', l))]

def canon(s):
    s = s.strip().rstrip('各')
    if s in ALIAS: return ALIAS[s]
    # strip common prefixes/suffixes and retry
    for p in ("新鲜","鲜","去皮","切好的","泡发好的","适量","少许","干净的"):
        if s.startswith(p) and s[len(p):] in ALIAS: return ALIAS[s[len(p):]]
    if len(s) == 1: return ""
    if re.search(r'[\d两一二三四五六七八九十]|各|小片|cm', s):          # quantity noise: find a known name inside
        best = max((a for a in ALIAS if len(a) >= 2 and a in s), key=len, default=None)
        if best: return ALIAS[best]
    return s

def parse_ing(raw):
    """-> ('ing', {alts:[..], optional:bool}) or ('tool', name)"""
    s = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', raw)               # images
    s = re.sub(r'\[([^\]]*)\]\([^)]*\)', r'\1', s)              # links
    s = re.sub(r'\*\*|`', '', s)
    optional = bool(re.search(r'可选|\[可选\]|可不|可无|可加|按需', s))
    s = re.sub(r'^\s*(必备|可选|必须)\s*[：:]\s*', '', s)
    s = re.sub(r'\[[^\]]*\]', '', s)
    s = re.sub(r'[（(][^）)]*[）)]', '', s)                      # parenthetical notes
    s = re.sub(r'二选一|任选其一|其中之一', '', s)
    s = re.split(r'[:：]', s)[0]
    s = re.sub(r'\s+[\d./]+.*$', '', s).strip()                 # trailing amounts
    s = re.sub(r'[一二三四五六七八九十\d]+\s*(个|把|块|只|根|片|条|勺|杯|张)$', '', s).strip()
    s = s.replace("葱姜蒜","葱、姜、大蒜")
    parts = [p.strip() for p in re.split(r'[、，,;；]', s) if p.strip() and p.strip() not in JUNK]
    out = []
    for p in parts:
        alts = [a.strip() for a in re.split(r'或者|或是|或|/|\bor\b', p) if a.strip()]
        alts = [c for c in (canon(a) for a in alts if 0 < len(a) <= 12) if c]
        if not alts: continue
        if all(TOOL_RE.search(a) and a not in FOOD_WHITELIST and a not in ALIAS for a in alts):
            out.append(("tool", alts[0]))
        else:
            out.append(("ing", {"alts": list(dict.fromkeys(alts)), "optional": optional}))
    return out

def main(root, outjs):
    recipes=[]; warn=[]
    base=os.path.join(root,"dishes")
    for cat in sorted(os.listdir(base)):
        if cat not in CATS: continue
        for dp,_,files in os.walk(os.path.join(base,cat)):
            for fn in sorted(files):
                if not fn.endswith(".md"): continue
                path=os.path.join(dp,fn)
                text=open(path,encoding="utf-8").read()
                title=(re.match(r'#\s*(.+)',text) or [None,fn[:-3]])[1].strip()
                name=re.sub(r'的做法$','',title).strip()
                diff=re.search(r'预估烹饪难度[：:]\s*(★+)',text)
                kcal=re.search(r'预估卡路里[：:]\s*(\d+)',text)
                paras=[p.strip() for p in text.split("\n\n")]
                desc=paras[1] if len(paras)>1 and not paras[1].startswith(("预估","#","!")) else ""
                ings=[]; tools=[]
                for raw in bullets(section(text,"必备原料和工具")):
                    for kind,v in parse_ing(raw):
                        (ings if kind=="ing" else tools).append(v)
                # de-dup ingredient groups
                seen=set(); uniq=[]
                for g in ings:
                    k=(tuple(g["alts"]),g["optional"])
                    if k not in seen: seen.add(k); uniq.append(g)
                steps=[re.sub(r'^\s*\d+\.\s*','',l).strip() for l in section(text,"操作").splitlines() if re.match(r'^\s*\d+\.',l)]
                amounts=[re.sub(r'\s*\*\s*份数$','',re.sub(r'!\[[^\]]*\]\([^)]*\)','',a)).strip() for a in bullets(section(text,"计算"))]
                rid=os.path.relpath(path,base).replace(os.sep,"/")[:-3]
                if not uniq: warn.append((rid,"no ingredients"))
                if not steps: warn.append((rid,"no steps"))
                recipes.append({"id":rid,"name":name,"cat":cat,"catZh":CATS[cat],
                    "diff":len(diff.group(1)) if diff else 0,"kcal":int(kcal.group(1)) if kcal else None,
                    "desc":re.sub(r'\s+',' ',desc),"ings":uniq,"tools":list(dict.fromkeys(tools)),
                    "amounts":amounts,"steps":steps,
                    "url":"https://github.com/Anduin2017/HowToCook/blob/master/dishes/"+rid+".md"})
    EN = {c:d["en"] for c,d in alias_src.items()}
    EN2ZH = {}
    for c,e in EN.items(): EN2ZH[e.lower()]=c
    blob = ("window.RECIPES="+json.dumps(recipes,ensure_ascii=False,separators=(",",":"))+";\n"
            "window.ALIAS="+json.dumps(ALIAS,ensure_ascii=False,separators=(",",":"))+";\n"
            "window.EN="+json.dumps(EN,ensure_ascii=False,separators=(",",":"))+";\n"
            "window.EN2ZH="+json.dumps(EN2ZH,ensure_ascii=False,separators=(",",":"))+";\n"
            "window.BASICS="+json.dumps(BASICS,ensure_ascii=False)+";\n")
    open(outjs,"w",encoding="utf-8").write(blob)
    print(f"{len(recipes)} recipes -> {outjs} ({len(blob)//1024} KB)")
    for rid,w in warn: print("WARN",rid,w)
    c=collections.Counter(a for r in recipes for g in r["ings"] for a in g["alts"])
    known=set(ALIAS)
    unk=[(k,v) for k,v in c.most_common() if k not in known]
    print(f"{len(c)} distinct ingredient names; top un-aliased:")
    print(", ".join(f"{k}×{v}" for k,v in unk[:60]))

if __name__=="__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv)>2 else os.path.join(HERE,"recipes.js"))
