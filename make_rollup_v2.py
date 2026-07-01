#!/usr/bin/env python3.11
"""
GoGofix 易拉架 — Léselle 极简风格
纯白背景 / 深黑文字 / 超细分隔线 / 近乎平面
800×2000px  — 修复底部文字溢出
"""
from PIL import Image, ImageDraw, ImageFont
import os

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
OUT       = "/workspace/gogofix_rollup.png"
W, H      = 800, 2000

# ── 网站 Léselle 配色 ──────────────────────────────────
BG      = (255,255,255)
ACCENT  = (26, 26, 26)
TEXT2   = (142,142,147)
TEXT3   = (199,199,204)
SEP     = (230,230,230)
ACC_L   = (240,240,240)

def f(s, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, s)

def tw(d,txt,fn): bb=d.textbbox((0,0),txt,font=fn); return bb[2]-bb[0]
def cx(d,txt,fn,y,color=ACCENT): x=(W-tw(d,txt,fn))//2; d.text((x,y),txt,fill=color,font=fn)
def line(d,y,lx=40,rx=760,color=SEP,w=1): d.line([(lx,y),(rx,y)],fill=color,width=w)

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
    ("Switch 維修","遊戲機",150,  680),
]

img = Image.new("RGB", (W,H), BG)
d   = ImageDraw.Draw(img)

# ── 顶部品牌 ────────────────────────────────────────
y = 44
f_logo = f(64); lw = tw(d, "GOGOFIX", f_logo)
d.text(((W-lw)//2, y), "GOGOFIX", fill=ACCENT, font=f_logo)
y += 88

f_sub = f(20, False); cx(d, "手機維修專門店", f_sub, y, TEXT2)
y += 36
line(d, y, lx=100, rx=700)
y += 28

# ── 标语 ────────────────────────────────────────────
f_tag = f(28); cx(d, "快 · 靚 · 正  一站式手機服務", f_tag, y, ACCENT)
y += 52
line(d, y, lx=60, rx=740)
y += 28

# ── 价目表标题 ──────────────────────────────────────
f_sec = f(24); cx(d, "維修服務價目表", f_sec, y, ACCENT)
y += 44

# 表头
f_hdr = f(16, False)
d.text((60, y), "服務項目", fill=TEXT2, font=f_hdr)
d.text((380, y), "類型", fill=TEXT2, font=f_hdr)
d.text((520, y), "價格 (HK$)", fill=TEXT2, font=f_hdr)
y += 24
line(d, y, lx=40, rx=760, color=SEP, w=1)
y += 12

# ── 价目行 ──────────────────────────────────────────
f_name  = f(24)
f_type  = f(18, False)
f_price = f(22)
row_h   = 88

for i, (name, dtype, pmin, pmax) in enumerate(SERVICES):
    if i % 2 == 0:
        d.rounded_rectangle([(44, y-2), (756, y+row_h-12)], radius=8, fill=ACC_L)
    # 服务名
    d.text((60, y+6), name, fill=ACCENT, font=f_name)
    # 类型标签
    type_c = {"手機":(245,245,248), "平板":(235,248,235), "遊戲機":(248,240,255)}
    tc = type_c.get(dtype, ACC_L)
    ttw = tw(d, dtype, f_type) + 14
    d.rounded_rectangle([(376, y+8), (376+ttw, y+30)], radius=5, fill=tc)
    d.text((383, y+10), dtype, fill=TEXT2, font=f_type)
    # 价格
    ps = f"${pmin} – ${pmax}"
    pw = tw(d, ps, f_price)
    d.text((756-pw, y+10), ps, fill=ACCENT, font=f_price)
    # 备注
    notes = {
        "換屏幕":"多種屏幕等級可選",
        "水浸維修":"視損壞程度報價",
        "軟體維修/解鎖":"純服務費，不含零件",
        "Switch 維修":"Joy-Con / 屏幕 / 主板",
    }
    note = notes.get(name, "零件費 + $300 服務費")
    f_note = f(16, False)
    d.text((60, y+44), note, fill=TEXT2, font=f_note)

    y += row_h
    line(d, y-10, lx=40, rx=760, color=SEP)

y += 10

# ── 功能卖点 ────────────────────────────────────────
line(d, y, lx=60, rx=740, color=SEP, w=1)
y += 18

highlights = [
    ("30分鐘快修", "即日完成"),
    ("品質零件", "Refox / Rewa"),
    ("透明報價", "網上即時查價"),
    ("郵寄維修", "全港到府取送"),
]
f_hl_t = f(20); f_hl_s = f(16, False)
hxs = [50, 250, 450, 630]
hw  = 170

for i, (t, s) in enumerate(highlights):
    x = hxs[i]
    d.rounded_rectangle([(x, y), (x+hw, y+60)], radius=10, outline=SEP, width=1)
    tw_ = tw(d, t, f_hl_t); d.text((x+(hw-tw_)//2, y+6), t, fill=ACCENT, font=f_hl_t)
    sw_ = tw(d, s, f_hl_s); d.text((x+(hw-sw_)//2, y+32), s, fill=TEXT2, font=f_hl_s)

y += 84
line(d, y, lx=60, rx=740, color=SEP)
y += 24

# ── 联系信息 ────────────────────────────────────────
f_hours = f(20, False); cx(d, "營業時間：每日 12:30 – 20:30", f_hours, y, TEXT2)
y += 36

f_tel = f(48); tel = "5238 2777"; tlw = tw(d, tel, f_tel)
d.text(((W-tlw)//2, y), tel, fill=ACCENT, font=f_tel)
y += 62

f_tell = f(20, False); cx(d, "WhatsApp / 電話 即時查詢", f_tell, y, TEXT2)
y += 34

f_url = f(22, False); cx(d, "gogofixhk.com", f_url, y, TEXT2)
y += 36

# QR 码
QR_Y = y  # 记录 QR 区域起始位置
try:
    qr_src = "/workspace/gogofix_app/static/img/contact_qr.png"
    qr = Image.open(qr_src).convert("RGBA")
    qw, qh = qr.size
    wa = qr.crop((qw//2, 0, qw, qh//2)).resize((160,160), Image.LANCZOS)
    img.paste(wa, (W//2-80, y), wa)
    y += 174
    f_qr = f(16, False); cx(d, "掃碼 WhatsApp 即時查詢", f_qr, y, TEXT3)
except Exception as e:
    print(f"QR码加载失败: {e}")

# 底部
y += 40
line(d, y, lx=60, rx=740, color=SEP)
y += 20
cx(d, "GoGofix 手機維修專門店", f(18, False), y, TEXT3)

print(f"总内容高度: y={y}px / 画布高度: {H}px")
if y > H:
    print(f"⚠️  警告：内容超出画布 {y - H}px！")
else:
    print(f"✅ 内容在画布内，剩余空间: {H - y}px")

img.save(OUT, "PNG", dpi=(150,150))
print(f"易拉架已保存: {OUT} ({os.path.getsize(OUT)//1024}KB)")
