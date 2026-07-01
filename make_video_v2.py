#!/usr/bin/env python3.11
"""
GoGofix 宣传短片 — Léselle 极简风格
纯白背景 / 深黑文字 / 超细分隔线 / 干净动画
1080×1920px · 15秒 · 30fps
"""
import os, subprocess, shutil
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG  = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FRAMES_DIR = "/tmp/gogofix_frames_v2"
OUT = "/workspace/gogofix_ad.mp4"
W, H = 1080, 1920
FPS = 30
TOTAL = 450

BG   = (255,255,255)
ACC  = (26,26,26)
T2   = (142,142,147)
T3   = (199,199,204)
SEP  = (230,230,230)
GREEN = (52,199,89)

os.makedirs(FRAMES_DIR, exist_ok=True)

def ft(s,b=True): return ImageFont.truetype(FONT_BOLD if b else FONT_REG,s)
def tw(d,t,f): bb=d.textbbox((0,0),t,font=f); return bb[2]-bb[0]
def cx(d,t,f,y,c=ACC): x=(W-tw(d,t,f))//2; d.text((x,y),t,fill=c,font=f)
def eo(t): return 1-(1-min(1,max(0,t)))**3
def ln(d,y,a=1.0):
    c = tuple(int(SEP[i]*a + BG[i]*(1-a)) for i in range(3))
    d.line([(80,y),(W-80,y)],fill=c,width=1)

print("渲染 450 帧...")
for fi in range(TOTAL):
    ts = fi/FPS
    img = Image.new("RGB",(W,H),BG)
    d = ImageDraw.Draw(img)

    # ── 顶部细线 ──
    d.rectangle([(0,0),(W,2)],fill=(int(ACC[0]*0.1),)*3)  # 几乎不可见

    if ts < 3:  # Scene 1: 品牌
        t = fi/90; a = eo(t*2)
        off = int(80*(1-a))
        fl = ft(150); lw = tw(d,"GOGOFIX",fl)
        ac = tuple(int(ACC[i]*a + BG[i]*(1-a)) for i in range(3))
        d.text(((W-lw)//2, H//2-240+off), "GOGOFIX", fill=ac, font=fl)
        if t > 0.5:
            a2 = eo((t-0.5)*2)
            cx(d,"手機維修專門店",ft(32,False),H//2-52,c=tuple(int(T2[i]*a2+BG[i]*(1-a2)) for i in range(3)))
            cx(d,"PHONE REPAIR SPECIALIST",ft(26,False),H//2+10,c=tuple(int(T3[i]*a2+BG[i]*(1-a2)) for i in range(3)))
            ln(d,H//2+56,a=a2*0.5)
        if t > 0.75:
            a3 = eo((t-0.75)*4)
            cx(d,"快 · 靚 · 正  一站式手機服務",ft(44),H//2+120,c=tuple(int(ACC[i]*a3+BG[i]*(1-a3)) for i in range(3)))

    elif ts < 7:  # Scene 2: 卖点
        t = (fi-90)/120
        # 小 logo
        fl = ft(60); lw = tw(d,"GOGOFIX",fl)
        d.text(((W-lw)//2,50),"GOGOFIX",fill=ACC,font=fl)
        ln(d,134,a=0.5)

        pts = [
            ("快","約30分鐘快修","大部分維修即日完成"),
            ("靚","品質保證零件","Refox / Rewa 正品"),
            ("正","透明誠信報價","網上即時查價"),
        ]
        for i,(big,title,sub) in enumerate(pts):
            dl = i*0.28; a = eo(max(0,t-dl)*3.5); off2 = int(60*(1-a))
            yb = 190 + i*520; ch = 440
            # 卡片
            bo = tuple(int(SEP[j]*a+BG[j]*(1-a)) for j in range(3))
            d.rounded_rectangle([(80,yb-off2),(W-80,yb+ch-off2)],radius=24,outline=bo,width=1)
            # 左边条
            lbc = tuple(int(ACC[j]*a*0.08+BG[j]*(1-a)) for j in range(3))
            d.rounded_rectangle([(80,yb-off2),(112,yb+ch-off2)],radius=12,fill=lbc)
            # 大字
            fb = ft(140); bw = tw(d,big,fb)
            bc = tuple(int(ACC[j]*a+BG[j]*(1-a)) for j in range(3))
            d.text(((W-bw)//2, yb+15-off2), big, fill=bc, font=fb)
            # 标题
            fti = ft(48); ttw = tw(d,title,fti)
            tc = tuple(int(ACC[j]*a+BG[j]*(1-a)) for j in range(3))
            d.text(((W-ttw)//2, yb+190-off2), title, fill=tc, font=fti)
            # 副标题
            fsu = ft(32,False); stw = tw(d,sub,fsu)
            sc = tuple(int(T2[j]*a+BG[j]*(1-a)) for j in range(3))
            d.text(((W-stw)//2, yb+256-off2), sub, fill=sc, font=fsu)

    elif ts < 11:  # Scene 3: 服务
        t = (fi-210)/120
        cx(d,"全面維修服務",ft(56),80,c=ACC)
        cx(d,"一站式解決 · 全港郵寄上門",ft(32,False),156,c=T2)
        ln(d,214,a=0.5)
        svcs = [
            ("換屏幕","$480–$1150"),("換電池","$380–$550"),
            ("水浸維修","$500–$850"),("換充電口","$360–$450"),
            ("換鏡頭","$420–$650"),("換聽筒","$350–$430"),
            ("換背蓋","$380–$520"),("軟體解鎖","$250–$450"),
            ("平板換屏","$580–$1050"),("Switch維修","$150–$680"),
        ]
        fn_ = ft(40); fp_ = ft(34)
        for i,(nm,pr) in enumerate(svcs):
            a = eo(max(0,t-i*0.065)*5); off3 = int(50*(1-a))
            y_ = 240 + i*158
            bc = tuple(int((242,242,242)[j]*a+BG[j]*(1-a)) for j in range(3))
            d.rounded_rectangle([(80,y_+off3),(W-80,y_+138+off3)],radius=14,fill=bc)
            nc = tuple(int(ACC[j]*a+BG[j]*(1-a)) for j in range(3))
            pc = tuple(int(ACC[j]*a+BG[j]*(1-a)) for j in range(3))
            d.text((110,y_+44+off3),nm,fill=nc,font=fn_)
            pw = tw(d,pr,fp_); d.text((W-110-pw,y_+46+off3),pr,fill=pc,font=fp_)

    elif ts < 14:  # Scene 4: CTA
        t = (fi-330)/90; a = eo(t*2.5)
        cx(d,"立即預約維修",ft(64),160,c=tuple(int(ACC[i]*a+BG[i]*(1-a)) for i in range(3)))
        ln(d,260,a=a*0.5)
        ftel = ft(108); tel = "5238 2777"; tw_ = tw(d,tel,ftel)
        d.text(((W-tw_)//2,290),tel,fill=tuple(int(ACC[i]*a+BG[i]*(1-a)) for i in range(3)),font=ftel)
        cx(d,"WhatsApp / 電話 即時查詢",ft(34,False),430,c=tuple(int(T2[i]*a+BG[i]*(1-a)) for i in range(3)))
        ln(d,500,a=a*0.4)
        items = [
            "約30分鐘快修",
            "品質零件 · 透明報價",
            "全港郵寄維修 足不出戶",
            "每日 12:30 – 20:30 營業",
        ]
        for i,item in enumerate(items):
            ia = eo(max(0,t-0.3-i*0.08)*3)
            cy2 = 540 + i*100
            gc = tuple(int(GREEN[j]*ia+BG[j]*(1-ia)) for j in range(3))
            d.ellipse([(108,cy2+16),(140,cy2+48)],fill=gc)
            d.text((168,cy2),item,fill=tuple(int(ACC[j]*ia+BG[j]*(1-ia)) for j in range(3)),font=ft(38,False))
        if t > 0.65:
            a3 = eo((t-0.65)*3)
            ln(d,980,a=a3*0.6)
            cx(d,"gogofixhk.com",ft(44),1000,c=tuple(int(ACC[j]*a3+BG[j]*(1-a3)) for j in range(3)))
        if t > 0.75:
            a4 = eo((t-0.75)*4)
            try:
                qr = Image.open("/workspace/gogofix_app/static/img/contact_qr.png").convert("RGBA")
                qw,qh = qr.size; wa = qr.crop((qw//2,0,qw,qh//2)).resize((240,240),Image.LANCZOS)
                ql = Image.new("RGBA",(W,H),(0,0,0,0)); ql.paste(wa,((W-240)//2,1080),wa)
                img = Image.blend(img, ql.convert("RGB"), a4*0.9)
                d = ImageDraw.Draw(img)
                cx(d,"掃碼 WhatsApp 即時查詢",ft(28,False),1338,c=tuple(int(T3[j]*a4+BG[j]*(1-a4)) for j in range(3)))
            except: pass

    else:  # Scene 5: 收尾
        t = (fi-420)/30
        fin = eo(t*2) * (1-eo(max(0,t-0.7)*3))
        fl = ft(150); lw = tw(d,"GOGOFIX",fl)
        gc2 = tuple(int(ACC[i]*fin+BG[i]*(1-fin)) for i in range(3))
        d.text(((W-lw)//2,H//2-120),"GOGOFIX",fill=gc2,font=fl)
        cx(d,"手機維修專門店",ft(38,False),H//2+60,c=tuple(int(T2[j]*fin+BG[j]*(1-fin)) for j in range(3)))
        cx(d,"gogofixhk.com",ft(34,False),H//2+130,c=tuple(int(ACC[j]*fin*0.7+BG[j]*(1-fin)) for j in range(3)))

    img.save(f"{FRAMES_DIR}/frame_{fi:04d}.png")
    if fi % 90 == 0: print(f"  帧{fi}/{TOTAL} ({ts:.0f}s)")

print("合成 MP4...")
r = subprocess.run([
    "ffmpeg","-y","-framerate","30","-i",f"{FRAMES_DIR}/frame_%04d.png",
    "-c:v","mpeg4","-q:v","3","-pix_fmt","yuv420p",OUT
], capture_output=True, text=True)
if r.returncode != 0:
    print("ffmpeg 错误:", r.stderr[-300:])
else:
    print(f"视频已保存: {OUT} ({os.path.getsize(OUT)//1024}KB)")
shutil.rmtree(FRAMES_DIR)
print("完成！")
