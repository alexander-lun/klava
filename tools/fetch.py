import sys, json, re, time, html, urllib.request, urllib.parse, os
API="https://ru.wikisource.org/w/api.php"
CACHE="cache"; os.makedirs(CACHE, exist_ok=True)
def api(**p):
    p.update(format="json", formatversion=2)
    url=API+"?"+urllib.parse.urlencode(p)
    for i in range(6):
        try:
            req=urllib.request.Request(url, headers={"User-Agent":"typing-trainer/1.0 (offline typing trainer; https://github.com/alexander-lun/klava)"})
            r=json.load(urllib.request.urlopen(req, timeout=60)); time.sleep(1.2); return r
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(10*(i+1)); continue
            raise
        except Exception as e:
            time.sleep(5)
    raise RuntimeError("failed "+url)
def page_html(title):
    fn=os.path.join(CACHE, re.sub(r'[/ ]','_',title)+".json")
    if os.path.exists(fn): return json.load(open(fn))
    r=api(action="parse", page=title, prop="text", redirects=1)
    if "error" in r: d={"error":r["error"]["code"]}
    else: d={"title":r["parse"]["title"], "html":r["parse"]["text"]}
    json.dump(d, open(fn,"w")); return d
OLD=re.compile(r'[ѣѢіІѳѲѵѴ]|[бвгджзклмнпрстфхцчшщ]ъ\b')
def paragraphs(h):
    h=re.sub(r'<sup[^>]*class="[^"]*reference.*?</sup>','',h,flags=re.S)
    h=re.sub(r'<(table|style|script)[^>]*>.*?</\1>','',h,flags=re.S)
    out=[]
    for m in re.finditer(r'<p[^>]*>(.*?)</p>',h,flags=re.S):
        t=html.unescape(re.sub(r'<[^>]+>','',m.group(1)))
        t=re.sub(r'\s+',' ',t).strip()
        if t: out.append(t)
    return out
def sublinks(title, h):
    base=urllib.parse.quote(title.replace(' ','_'))
    seen=[]; 
    for m in re.finditer(r'href="/wiki/([^"#]+)"',h):
        t=urllib.parse.unquote(m.group(1)).replace('_',' ')
        if t.startswith(title+'/') and t not in seen and 'ДО' not in t.split('/')[-1]: seen.append(t)
    return seen
def work(title, depth=0):
    d=page_html(title)
    if "error" in d: return None, d["error"]
    ps=paragraphs(d["html"]); subs=sublinks(d["title"], d["html"])
    if subs and depth<2:
        allp=[]
        for s in subs:
            sp,_=work(s, depth+1)
            if sp: allp+=sp
        if sum(map(len,allp))>sum(map(len,ps)): ps=allp
    return ps, d["title"]
if __name__=="__main__":
    res={}
    for line in open(sys.argv[1],encoding='utf-8'):
        line=line.strip()
        if not line or line.startswith('#'): continue
        key,title=line.split('|',1)
        ps,info=work(title)
        if not ps: print("FAIL",title,info,flush=True); continue
        txt=' '.join(ps); old=len(OLD.findall(txt))
        print(f"{'OLD' if old>20 else 'ok '} {len(ps):4d}p {len(txt):7d}ch old={old:4d} {title}",flush=True)
        res[key]={"title":title,"paras":ps,"old":old}
    json.dump(res,open(sys.argv[2],"w",encoding='utf-8'),ensure_ascii=False)
