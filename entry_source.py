#!/usr/bin/env python3
"""Tiny-Chess-01 source (compressed to main.py via makefun compress)."""
import json,os,sys,urllib.request
sys.setrecursionlimit(3000)
E=os.environ.get("MAKEFUN_ENV_URL")or sys.exit("MAKEFUN_ENV_URL is not set")
def post(p,b):
 r=urllib.request.Request(E+p,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"})
 return json.load(urllib.request.urlopen(r,timeout=30))
P8=(-21,-19,-12,-8,8,12,19,21)
DG=(-11,-9,9,11);OR=(-10,-1,1,10);AL=DG+OR
VAL={"P":100,"N":320,"B":330,"R":500,"Q":900,"K":0,"p":-100,"n":-320,"b":-330,"r":-500,"q":-900,"k":0}
def centre(i):return min(i,7-i)
def mkpst():
 pa=[0,0,4,8,14,24,40,0];pc=[0,0,0,10,15,10,5,0]
 T={k:[0]*64 for k in"PNBRQKE"}
 for r in range(8):
  for f in range(8):
   i=r*8+f;c=centre(f)+centre(r)
   T["P"][i]=pa[r]+(pc[r]if f in(3,4)else 0)
   T["N"][i]=6*c-20;T["B"][i]=4*c-8
   T["R"][i]=(15 if r==6 else 0)+(5 if r==0 and f in(3,4)else 0)
   T["Q"][i]=2*c-6
   T["K"][i]=[20,25,10,0,0,10,25,20][f]if r==0 else max(-50,-15*r)
   T["E"][i]=8*c-24
 return T
PS=mkpst();OM=6400
B=["x"]*120;W=True;EP=0;CR="KQkq";NODES=0;BUD=250000;MATE=100000;STOP=False;EV=0
NP=0;WB=0;BB=0;KSQ=0;BSQ=0;HP=0
PID={"P":1,"N":2,"B":3,"R":4,"Q":5,"K":6,"p":7,"n":8,"b":9,"r":10,"q":11,"k":12}
Z=[]
_r=123456789
for _i in range(2300):
 _r=(_r*6364136223846793005+1442695040888963407)&0x3FFFFFFFFFFFFFF;Z.append(_r)
C1=Z[2000];HK=0
def keyk():return HK^(C1 if W else 0)^(0 if EP==0 else Z[2200+EP])^Z[2100+((1 if"K"in CR else 0)+(2 if"Q"in CR else 0)+(4 if"k"in CR else 0)+(8 if"q"in CR else 0))]
def rel(s,w):
 row=s//10-2;f=s%10-1
 return row*8+f if w else(7-row)*8+f
def kt(rel):
 p=min(NP,OM)
 return round((PS["K"][rel]*p+PS["E"][rel]*(OM-p))/OM)
KC={}
def kingd():
 return kkt(KSQ,1)-kkt(BSQ,0)
def kkt(s,w):
 p=min(NP,OM)
 return round((PS["K"][rel(s,w)]*p+PS["E"][rel(s,w)]*(OM-p))/OM)
def pev(s,c):
 r=s//10-2;f=s%10-1
 t=PS[c.upper()]
 if c<"a":return VAL[c]+t[r*8+f]
 return -(VAL[c.upper()]+t[(7-r)*8+f])
def load(fen):
 global B,W,EP,CR,EV,HK,NP,WB,BB,KSQ,BSQ,HP
 B=["x"]*120
 for r in range(8):
  for f in range(8):B[21+10*r+f]="."
 p,stm,cr,ep=fen.split()[:4]
 for ri,row in enumerate(p.split("/")):
  f=0
  for c in row:
   if c.isdigit():f+=int(c)
   else:B[21+10*(7-ri)+f]=c;f+=1
 W=stm=="w";CR=cr
 EP=0 if ep=="-"else 21+10*(int(ep[1])-1)+ord(ep[0])-97
 HP=int(fen.split()[4])if len(fen.split())>4 else 0
 EV=0;HK=0;NP=0;WB=0;BB=0
 for s in range(21,99):
  c=B[s]
  if c not in".x":
   if c=="K":KSQ=s
   if c=="k":BSQ=s
   EV+=pev(s,c);HK^=Z[s*16+PID[c]]
   if c in"NBRQnbrq":NP+=abs(VAL[c.upper()])
   if c=="B":WB+=1
   if c=="b":BB+=1
 EV+=kingd()
 EV+=30 if WB>=2 else 0
 EV-=30 if BB>=2 else 0
def isp(s,w):
 b=B
 if w:
  if b[s-9]=="P"or b[s-11]=="P":return 1
  n,k,rq,bq="N","K","RQ","BQ"
 else:
  if b[s+9]=="p"or b[s+11]=="p":return 1
  n,k,rq,bq="n","k","rq","bq"
 for d in P8:
  if b[s+d]==n:return 1
 for d in AL:
  if b[s+d]==k:return 1
 for d in OR:
  t=s+d
  while 21<=t<99:
   c=b[t]
   if c!=".":
    if c in rq:return 1
    break
   t+=d
 for d in DG:
  t=s+d
  while 21<=t<99:
   c=b[t]
   if c!=".":
    if c in bq:return 1
    break
   t+=d
 return 0
def gen():
 ms=[];b=B;own="PNBRQK"if W else"pnbrqk";foe=W
 for s in range(21,99):
  p=b[s]
  if p not in own:continue
  if p in"Pp":
   d=10 if W else-10;t=s+d
   if b[t]==".":
    if t>90 or t<29:
     for q in"qnbr":ms.append((s,t,q))
    else:
     ms.append((s,t,""))
     if(31<=s<=38 if W else 81<=s<=88)and b[t+d]==".":ms.append((s,t+d,""))
   for dd in(d-1,d+1):
    t=s+dd;c=b[t]
    if c!="."and c!="x"and c.islower()==foe:
     if t>90 or t<29:
      for q in"qnbr":ms.append((s,t,q))
     else:ms.append((s,t,""))
    elif EP and t==EP:ms.append((s,t,"e"))
  elif p in"Nn"or p in"Kk":
   for dd in(P8 if p in"Nn"else AL):
    t=s+dd;c=b[t]
    if c=="."or(c!="x"and c.islower()==foe):ms.append((s,t,""))
  else:
   for dd in(OR if p in"Rr"else DG if p in"Bb"else AL):
    t=s+dd
    while 21<=t<99:
     c=b[t]
     if c==".":
      ms.append((s,t,""));t+=dd;continue
     if c!="x"and c.islower()==foe:ms.append((s,t,""))
     break
 if W:
  if"K"in CR and b[25]=="K"and b[28]=="R"and b[26]==b[27]=="."and not isp(25,0)and not isp(26,0)and not isp(27,0):ms.append((25,27,"c"))
  if"Q"in CR and b[25]=="K"and b[21]=="R"and b[22]==b[23]==b[24]=="."and not isp(25,0)and not isp(24,0)and not isp(23,0):ms.append((25,23,"c"))
 else:
  if"k"in CR and b[95]=="k"and b[98]=="r"and b[96]==b[97]=="."and not isp(95,1)and not isp(96,1)and not isp(97,1):ms.append((95,97,"c"))
  if"q"in CR and b[95]=="k"and b[91]=="r"and b[92]==b[93]==b[94]=="."and not isp(95,1)and not isp(94,1)and not isp(93,1):ms.append((95,93,"c"))
 return ms
def mk(m):
 global EP,CR,W,EV,HK,NP,WB,BB,KSQ,BSQ,HP
 s,t,q=m;b=B;e=EP;c=CR;h=HK;hp=HP
 mv=b[s];d1=pev(t,mv)-pev(s,mv)
 HK^=Z[s*16+PID[mv]]
 kd=kingd();kn=NP;bp0=(30 if WB>=2 else 0)-(30 if BB>=2 else 0)
 if q=="c":
  cap="."
  if t==27:b[26],b[28]=b[28],".";d1+=pev(26,"R")-pev(28,"R");HK^=Z[26*16+PID["R"]]^Z[28*16+PID["R"]]
  elif t==23:b[24],b[21]=b[21],".";d1+=pev(24,"R")-pev(21,"R");HK^=Z[24*16+PID["R"]]^Z[21*16+PID["R"]]
  elif t==97:b[96],b[98]=b[98],".";d1+=pev(96,"r")-pev(98,"r");HK^=Z[96*16+PID["r"]]^Z[98*16+PID["r"]]
  else:b[94],b[91]=b[91],".";d1+=pev(94,"r")-pev(91,"r");HK^=Z[94*16+PID["r"]]^Z[91*16+PID["r"]]
 elif q=="e":
  cap=b[t-(10 if W else-10)];b[t-(10 if W else-10)]="."
  d1-=pev(t-(10 if W else-10),"P"if W else"p");HK^=Z[(t-(10 if W else-10))*16+PID["P"if W else"p"]]
 else:
  cap=b[t]
  if cap!=".":d1-=pev(t,cap);HK^=Z[t*16+PID[cap]]
 b[t]=(q.upper()if W else q)if q not in"ce"else b[s]
 b[s]="."
 if mv=="K":KSQ=t
 elif mv=="k":BSQ=t
 EP=(s+t)//2 if b[t]in"pP"and abs(t-s)==20 else 0
 if q and q not in"ce":
  pc=q.upper()if W else q
  b[t]=pc
  d1+=pev(t,pc)-pev(t,mv)
 HK^=Z[t*16+PID[b[t]]]
 if cap not in".x"and cap not in"Pp":NP-=abs(VAL[cap.upper()])
 if q and q not in"ce":NP+=VAL[q.upper()]-100
 if cap=="B":WB-=1
 elif cap=="b":BB-=1
 if q and q not in"ce"and q.upper()=="B":
  if W:WB+=1
  else:BB+=1
 if b[t]=="K":CR=CR.replace("K","").replace("Q","")
 elif b[t]=="k":CR=CR.replace("k","").replace("q","")
 if s==21 or t==21:CR=CR.replace("Q","")
 if s==28 or t==28:CR=CR.replace("K","")
 if s==91 or t==91:CR=CR.replace("q","")
 if s==98 or t==98:CR=CR.replace("k","")
 if mv in"Kk"or(cap not in".x")or(q and q not in"ce"):
  if NP!=kn:KC.clear()
  kd2=kingd()
 else:
  kd2=kd
  NP=kn
 d1+=kd2-kd
 d1+=(30 if WB>=2 else 0)-(30 if BB>=2 else 0)-bp0
 if mv in"Pp"or cap not in".x":HP=0
 else:HP+=1
 EV+=d1
 W=not W;HK^=C1
 return(cap,e,c,d1,h,WB,BB,NP,hp)
def um(m,u):
 global EP,CR,W,EV,HK,NP,WB,BB,KSQ,BSQ,HP
 s,t,q=m;b=B;cap,e,c,d1,h,wb,bb,np,hp=u;W=not W
 b[s]=("P"if W else"p")if q not in"ce"else b[t]
 b[t]="."if q=="e"else cap
 if q=="e":b[t-(10 if W else-10)]="p"if W else"P"
 if q=="c":
  if t==27:b[28],b[26]="R","."
  elif t==23:b[21],b[24]="R","."
  elif t==97:b[98],b[96]="r","."
  else:b[91],b[94]="r","."
 EP=e;CR=c;EV-=d1;HK=h;WB=wb;BB=bb;NP=np;KC.clear()
def ordk(m):
 c=B[m[1]]
 return-(VAL.get(c,0)if c!="."else(900 if m[2]and m[2]not in"ce"else 0))
def qs(a,z,qd=0):
 global NODES
 NODES+=1
 if qd>6 or HP>90:return EV if W else-EV
 w=W
 k=KSQ if w else BSQ
 ic=isp(k,not w)
 if ic:
  ms=gen();leg=0;best=-MATE
  for m in ms:
   u=mk(m)
   if isp(KSQ if w else BSQ,not w):um(m,u);continue
   leg+=1
   sc=-qs(-z,-a,qd+1);um(m,u)
   if sc>best:best=sc
   if sc>a:a=sc
   if a>=z:break
  return best if leg else-MATE
 NODES+=1
 v=EV if W else-EV
 if v>=z:return v
 if v>a:a=v
 ms=[m for m in gen()if B[m[1]]!="."or m[2]=="e"or(m[2]and m[2]not in"ce")]
 ms.sort(key=ordk)
 w=W
 for m in ms:
  u=mk(m)
  if isp(KSQ if w else BSQ,not w):um(m,u);continue
  sc=-qs(-z,-a,qd+1);um(m,u)
  if sc>=z:return sc
  if sc>a:a=sc
 return a
def sr(d,a,z,pl):
 global NODES,STOP
 NODES+=1
 w=W
 k=KSQ if w else BSQ
 ic=isp(k,not w)
 if ic:d+=1
 if NODES>BUD:STOP=True
 if STOP:return EV if W else-EV
 if d<=0:return qs(a,z)
 kk=keyk()
 e=TT.get(kk)
 tm=None
 if e:
  ed,ef,es,em=e
  if ed>=d and abs(es)<MATE-1000:
   if ef==0:return es
   if ef==1 and es>a:
    a=es
    if a>=z:return es
   if ef==2 and es<z:
    z=es
    if a>=z:return es
  tm=em
 if e:tm=e[3]
 ms=gen()
 kl=KL.get(pl)
 if tm in ms:ms.sort(key=lambda m:0 if m==tm else(-20000 if kl and m in kl else ordk(m)))
 else:ms.sort(key=ordk if not kl else lambda m:-20000 if m in kl else ordk(m))
 leg=0;best=-MATE;bm=None;oa=a;oz=z
 for m in ms:
  u=mk(m)
  if isp(KSQ if w else BSQ,not w):um(m,u);continue
  leg+=1
  sc=-sr(d-1,-z,-a,pl+1);um(m,u)
  if STOP:break
  if sc>best:
   best=sc;bm=m
   if sc>a:
    a=sc
    if a>=z:
     KL[pl]=[m]+KL.get(pl,[])[:2]
     break
 if not leg:return-MATE+pl if ic else 0
 if not STOP and len(TT)<150000:TT[kk]=(d,0 if oa<best<oz else(1 if best>=oz else 2),best,bm)
 return best
def uci(m):
 s,t,q=m
 return"abcdefgh"[s%10-1]+str(s//10-1)+"abcdefgh"[t%10-1]+str(t//10-1)+(q if q in"qnr"else"")
def gfbl(legal):
 b=B;bv=-1;best=legal[0]
 for u in legal:
  t=21+10*(int(u[3])-1)+ord(u[2])-97
  v=VAL.get(b[t],1)
  if v>bv:bv=v;best=u
 return best
TT={}
KL={}
HIST=[]
def think(bud,legal):
 global NODES,BUD,STOP,HK
 BUD=bud;NODES=0;STOP=False
 TT.clear();KL.clear();RP=set(HIST[-30:]);HIST.append(keyk())
 bl=set(legal)
 ms=[m for m in gen()if uci(m)in bl]
 if not ms:return gfbl(legal)
 best=None
 for d in range(1,20):
  a=-MATE;bb=None
  ms.sort(key=lambda m:0 if m==best else ordk(m))
  for m in ms:
   u=mk(m)
   if isp(KSQ if not W else BSQ,W):um(m,u);continue
   k2=keyk()
   sc=-sr(d-1,-MATE,-a,1)
   if k2 in RP:sc-=40
   um(m,u)
   if STOP:break
   if sc>a:a=sc;bb=m
  if STOP:break
  if bb:best=bb
 return uci(best)if best else legal[0]
if __name__=="__main__":
 while 1:
  g=post("/game",{})
  if g["status"]=="done":break
  while g["status"]=="your_move":
   load(g["fen"])
   mv=think(250000,g["legal_moves"])
   g=post("/move",{"game":g["game"],"move":mv})
  print(f"game {g['game']}: {g['outcome']} by {g['reason']}",file=sys.stderr)
 print(f"done: {g.get('wins')} won, {g.get('draws')} drawn, {g.get('losses')} lost",file=sys.stderr)
