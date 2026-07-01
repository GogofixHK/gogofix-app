#!/usr/bin/env python3.11
"""
GoGofix 宣传短片 — 1080×1920px，15秒，30fps = 450帧
竖屏 9:16，适合 IG/FB Reels、WhatsApp Status
场景切换：
  Scene 1 (0-3s):   品牌开场，GOGOFIX 大字渐入
  Scene 2 (3-7s):   三大卖点逐一弹出（快/靚/正）
  Scene 3 (7-11s):  服务列表滚动展示
  Scene 4 (11-14s): 联系信息 + 行动呼吁
  Scene 5 (14-15s): GOGOFIX 收尾
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, math, subprocess, shutil, tempfile

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FRAMES_DIR = tempfile.mkdtemp(prefix="gogofix_frames_")
OUT_FILE   = "/workspace/gogofix_ad.mp4"
W, H = 1080, 1920
FPS  = 30
TOTAL_FRAMES = FPS * 15  # 450

# 调色板
BG_DARK     = (10,  10,  18)
GOLD        = (212, 175, 83)
GOLD_LITE   = (255, 220, 120)
WHITE       = (255, 255, 255)
GRAY1       = (170, 165, 155)
GRAY2       = (90,  88,  95)
GREEN       = (52,  199, 89)
CARD        = (22,  22,  36)

def fnt(size, bold=True):
    return ImageFont.truetype(FONT_BOLD if bold else FONT_REG, size)

def tw(d, txt, f):
    bb = d.textbbox((0,0), txt, font=f)
    return bb[2]-bb[0]

def th(d, txt, f):
    bb = d.textbbox((0,0), txt, font=f)
    return bb[3]-bb[1]

def cx(d, txt, f, y, color=WHITE, alpha=1.0):
    x = (W - tw(d, txt, f)) // 2
    # simulate alpha by blending with dark bg
    r,g,b = color
    r2,g2,b2 = BG_DARK
    r = int(r*alpha + r2*(1-alpha))
    g = int(g*alpha + g2*(1-alpha))
    b = int(b*alpha + b2*(1-alpha))
    d.text((x, y), txt, fill=(r,g,b), font=f)

def easeout(t):  # t in [0,1]
    return 1 - (1-t)**3

def easein(t):
    return t**2

def make_base_img():
    img = Image.new("RGB", (W, H), BG_DARK)
    d = ImageDraw.Draw(img)
    # 顶部金光晕
    for r in range(500, 0, -4):
        alpha = int(18 * (1 - r/500))
        c = (
            min(255, BG_DARK[0] + int((GOLD[0]-BG_DARK[0]) * alpha/18)),
            min(255, BG_DARK[1] + int((GOLD[1]-BG_DARK[1]) * alpha/18)),
            min(255, BG_DARK[2] + int((GOLD[2]-BG_DARK[2]) * alpha/18)),
        )
        d.ellipse([(W//2-r, -200), (W//2+r, r-80)], fill=c)
    return img

def draw_gold_line(d, y, alpha=1.0):
    c = tuple(int(GOLD[i]*alpha + BG_DARK[i]*(1-alpha)) for i in range(3))
    d.line([(80, y), (W-80, y)], fill=c, width=2)

# ── 场景帧函数 ──────────────────────────────────────────

def scene1(f, total=90):
    """0-3s: GOGOFIX 渐入 + 副标题"""
    t = f / total
    img = make_base_img()
    d = ImageDraw.Draw(img)

    # 金色顶线 渐入
    line_a = easeout(min(1, t*3))
    draw_gold_line(d, 6, alpha=line_a)
    d.rectangle([(0,0),(W,6)], fill=tuple(int(GOLD[i]*line_a) for i in range(3)))

    # GOGOFIX 大字 从下飞入
    a = easeout(min(1, t*2))
    offset = int(120 * (1-a))
    f_logo = fnt(160)
    logo_txt = "GOGOFIX"
    lw = tw(d, logo_txt, f_logo)
    y_logo = int(H//2 - 220 + offset)
    # 模糊效果
    if a < 0.95:
        tmp = Image.new("RGB", (W, H), BG_DARK)
        td = ImageDraw.Draw(tmp)
        td.text(((W-lw)//2, y_logo), logo_txt, fill=GOLD, font=f_logo)
        tmp = tmp.filter(ImageFilter.GaussianBlur(radius=int(8*(1-a))+1))
        img = Image.blend(img, tmp, a*0.6)
        d = ImageDraw.Draw(img)
    d.text(((W-lw)//2, y_logo), logo_txt, fill=GOLD, font=f_logo)

    # 副标题渐入
    if t > 0.5:
        a2 = easeout((t-0.5)*2)
        f_sub = fnt(34, bold=False)
        sub = "手機維修專門店"
        cx(d, sub, f_sub, H//2-20, color=GRAY1, alpha=a2)
        f_sub2 = fnt(28, bold=False)
        cx(d, "PHONE REPAIR SPECIALIST", f_sub2, H//2+36, color=GRAY2, alpha=a2)
        draw_gold_line(d, H//2+90, alpha=a2*0.5)

    # 底部金线
    d.rectangle([(0,H-6),(W,H)], fill=tuple(int(GOLD[i]*line_a) for i in range(3)))
    return img

def scene2(f, total=120):
    """3-7s: 快·靚·正 逐一弹出"""
    t = f / total
    img = make_base_img()
    d = ImageDraw.Draw(img)
    d.rectangle([(0,0),(W,6)], fill=GOLD)
    d.rectangle([(0,H-6),(W,H)], fill=GOLD)

    # 顶部小logo
    f_logo_s = fnt(72)
    lw = tw(d, "GOGOFIX", f_logo_s)
    d.text(((W-lw)//2, 60), "GOGOFIX", fill=GOLD, font=f_logo_s)
    draw_gold_line(d, 160)

    # 三大卖点
    points = [
        ("快", "約30分鐘快修",  "大部分維修即日完成"),
        ("靚", "品質保證零件",  "Refox / Rewa 正品"),
        ("正", "透明誠信報價",  "網上即時查價"),
    ]
    for i, (big, title, sub) in enumerate(points):
        delay = i * 0.28
        if t < delay:
            continue
        a = easeout(min(1, (t-delay)*3.5))
        offset = int(80*(1-a))

        y_base = 260 + i * 420
        # 卡片
        card_y = y_base - offset
        c_a = tuple(int(CARD[j]*a + BG_DARK[j]*(1-a)) for j in range(3))
        d.rounded_rectangle([(80, card_y), (W-80, card_y+360)],
                             radius=24, fill=c_a)
        # 金色左边条
        bar_c = tuple(int(GOLD[j]*a) for j in range(3))
        d.rounded_rectangle([(80, card_y), (108, card_y+360)],
                             radius=12, fill=bar_c)

        # 大字
        f_big = fnt(140)
        bw = tw(d, big, f_big)
        bc = tuple(int(GOLD_LITE[j]*a + BG_DARK[j]*(1-a)) for j in range(3))
        d.text(((W-bw)//2, card_y+20), big, fill=bc, font=f_big)

        # 标题
        f_title = fnt(46)
        tc = tuple(int(WHITE[j]*a + BG_DARK[j]*(1-a)) for j in range(3))
        ttw = tw(d, title, f_title)
        d.text(((W-ttw)//2, card_y+178), title, fill=tc, font=f_title)

        # 副标题
        f_sub = fnt(32, bold=False)
        sc = tuple(int(GRAY1[j]*a + BG_DARK[j]*(1-a)) for j in range(3))
        stw = tw(d, sub, f_sub)
        d.text(((W-stw)//2, card_y+240), sub, fill=sc, font=f_sub)

    return img

def scene3(f, total=120):
    """7-11s: 服务列表 滚动展示"""
    t = f / total
    img = make_base_img()
    d = ImageDraw.Draw(img)
    d.rectangle([(0,0),(W,6)], fill=GOLD)
    d.rectangle([(0,H-6),(W,H)], fill=GOLD)

    # 标题
    f_sec = fnt(52)
    a_sec = easeout(min(1, t*4))
    cx(d, "全面維修服務", f_sec, 80, color=WHITE, alpha=a_sec)
    f_sub = fnt(34, bold=False)
    cx(d, "一站式解決  · 全港郵寄上門", f_sub, 152, color=GRAY1, alpha=a_sec)
    draw_gold_line(d, 210, alpha=a_sec)

    services = [
        ("換屏幕",    "$480 – $1150"),
        ("換電池",    "$380 – $550"),
        ("水浸維修",  "$500 – $850"),
        ("換充電口",  "$360 – $450"),
        ("換鏡頭",    "$420 – $650"),
        ("換聽筒/喇叭","$350 – $430"),
        ("換玻璃背蓋","$380 – $520"),
        ("軟體維修",  "$250 – $450"),
        ("平板換屏",  "$580 – $1050"),
        ("Switch維修","$150 – $680"),
    ]
    f_name  = fnt(40)
    f_price = fnt(36)
    row_h = 150
    y0 = 240

    for i, (name, price) in enumerate(services):
        delay = i * 0.06
        if t < delay:
            break
        a = easeout(min(1, (t-delay)*5))
        slide = int(60*(1-a))

        y = y0 + i*row_h
        # 行底
        c_bg = tuple(int(CARD[j]*a) for j in range(3))
        d.rounded_rectangle([(80, y+slide), (W-80, y+row_h-8+slide)],
                             radius=14, fill=c_bg)
        # 分割线
        lc = tuple(int(GOLD[j]*a*0.3) for j in range(3))
        d.line([(100, y+row_h-10+slide), (W-100, y+row_h-10+slide)], fill=lc, width=1)

        nc = tuple(int(WHITE[j]*a) for j in range(3))
        pc = tuple(int(GOLD_LITE[j]*a) for j in range(3))
        d.text((110, y+row_h//2-22+slide), name,  fill=nc, font=f_name)
        pw = tw(d, price, f_price)
        d.text((W-100-pw, y+row_h//2-18+slide), price, fill=pc, font=f_price)

    return img

def scene4(f, total=90):
    """11-14s: 联系信息"""
    t = f / total
    img = make_base_img()
    d = ImageDraw.Draw(img)
    d.rectangle([(0,0),(W,6)], fill=GOLD)
    d.rectangle([(0,H-6),(W,H)], fill=GOLD)

    a_all = easeout(min(1, t*2.5))

    # 立即预约
    f_cta = fnt(64)
    cx(d, "立即預約維修", f_cta, 180, color=GOLD_LITE, alpha=a_all)

    draw_gold_line(d, 280, alpha=a_all*0.6)

    # 电话大字
    f_tel = fnt(120)
    tel = "5238 2777"
    telw = tw(d, tel, f_tel)
    tc = tuple(int(WHITE[j]*a_all + BG_DARK[j]*(1-a_all)) for j in range(3))
    d.text(((W-telw)//2, 340), tel, fill=tc, font=f_tel)

    f_label = fnt(36, bold=False)
    cx(d, "WhatsApp / 電話 即時查詢", f_label, 492, color=GRAY1, alpha=a_all)

    draw_gold_line(d, 570, alpha=a_all*0.4)

    # 亮点列表
    if t > 0.3:
        a2 = easeout(min(1, (t-0.3)*2.5))
        items = [
            "約30分鐘快修",
            "品質零件  · 透明報價",
            "全港郵寄維修  足不出戶",
            "每日 12:30 – 20:30 營業",
        ]
        f_item = fnt(38, bold=False)
        for i, item in enumerate(items):
            ia = easeout(min(1, max(0, (t-0.3-i*0.08)*3)))
            cy_item = 620 + i*100
            # 圆点
            dot_c = tuple(int(GREEN[j]*ia) for j in range(3))
            d.ellipse([(130, cy_item+14), (158, cy_item+42)], fill=dot_c)
            ic = tuple(int(WHITE[j]*ia + BG_DARK[j]*(1-ia)) for j in range(3))
            d.text((178, cy_item), item, fill=ic, font=f_item)

    # 网址
    if t > 0.65:
        a3 = easeout(min(1, (t-0.65)*3))
        draw_gold_line(d, 1060, alpha=a3*0.6)
        f_url = fnt(44)
        cx(d, "gogofixhk.com", f_url, 1080, color=GOLD, alpha=a3)

    # 加载 QR 码
    if t > 0.75:
        a4 = easeout(min(1, (t-0.75)*4))
        try:
            qr_src = "/workspace/gogofix_app/static/img/contact_qr.png"
            qr = Image.open(qr_src).convert("RGBA")
            qw, qh = qr.size
            wa_qr = qr.crop((qw//2, 0, qw, qh//2)).resize((260,260), Image.LANCZOS)
            qr_layer = Image.new("RGBA", (W,H), (0,0,0,0))
            qr_layer.paste(wa_qr, ((W-260)//2, 1160), wa_qr)
            qr_rgb = qr_layer.convert("RGB")
            img = Image.blend(img, qr_rgb, a4*0.95)
            d = ImageDraw.Draw(img)
            f_qr = fnt(28, bold=False)
            cx(d, "掃碼 WhatsApp 即時查詢", f_qr, 1440, color=GRAY1, alpha=a4)
        except:
            pass

    return img

def scene5(f, total=30):
    """14-15s: 收尾 GOGOFIX"""
    t = f / total
    img = make_base_img()
    d = ImageDraw.Draw(img)
    a = easeout(min(1, t*2))
    da = 1 - easeout(min(1, max(0, (t-0.7)*3)))
    final_a = a * da if t > 0.7 else a

    d.rectangle([(0,0),(W,6)], fill=tuple(int(GOLD[i]*final_a) for i in range(3)))
    d.rectangle([(0,H-6),(W,H)], fill=tuple(int(GOLD[i]*final_a) for i in range(3)))

    f_logo = fnt(160)
    logo_txt = "GOGOFIX"
    lw = tw(d, logo_txt, f_logo)
    gc = tuple(int(GOLD[i]*final_a) for i in range(3))
    d.text(((W-lw)//2, H//2-120), logo_txt, fill=gc, font=f_logo)
    f_sub = fnt(38, bold=False)
    cx(d, "手機維修專門店", f_sub, H//2+60, color=GRAY1, alpha=final_a)
    f_url = fnt(34, bold=False)
    cx(d, "gogofixhk.com", f_url, H//2+130, color=GOLD, alpha=final_a*0.8)
    return img

# ── 主渲染循环 ──────────────────────────────────────────
print(f"开始渲染 {TOTAL_FRAMES} 帧...")
for frame_idx in range(TOTAL_FRAMES):
    t_sec = frame_idx / FPS
    # 场景分配
    if t_sec < 3:
        img = scene1(frame_idx, total=90)
    elif t_sec < 7:
        img = scene2(frame_idx - 90, total=120)
    elif t_sec < 11:
        img = scene3(frame_idx - 210, total=120)
    elif t_sec < 14:
        img = scene4(frame_idx - 330, total=90)
    else:
        img = scene5(frame_idx - 420, total=30)

    img.save(os.path.join(FRAMES_DIR, f"frame_{frame_idx:04d}.png"))
    if frame_idx % 90 == 0:
        print(f"  帧 {frame_idx}/{TOTAL_FRAMES}  ({t_sec:.1f}s)")

print("帧渲染完成，开始合成视频...")

# ── 用 ffmpeg 合成 MP4 ──────────────────────────────────
cmd = [
    "ffmpeg", "-y",
    "-framerate", str(FPS),
    "-i", os.path.join(FRAMES_DIR, "frame_%04d.png"),
    "-c:v", "libx264",
    "-profile:v", "high",
    "-crf", "20",
    "-pix_fmt", "yuv420p",
    "-movflags", "+faststart",
    OUT_FILE
]
result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print("ffmpeg 错误:", result.stderr[-500:])
else:
    size = os.path.getsize(OUT_FILE)
    print(f"视频已保存: {OUT_FILE}  ({size//1024}KB)")

shutil.rmtree(FRAMES_DIR)
print("完成！")
