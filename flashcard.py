"""
单词闪卡 - Flashcard Vocabulary App
用法: python flashcard.py
支持翻页笔 (PageDown/PageUp) 和鼠标点击操作

文件格式 (CSV 或 TXT):
  英文单词,中文释义
  或: 英文单词[Tab]中文释义
"""

import tkinter as tk
import random
from tkinter import filedialog, messagebox


class FlashcardApp:
    # ── 颜色主题 ──────────────────────────────────────────────
    BG       = '#1a1a2e'
    CARD_BG  = '#16213e'
    FG       = '#e8e8e8'
    ANSWER   = '#e94560'
    BTN_BG   = '#0f3460'
    DIM      = '#555566'

    def __init__(self):
        self.root = tk.Tk()
        self.root.title('单词闪卡')
        self.root.configure(bg=self.BG)
        self.root.attributes('-fullscreen', True)

        self.cards   = []   # 全部导入的 (word, meaning)
        self.deck    = []   # 本轮打乱后的列表
        self.idx     = 0
        self.flipped = False
        self.mode    = 'home'

        self._bind_keys()
        self._show_home()
        self.root.mainloop()

    # ── 按键绑定 ──────────────────────────────────────────────
    def _bind_keys(self):
        root = self.root
        root.bind('<Escape>',  self._esc)
        root.bind('<F11>',     lambda e: root.attributes('-fullscreen',
                               not root.attributes('-fullscreen')))
        # 前进: 点击、空格、回车、翻页笔 PageDown / 右方向键
        root.bind('<Button-1>', self._on_click)
        root.bind('<space>',    self._on_key)
        root.bind('<Return>',   self._on_key)
        root.bind('<Next>',     self._on_key)   # PageDown
        root.bind('<Right>',    self._on_key)
        # 后退: 翻页笔 PageUp / 左方向键
        root.bind('<Prior>',    self._go_prev)  # PageUp
        root.bind('<Left>',     self._go_prev)

    def _esc(self, _=None):
        if self.mode == 'study':
            self._show_home()
        else:
            self.root.attributes('-fullscreen', False)

    def _on_click(self, event=None):
        if self.mode != 'study':
            return
        # 忽略左上角主页按钮区域的点击（避免误触后仍触发翻牌）
        if event and event.x < 160 and event.y < 60:
            return
        self._advance()

    def _on_key(self, _=None):
        if self.mode == 'study':
            self._advance()

    def _advance(self):
        if not self.flipped:
            self._flip()
        else:
            self._go_next()

    # ── 清屏工具 ──────────────────────────────────────────────
    def _clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    # ── 主页 ──────────────────────────────────────────────────
    def _show_home(self):
        self.mode = 'home'
        self._clear()
        self.root.configure(bg=self.BG)

        center = tk.Frame(self.root, bg=self.BG)
        center.place(relx=.5, rely=.46, anchor=tk.CENTER)

        tk.Label(center, text='单词闪卡',
                 font=('Microsoft YaHei', 56, 'bold'),
                 bg=self.BG, fg=self.FG).pack(pady=(0, 6))

        if self.cards:
            tk.Label(center, text=f'已加载  {len(self.cards)}  个单词',
                     font=('Microsoft YaHei', 20),
                     bg=self.BG, fg=self.DIM).pack(pady=(0, 30))
        else:
            tk.Label(center, text='请先导入单词文件',
                     font=('Microsoft YaHei', 20),
                     bg=self.BG, fg=self.DIM).pack(pady=(0, 30))

        row = tk.Frame(center, bg=self.BG)
        row.pack()

        self._btn(row, '导入单词', self._import, '#0f3460').pack(side=tk.LEFT, padx=12)
        if self.cards:
            self._btn(row, '开始学习', self._start, '#c0392b').pack(side=tk.LEFT, padx=12)

        tk.Label(center,
                 text='文件格式：每行  英文单词,中文释义  或  英文单词[Tab]中文释义',
                 font=('Microsoft YaHei', 13),
                 bg=self.BG, fg=self.DIM).pack(pady=(36, 0))

        tk.Label(self.root,
                 text='ESC 返回 / F11 切换全屏',
                 font=('Microsoft YaHei', 12),
                 bg=self.BG, fg='#333344').place(relx=.5, rely=.96, anchor=tk.CENTER)

    # ── 导入文件 ──────────────────────────────────────────────
    def _import(self):
        path = filedialog.askopenfilename(
            title='选择单词文件',
            filetypes=[('支持格式', '*.csv *.txt'), ('所有文件', '*.*')]
        )
        if not path:
            return

        cards = []
        try:
            with open(path, encoding='utf-8-sig') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    sep = '\t' if '\t' in line else ','
                    parts = line.split(sep, 1)
                    if len(parts) == 2:
                        w, m = parts[0].strip(), parts[1].strip()
                        if w and m:
                            cards.append((w, m))
        except Exception as exc:
            messagebox.showerror('读取失败', str(exc))
            return

        if not cards:
            messagebox.showerror('格式错误',
                '未找到有效单词。\n每行格式：英文单词,中文释义')
            return

        self.cards = cards
        messagebox.showinfo('导入成功', f'成功导入 {len(cards)} 个单词！')
        self._show_home()

    # ── 开始学习 ──────────────────────────────────────────────
    def _start(self):
        self.deck = self.cards.copy()
        random.shuffle(self.deck)
        self.idx     = 0
        self.flipped = False
        self._build_study_ui()

    def _build_study_ui(self):
        self.mode = 'study'
        self._clear()
        self.root.configure(bg=self.BG)

        # 进度
        self._progress_var = tk.StringVar()
        tk.Label(self.root, textvariable=self._progress_var,
                 font=('Microsoft YaHei', 18),
                 bg=self.BG, fg=self.DIM).place(relx=.5, rely=.07, anchor=tk.CENTER)

        # 主页按钮
        self._btn(self.root, '← 主页', self._show_home, self.BG,
                  fg=self.DIM, font_size=15).place(x=24, y=18)

        # 卡片
        card = tk.Frame(self.root, bg=self.CARD_BG)
        card.place(relx=.5, rely=.5, anchor=tk.CENTER,
                   relwidth=.76, relheight=.64)

        # 分隔线（默认隐藏）
        self._sep = tk.Frame(card, bg='#2a2a4a', height=2)

        self._word_lbl = tk.Label(card,
                                  font=('Georgia', 70, 'bold'),
                                  bg=self.CARD_BG, fg=self.FG,
                                  wraplength=1100, justify=tk.CENTER)
        self._word_lbl.place(relx=.5, rely=.38, anchor=tk.CENTER)

        self._ans_lbl = tk.Label(card,
                                 font=('Microsoft YaHei', 44),
                                 bg=self.CARD_BG, fg=self.ANSWER,
                                 wraplength=1100, justify=tk.CENTER)
        self._ans_lbl.place(relx=.5, rely=.70, anchor=tk.CENTER)

        # 提示
        self._hint_var = tk.StringVar()
        tk.Label(self.root, textvariable=self._hint_var,
                 font=('Microsoft YaHei', 15),
                 bg=self.BG, fg=self.DIM).place(relx=.5, rely=.90, anchor=tk.CENTER)

        self._show_card()

    # ── 卡片操作 ──────────────────────────────────────────────
    def _show_card(self):
        self.flipped = False
        word, _ = self.deck[self.idx]
        self._word_lbl.config(text=word)
        self._ans_lbl.config(text='')
        self._sep.place_forget()
        self._hint_var.set('点击屏幕 / 空格 / 翻页键  ▶  查看中文')
        self._update_progress()

    def _flip(self):
        self.flipped = True
        _, meaning = self.deck[self.idx]
        self._ans_lbl.config(text=meaning)
        self._sep.place(relx=.05, rely=.56, relwidth=.9, height=2)
        self._hint_var.set('再次点击 / 按键  ▶  下一个单词')

    def _go_next(self, _=None):
        self.idx += 1
        if self.idx >= len(self.deck):
            self._show_done()
        else:
            self._show_card()

    def _go_prev(self, _=None):
        if self.mode != 'study':
            return
        if self.idx > 0:
            self.idx -= 1
        self._show_card()

    def _update_progress(self):
        self._progress_var.set(f'{self.idx + 1}  /  {len(self.deck)}')

    # ── 完成页 ────────────────────────────────────────────────
    def _show_done(self):
        self.mode = 'done'
        self._clear()
        self.root.configure(bg=self.BG)

        center = tk.Frame(self.root, bg=self.BG)
        center.place(relx=.5, rely=.46, anchor=tk.CENTER)

        tk.Label(center, text='全部完成！',
                 font=('Microsoft YaHei', 58, 'bold'),
                 bg=self.BG, fg='#2ecc71').pack(pady=(0, 10))
        tk.Label(center, text=f'本轮共学习  {len(self.deck)}  个单词',
                 font=('Microsoft YaHei', 24),
                 bg=self.BG, fg=self.FG).pack(pady=(0, 40))

        row = tk.Frame(center, bg=self.BG)
        row.pack()
        self._btn(row, '再来一遍', self._start,    '#c0392b').pack(side=tk.LEFT, padx=14)
        self._btn(row, '回到主页', self._show_home, '#0f3460').pack(side=tk.LEFT, padx=14)

    # ── 通用按钮工厂 ──────────────────────────────────────────
    def _btn(self, parent, text, cmd, bg, fg=None, font_size=20):
        return tk.Button(parent, text=text,
                         font=('Microsoft YaHei', font_size),
                         bg=bg, fg=fg or self.FG,
                         activebackground=bg, activeforeground=fg or self.FG,
                         relief=tk.FLAT, bd=0,
                         padx=28, pady=12,
                         cursor='hand2',
                         command=cmd)


if __name__ == '__main__':
    FlashcardApp()
