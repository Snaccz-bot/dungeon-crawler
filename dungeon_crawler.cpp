// DUNGEON CRAWLER - Retro ASCII OOP Game (C++11)
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <exception>
#include <stdexcept>
#include <cstdlib>
#include <ctime>
#include <cctype>
using namespace std;

class InvalidMoveException : public exception {
    string msg;
public:
    explicit InvalidMoveException(const string& m) : msg(m) {}
    const char* what() const noexcept override { return msg.c_str(); }
};

struct Bonus { int hp, atk; Bonus(int h, int a) : hp(h), atk(a) {} };

class Entity {
protected:
    string name;
    int hp, attack, x, y;
public:
    Entity(const string& n, int h, int a, int px, int py) : name(n), hp(h), attack(a), x(px), y(py) {}
    virtual ~Entity() {}
    virtual char symbol() const = 0;
    virtual int rollDamage() = 0;
    virtual string hitMessage(int dmg) const = 0;
    bool isAlive() const { return hp > 0; }
    void takeDamage(int d) { hp = (hp - d < 0) ? 0 : hp - d; }
    void moveTo(int nx, int ny) { x = nx; y = ny; }
    string getName() const { return name; }
    int getX() const { return x; } int getY() const { return y; }
    int getHP() const { return hp; } int getAttack() const { return attack; }
    friend ostream& operator<<(ostream& out, const Entity& e) { return out << e.name << "  HP: " << e.hp << "  ATK: " << e.attack; }
};

class Player : public Entity {
    int maxHP;
public:
    Player(int px, int py) : Entity("Hero", 50, 6, px, py), maxHP(50) {}
    char symbol() const override { return '@'; }
    int rollDamage() override { return attack + rand() % 3; }
    string hitMessage(int dmg) const override { ostringstream s; s << "You strike for " << dmg << " damage!"; return s.str(); }
    Player operator+(const Bonus& b) const {
        Player r = *this; r.hp = (r.hp + b.hp > r.maxHP) ? r.maxHP : r.hp + b.hp; r.attack += b.atk; return r;
    }
};

class Goblin : public Entity {
public:
    Goblin(int px, int py) : Entity("Goblin", 28, 7, px, py) {}
    char symbol() const override { return 'G'; }
    int rollDamage() override { return (rand() % 4 == 0) ? attack * 2 : attack; }
    string hitMessage(int dmg) const override {
        ostringstream s; s << (dmg > attack ? "The Goblin stabs you from behind for " : "The Goblin slashes you for ") << dmg << " damage" << (dmg > attack ? "!" : "."); return s.str();
    }
};

class Game {
    static const int W = 10, H = 10;
    char map[H][W + 1];
    Player player;
    vector<Entity*> monsters;
    string message, oopNote;
    int turns, goblinsDefeated;
    bool won, quit, oopMode;

    Entity* monsterAt(int mx, int my) {
        for (size_t i = 0; i < monsters.size(); i++)
            if (monsters[i]->getX() == mx && monsters[i]->getY() == my) return monsters[i];
        return NULL;
    }

    void loadMap() {
        const char* layout[H] = {
            "##########", "#@...#...#", "#.##.#.#.#", "#.P#...#.#", "#.G#.###.#",
            "#.##..#..#", "#....G#.##", "#.####...#", "#..P.S.GE#", "##########"
        };
        for (int r = 0; r < H; r++) {
            for (int c = 0; c < W; c++) {
                char ch = layout[r][c];
                if (ch == '@') ch = '.';
                if (ch == 'G') { monsters.push_back(new Goblin(c, r)); ch = '.'; }
                map[r][c] = ch;
            }
            map[r][W] = '\0';
        }
    }

    void fight(Entity* m) {
        ostringstream log;
        int dmg = player.rollDamage();
        m->takeDamage(dmg);
        log << player.hitMessage(dmg);
        if (!m->isAlive()) {
            log << " The " << m->getName() << " is defeated!";
            goblinsDefeated++;
            for (size_t i = 0; i < monsters.size(); i++)
                if (monsters[i] == m) { delete monsters[i]; monsters.erase(monsters.begin() + i); break; }
        } else {
            int back = m->rollDamage();
            player.takeDamage(back);
            log << "\n  " << m->hitMessage(back);
        }
        message = log.str();
        oopNote = "[Polymorphism] Entity* -> virtual rollDamage() & hitMessage()";
    }

    void moveGoblins(Entity* skip = NULL) {
        const int dx[4] = {0, 0, -1, 1}, dy[4] = {-1, 1, 0, 0};
        for (size_t i = 0; i < monsters.size() && player.isAlive(); i++) {
            Entity* m = monsters[i];
            if (m == skip) continue;
            int start = rand() % 4;
            for (int k = 0; k < 4; k++) {
                int d = (start + k) % 4, nx = m->getX() + dx[d], ny = m->getY() + dy[d];
                if (nx == player.getX() && ny == player.getY()) {
                    int back = m->rollDamage();
                    player.takeDamage(back);
                    if (!message.empty()) message += "\n  ";
                    message += m->hitMessage(back);
                    break;
                }
                if (nx >= 0 && ny >= 0 && nx < W && ny < H && map[ny][nx] == '.' && !monsterAt(nx, ny)) {
                    m->moveTo(nx, ny); break;
                }
            }
        }
    }

    void tryMove(int dx, int dy) {
        int nx = player.getX() + dx, ny = player.getY() + dy;
        if (nx < 0 || ny < 0 || nx >= W || ny >= H) throw InvalidMoveException("You cannot leave the dungeon!");
        if (map[ny][nx] == '#') throw InvalidMoveException("Ouch! That is a wall.");
        turns++;
        if (Entity* m = monsterAt(nx, ny)) { fight(m); moveGoblins(m); return; }
        if (map[ny][nx] == 'E') {
            if (!monsters.empty()) { turns--; throw InvalidMoveException("The exit is locked until every Goblin is defeated!"); }
            player.moveTo(nx, ny); won = true; oopNote = "[File Handling] Game::saveScore() writing via fstream"; return;
        }
        player.moveTo(nx, ny); message = ""; oopNote = "[Encapsulation] Player::moveTo() updated private (x, y)";
        if (map[ny][nx] == 'P') { player = player + Bonus(20, 0); map[ny][nx] = '.'; message = "You drink a potion: +20 HP!"; oopNote = "[Operator Overloading] Player::operator+(Bonus(20, 0))"; }
        else if (map[ny][nx] == 'S') { player = player + Bonus(0, 5); map[ny][nx] = '.'; message = "You pick up a sword: +5 Attack!"; oopNote = "[Operator Overloading] Player::operator+(Bonus(0, 5))"; }
        moveGoblins();
    }

    void draw() const {
        cout << "\n";
        for (int r = 0; r < H; r++) {
            cout << "   ";
            for (int c = 0; c < W; c++) {
                char ch = map[r][c];
                if (player.getX() == c && player.getY() == r) ch = player.symbol();
                else for (size_t i = 0; i < monsters.size(); i++)
                    if (monsters[i]->getX() == c && monsters[i]->getY() == r) ch = monsters[i]->symbol();
                cout << ch << ' ';
            }
            cout << "\n";
        }
        cout << "\n   " << player << "   Goblins left: " << monsters.size() << "\n";
        if (!message.empty()) cout << "\n  " << message << "\n";
        if (oopMode && !oopNote.empty()) cout << "  [OOP] " << oopNote << "\n";
    }

    void saveScore() const {
        ofstream out("scores.txt", ios::app);
        if (!out) throw runtime_error("Could not open scores.txt for writing.");
        out << (won ? "WIN " : "LOSS") << " | turns: " << turns
            << " | goblins defeated: " << goblinsDefeated << " | HP left: " << player.getHP() << "\n";
    }

public:
    Game() : player(1, 1), oopNote("[Abstraction] Player & Goblin inherit abstract Entity"),
             turns(0), goblinsDefeated(0), won(false), quit(false), oopMode(true) { loadMap(); }
    ~Game() { for (size_t i = 0; i < monsters.size(); i++) delete monsters[i]; }

    static void showHallOfFame() {
        ifstream in("scores.txt");
        if (!in) throw runtime_error("No past runs yet - you are the first hero!");
        vector<string> lines; string line;
        while (getline(in, line)) lines.push_back(line);
        cout << "\n  --- HALL OF FAME (last runs) ---\n";
        for (size_t i = lines.size() > 5 ? lines.size() - 5 : 0; i < lines.size(); i++) cout << "  " << lines[i] << "\n";
    }

    static void showIntro() {
        cout << "\n  ==========================================\n"
             << "  =        D U N G E O N   C R A W L E R   =\n"
             << "  ==========================================\n"
             << "\n  Defeat every Goblin, then escape through the exit (E).\n"
             << "    @ you   G goblin   P potion (+20 HP)   S sword (+5 ATK)   E exit\n"
             << "  Move with W A S D + Enter. Walk into a Goblin to fight. Q = quit.\n";
    }

    void run() {
        while (!won && player.isAlive() && !quit) {
            draw(); message = "";
            cout << "\n  Your move (W/A/S/D, L=OOP, Q to quit): " << flush;
            string line;
            if (!getline(cin, line)) { quit = true; break; }
            try {
                if (line.empty()) throw InvalidMoveException("Type W, A, S or D and press Enter.");
                switch ((char)tolower((unsigned char)line[0])) {
                    case 'w': tryMove(0, -1); break; case 's': tryMove(0, 1); break;
                    case 'a': tryMove(-1, 0); break; case 'd': tryMove(1, 0); break;
                    case 'l': oopMode = !oopMode; oopNote = oopMode ? "[Encapsulation] OOP Learning Mode ON" : ""; message = oopMode ? "OOP Learning Mode ON." : "OOP Learning Mode OFF."; break;
                    case 'q': quit = true; break;
                    default: throw InvalidMoveException("Unknown key. Use W, A, S, D, L or Q.");
                }
            } catch (const InvalidMoveException& e) { message = string("! ") + e.what(); oopNote = "[Exception Handling] Caught InvalidMoveException::what()"; }
        }
        draw();
        cout << "\n  ==========================================\n";
        if (won) cout << "  YOU ESCAPED THE DUNGEON! Victory in " << turns << " turns.\n";
        else if (!player.isAlive()) cout << "  YOU DIED... The goblins win this time.\n";
        else cout << "  You left the dungeon. Game over.\n";
        cout << "  ==========================================\n";
        if (won || !player.isAlive()) { try { saveScore(); } catch (const runtime_error& e) { cout << "  (" << e.what() << ")\n"; } }
    }
};

int main() {
    srand((unsigned)(time(NULL) ^ clock()));
    Game::showIntro();
    try { Game::showHallOfFame(); } catch (const runtime_error& e) { cout << "\n  " << e.what() << "\n"; }
    cout << "\n  Press Enter to start..." << flush;
    string dummy; getline(cin, dummy);
    Game game; game.run();
    try { Game::showHallOfFame(); } catch (const runtime_error& e) { cout << "\n  " << e.what() << "\n"; }
    return 0;
}
