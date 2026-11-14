#!/usr/bin/env python3
import http.server, json, os, re, subprocess, threading, urllib.parse, webbrowser

DIR = os.path.dirname(os.path.abspath(__file__))
CPP, BIN = os.path.join(DIR, "dungeon_crawler.cpp"), os.path.join(DIR, "dungeon.exe" if os.name == "nt" else "dungeon")

HTML = r"""<!doctype html><html><head><meta charset="utf-8"><title>DUNGEON CRAWLER</title><style>
*{box-sizing:border-box;margin:0;padding:0}
body{background:#090b10;color:#d8e2dc;font-family:"Courier New",monospace;display:flex;justify-content:center;align-items:center;min-height:100vh;padding:12px}
.wrap{background:#111622;border:3px solid #2b3a55;border-radius:12px;padding:18px;max-width:740px;width:100%;box-shadow:0 0 30px rgba(80,140,255,.15)}
h1{text-align:center;color:#ffd166;letter-spacing:4px;font-size:20px;margin-bottom:12px}
.row{display:flex;gap:18px;flex-wrap:wrap;justify-content:center}
canvas{background:#12151f;border:3px solid #354766;border-radius:6px;image-rendering:pixelated;width:400px;height:400px}
.side{flex:1;min-width:230px;display:flex;flex-direction:column;gap:10px}
.box{background:#0b0e17;border:1px solid #27354d;border-radius:6px;padding:10px;font-size:13px}
.bar{background:#1f2838;height:10px;border-radius:4px;overflow:hidden;margin:6px 0}
.fill{background:#3ddc84;height:100%;transition:width .15s}
.log{min-height:50px;color:#ffd166;white-space:pre-line;line-height:1.4}
.win{color:#5dff9e;font-weight:bold}.loss{color:#ff5566;font-weight:bold}
.pad{display:grid;grid-template-columns:repeat(3,38px);gap:4px}
button{background:#1a2436;color:#d8e2dc;border:1px solid #3b5278;border-radius:5px;padding:7px;font-family:inherit;font-weight:bold;cursor:pointer}
button:hover{background:#263550;border-color:#ffd166}
.hof{font-size:11px;color:#8fa3bf;white-space:pre-line;line-height:1.4}
</style></head><body><div class="wrap"><h1>DUNGEON CRAWLER</h1><div class="row">
<canvas id="c" width="400" height="400"></canvas><div class="side">
<div class="box"><div style="display:flex;justify-content:space-between"><span>HP: <b id="hp">50</b>/50</span><span>ATK: <b id="atk">6</b></span><span>GOBLINS: <b id="gobs">3</b></span></div>
<div class="bar"><div id="hpbar" class="fill" style="width:100%"></div></div></div>
<div class="box log" id="log">Arrow keys or W A S D to move. Bump G to fight!</div>
<div class="box" style="display:flex;justify-content:space-between;align-items:center">
<div class="pad"><div></div><button onclick="go('w')">▲</button><div></div><button onclick="go('a')">◀</button><button onclick="go('s')">▼</button><button onclick="go('d')">▶</button></div>
<button onclick="rst()" style="padding:10px 12px">NEW GAME (R)</button></div>
<div class="box" style="font-size:12px;color:#9ab">Move: Arrows / WASD | Kill all Goblins, then enter Portal</div>
<div class="box hof" id="hof"></div></div></div></div><script>
const PAL={K:'#0b0e14',W:'#d9e4ec',S:'#7f93a3',V:'#1c2630',P:'#8f3985',G:'#4ec94e',D:'#256b25',R:'#ff4757',Y:'#ffd166',B:'#3a4654',L:'#556575',U:'#b469ff'};
const SPR={'@':['..KKKK..','.KWWWWK.','.KWVVWK.','PKSSSSKP','PKWWWWKP','.KSSSSK.','.KW..WK.','.KK..KK.'],'G':['K......K','KGGGGGGK','.KGRRGK.','.KGGGGK.','.KDDDDK.','.KGGGGWK','.KD..DK.','.KK..KK.'],'P':['...YY...','...KK...','..KWWK..','.KRRRRK.','KRRRRRRK','KRRRRRRK','.KRRRRK.','..KKKK..'],'S':['......WK','.....WWK','....WWK.','...WWK..','.YWWK...','..YY....','.Y..Y...','K.......'],'E':['.BBBBBB.','BBUUUUBB','BUUUUUUB','BUUWWUUB','BUUUUUUB','BUUUUUUB','BBUUUUBB','BBBBBBBB'],'#':['LLLLLLLK','LBBBBBBK','LBBBBBBK','KKKKKKKK','LLLKLLLK','BBBKBBBK','BBBKBBBK','KKKKKKKK']};
const ctx=document.getElementById('c').getContext('2d');let over=false;
function draw(ch,gx,gy){const s=SPR[ch];if(s)for(let y=0;y<8;y++)for(let x=0;x<8;x++){const c=PAL[s[y][x]];if(c){ctx.fillStyle=c;ctx.fillRect(gx*40+x*5,gy*40+y*5,5,5);}}}
function render(s){
  over=s.over;ctx.fillStyle='#141824';ctx.fillRect(0,0,400,400);
  s.grid.forEach((r,y)=>r.forEach((ch,x)=>{ctx.fillStyle=(x+y)%2?'#161b28':'#121622';ctx.fillRect(x*40,y*40,40,40);if(ch!=='.')draw(ch,x,y);}));
  document.getElementById('hp').textContent=s.hp;document.getElementById('hpbar').style.width=Math.max(0,Math.min(100,s.hp*2))+'%';
  document.getElementById('atk').textContent=s.atk;document.getElementById('gobs').textContent=s.goblins;
  const log=document.getElementById('log');log.className='box log'+(s.status==='win'?' win':s.status==='loss'?' loss':'');
  log.textContent=s.message||'Explore the dungeon. Defeat all Goblins, then reach the Portal!';
  document.getElementById('hof').textContent=s.hof?'HALL OF FAME:\n'+s.hof:'No past runs yet.';
}
async function go(k){if(!over)render(await(await fetch('/move?k='+k)).json());}
async function rst(){render(await(await fetch('/reset')).json());}
window.addEventListener('keydown',e=>{const m={ArrowUp:'w',ArrowDown:'s',ArrowLeft:'a',ArrowRight:'d',w:'w',a:'a',s:'s',d:'d'},k=m[e.key]||m[e.key.toLowerCase()];if(k){e.preventDefault();go(k);}else if(e.key.toLowerCase()==='r'){e.preventDefault();rst();}});
fetch('/state').then(r=>r.json()).then(render);
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
        msg, cap = [], False
        for ln in lines:
            if "Goblins left:" in ln: cap, msg = True, []; continue
            if cap:
                if "Your move" in ln or "======" in ln: break
                if ln.strip(): msg.append(ln.strip())
        status, over = "playing", False
        if "YOU ESCAPED THE DUNGEON!" in text: status, over, msg = "win", True, [l.strip() for l in lines if "YOU ESCAPED THE DUNGEON!" in l]
        elif "YOU DIED..." in text: status, over, msg = "loss", True, [l.strip() for l in lines if "YOU DIED..." in l]
        hof_f = os.path.join(DIR, "scores.txt")
        hof = "\n".join([l.strip() for l in open(hof_f) if l.strip()][-5:]) if os.path.exists(hof_f) else ""
        self.state = {"grid": grid[-1] if grid else self.state.get("grid", []), "hp": hp, "atk": atk, "goblins": gobs,
                      "message": "\n".join(msg), "status": status, "over": over, "hof": hof}
    def start(self):
        if not os.path.exists(BIN) or os.path.getmtime(CPP) > os.path.getmtime(BIN):
            subprocess.check_call(["g++", "-std=c++11", "-Wall", "-Wextra", CPP, "-o", BIN])
        if self.proc and self.proc.poll() is None: self.proc.kill()
        self.proc = subprocess.Popen([BIN], cwd=DIR, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        self._read(); self.proc.stdin.write("\n"); self.proc.stdin.flush(); self._parse(self._read())
    def move(self, k):
        with self.lock:
            if not self.state.get("over") and self.proc.poll() is None:
                self.proc.stdin.write(k + "\n"); self.proc.stdin.flush(); self._parse(self._read())
            return self.state
    def reset(self):
        with self.lock: self.start(); return self.state

ENGINE = Engine()

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        p = urllib.parse.urlparse(self.path)
        if p.path == "/":
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers(); self.wfile.write(HTML.encode())
        elif p.path in ("/state", "/move", "/reset"):
            d = ENGINE.state if p.path == "/state" else (ENGINE.reset() if p.path == "/reset" else ENGINE.move(urllib.parse.parse_qs(p.query).get("k", ["w"])[0]))
            self.send_response(200); self.send_header("Content-Type", "application/json"); self.end_headers(); self.wfile.write(json.dumps(d).encode())
        else: self.send_error(404)
    def log_message(self, *args): pass

if __name__ == "__main__":
    print("Dungeon Crawler running at http://localhost:8080  (Ctrl+C to stop)")
    threading.Timer(0.5, lambda: webbrowser.open("http://localhost:8080")).start()
    http.server.HTTPServer(("127.0.0.1", 8080), Handler).serve_forever()
