import json, re, sys, unicodedata
LANG=sys.argv[1]; sys.argv=sys.argv[1:]
AUTH={'Пушкин':'А. С. Пушкин','Лермонтов':'М. Ю. Лермонтов','Гоголь':'Н. В. Гоголь','Тургенев':'И. С. Тургенев','Чехов':'А. П. Чехов',
'Толстой':'Л. Н. Толстой','Достоевский':'Ф. М. Достоевский','Куприн':'А. И. Куприн','Бунин':'И. А. Бунин','Гаршин':'В. М. Гаршин','Короленко':'В. Г. Короленко'}
RU_OK=set('ё1234567890-=йцукенгшщзхъ\\фывапролджэячсмитьбю.Ё!"№;%:?*()_+ЙЦУКЕНГШЩЗХЪ/ФЫВАПРОЛДЖЭЯЧСМИТЬБЮ, ')
STOP=re.compile(r'^(Примечани|Комментари|Впервые (напечатан|опубликован)|Версия \d|Публичная Электронная|Источник|Текст печатается|Печатается по)')
EN_OK=set("`1234567890-=qwertyuiop[]\\asdfghjkl;'zxcvbnm,./~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:\"ZXCVBNM<>? ")
OK=RU_OK if LANG=='ru' else EN_OK
BAD=re.compile((r'[A-Za-z]|' if LANG=='ru' else r'[А-Яа-я]|\[Illustration|\bCHAPTER\b|\bPage \d|')+r'http|www\.|\.\s?\.\s?\.\s?\.\s?\.|изд-во|ПСС|Т\. \d')
def norm(t):
    t=re.sub('[​‌‍⁠﻿]','',t)
    t=t.replace('́','').replace(' ',' ').replace(' ',' ').replace('­','')
    t=re.sub(r'[«»„“”]','"',t); t=re.sub(r'[—–‒−]','-',t); t=t.replace('…','...').replace('’',"'")
    t=re.sub(r'\[\d+\]|\*','',t)
    if LANG=='en':
        t=t.replace('‘',"'").replace('æ','ae').replace('Æ','Ae').replace('œ','oe')
        t=''.join(c for c in unicodedata.normalize('NFKD',t) if not unicodedata.combining(c))
    t=re.sub(r'\s+',' ',t).strip()
    t=re.sub(r'\.\.\. ?\.','...',t)
    return t
def key(t): return re.sub(r'[^а-яa-z]','',t.lower().replace('ё','е'))[:200]
def sentences(t):
    return re.findall(r""".+?(?:[.!?]+["']?(?=\s+[-"'А-ЯЁA-Z])|$)""",t)
def passages(paras, lo=320, hi=750):
    out=[]; cur=''
    def flush():
        nonlocal cur
        if cur: out.append(cur.strip()); cur=''
    for p in paras:
        if len(p)>hi:
            flush(); chunk=''
            for s in sentences(p):
                s=s.strip()
                if chunk and len(chunk)+len(s)>hi*0.8: out.append(chunk); chunk=''
                chunk=(chunk+' '+s).strip()
            if chunk:
                if len(chunk)<lo/2 and out: out[-1]+=' '+chunk
                else: out.append(chunk)
            continue
        cur=(cur+' '+p).strip()
        if len(cur)>=lo: flush()
    if cur:
        if len(cur)<lo/2 and out: out[-1]+=' '+cur
        else: out.append(cur)
    return out
works=[]
for fn in sys.argv[2:]:
    for k,v in json.load(open(fn,encoding='utf-8')).items():
        a,t=k.split('~')
        seen=set(); res=[]; dropped=0
        raw=v['paras']
        ks=[key(norm(x))[:40] for x in raw]
        first=next((i for i,x in enumerate(ks) if len(x)>=40),None)
        if first is not None:
            again=[j for j in range(first+1,len(ks)) if ks[j]==ks[first]]
            if again: print('  cut second edition at',again[0],'of',len(raw)); raw=raw[:again[0]]
        for p in raw:
            if STOP.search(p) and len(res)>5: break
            p=norm(p)
            if len(p)<2 or BAD.search(p) or any(c not in OK for c in p): dropped+=1; continue
            kk=key(p)[:40]
            if len(kk)>=40 and kk in seen: continue
            seen.add(kk); res.append(p)
        ps=passages(res)
        works.append({'a':AUTH.get(a,a),'t':t,'p':ps})
        print(f"{AUTH.get(a,a):18} {t:30} paras={len(res):4} drop={dropped:3} passages={len(ps):4} chars={sum(map(len,ps)):7}")
works.sort(key=lambda w:(w['a'].split()[-1],w['t']))
js=f'// Отрывки из классической прозы (общественное достояние), источник: {LANG}.wikisource.org\nwindow.CLASSICS_{LANG.upper()}='+json.dumps(works,ensure_ascii=False,separators=(',',':'))+';\n'
open(sys.argv[1],'w',encoding='utf-8').write(js)
print('total passages',sum(len(w['p']) for w in works),'chars',sum(len(x) for w in works for x in w['p']),'bytes',len(js.encode()))
