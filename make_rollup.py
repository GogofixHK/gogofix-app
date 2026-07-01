#!/usr/bin/env python3.11
"""
GoGofix 易拉架 — 800×2000px
深色 + 金色强调，专业维修价目表风格
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math

FONT_BOLD   = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG    = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
OUT_DIR     = "/workspace"
W, H        = 800, 2000

# ── 调色板 ──────────────────────────────────────────────
BG          = (10, 10, 18)        # 近黑背景
ACCENT_GOLD = (212, 175, 83)      # 金色
ACCENT_LITE = (255, 220, 120)     # 亮金
WHITE       = (255, 255, 255)
GRAY1       = (180, 180, 185)
GRAY2       = (90,  90, 100)
CARD_BG     = (22,  22, 35)
CARD_BOR    = (50,  50, 70)
GREEN       = (52, 199, 89)

def font(size, bold=True):
    f = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(f, size)

def text_w(draw, txt, fnt):
    bb = draw.textbbox((0,0), txt, font=fnt)
    return bb[2] - bb[0]

def center_text(draw, txt, fnt, y, color=WHITE):
    x = (W - text_w(draw, txt, fnt)) // 2
    draw.text((x, y), txt, fill=color, font=fnt)

def draw_line(draw, y, lx=40, rx=760, color=CARD_BOR, width=1):
    draw.line([(lx, y), (rx, y)], fill=color, width=width)

# ── 渐变背景 ────────────────────────────────────────────
def make_bg():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # 顶部金色光晕
    for r in range(300, 0, -1):
        alpha = int(30 * (1 - r/300))
        c = tuple(min(255, BG[i] + int((ACCENT_GOLD[i]-BG[i]) * alpha/30)) for i in range(3))
        d.ellipse([(W//2-r, -r//2), (W//2+r, r//2+100)], fill=c)
    return img

# ── 服务数据 ─────────────────────────────────────────────
SERVICES = [
    ("換屏幕",   "手機",   480,  1150),
    ("換電池",   "手機",   380,   550),
    ("水浸維修", "手機",   500,   850),
    ("換充電口", "手機",   360,   450),
    ("換鏡頭",   "手機",   420,   650),
    ("換聽筒/喇叭","手機", 350,   430),
    ("換玻璃背蓋","手機",  380,   520),
    ("軟體維修/解鎖","手機",250,  450),
    ("換顯示屏", "平板",   580,  1050),
    ("Switch 維修","遊戲機",150,   680),
]

def make_rollup():
    img = make_bg()
    d = ImageDraw.Draw(img)

    # ── 顶部 LOGO 区 ─────────────────────────────
    # 金色装饰横线
    d.rectangle([(0, 0), (W, 6)], fill=ACCENT_GOLD)

    # GOGOFIX 大字
    f_logo = font(88)
    lw = text_w(d, "GOGOFIX", f_logo)
    # 文字阴影
    d.text(((W-lw)//2+3, 33), "GOGOFIX", fill=(0,0,0,120), font=f_logo)
    d.text(((W-lw)//2, 30), "GOGOFIX", fill=ACCENT_GOLD, font=f_logo)

    # 副标题
    f_sub = font(26, bold=False)
    sub = "手機維修專門店  ·  PHONE REPAIR SPECIALIST"
    center_text(d, sub, f_sub, 128, color=GRAY1)

    # 金色细分隔线
    draw_line(d, 170, lx=60, rx=740, color=ACCENT_GOLD, width=1)

    # ── 标语 ─────────────────────────────────────
    f_tag = font(34)
    center_text(d, "快 · 靚 · 正  一站式手機服務", f_tag, 188, color=WHITE)

    draw_line(d, 240, lx=60, rx=740, color=CARD_BOR)

    # ── 价目表标题 ───────────────────────────────
    f_sec = font(30)
    center_text(d, "維修服務價目表", f_sec, 256, color=ACCENT_GOLD)

    # 表头
    f_hdr = font(20)
    d.text((60,  300), "服務項目", fill=GRAY1, font=f_hdr)
    d.text((390, 300), "類型",     fill=GRAY1, font=f_hdr)
    d.text((510, 300), "價格 (HK$)", fill=GRAY1, font=f_hdr)
    draw_line(d, 328, lx=40, rx=760, color=ACCENT_GOLD, width=1)

    # ── 价目列表 ─────────────────────────────────
    f_name = font(28)
    f_type = font(22, bold=False)
    f_price = font(26)
    row_h = 108
    y0 = 342

    for i, (name, dtype, pmin, pmax) in enumerate(SERVICES):
        y = y0 + i * row_h
        # 交替行底色
        if i % 2 == 0:
            d.rectangle([(40, y-6), (760, y+row_h-10)], fill=(28, 28, 42))

        # 服务名
        d.text((60, y+8), name, fill=WHITE, font=f_name)
        # 类型标签
        tag_color = {"手機":(40,80,160), "平板":(60,120,80), "遊戲機":(120,60,160)}
        tc = tag_color.get(dtype, (60,60,80))
        tw = text_w(d, dtype, f_type) + 16
        d.rounded_rectangle([(388, y+10), (388+tw, y+38)], radius=8, fill=tc)
        d.text((396, y+12), dtype, fill=WHITE, font=f_type)
        # 价格
        price_str = f"${pmin} – ${pmax}"
        pw = text_w(d, price_str, f_price)
        d.text((760-pw, y+12), price_str, fill=ACCENT_LITE, font=f_price)

        # 备注小字
        note_map = {
            "換屏幕":   "多種屏幕等級可選",
            "水浸維修": "視損壞程度報價",
            "軟體維修/解鎖": "純服務費，不含零件",
            "Switch 維修": "Joy-Con / 屏幕 / 主板",
        }
        note = note_map.get(name, "零件費 + $300 服務費")
        f_note = font(18, bold=False)
        d.text((60, y+46), note, fill=GRAY2, font=f_note)

        # 行分隔
        draw_line(d, y+row_h-12, lx=40, rx=760, color=CARD_BOR)

    # ── 底部功能卖点 ──────────────────────────────
    y_bot = y0 + len(SERVICES) * row_h + 20
    draw_line(d, y_bot, lx=40, rx=760, color=ACCENT_GOLD, width=1)

    highlights = [
        ("約30分鐘快修", "大部分維修即日完成"),
        ("品質零件",     "採用 Refox / Rewa"),
        ("透明報價",     "網上即時查價"),
        ("郵寄維修",     "到府取送，全港服務"),
    ]
    f_hl_title = font(24)
    f_hl_sub   = font(19, bold=False)
    hx = [60, 260, 460, 640]
    hy = y_bot + 20
    box_w = 175

    for i, (t, s) in enumerate(highlights):
        x = hx[i]
        # 小方块
        d.rounded_rectangle([(x, hy), (x+box_w, hy+72)], radius=10,
                             fill=CARD_BG, outline=ACCENT_GOLD, width=1)
        d.text((x+10, hy+8),  t, fill=ACCENT_LITE, font=f_hl_title)
        d.text((x+10, hy+38), s, fill=GRAY1,        font=f_hl_sub)

    # ── 联系信息 ──────────────────────────────────
    y_contact = hy + 100
    draw_line(d, y_contact, lx=40, rx=760, color=CARD_BOR)

    # 营业时间
    f_info = font(24, bold=False)
    f_info_b = font(26)
    center_text(d, "營業時間：每日 12:30 – 20:30", f_info, y_contact+18, color=GRAY1)

    # 电话大字
    f_tel = font(52)
    center_text(d, "5238 2777", f_tel, y_contact+56, color=WHITE)

    f_tel_label = font(22, bold=False)
    center_text(d, "WhatsApp / 電話  ·  即時查詢", f_tel_label, y_contact+118, color=GRAY1)

    # 网站
    f_web = font(22, bold=False)
    center_text(d, "www.gogofixhk.com", f_web, y_contact+152, color=ACCENT_GOLD)

    # 底部金线
    d.rectangle([(0, H-6), (W, H)], fill=ACCENT_GOLD)

    # ── 导入联系二维码 ────────────────────────────
    try:
        qr_src = "/workspace/gogofix_app/static/img/contact_qr.png"
        qr = Image.open(qr_src).convert("RGBA")
        # 裁出右半（WhatsApp QR）
        qw, qh = qr.size
        wa_qr = qr.crop((qw//2, 0, qw, qh//2))
        wa_qr = wa_qr.resize((160, 160), Image.LANCZOS)
        img.paste(wa_qr, (W//2-80, y_contact+188), wa_qr)
        f_qr = font(18, bold=False)
        center_text(d, "掃碼 WhatsApp 即時查詢", f_qr, y_contact+356, color=GRAY1)
    except Exception as e:
        print(f"QR 載入失敗: {e}")

    img.save(os.path.join(OUT_DIR, "gogofix_rollup.png"), "PNG", dpi=(150,150))
    print(f"易拉架已保存: {OUT_DIR}/gogofix_rollup.png ({os.path.getsize(OUT_DIR+'/gogofix_rollup.png')//1024}KB)")

if __name__ == "__main__":
    make_rollup()
