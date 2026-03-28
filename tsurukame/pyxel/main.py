import pyxel
import random

# ============================================================
# SPACE TSURUKAME - Pyxel版
# ============================================================

W, H = 160, 240   # 画面サイズ (px)

# Pyxelパレット色番号
BLACK  = 0
NAVY   = 1
RED    = 8
ORANGE = 9
YELLOW = 10
CYAN   = 12
BLUE   = 13
PINK   = 14
WHITE  = 7
DGRAY  = 5

# キャラクター定義
CHARACTERS = [
    {"id": "2legs", "name": "2HONAШИ", "color": RED,    "legs": 2},
    {"id": "3legs", "name": "3HONAШИ", "color": CYAN,   "legs": 3},
    {"id": "4legs", "name": "4HONAШИ", "color": PINK,   "legs": 4},
    {"id": "5legs", "name": "5HONAШИ", "color": ORANGE, "legs": 5},
]


class TsuruKame:
    def __init__(self):
        pyxel.init(W, H, title="SPACE TSURUKAME", fps=30)
        pyxel.mouse(True)
        self._setup_sounds()
        self._reset()
        pyxel.run(self.update, self.draw)

    # --------------------------------------------------------
    # 初期化
    # --------------------------------------------------------
    def _reset(self):
        self.state          = "title"   # title / animating / playing / result / clear
        self.stage          = 1         # 1〜3
        self.problem        = None
        self.user_ans       = [0, 0]
        self.is_correct     = False
        self.message        = ""
        self.frame          = 0         # 全体フレームカウンタ
        self.timer          = 0         # ステート内タイマー
        self.cover_y        = 0         # カバーパネルのY位置(reveal演出用)

    def _setup_sounds(self):
        # sound(0): スタート
        pyxel.sound(0).set("c3e3g3c4", "s", "5543", "nnnn", 12)
        # sound(1): 選択
        pyxel.sound(1).set("g4", "s", "4", "n", 8)
        # sound(2): 正解
        pyxel.sound(2).set("c4e4g4c4", "s", "4444", "nnnn", 10)
        # sound(3): 不正解
        pyxel.sound(3).set("b2a2f2", "s", "444", "nnn", 8)
        # sound(4): 全クリア
        pyxel.sound(4).set("c4c4c4e4g4c4", "s", "444446", "nnnnnn", 10)

    # --------------------------------------------------------
    # 問題生成
    # --------------------------------------------------------
    def _gen_problem(self, stage):
        if stage == 1:
            ca, cb = CHARACTERS[0], CHARACTERS[2]           # 2脚 vs 4脚
            na, nb = random.randint(2, 3), random.randint(1, 2)
        elif stage == 2:
            ca = random.choice([CHARACTERS[0], CHARACTERS[2]])
            cb = random.choice([CHARACTERS[1], CHARACTERS[3]])
            na, nb = random.randint(2, 4), random.randint(2, 3)
        else:
            ca, cb = random.sample(CHARACTERS, 2)
            na, nb = random.randint(2, 4), random.randint(2, 4)

        chars  = sorted([ca, cb], key=lambda c: c["legs"])
        counts = [na if c["id"] == ca["id"] else nb for c in chars]

        self.problem = {
            "chars":       chars,
            "counts":      counts,
            "total_heads": na + nb,
            "total_legs":  chars[0]["legs"] * counts[0] + chars[1]["legs"] * counts[1],
        }
        self.user_ans   = [0, 0]
        self.is_correct = False
        self.message    = ""
        self.timer      = 0
        self.cover_y    = 0
        self.state      = "animating"

    # --------------------------------------------------------
    # 更新
    # --------------------------------------------------------
    def update(self):
        self.frame += 1
        self.timer += 1

        if self.state == "title":
            if self._clicked(W // 2 - 32, 185, 64, 18):
                pyxel.play(0, 0)
                self.stage = 1
                self._gen_problem(1)

        elif self.state == "animating":
            # 60フレーム(2秒)後にプレイへ
            if self.timer >= 60:
                self.state = "playing"
                self.timer = 0
                self.message = ("ダレガ ナンビキ イルカ？"
                                if self.stage >= 3 else
                                "イロヲ アワセヨウ！")

        elif self.state == "playing":
            p = self.problem
            # キャラ0の -/+
            if self._clicked(8, 185, 14, 12):
                self.user_ans[0] = max(0, self.user_ans[0] - 1)
                pyxel.play(0, 1)
            if self._clicked(48, 185, 14, 12):
                self.user_ans[0] += 1
                pyxel.play(0, 1)
            # キャラ1の -/+
            if self._clicked(88, 185, 14, 12):
                self.user_ans[1] = max(0, self.user_ans[1] - 1)
                pyxel.play(0, 1)
            if self._clicked(128, 185, 14, 12):
                self.user_ans[1] += 1
                pyxel.play(0, 1)
            # 答え合わせ
            if self._clicked(20, 218, W - 40, 16):
                self._check()

        elif self.state == "result":
            # cover_y を上にスライドさせて正解演出
            if self.is_correct:
                self.cover_y = max(self.cover_y - 4, -H)
            if self.timer >= 105:   # 3.5秒後
                if self.stage >= 3:
                    pyxel.play(0, 4)
                    self.state = "clear"
                    self.timer = 0
                else:
                    self.stage += 1
                    self._gen_problem(self.stage)

        elif self.state == "clear":
            if self._clicked(W // 2 - 32, 205, 64, 18):
                self._reset()

    def _check(self):
        p = self.problem
        if (self.user_ans[0] == p["counts"][0] and
                self.user_ans[1] == p["counts"][1]):
            self.is_correct = True
            self.message    = "SEIKAI!! CLEAR!!"
            pyxel.play(0, 2)
            self.state = "result"
            self.timer = 0
        else:
            pyxel.play(0, 3)
            self.message = "CHIGAU YOUDA..."

    # --------------------------------------------------------
    # 描画
    # --------------------------------------------------------
    def draw(self):
        pyxel.cls(BLACK)

        if self.state == "title":
            self._draw_title()
        elif self.state in ("animating", "playing", "result"):
            self._draw_game()
        elif self.state == "clear":
            self._draw_clear()

    # ---- タイトル画面 ----------------------------------------
    def _draw_title(self):
        pyxel.text(W // 2 - 20, 18, "SPACE",     YELLOW)
        pyxel.text(W // 2 - 36, 28, "TSURUKAME", YELLOW)
        pyxel.text(W // 2 - 32, 42, "3 STAGES TO CLEAR", CYAN)

        for i, c in enumerate(CHARACTERS):
            bob = abs((self.frame + i * 8) % 20 - 10)
            x   = 18 + i * 35
            y   = 80 - bob
            mw  = c["legs"] * 5 + 4
            self._draw_monster(x, y, mw, 20, c["color"], c["legs"])

        # STARTボタン (点滅)
        btn_col = RED if self.frame % 30 < 15 else ORANGE
        self._draw_btn(W // 2 - 32, 185, 64, 18, "START GAME", btn_col)

    # ---- ゲーム画面 ------------------------------------------
    def _draw_game(self):
        p = self.problem

        # --- ヘッダー ---
        pyxel.rect(0, 0, W, 40, NAVY)
        pyxel.text(4, 4, f"STAGE {self.stage}", WHITE)
        if self.stage >= 3:
            col = YELLOW if self.frame % 20 < 10 else ORANGE
            pyxel.text(70, 4, "CHALLENGE!", col)

        cur_heads = self.user_ans[0] + self.user_ans[1]
        cur_legs  = (self.user_ans[0] * p["chars"][0]["legs"] +
                     self.user_ans[1] * p["chars"][1]["legs"])
        hcol = 11 if cur_heads == p["total_heads"] else WHITE
        lcol = 11 if cur_legs  == p["total_legs"]  else WHITE

        pyxel.text(4,  20, f"HEADS:{cur_heads}/{p['total_heads']}", hcol)
        pyxel.text(82, 20, f"LEGS:{cur_legs}/{p['total_legs']}",   lcol)
        pyxel.line(0, 40, W, 40, BLUE)

        # --- モンスターエリア ---
        AREA_Y, AREA_H = 42, 72
        pyxel.rect(0, AREA_Y, W, AREA_H, BLACK)

        x_off = 6
        for idx, char in enumerate(p["chars"]):
            cnt = p["counts"][idx]
            mw  = char["legs"] * 5 + 4
            for _ in range(cnt):
                self._draw_monster(x_off, AREA_Y + 12, mw, 22,
                                   char["color"], char["legs"])
                x_off += mw + 4

        # カバーパネル (正解時は上にスライドアウト)
        cover_top = AREA_Y + self.cover_y
        if self.cover_y > -H:
            pyxel.rect(0, cover_top, W, AREA_H, NAVY)
            pyxel.rectb(0, cover_top, W, AREA_H, BLUE)
            if self.state == "animating":
                dots = "." * ((self.timer // 10) % 4)
                pyxel.text(W // 2 - 20, cover_top + AREA_H // 2 - 3,
                           f"LOADING{dots}", CYAN)
            else:
                pyxel.text(W // 2 - 8, cover_top + AREA_H // 2 - 3,
                           "???", CYAN)

        pyxel.line(0, AREA_Y + AREA_H, W, AREA_Y + AREA_H, BLUE)

        # --- メッセージバー ---
        pyxel.rect(0, 116, W, 12, DGRAY)
        msg_col = 11 if self.is_correct else YELLOW
        mx = max(2, W // 2 - len(self.message) * 2)
        pyxel.text(mx, 119, self.message, msg_col)

        # --- 入力エリア (playing時のみ) ---
        if self.state in ("playing", "result"):
            for i, char in enumerate(p["chars"]):
                bx = 4 + i * 78
                pyxel.rect(bx, 133, 72, 78, DGRAY)
                pyxel.rectb(bx, 133, 72, 78, char["color"])

                # ミニモンスター
                mw = char["legs"] * 4 + 4
                self._draw_monster(bx + 4, 138, mw, 16, char["color"], char["legs"])

                # カウンター表示
                pyxel.text(bx + 4, 157, char["name"][:8], char["color"])

                active = self.state == "playing"
                btn_col_m = RED  if active else DGRAY
                btn_col_p = BLUE if active else DGRAY
                self._draw_btn(bx + 6,  183, 14, 12, "-", btn_col_m)
                pyxel.text(bx + 28, 186, str(self.user_ans[i]), WHITE)
                self._draw_btn(bx + 50, 183, 14, 12, "+", btn_col_p)

            # ---- ここだ！ボタン ----
            if self.state == "playing":
                self._draw_btn(20, 217, W - 40, 16, "KOKODA!", YELLOW, BLACK)
            else:
                # result: ボタングレーアウト
                self._draw_btn(20, 217, W - 40, 16, "KOKODA!", DGRAY)

    # ---- クリア画面 ------------------------------------------
    def _draw_clear(self):
        pyxel.text(W // 2 - 44, 30, "CONGRATULATIONS!", YELLOW)
        pyxel.text(W // 2 - 28, 44, "ALL CLEAR!!",      11)

        for i, c in enumerate(CHARACTERS):
            bob = abs((self.frame + i * 7) % 18 - 9)
            x   = 14 + i * 35
            y   = 85 - bob
            mw  = c["legs"] * 5 + 4
            self._draw_monster(x, y, mw, 20, c["color"], c["legs"])

        pyxel.text(W // 2 - 60, 130,
                   "TSURUKAME MASTER DA!", CYAN)

        self._draw_btn(W // 2 - 32, 205, 64, 18, "PLAY AGAIN", BLUE)

    # --------------------------------------------------------
    # ヘルパー: モンスター描画
    # --------------------------------------------------------
    def _draw_monster(self, x, y, w, h, color, legs):
        body_h = max(4, int(h * 0.65))
        # 体
        pyxel.rect(x, y, w, body_h, color)
        # 目
        eye_y = y + max(1, body_h // 3)
        pyxel.pset(x + w // 3,     eye_y, WHITE)
        pyxel.pset(x + 2 * w // 3, eye_y, WHITE)
        # 脚
        lw = max(1, w // (legs * 2))
        lh = h - body_h
        for i in range(legs):
            lx = x + int(w * (i + 0.5) / legs) - lw // 2
            pyxel.rect(lx, y + body_h, lw, lh, WHITE)

    # --------------------------------------------------------
    # ヘルパー: ボタン描画 / クリック判定
    # --------------------------------------------------------
    def _draw_btn(self, x, y, w, h, label, bg, fg=WHITE):
        pyxel.rect(x, y, w, h, bg)
        pyxel.rectb(x, y, w, h, WHITE)
        tx = x + (w - len(label) * 4) // 2
        ty = y + (h - 5) // 2
        pyxel.text(tx, ty, label, fg)

    def _clicked(self, x, y, w, h):
        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            mx, my = pyxel.mouse_x, pyxel.mouse_y
            return x <= mx < x + w and y <= my < y + h
        return False


# ============================================================
TsuruKame()
