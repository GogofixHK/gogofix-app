#!/usr/bin/env python3.11
"""
GoGofix 宣传海报 — Léselle 极简风格
纯白背景 / 深黑文字 / 超细分隔线 / 近乎平面
1080×1440px  — 修复底部溢出
"""
from PIL import Image, ImageDraw, ImageFont
import os

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
OUT       = "/workspace/gogofix_poster.png"
W, H      = 1080, 1440

BG     = (255,255,255)
ACCENT = (26,26,26)
TEXT   = (26,26,26)
TEXT2  = (142,142,147)
TEXT3  = (199,199,204)
SEP    = (230,230,230)
ACC_L  = (242,242,242)
GREEN  = (52,199,89)

def f(s,b=True): return ImageFont.truetype(FONT_BOLD if b else FONT_REG,s)
def tw(d,txt,fn): bb=d.textbbox((0,0),txt,font=fn); return bb[2]-bb[0]
def cx(d,txt,fn,y,c=TEXT): x=(W-tw(d,txt,fn))//2; d.text((x,y),txt,fill=c,font=fn)
def ln(d,y,lx=40,rx=W-40,c=SEP,w=1): d.line([(lx,y),(rx,y)],fill=c,width=w)

img = Image.new("RGB",(W,H),BG)
d = ImageDraw.Draw(img)

# ── 顶部品牌 ──────────────────────────────────────
y = 56
f_logo = f(90); lw = tw(d,"GOGOFIX",f_logo)
d.text(((W-lw)//2,y),"GOGOFIX",fill=ACCENT,font=f_logo)
y += 114
f_sub = f(28,False); cx(d,"手機維修專門店  ·  PHONE REPAIR SPECIALIST",f_sub,y,TEXT2)
y += 46
ln(d,y,lx=140,rx=W-140,c=SEP,w=1)
y += 30

# ── 标语 ──────────────────────────────────────────
f_tag = f(42); cx(d,"快 · 靚 · 正",f_tag,y,ACCENT)
y += 56
f_tag2 = f(28,False); cx(d,"一站式手機服務",f_tag2,y,TEXT2)
y += 52
ln(d,y,lx=60,rx=W-60,c=SEP)
y += 34

# ── 三大卖点 ─────────────────────────────────────
cards = [
    ("30分鐘","快速維修","大部分維修\n即日完成"),
    ("品質","零件保證","Refox / Rewa\n正品零件"),
    ("透明","誠信報價","網上即時查價\n無隱藏收費"),
]
cw = 310; ch = 240; gaps = [40, 385, 730]
for i,(big,title,desc) in enumerate(cards):
    x = gaps[i]
    d.rounded_rectangle([(x,y),(x+cw,y+ch)],radius=16,outline=SEP,width=1)
    f_big = f(52); bw_ = tw(d,big,f_big); d.text((x+(cw-bw_)//2,y+16),big,fill=ACCENT,font=f_big)
    f_t = f(30); tw_ = tw(d,title,f_t); d.text((x+(cw-tw_)//2,y+86),title,fill=ACCENT,font=f_t)
    ln(d,y+126,lx=x+30,rx=x+cw-30,c=SEP)
    f_d = f(22,False)
    for j,line in enumerate(desc.split("\n")):
        lw2 = tw(d,line,f_d); d.text((x+(cw-lw2)//2,y+140+j*34),line,fill=TEXT2,font=f_d)

y += ch + 32

# ── 服务网格 ─────────────────────────────────────
ln(d,y,lx=60,rx=W-60,c=SEP,w=1)
y += 20
f_sec = f(32); cx(d,"全面維修服務  全港郵寄上門",f_sec,y,ACCENT)
y += 50

svcs = [
    "換屏幕","換電池","水浸維修","換充電口",
    "換鏡頭","換聽筒","換背蓋","軟體解鎖",
    "平板維修","Switch維修",
]
f_srv = f(26); sw = 240; sh = 56; cols = 4; x0 = 52
for idx,svc in enumerate(svcs):
    col = idx % cols; row = idx // cols
    sx = x0 + col*(sw+12); sy = y + row*(sh+10)
    d.rounded_rectangle([(sx,sy),(sx+sw,sy+sh)],radius=10,outline=SEP,width=1)
    sww = tw(d,svc,f_srv); d.text((sx+(sw-sww)//2,sy+12),svc,fill=ACCENT,font=f_srv)

y += 3*(sh+10) + 24

# ── 邮寄维修条 ───────────────────────────────────
d.rounded_rectangle([(52,y),(W-52,y+62)],radius=12,outline=SEP,width=1)
f_mail = f(28,False); mt="全港郵寄維修 — 快遞上門取送，足不出戶"; mw=tw(d,mt,f_mail)
d.text(((W-mw)//2,y+15),mt,fill=ACCENT,font=f_mail)

y += 84
ln(d,y,lx=60,rx=W-60,c=SEP,w=1)
y += 24

# ── 联系区 ───────────────────────────────────────
f_cta = f(44); cx(d,"立即預約維修",f_cta,y,ACCENT)
y += 60
f_tel = f(72); tel="5238 2777"; tw_=tw(d,tel,f_tel)
d.text(((W-tw_)//2,y),tel,fill=ACCENT,font=f_tel)
y += 86
f_lbl = f(26,False); cx(d,"WhatsApp / 電話  即時查詢",f_lbl,y,TEXT2)
y += 42
f_url = f(30,False); cx(d,"gogofixhk.com",f_url,y,TEXT2)
y += 44
f_hrs = f(22,False); cx(d,"每日 12:30 – 20:30",f_hrs,y,TEXT3)

# QR — 贴在右下角，不占用主流程的 y
try:
    qr_src="/workspace/gogofix_app/static/img/contact_qr.png"
    qr=Image.open(qr_src).convert("RGBA"); qw,qh=qr.size
    wa=qr.crop((qw//2,0,qw,qh//2)).resize((170,170),Image.LANCZOS)
    qx, qy = W - 220, H - 210
    img.paste(wa,(qx,qy),wa)
    f_qr=f(18,False); cx(d,"掃碼 WhatsApp 即時預約",f_qr,qy+174,TEXT3)
except Exception as e:
    print(f"QR码加载失败: {e}")

# 底部线
y += 46
ln(d,y,lx=60,rx=W-60,c=SEP,w=1)
y += 18
cx(d,"GoGofix 手機維修專門店",f(20,False),y,TEXT3)

print(f"总内容高度: y={y}px / 画布高度: {H}px")
if y > H:
    print(f"⚠️  警告：内容超出画布 {y - H}px！")
else:
    print(f"✅ 内容在画布内，剩余空间: {H - y}px")

img.save(OUT,"PNG",dpi=(150,150))
print(f"海報已保存: {OUT} ({os.path.getsize(OUT)//1024}KB)")
