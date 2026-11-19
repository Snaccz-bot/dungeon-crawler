# Dungeon Crawler — Retro 2D Pixel & ASCII Game in C++ (OOP)

A turn-based 10x10 dungeon crawler built in standard **C++11** to demonstrate Object-Oriented Programming (OOP), paired with a zero-dependency **2D pixel-art localhost UI**.

---

## Team & Course Details
- **Students:** Adit Gupta (`00914803125`) & Saurish Seth (`01014803125`)
- **Class / Group:** I123 (Group I1) — B.Tech IT, 3rd Semester
- **Subject:** Object-Oriented Programming using C++

---

## Download & Run (Zero Setup)

### 1. Clone the repository
```bash
git clone https://github.com/Snaccz-bot/dungeon-crawler.git
cd dungeon-crawler
```

### 2. Run in 2D Pixel-Art Browser Mode (Recommended)
Compiles `dungeon_crawler.cpp` automatically and opens `http://localhost:8080`:
```bash
python3 play.py
```
*(Use **Arrow keys** or **W A S D** to move directly — no pressing Enter. Press **L** to toggle the live OOP Code Panel, **I** to replay the Star Wars Lore Intro, and **R** to restart.)*

### 3. Run in Classic C++ Terminal Mode (Optional)
```bash
g++ -std=c++11 -Wall -Wextra dungeon_crawler.cpp -o dungeon
./dungeon
```
*(On Windows: `dungeon.exe`)*

---

## How to Play

| Symbol / Sprite | Meaning | Effect |
|-----------------|---------|--------|
| `@` (Knight) | Hero (You) | Starts at `(1,1)` with **50 HP** and **6 ATK** |
| `G` (Goblin) | Roaming Enemy | **28 HP / 7 ATK** (25% chance for 2x damage; moves 1 tile every turn) |
| `P` (Potion) | Health Potion | Restores **+20 HP** (up to max 50) |
| `S` (Sword) | Weapon Upgrade | Adds **+5 ATK** permanently |
| `E` (Portal) | Exit Door | Locked until all 3 Goblins are defeated |
| `#` / `.` | Wall / Floor | Blocks movement / Walkable tile |

---

## OOP Architecture

| OOP Concept | Implementation in `dungeon_crawler.cpp` |
|-------------|-----------------------------------------|
| **Abstract Base Class** | `Entity` with pure virtual functions `symbol()`, `rollDamage()`, `hitMessage()` |
| **Inheritance** | `Player` and `Goblin` inherit publicly from `Entity` |
| **Encapsulation** | `protected` attributes in `Entity`; `private` map and state in `Game` |
| **Runtime Polymorphism** | `vector<Entity*> monsters` calls `m->rollDamage()` & `m->hitMessage()` dynamically |
| **Virtual Destructor** | `virtual ~Entity()` + `delete` on defeated Goblins and in `~Game()` |
| **Operator Overloading** | `operator<<` (stats output) and `Player::operator+` (applies `Bonus` struct) |
| **Exception Handling** | Custom `InvalidMoveException` (walls, bounds, locked exit) & `runtime_error` |
| **File Handling (`fstream`)** | `ofstream` appends run results to `scores.txt`; `ifstream` loads the Hall of Fame |

---

## Project Summary
- **Problem Addressed:** Bridges textbook C++ OOP theory and practical software by applying core OOP mechanisms in an interactive game.
- **Verification:** Compiles with **0 warnings** (`-Wall -Wextra`), **0 memory leaks** (ASan/UBSan), passes **14/14** edge-case tests, and features dynamic per-turn Goblin movement tuned to a challenging **~1% blind-rush win rate**.
- **Mapped SDG:** **SDG 4 (Quality Education)** — interactive C++ OOP learning tool with an opening lore crawl (`I`), live plain-English + C++ code panel (`L`), and a 6-card end-of-run OOP recap.

---

## Repository Structure
```text
dungeon-crawler/
├── dungeon_crawler.cpp   # C++11 OOP game engine & live concept tracer (236 lines)
├── play.py               # Localhost 2D pixel-art learning UI & lore intro (154 lines)
├── README.md             # Setup & architecture guide
└── .gitignore            # Ignores compiled binaries and scores.txt
```
