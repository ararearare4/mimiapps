import pyxel
import random

# ============================================================
# SPACE TSURUKAME - Pyxel版
# ============================================================

W, H = 160, 240

BLACK  = 0
NAVY   = 1
RED    = 8
ORANGE = 9
YELLOW = 10
GREEN  = 11
CYAN   = 12
BLUE   = 13
PINK   = 14
WHITE  = 7
DGRAY  = 5

CHARACTERS = [
    {"id": "2legs", "name": "2HONA", "color": RED,    "legs": 2},
    {"id": "3legs", "name": "3HONA", "color": CYAN,   "legs": 3},
    {"id": "4legs", "name": "4HONA", "color": PINK,   "legs": 4},
    {"id": "5legs", "name": "5HONA", "color": ORANGE, "legs": 5},
]

# --- レイアウト定数 ---
HDR_H    = 38              # ヘッダー高さ
AREA_Y   = HDR_H + 2      # モンスターエリア上端 = 40
BODY_H   = 20              # ボディ高さ (脚より大きく)
LEG_W    = 2               # 脚の幅 (px)
LEG_H    = 8               # 脚の高さ (短め)
LEG_Y    = AREA_Y + BODY_H # 脚の上端 = 60
MSG_Y    = LEG_Y + LEG_H + 3   # = 71
MSG_H    = 12
INPUT_Y  = MSG_Y + MSG_H + 3   # = 86


class TsuruKame:
    def __init__(self):
        pyxel.init(W, H, title="SPACE TSURUKAME", fps=30)
        pyxel.mouse(True)
        self._setup_sounds()
        self._reset()
        pyxel.run(self.update, self.draw)

    def _reset(self):
        self.state      = "title"
        self.stage      = 1
        self.problem    = None
        self.user_ans   = [0, 0]
        self.sel        = 0
        self.is_correct = False
        self.message    = ""
        self.frame      = 0
        self.timer      = 0
        self.cover_off  = 0

    def _setup_sounds(self):
        pyxel.sound(0).set("c3e3g3c4",      "s", "5543",   "nnnn",   12)
        pyxel.sound(1).set("g4",            "s", "4",      "n",       8)
        pyxel.sound(2).set("c4e4g4c4",      "s", "4444",   "nnnn",   10)
        pyxel.sound(3).set("b2a2f2",        "s", "444",    "nnn",     8)
        pyxel.sound(4).set("c4c4c4e4g4c4", "s", "444446", "nnnnnn", 10)

    def _gen_problem(self, stage):
        if stage == 1:
            ca, cb = CHARACTERS[0], CHARACTERS[2]
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
        self.sel        = 0
        self.is_correct = False
        self.message    = ""
        self.timer      = 0
        self.cover_off  = 0
        self.state      = "animating"

    # --------------------------------------------------------
    # 更新
    # --------------------------------------------------------
    def update(self):
        self.frame += 1
        self.timer += 1

        if self.state == "title":
            if (self._clicked(W//2 - 32, 185, 64, 18) or
                    self._any_start_btn()):
                pyxel.play(0, 0)
                self.stage = 1
                self._gen_problem(1)

        elif self.state == "animating":
            if self.timer >= 60:
                self.state   = "playing"
                self.timer   = 0
                self.message = ("ダレガ ナンビキ？" if self.stage >= 3
                                else "イロデ カゾエヨウ！")

        elif self.state == "playing":
            self._handle_play_input()

        elif self.state == "result":
            if self.is_correct and self.cover_off > -(BODY_H + 2):
                self.cover_off -= 2
            if self.timer >= 105:
                if self.stage >= 3:
                    pyxel.play(0, 4)
                    self.state = "clear"
                    self.timer = 0
                else:
                    self.stage += 1
                    self._gen_problem(self.stage)

        elif self.state == "clear":
            if (self._clicked(W//2 - 32, 195, 64, 18) or
                    self._any_start_btn()):
                self._reset()

    def _any_start_btn(self):
        """タイトル/クリア画面の決定操作"""
        return (pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A) or
                pyxel.btnp(pyxel.KEY_A) or
                pyxel.btnp(pyxel.KEY_SPACE) or
                pyxel.btnp(pyxel.KEY_RETURN))

    def _handle_play_input(self):
        # ゲームパッド
        gp_left  = pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_LEFT)
        gp_right = pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_RIGHT)
        gp_up    = pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_UP)
        gp_down  = pyxel.btnp(pyxel.GAMEPAD1_BUTTON_DPAD_DOWN)
        gp_ok    = pyxel.btnp(pyxel.GAMEPAD1_BUTTON_A)

        # キーボード
        kb_left  = pyxel.btnp(pyxel.KEY_LEFT)
        kb_right = pyxel.btnp(pyxel.KEY_RIGHT)
        kb_up    = pyxel.btnp(pyxel.KEY_UP)
        kb_down  = pyxel.btnp(pyxel.KEY_DOWN)
        kb_ok    = (pyxel.btnp(pyxel.KEY_A) or
                    pyxel.btnp(pyxel.KEY_SPACE) or
                    pyxel.btnp(pyxel.KEY_RETURN))

        if gp_left or kb_left:
            self.sel = (self.sel - 1) % 2
            pyxel.play(0, 1)
        if gp_right or kb_right:
            self.sel = (self.sel + 1) % 2
            pyxel.play(0, 1)
        if gp_up or kb_up:
            self.user_ans[self.sel] += 1
            pyxel.play(0, 1)
        if gp_down or kb_down:
            self.user_ans[self.sel] = max(0, self.user_ans[self.sel] - 1)
            pyxel.play(0, 1)
        if gp_ok or kb_ok:
            self._check()

        # タップでキャラ選択 (パネルをタップ)
        for i in range(2):
            if self._clicked(4 + i * 78, INPUT_Y, 72, 68):
                self.sel = i
        # 決定ボタンタップ
        if self._clicked(20, INPUT_Y + 74, W - 40, 16):
            self._check()

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

    def _draw_title(self):
        pyxel.text(W//2 - 20, 18, "SPACE",     YELLOW)
        pyxel.text(W//2 - 36, 28, "TSURUKAME", YELLOW)
        pyxel.text(W//2 - 32, 42, "3 STAGES TO CLEAR", CYAN)
        for i, c in enumerate(CHARACTERS):
            bob = abs((self.frame + i * 8) % 20 - 10)
            x   = 18 + i * 35
            y   = 80 - bob
            mw  = c["legs"] * 5 + 4
            self._draw_monster(x, y, mw, 20, c["color"], c["legs"])
        btn_col = RED if self.frame % 30 < 15 else ORANGE
        self._draw_btn(W//2 - 32, 185, 64, 18, "START GAME", btn_col)
        pyxel.text(W//2 - 44, 208, "A/SPC/ENTER OR TAP", DGRAY)

    def _draw_game(self):
        p = self.problem

        # ヘッダー
        pyxel.rect(0, 0, W, HDR_H, NAVY)
        pyxel.text(4, 4, f"STAGE {self.stage}", WHITE)
        if self.stage >= 3:
            col = YELLOW if self.frame % 20 < 10 else ORANGE
            pyxel.text(60, 4, "CHALLENGE!", col)
        cur_heads = self.user_ans[0] + self.user_ans[1]
        cur_legs  = (self.user_ans[0] * p["chars"][0]["legs"] +
                     self.user_ans[1] * p["chars"][1]["legs"])
        hcol = GREEN if cur_heads == p["total_heads"] else WHITE
        lcol = GREEN if cur_legs  == p["total_legs"]  else WHITE
        pyxel.text(4,  20, f"HEADS:{cur_heads}/{p['total_heads']}", hcol)
        pyxel.text(82, 20, f"LEGS:{cur_legs}/{p['total_legs']}",   lcol)
        pyxel.line(0, HDR_H, W, HDR_H, BLUE)

        self._draw_stage_area(p)

        # メッセージバー
        pyxel.rect(0, MSG_Y, W, MSG_H, DGRAY)
        msg_col = GREEN if self.is_correct else YELLOW
        mx = max(2, W//2 - len(self.message) * 2)
        pyxel.text(mx, MSG_Y + 3, self.message, msg_col)

        if self.state in ("playing", "result"):
            self._draw_input(p)

    def _draw_stage_area(self, p):
        """ボディ + 脚(常に表示・色変化) + カバー"""
        chars      = p["chars"]
        counts     = p["counts"]
        total_legs = p["total_legs"]
        is_ch      = self.stage >= 3

        # 脚1本あたりの幅を動的に決定 (モンスターが画面に収まるよう)
        leg_slot = max(3, min(6, (W - 8) // total_legs))
        total_w  = total_legs * leg_slot
        sx       = (W - total_w) // 2

        # 脚の色判定 (元ゲームと同ロジック)
        left_limit  = self.user_ans[0] * chars[0]["legs"]
        right_limit = total_legs - self.user_ans[1] * chars[1]["legs"]

        # ボディ描画
        lo = 0
        for ci, char in enumerate(chars):
            for _ in range(counts[ci]):
                bx = sx + lo * leg_slot
                bw = char["legs"] * leg_slot - 1
                pyxel.rect(bx, AREA_Y, bw, BODY_H, char["color"])
                eye_y = AREA_Y + 6
                pyxel.pset(bx + bw // 3,     eye_y, WHITE)
                pyxel.pset(bx + 2 * bw // 3, eye_y, WHITE)
                lo += char["legs"]

        # 脚描画 (常に見える・色がヒント)
        for li in range(total_legs):
            lx = sx + li * leg_slot
            if not is_ch:
                if li < left_limit:
                    col = chars[0]["color"]
                elif li >= right_limit:
                    col = chars[1]["color"]
                else:
                    col = WHITE
            else:
                col = WHITE
            pyxel.rect(lx, LEG_Y, LEG_W, LEG_H, col)

        # 区切り線
        pyxel.line(0, LEG_Y + LEG_H, W, LEG_Y + LEG_H, BLUE)

        # カバー (ボディ部分のみ・スライドアップで開く)
        cover_top = AREA_Y + self.cover_off
        vis_top   = max(cover_top, AREA_Y)
        vis_bot   = min(cover_top + BODY_H, AREA_Y + BODY_H)
        vis_h     = vis_bot - vis_top
        if vis_h > 0:
            pyxel.rect(0, vis_top, W, vis_h, NAVY)
            if vis_h >= 6:
                text_y = vis_top + vis_h // 2 - 3
                if self.state == "animating":
                    dots = "." * ((self.timer // 10) % 4)
                    pyxel.text(W//2 - 16, text_y, f"WAIT{dots}", CYAN)
                else:
                    pyxel.text(W//2 - 8, text_y, "???", CYAN)
            if cover_top + BODY_H <= AREA_Y + BODY_H:
                pyxel.line(0, cover_top + BODY_H, W, cover_top + BODY_H, BLUE)

    def _draw_input(self, p):
        """キャラ選択パネル (ボタンなし・ゲームパッド/キーボード操作)"""
        active = self.state == "playing"
        for i, char in enumerate(p["chars"]):
            bx = 4 + i * 78

            border_col = char["color"] if (i == self.sel and active) else DGRAY
            pyxel.rect(bx, INPUT_Y, 72, 68, DGRAY)
            pyxel.rectb(bx, INPUT_Y, 72, 68, border_col)

            # 選択インジケーター
            if i == self.sel and active:
                pyxel.text(bx + 20, INPUT_Y + 2, "* SEL *", border_col)

            # ミニモンスター (入力パネルと同スタイル)
            mw = char["legs"] * 4 + 2
            self._draw_monster(bx + 4, INPUT_Y + 12, mw, 16,
                               char["color"], char["legs"])

            # キャラ名
            pyxel.text(bx + 4, INPUT_Y + 30, char["name"], char["color"])

            # カウント (枠付きで中央に)
            pyxel.rect(bx + 22, INPUT_Y + 40, 24, 16, BLACK)
            pyxel.rectb(bx + 22, INPUT_Y + 40, 24, 16, border_col)
            count_str = str(self.user_ans[i])
            cx = bx + 34 - len(count_str) * 2
            pyxel.text(cx, INPUT_Y + 45, count_str, WHITE)

        # 決定ボタン
        kok_col = YELLOW if active else DGRAY
        kok_fg  = BLACK  if active else WHITE
        self._draw_btn(20, INPUT_Y + 74, W - 40, 16, "KOKODA! [A]", kok_col, kok_fg)

        # 操作ヒント
        if active:
            pyxel.text(6, INPUT_Y + 94, "<>:SEL  ^v:COUNT  A:OK", DGRAY)

    def _draw_clear(self):
        pyxel.text(W//2 - 44, 30, "CONGRATULATIONS!", YELLOW)
        pyxel.text(W//2 - 24, 44, "ALL CLEAR!!", GREEN)
        for i, c in enumerate(CHARACTERS):
            bob = abs((self.frame + i * 7) % 18 - 9)
            x   = 14 + i * 35
            y   = 90 - bob
            mw  = c["legs"] * 5 + 4
            self._draw_monster(x, y, mw, 20, c["color"], c["legs"])
        pyxel.text(W//2 - 52, 135, "YOU ARE TSURUKAME MASTER!", CYAN)
        self._draw_btn(W//2 - 32, 195, 64, 18, "PLAY AGAIN", BLUE)
        pyxel.text(W//2 - 44, 218, "A/SPC/ENTER OR TAP", DGRAY)

    # --------------------------------------------------------
    # ヘルパー
    # --------------------------------------------------------
    def _draw_monster(self, x, y, w, h, color, legs):
        body_h = max(4, int(h * 0.65))
        pyxel.rect(x, y, w, body_h, color)
        eye_y = y + max(1, body_h // 3)
        pyxel.pset(x + w // 3,     eye_y, WHITE)
        pyxel.pset(x + 2 * w // 3, eye_y, WHITE)
        lw = max(1, w // (legs * 2))
        lh = h - body_h
        for i in range(legs):
            lx = x + int(w * (i + 0.5) / legs) - lw // 2
            pyxel.rect(lx, y + body_h, lw, lh, WHITE)

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
