#!/usr/bin/env python3
import http.server, json, os, re, subprocess, threading, urllib.parse, webbrowser

DIR = os.path.dirname(os.path.abspath(__file__))
CPP, BIN = os.path.join(DIR, "dungeon_crawler.cpp"), os.path.join(DIR, "dungeon.exe" if os.name == "nt" else "dungeon")

HTML = r"""<!doctype html><html><head><meta charset="utf-8"><title>DUNGEON CRAWLER</title><style>
*{box-sizing:border-box;margin:0;padding:0}body{background:#090b10;color:#e6edf3;font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;display:flex;justify-content:center;align-items:center;height:100vh;padding:16px;overflow:hidden}
.rail{position:fixed;top:14px;left:14px;display:flex;gap:8px;z-index:20}.rail button{background:#111622;color:#b8c7d9;border:1px solid #2b3a55;border-radius:6px;padding:7px 12px;font:600 12px inherit;cursor:pointer}.rail button:hover{color:#ffd166;border-color:#ffd166}
.wrap{background:#111622;border:2px solid #2b3a55;border-radius:12px;padding:18px 20px;width:980px;max-width:calc(100vw - 32px);display:flex;flex-direction:column;gap:14px;box-shadow:0 0 36px rgba(80,140,255,.12)}
.hdr{display:flex;justify-content:space-between;align-items:baseline;border-bottom:1px solid #222e44;padding-bottom:10px}h1{font-family:"Courier New",monospace;color:#ffd166;letter-spacing:3px;font-size:20px}.sub{color:#7ec8e3;font-size:12px;font-weight:500}
.stage{display:grid;grid-template-columns:460px 1fr;gap:16px;align-items:stretch}canvas{background:#12151f;border:2px solid #354766;border-radius:8px;image-rendering:pixelated;width:460px;height:460px;display:block}
.right{display:flex;flex-direction:column;gap:12px;height:460px;min-width:0}.box{background:#0b0e17;border:1px solid #27354d;border-radius:8px;padding:12px 14px}
.stats{display:flex;justify-content:space-between;font-family:"Courier New",monospace;font-size:13.5px;color:#b8c7d9}.stats b{color:#fff}.bar{background:#1f2838;height:9px;border-radius:4px;overflow:hidden;margin-top:8px}.fill{background:#3ddc84;height:100%;transition:width .15s}
.log{min-height:54px;color:#ffd166;white-space:pre-line;line-height:1.45;font-size:14px;font-weight:500;display:flex;align-items:center}
.oop{border-color:#2c4a6e;background:#0a1220;flex:1;display:flex;flex-direction:column;gap:10px;justify-content:space-between;min-height:0}.oop-hdr{display:flex;justify-content:space-between;align-items:center}.oop-hdr b{color:#5dff9e;font-size:15.5px}
.oop-tag{background:#16324f;color:#7ec8e3;padding:3px 9px;border-radius:99px;font-size:11px;font-weight:600}.oop-desc{color:#dbe4ee;font-size:15px;line-height:1.58}
.oop pre,.r-card pre{background:#060911;border:1px solid #1e3148;border-radius:6px;color:#a8e6cf;font-family:"Courier New",monospace;overflow-x:auto}.oop pre{padding:11px 13px;font-size:12.5px;line-height:1.5}
.hint{font-size:12px;color:#7f93ab;text-align:right;margin-top:-4px}.win{color:#5dff9e}.loss{color:#ff5c6c}
.gameover{display:none;flex-direction:column;gap:12px}.go-top{display:flex;justify-content:space-between;align-items:center;gap:12px}.go-title{font-family:"Courier New",monospace;font-size:18px;font-weight:bold;letter-spacing:1px}.go-sub{font-size:13.5px;color:#9fb2c8;margin-top:2px}
.go-btn{background:#ffd166;color:#090b10;border:none;border-radius:6px;padding:9px 16px;font:700 13px inherit;cursor:pointer;flex-shrink:0}.go-btn:hover{background:#ffe08a}
.recap-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.r-card{background:#0b0e17;border:1px solid #27354d;border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:7px}
.r-card.seen{border-color:#2d6a4f;background:#0a1514}.r-card b{font-size:13.5px;color:#ffd166}.r-card.seen b{color:#5dff9e}.r-card p{font-size:12.5px;color:#cdd8e5;line-height:1.45}.r-card pre{padding:7px 9px;font-size:10.5px;line-height:1.38;margin-top:auto}
@media(max-width:1020px){body{height:auto;overflow:auto;padding-top:56px}.stage,.recap-grid{grid-template-columns:1fr}.right{height:auto}}
#intro{position:fixed;inset:0;background:radial-gradient(ellipse at center,#0d1324 0%,#030408 100%);z-index:50;display:flex;flex-direction:column;align-items:center;justify-content:flex-end;overflow:hidden;padding-bottom:28px}
.stars{position:absolute;inset:0;background-image:radial-gradient(1.5px 1.5px at 20px 30px,#fff,transparent),radial-gradient(1px 1px at 90px 140px,#9ec5ff,transparent),radial-gradient(1.5px 1.5px at 180px 80px,#ffd166,transparent),radial-gradient(1px 1px at 260px 210px,#fff,transparent);background-size:300px 260px;opacity:.55;pointer-events:none}
.crawl-stage{position:absolute;inset:0;perspective:340px;overflow:hidden;display:flex;justify-content:center;pointer-events:none}
.crawl{position:absolute;top:100%;width:min(640px,88vw);color:#ffd166;font-size:19px;line-height:1.65;text-align:justify;transform-origin:50% 100%;animation:crawl 36s linear forwards}
.crawl h2{text-align:center;font-size:14px;letter-spacing:4px;color:#7ec8e3;margin-bottom:6px;text-transform:uppercase}.crawl h1{font-size:32px;letter-spacing:3px;color:#ffd166;margin-bottom:22px;text-align:center}.crawl p{margin-bottom:18px}.crawl code{background:rgba(126,200,227,.15);color:#5dff9e;padding:2px 6px;border-radius:4px;font-family:"Courier New",monospace;font-size:16px}
@keyframes crawl{0%{top:92%;transform:rotateX(22deg) translateZ(0)}100%{top:-210%;transform:rotateX(24deg) translateZ(-120px)}}
.skip-btn{position:relative;z-index:60;background:#ffd166;color:#090b10;border:none;padding:11px 22px;font:700 14px inherit;border-radius:8px;box-shadow:0 0 24px rgba(255,209,102,.35);cursor:pointer}.skip-btn:hover{background:#ffe08a}
</style></head><body>
<div id="intro"><div class="stars"></div><div class="crawl-stage"><div class="crawl" id="crawlText">
<h2>Episode IV &bull; SDG 4: Quality Education</h2><h1>THE OOP DUNGEON</h1>
<p>A long time ago, in a C++ memory space far, far away... you enter a 10&times;10 grid built out of <b>Object-Oriented Programming (OOP)</b>.</p>
<p>Before you take a single step, meet the <b>5 Building Blocks</b> defined in the code:</p>
<p><b>1. THE BLUEPRINT (<code>class Entity</code>):</b> Every creature, both you (<code>Player</code>) and the 3 <code>Goblin</code>s, gets its HP, Attack, and position from one shared master blueprint.</p>
<p><b>2. THE LOCKBOX (Encapsulation):</b> Your position <code>(x, y)</code> is private. Nothing can move you except safe rules like <code>moveTo()</code>.</p>
<p><b>3. THE MAGIC COMBINER (<code>operator+</code>):</b> Potions (+20 HP) and Swords (+5 ATK) are <code>Bonus</code> items. We taught C++ how to add them directly to you: <code>player + Bonus</code>.</p>
<p><b>4. THE SAFETY NET (<code>InvalidMoveException</code>):</b> Walk into a wall or a locked portal, and C++ raises a safe warning instead of crashing.</p>
<p><b>5. THE CHRONICLER (<code>scores.txt</code>):</b> Defeat all 3 Goblins, escape through the Portal, and <code>fstream</code> saves your run to disk.</p>
<p>Watch the live C++ code panel as you play. No coding background needed.</p>
</div></div><button class="skip-btn" onclick="closeIntro()">ENTER DUNGEON (SPACE)</button></div>
<div class="rail"><button onclick="go('l')">OOP Panel (L)</button><button onclick="openIntro()">Lore Intro (I)</button></div>
<div class="wrap">
  <div class="hdr"><h1>DUNGEON CRAWLER</h1><div class="sub">SDG 4: Quality Education &bull; Learn C++ OOP by Playing</div></div>
  <div class="stage" id="stage">
    <canvas id="c" width="460" height="460"></canvas>
    <div class="right">
      <div class="box"><div class="stats"><span>HP: <b id="hp">50</b>/50</span><span>ATK: <b id="atk">6</b></span><span>GOBLINS: <b id="gobs">3</b></span></div><div class="bar"><div id="hpbar" class="fill" style="width:100%"></div></div></div>
      <div class="box log" id="log">Arrow keys or W A S D to move. Bump G to fight!</div>
      <div class="box oop" id="oopBox"><div class="oop-hdr"><b id="oopTitle">1. Abstraction &amp; Inheritance</b><span class="oop-tag" id="oopTag">Blueprint</span></div><div class="oop-desc" id="oopDesc">Loading...</div><pre id="oopCode"></pre></div>
      <div class="hint">Arrows / WASD to move &bull; R or Reload to restart</div>
    </div>
  </div>
  <div class="gameover" id="gameover"><div class="go-top"><div><div class="go-title" id="goTitle"></div><div class="go-sub" id="goSub"></div></div><button class="go-btn" onclick="rst()">PLAY AGAIN (R)</button></div><div class="recap-grid" id="recapGrid"></div></div>
</div><script>
const PAL={K:'#0b0e14',W:'#d9e4ec',S:'#7f93a3',V:'#1c2630',P:'#8f3985',G:'#4ec94e',D:'#256b25',R:'#ff4757',Y:'#ffd166',B:'#3a4654',L:'#556575',U:'#b469ff'};
const SPR={'@':['..KKKK..','.KWWWWK.','.KWVVWK.','PKSSSSKP','PKWWWWKP','.KSSSSK.','.KW..WK.','.KK..KK.'],'G':['K......K','KGGGGGGK','.KGRRGK.','.KGGGGK.','.KDDDDK.','.KGGGGWK','.KD..DK.','.KK..KK.'],'P':['...YY...','...KK...','..KWWK..','.KRRRRK.','KRRRRRRK','KRRRRRRK','.KRRRRK.','..KKKK..'],'S':['......WK','.....WWK','....WWK.','...WWK..','.YWWK...','..YY....','.Y..Y...','K.......'],'E':['.BBBBBB.','BBUUUUBB','BUUUUUUB','BUUWWUUB','BUUUUUUB','BUUUUUUB','BBUUUUBB','BBBBBBBB'],'#':['LLLLLLLK','LBBBBBBK','LBBBBBBK','KKKKKKKK','LLLKLLLK','BBBKBBBK','BBBKBBBK','KKKKKKKK']};
const LESSONS={
  ABSTRACTION:{title:'1. Abstraction & Inheritance',tag:'Blueprint',desc:'Think of Entity as a master character sheet. Both your Hero and the Goblins share the same basics like health, attack power, and map spot, so we only write that code once.',code:'class Entity {\n  int hp, attack, x, y;\n  virtual int rollDamage() = 0;\n};\nclass Player : public Entity {};\nclass Goblin : public Entity {};'},
  ENCAPSULATION:{title:'2. Encapsulation',tag:'Lockbox',desc:'Your Hero\'s position (x, y) is kept inside a locked box. Nothing else can randomly teleport you. Only the Hero\'s own moveTo() rule is allowed to change where you stand.',code:'class Entity {\nprotected: int x, y;\npublic:\n  void moveTo(int nx, int ny) { x = nx; y = ny; }\n};'},
  EXCEPTION:{title:'3. Exception Handling',tag:'Safety Net',desc:'When you walk into a wall or locked portal, the program doesn\'t freeze or crash. C++ raises a safe warning, catches it, and shows you a friendly message.',code:'if (map[ny][nx] == \'#\') throw InvalidMoveException("Wall!");\ncatch (const InvalidMoveException& e) { message = e.what(); }'},
  POLYMORPHISM:{title:'4. Runtime Polymorphism',tag:'Smart Combat',desc:'The game treats all monsters as a generic Entity. When you bump into a Goblin, C++ checks what it actually is right then and runs the Goblin\'s own attack rules.',code:'Entity* m = monsterAt(nx, ny);\nm->takeDamage(player.rollDamage());\nint back = m->rollDamage();'},
  OPERATOR:{title:'5. Operator Overloading (+)',tag:'Power-Up',desc:'Normally + only adds numbers like 2 + 3. Here we taught C++ what player + Bonus means, so grabbing a Potion or Sword directly boosts your Hero\'s stats.',code:'Player operator+(const Bonus& b) {\n  Player r = *this; r.hp += b.hp; r.attack += b.atk; return r;\n}'},
  FILEIO:{title:'6. File Handling (fstream)',tag:'Disk Save',desc:'Everything in a game normally vanishes when you close it. Using ofstream, C++ opens a real text file (scores.txt) on your computer and saves your result.',code:'ofstream out("scores.txt", ios::app);\nout << (won ? "WIN " : "LOSS") << " | turns: " << turns << "\\n";'}
};
let seen=new Set(['ABSTRACTION']),introOpen=true,over=false;const ctx=document.getElementById('c').getContext('2d');
const match=(o,s)=>(s==='win'||s==='loss')?'FILEIO':o.includes('Polymorphism')?'POLYMORPHISM':o.includes('Operator')?'OPERATOR':o.includes('Exception')?'EXCEPTION':o.includes('Encapsulation')?'ENCAPSULATION':'ABSTRACTION';
function closeIntro(){introOpen=false;document.getElementById('intro').style.display='none';}
function openIntro(){introOpen=true;const e=document.getElementById('intro'),c=document.getElementById('crawlText');e.style.display='flex';c.style.animation='none';c.offsetHeight;c.style.animation='crawl 36s linear forwards';}
function draw(ch,gx,gy){const s=SPR[ch];if(s)for(let y=0;y<8;y++)for(let x=0;x<8;x++){const c=PAL[s[y][x]];if(c){ctx.fillStyle=c;ctx.fillRect(gx*46+x*5.75,gy*46+y*5.75,5.75,5.75);}}}
function render(s){
  over=s.over;const stg=document.getElementById('stage'),gov=document.getElementById('gameover');
  if(s.over){
    seen.add('FILEIO');stg.style.display='none';gov.style.display='flex';
    const gt=document.getElementById('goTitle');gt.textContent=s.status==='win'?'VICTORY! YOU ESCAPED THE DUNGEON':'GAME OVER — DEFEATED BY GOBLINS';gt.className='go-title '+(s.status==='win'?'win':'loss');
    document.getElementById('goSub').textContent='You saw '+seen.size+' of 6 C++ OOP concepts in action during this run:';
    document.getElementById('recapGrid').innerHTML=Object.entries(LESSONS).map(([,v])=>'<div class="r-card'+(seen.has(Object.keys(LESSONS).find(k=>LESSONS[k]===v))?' seen':'')+'"><b>'+v.title+'</b><p>'+v.desc+'</p><pre>'+v.code+'</pre></div>').join('');
    return;
  }
  stg.style.display='grid';gov.style.display='none';ctx.fillStyle='#141824';ctx.fillRect(0,0,460,460);
  s.grid.forEach((r,y)=>r.forEach((ch,x)=>{ctx.fillStyle=(x+y)%2?'#161b28':'#121622';ctx.fillRect(x*46,y*46,46,46);if(ch!=='.')draw(ch,x,y);}));
  document.getElementById('hp').textContent=s.hp;document.getElementById('hpbar').style.width=Math.max(0,Math.min(100,s.hp*2))+'%';
  document.getElementById('atk').textContent=s.atk;document.getElementById('gobs').textContent=s.goblins;
  document.getElementById('log').textContent=s.message||'Explore the dungeon. Defeat all Goblins, then reach the Portal!';
  const ob=document.getElementById('oopBox');
  if(!s.oop){ob.style.opacity='0.4';document.getElementById('oopTitle').textContent='OOP Panel Hidden';document.getElementById('oopTag').textContent='Off';document.getElementById('oopDesc').textContent='Press L to turn live C++ explanations back on.';document.getElementById('oopCode').textContent='';}
  else{ob.style.opacity='1';const k=match(s.oop,s.status),L=LESSONS[k];seen.add(k);document.getElementById('oopTitle').textContent=L.title;document.getElementById('oopTag').textContent=L.tag;document.getElementById('oopDesc').textContent=L.desc;document.getElementById('oopCode').textContent=L.code;}
}
async function go(k){if(!over||k==='l')render(await(await fetch('/move?k='+k)).json());}
async function rst(){seen=new Set(['ABSTRACTION']);render(await(await fetch('/reset')).json());}
window.addEventListener('keydown',e=>{if(introOpen){if([' ','Enter','Escape'].includes(e.key)){e.preventDefault();closeIntro();}return;}const m={ArrowUp:'w',ArrowDown:'s',ArrowLeft:'a',ArrowRight:'d',w:'w',a:'a',s:'s',d:'d',l:'l'},k=m[e.key]||m[e.key.toLowerCase()];if(k){e.preventDefault();go(k);}else if(e.key.toLowerCase()==='r'){e.preventDefault();rst();}else if(e.key.toLowerCase()==='i'){e.preventDefault();openIntro();}});
rst();
</script></body></html>"""

class Engine:
    def __init__(self):
        self.lock, self.proc, self.state = threading.Lock(), None, {}
        self.start()
    def _read(self):
        buf = ""
        while True:
            ch = self.proc.stdout.read(1)
            if not ch: break
            buf += ch
            if buf.endswith("Q to quit): ") or buf.endswith("Press Enter to start..."): break
        return buf
    def _parse(self, text):
        lines = text.splitlines()
        grid = [[lines[i+j].strip().split() for j in range(10)] for i in range(len(lines)-9)
                if lines[i].strip().startswith("# # # # # # # # # #") and all(len(lines[i+j].strip().split()) == 10 for j in range(10))]
        m = re.findall(r"Hero\s+HP:\s*(\d+)\s+ATK:\s*(\d+)\s+Goblins left:\s*(\d+)", text)
        hp, atk, gobs = map(int, m[-1]) if m else (50, 6, 3)
        msg, oop, cap = [], "", False
        for ln in lines:
            if "Goblins left:" in ln: cap, msg = True, []; continue
            if cap:
                if "Your move" in ln or "======" in ln: break
                s = ln.strip()
                if s.startswith("[OOP] "): oop = s[6:]
                elif s: msg.append(s)
        status, over = ("win", True) if "YOU ESCAPED THE DUNGEON!" in text else (("loss", True) if "YOU DIED..." in text else ("playing", False))
        if over: msg = [l.strip() for l in lines if "YOU ESCAPED" in l or "YOU DIED" in l]
        self.state = {"grid": grid[-1] if grid else self.state.get("grid", []), "hp": hp, "atk": atk, "goblins": gobs,
                      "message": "\n".join(msg), "oop": oop, "status": status, "over": over}
    def start(self):
        if not os.path.exists(BIN) or os.path.getmtime(CPP) > os.path.getmtime(BIN):
            subprocess.check_call(["g++", "-std=c++11", "-Wall", "-Wextra", CPP, "-o", BIN])
        if self.proc and self.proc.poll() is None: self.proc.kill()
        self.proc = subprocess.Popen([BIN], cwd=DIR, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self._read(); self.proc.stdin.write("\n"); self.proc.stdin.flush(); self._parse(self._read())
    def move(self, k):
        with self.lock:
            if not self.state.get("over") and self.proc.poll() is None: self.proc.stdin.write(k + "\n"); self.proc.stdin.flush(); self._parse(self._read())
            return self.state
    def reset(self):
        with self.lock: self.start(); return self.state

ENGINE = Engine()
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/": self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers(); self.wfile.write(HTML.encode())
        elif p.path in ("/state", "/move", "/reset"):
            d = ENGINE.state if p.path == "/state" else (ENGINE.reset() if p.path == "/reset" else ENGINE.move(urllib.parse.parse_qs(p.query).get("k", ["w"])[0]))
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(json.dumps(d).encode())
        else: self.send_error(404)
    def log_message(self, *args): pass

if __name__ == "__main__":
    print("Dungeon Crawler running at http://localhost:8080  (Ctrl+C to stop)")
    threading.Timer(0.5, lambda: webbrowser.open("http://localhost:8080")).start()
    http.server.HTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
