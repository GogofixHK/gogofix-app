#!/usr/bin/env python3.11
"""
GoGofix 品牌宣传海报 — 1080×1440px
简洁有力，白底黑字+金色点缀，适合店面张贴和社交媒体
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
OUT_DIR   = "/workspace"
W, H      = 1080, 1440

WHITE       = (255, 255, 255)
BLACK       = (10,  10,  18)
ACCENT_GOLD = (190, 150, 50)
GOLD_LIGHT  = (212, 175, 83)
DARK_BG     = (16,  16,  28)
GRAY1       = (100, 100, 110)
GRAY_LIGHT  = (235, 235, 240)
RED_ACCENT  = (220, 40,  40)

def font(size, bold=True):
    f = FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(f, size)

def tw(draw, txt, fnt):
    bb = draw.textbbox((0,0), txt, font=fnt)
    return bb[2]-bb[0]

def cx(draw, txt, fnt, y, color=BLACK, img=None):
    x = (W - tw(draw, txt, fnt)) // 2
    draw.text((x, y), txt, fill=color, font=fnt)

def make_poster():
    img = Image.new("RGB", (W, H), WHITE)
    d   = ImageDraw.Draw(img)

    # ── 顶部黑色header区 ────────────────────────────────
    d.rectangle([(0,0),(W, 340)], fill=DARK_BG)

    # 金色顶线
    d.rectangle([(0,0),(W,6)], fill=GOLD_LIGHT)

    # GOGOFIX
    f_logo = font(110)
    logo_w = tw(d, "GOGOFIX", f_logo)
    d.text(((W-logo_w)//2+3, 38), "GOGOFIX", fill=(0,0,0), font=f_logo)
    d.text(((W-logo_w)//2, 35), "GOGOFIX", fill=GOLD_LIGHT, font=f_logo)

    # 副标题
    f_sub = font(28, bold=False)
    sub = "手機維修專門店  ·  PHONE REPAIR SPECIALIST"
    cx(d, sub, f_sub, 168, color=(180,175,160))

    # 底部金线
    d.rectangle([(60,218),(W-60,220)], fill=GOLD_LIGHT)

    # 卖点大字
    f_hero = font(44)
    cx(d, "快 · 靚 · 正", f_hero, 236, color=WHITE)

    # ── 核心三大亮点区 ───────────────────────────────────
    y_cards = 360
    cards = [
        ("30分鐘", "快速維修",  "大部分維修即日完成\n無需等候"),
        ("品質零件", "正品保障", "Refox / Rewa\n專業維修零件"),
        ("透明報價", "誠信服務", "網上即時查價\n無隱藏收費"),
    ]
    card_w = 310
    gaps   = [40, 385, 730]

    for i, (big, title, desc) in enumerate(cards):
        x = gaps[i]
        # 卡片底色
        d.rounded_rectangle([(x, y_cards), (x+card_w, y_cards+280)],
                             radius=18, fill=GRAY_LIGHT)
        # 金色顶条
        d.rounded_rectangle([(x, y_cards), (x+card_w, y_cards+6)],
                             radius=18, fill=GOLD_LIGHT)
        # 大数字/词
        f_big = font(52)
        bw = tw(d, big, f_big)
        d.text((x+(card_w-bw)//2, y_cards+20), big, fill=DARK_BG, font=f_big)
        # 标题
        f_ct = font(30)
        ctw = tw(d, title, f_ct)
        d.text((x+(card_w-ctw)//2, y_cards+90), title, fill=ACCENT_GOLD, font=f_ct)
        # 分割线
        d.line([(x+30, y_cards+134),(x+card_w-30, y_cards+134)], fill=(200,195,185), width=1)
        # 描述
        f_desc = font(22, bold=False)
        for j, line in enumerate(desc.split("\n")):
            lw = tw(d, line, f_desc)
            d.text((x+(card_w-lw)//2, y_cards+148+j*34), line, fill=GRAY1, font=f_desc)

    # ── 服务网格 ─────────────────────────────────────────
    y_grid = y_cards + 310
    d.rectangle([(0, y_grid-16),(W, y_grid-14)], fill=GOLD_LIGHT)

    f_sec = font(32)
    cx(d, "全面維修服務  一站式解決", f_sec, y_grid+2, color=DARK_BG)

    services = [
        "換屏幕", "換電池", "水浸維修", "換充電口",
        "換鏡頭", "換聽筒", "換背蓋",  "軟體解鎖",
        "平板維修","Switch維修",
    ]
    f_srv = font(26)
    srv_w = 220
    srv_h = 60
    srv_cols = 4
    srv_x0 = 44
    srv_y0 = y_grid + 58

    for idx, svc in enumerate(services):
        col = idx % srv_cols
        row = idx // srv_cols
        sx = srv_x0 + col * (srv_w + 14)
        sy = srv_y0 + row * (srv_h + 12)
        d.rounded_rectangle([(sx, sy),(sx+srv_w, sy+srv_h)],
                             radius=12, fill=DARK_BG)
        sw = tw(d, svc, f_srv)
        d.text((sx+(srv_w-sw)//2, sy+14), svc, fill=WHITE, font=f_srv)

    # ── 郵寄維修 横幅 ─────────────────────────────────────
    y_mail = srv_y0 + 3*(srv_h+12) + 16
    d.rounded_rectangle([(44, y_mail),(W-44, y_mail+80)],
                        radius=14, fill=(220,245,220))
    d.rounded_rectangle([(44, y_mail),(W-44, y_mail+4)],
                        radius=14, fill=(52,199,89))
    f_mail = font(30)
    mail_txt = "全港郵寄維修  — 快遞上門取送，足不出戶"
    mw = tw(d, mail_txt, f_mail)
    d.text(((W-mw)//2, y_mail+22), mail_txt, fill=(20,80,40), font=f_mail)

    # ── 联系区 ──────────────────────────────────────────
    y_contact = y_mail + 106
    d.rectangle([(0, y_contact),(W, H)], fill=DARK_BG)
    d.rectangle([(0, y_contact),(W, y_contact+4)], fill=GOLD_LIGHT)

    # 电话
    f_tel = font(68)
    tel = "5238  2777"
    telw = tw(d, tel, f_tel)
    d.text(((W-telw)//2, y_contact+28), tel, fill=WHITE, font=f_tel)

    f_label = font(26, bold=False)
    cx(d, "WhatsApp / 電話  即時查詢", f_label, y_contact+108, color=(160,155,145))

    # 网址
    f_url = font(30)
    url = "gogofixhk.com"
    uw = tw(d, url, f_url)
    d.text(((W-uw)//2, y_contact+152), url, fill=GOLD_LIGHT, font=f_url)

    # 营业时间
    f_hours = font(24, bold=False)
    cx(d, "每日 12:30 – 20:30", f_hours, y_contact+200, color=(130,125,115))

    # QR 码
    try:
        qr_src = "/workspace/gogofix_app/static/img/contact_qr.png"
        qr = Image.open(qr_src).convert("RGBA")
        qw, qh = qr.size
        wa_qr = qr.crop((qw//2, 0, qw, qh//2))
        wa_qr = wa_qr.resize((160, 160), Image.LANCZOS)
        img.paste(wa_qr, (W//2-80, y_contact+240), wa_qr)
        f_qr = font(20, bold=False)
        cx(d, "掃碼 WhatsApp 即時預約", f_qr, y_contact+412, color=(150,145,135))
    except Exception as e:
        print(f"QR 失敗: {e}")

    # 底部金线
    d.rectangle([(0, H-6),(W, H)], fill=GOLD_LIGHT)

    out = os.path.join(OUT_DIR, "gogofix_poster.png")
    img.save(out, "PNG", dpi=(150,150))
    print(f"海報已保存: {out} ({os.path.getsize(out)//1024}KB)")

if __name__ == "__main__":
    make_poster()
