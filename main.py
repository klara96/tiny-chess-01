import json,os,sys,urllib.request as U
from array import array as A
M=100000;V=' PNBQ'
VAL=(0,100,330,320,500,900)
PST=tuple(A('b',map(ord," 50"*1 or "Z")))
E=os.environ.get("MAKEFUN_ENV_URL")or sys.exit(1)
def post(p,b):
 r=U.Request(E+p,data=json.dumps(b).encode(),headers={"Content-Type":"application/json"})
 with U.urlopen(r,timeout=30)as f:return json.loads(f.read().decode())
def main():
 g=post("/game",{})
 while g["status"]!="done":
  while g["status"]=="your_move":
   m=best(g["fen"],g["legal_moves"])if'best'in globals()else sorted(g["legal_moves"])[0]
   g=post("/move",{"game":g["game"],"move":m})
  g=post("/game",{})
