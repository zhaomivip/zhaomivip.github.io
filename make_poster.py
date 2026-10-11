# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os, sys, glob

W,H = 1350,3150
BASE=os.path.dirname(os.path.abspath(__file__))
ASSETS=os.path.join(BASE,'assets')
SRC=os.path.join(ASSETS,'poster-bg-portrait2.jpg')
QR=os.path.join(ASSETS,'qr.png')
OUT=os.path.join(ASSETS,'poster_blackgold.jpg')

# 字体搜索路径（跨平台）：Linux / macOS / Windows 常见位置
FONT_DIRS=[
    '/usr/share/fonts/opentype/noto',
    '/usr/share/fonts/truetype/noto',
    '/usr/share/fonts/opentype',
    '/usr/share/fonts/truetype',
    '/System/Library/Fonts',
    '/Library/Fonts',
    'C:/Windows/Fonts',
]
def find_font(name):
    """在多个字体目录中查找字体文件，找不到则返回 None"""
    for d in FONT_DIRS:
        p=os.path.join(d,name)
        if os.path.isfile(p): return p
    # 递归兜底搜索
    for d in FONT_DIRS:
        for p in glob.glob(os.path.join(d,'**',name),recursive=True):
            if os.path.isfile(p): return p
    return None

CJK_MAP={'Black':'NotoSerifCJK-Black.ttc','Bold':'NotoSerifCJK-Bold.ttc','SemiBold':'NotoSerifCJK-SemiBold.ttc','Medium':'NotoSerifCJK-Medium.ttc','Regular':'NotoSerifCJK-Regular.ttc'}
SANS_MAP={'Regular':'NotoSansCJK-Regular.ttc','Medium':'NotoSansCJK-Medium.ttc','Bold':'NotoSansCJK-Bold.ttc'}
LATIN_MAP={'display':'NotoSerifDisplay-CondensedExtraBold.ttf','sans':'NotoSans-CondensedBold.ttf'}

def _load(size, name_map, weight):
    fn=name_map[weight]
    p=find_font(fn)
    if p: return ImageFont.truetype(p,size)
    # 降级：尝试任意 CJK 字体
    for cand in name_map.values():
        p=find_font(cand)
        if p: return ImageFont.truetype(p,size)
    # 最终降级到 PIL 默认
    print(f'[warn] 未找到字体 {fn}，使用默认字体', file=sys.stderr)
    return ImageFont.load_default()

def CJK(size,weight='Black'):  return _load(size,CJK_MAP,weight)
def SANS(size,weight='Regular'): return _load(size,SANS_MAP,weight)
def LATIN(size,style='display'): return _load(size,LATIN_MAP,style)

# 关键资源检查
for label,p in [('背景图',SRC),('二维码',QR)]:
    if not os.path.isfile(p):
        print(f'[error] 缺少{label}：{p}', file=sys.stderr); sys.exit(1)

GOLD_HI=(255,247,214); GOLD=(247,224,138); GOLD_DK=(138,109,31)
CREAM=(244,236,216); MUTED=(185,169,138); DIM=(92,80,64)

base=Image.open(SRC).convert('RGBA')
canvas=base.copy()
ov=Image.new('RGBA',(W,H),(8,6,3,120))
canvas=Image.alpha_composite(canvas,ov)
draw=ImageDraw.Draw(canvas,'RGBA')

def rrect(xy,r,fill=None,outline=None,w=0):
    draw.rounded_rectangle(xy,radius=r,fill=fill,outline=outline,width=w)

def gold_grad_text(text,font):
    big=Image.new('L',(4000,800),0); d=ImageDraw.Draw(big)
    d.text((60,60),text,font=font,fill=255)
    bb=big.getbbox() or (0,0,200,80)
    l,t,r,b2=bb; m=14
    l,t,r,b2=l-m,t-m,r+m,b2+m
    w,h=r-l,b2-t
    mask=big.crop((l,t,r,b2))
    grad=Image.new('RGBA',(w,h))
    for y in range(h):
        tt=y/max(h-1,1)
        cr=int(GOLD_HI[0]+(GOLD_DK[0]-GOLD_HI[0])*tt)
        cg=int(GOLD_HI[1]+(GOLD_DK[1]-GOLD_HI[1])*tt)
        cb=int(GOLD_HI[2]+(GOLD_DK[2]-GOLD_HI[2])*tt)
        ImageDraw.Draw(grad).line([(0,y),(w,y)],fill=(cr,cg,cb,255))
    grad.putalpha(mask)
    return grad

def gold_text(x,y,text,font,anchor='la'):
    g=gold_grad_text(text,font); w,h=g.size
    px,py={'la':(x,y),'ma':(x-w//2,y),'ra':(x-w,y),'lm':(x,y-h//2),'mm':(x-w//2,y-h//2),'rm':(x-w,y-h//2)}[anchor]
    canvas.alpha_composite(g,(int(px),int(py)))

def tsize(text,font):
    l,t,r,b=font.getbbox(text); return r-l, b-t

def txt(x,y,text,font,fill,anchor='la',shadow=False):
    if shadow: draw.text((x+2,y+2),text,font=font,fill=(0,0,0,140),anchor=anchor)
    draw.text((x,y),text,font=font,fill=fill,anchor=anchor)

CX=W//2

# ===== 标题区（放大）=====
ey='NOBILITAS · AURUM · NIGRA'
ef=LATIN(30,'display'); ew,eh=tsize(ey,ef)
ey_y=116
txt(CX,ey_y,ey,ef,GOLD,'ma')
draw.line([(CX-ew//2-50,ey_y+eh//2),(CX-ew//2-14,ey_y+eh//2)],fill=(212,175,55,200),width=2)
draw.line([(CX+ew//2+14,ey_y+eh//2),(CX+ew//2+50,ey_y+eh//2)],fill=(212,175,55,200),width=2)

title='着迷黑金贵族体系'
tf=CJK(140,'Black')
ty=ey_y+eh+22
# 标题字距（艺术化拉开）
SPACING=14
# 计算带字距的总宽
title_w=sum(tsize(ch,tf)[0] for ch in title)+SPACING*(len(title)-1)
tx0=CX-title_w//2
# 标题金色光晕
glow=Image.new('RGBA',(W,420),(0,0,0,0))
gd=ImageDraw.Draw(glow)
gx=tx0
for ch in title:
    cw,_=tsize(ch,tf)
    gd.text((gx,210-ty),ch,font=tf,fill=(212,175,55,130),anchor='la')
    gx+=cw+SPACING
glow=glow.filter(ImageFilter.GaussianBlur(24))
canvas.alpha_composite(glow,(0,ty-210))
# 逐字绘制：深色投影 + 金色描边 + 金色渐变填充
gx=tx0
for ch in title:
    cw,chh=tsize(ch,tf)
    ccx=gx+cw//2
    # 投影
    draw.text((ccx+3,ty+3),ch,font=tf,fill=(0,0,0,160),anchor='ma')
    # 金色描边
    draw.text((ccx,ty),ch,font=tf,fill=(255,238,168,0),anchor='ma',stroke_width=3,stroke_fill=(120,88,20,230))
    # 金色渐变填充
    gold_text(ccx,ty,ch,tf,'ma')
    gx+=cw+SPACING

sub='九阶黑金 · 逐档尊享'
sf=CJK(44,'SemiBold')
sub_sp=10
sub_w=sum(tsize(ch,sf)[0] for ch in sub)+sub_sp*(len(sub)-1)
sx0=CX-sub_w//2
sub_y=ty+tsize(title,tf)[1]+18
sx=sx0
for ch in sub:
    cw,_=tsize(ch,sf)
    gold_text(sx+cw//2,sub_y,ch,sf,'ma')
    sx+=cw+sub_sp

lead='BLACK GOLD NOBILITY · NINE TIERS'
lf=LATIN(24,'sans')
ly=sub_y+tsize(sub,sf)[1]+20
txt(CX,ly,lead,lf,MUTED,'ma')

dy=ly+36
# 标题分隔线（两端菱形端饰）
draw.line([(150,dy),(CX-16,dy)],fill=(212,175,55,130),width=1)
draw.line([(CX+16,dy),(W-150,dy)],fill=(212,175,55,130),width=1)
draw.polygon([(CX,dy-6),(CX+6,dy),(CX,dy+6),(CX-6,dy)],fill=(212,175,55,220))

# ===== 九档卡片（3x3）=====
# 每档按四大类提炼：(项数, [代表权益1, 代表权益2])
TIERS=[
  {'id':'I','wealth':3000,'group':'初阶',
   'cats':[('每月福利',3,['灵石 4,000','粉钻 20']),
           ('尊享权益',4,['六字头衔','中级马甲']),
           ('黑金专享',3,['生日 1档','返现 10%']),
           ('拍卖特权',0,['—'])]},
  {'id':'II','wealth':4500,'group':'初阶',
   'cats':[('每月福利',3,['灵石 7,000','粉钻 30']),
           ('尊享权益',5,['永久无流放','95折']),
           ('黑金专享',3,['生日 2档','返现 10%']),
           ('拍卖特权',0,['—'])]},
  {'id':'III','wealth':6000,'group':'中阶',
   'cats':[('每月福利',3,['灵石 10,000','粉钻 40']),
           ('尊享权益',7,['个人认证卡','名人堂']),
           ('黑金专享',4,['生日 3档','拍卖 9折']),
           ('拍卖特权',3,['清单查阅','匿名出价'])]},
  {'id':'IV','wealth':8000,'group':'中阶',
   'cats':[('每月福利',3,['灵石 14,000','粉钻 50']),
           ('尊享权益',8,['专属C卡','9折']),
           ('黑金专享',4,['生日 4档','返现 10%']),
           ('拍卖特权',3,['清单查阅','匿名出价'])]},
  {'id':'V','wealth':10000,'group':'高级',
   'cats':[('每月福利',3,['灵石 17,000','粉钻 60']),
           ('尊享权益',8,['至尊一字','双人认证']),
           ('黑金专享',7,['专属俱乐部','CP共享']),
           ('拍卖特权',4,['清单查阅','流拍内购'])]},
  {'id':'VI','wealth':12000,'group':'高级',
   'cats':[('每月福利',3,['灵石 20,000','粉钻 70']),
           ('尊享权益',8,['挚友1名','85折']),
           ('黑金专享',8,['生日电台','包场15首']),
           ('拍卖特权',4,['清单查阅','流拍内购'])]},
  {'id':'VII','wealth':15000,'group':'高级',
   'cats':[('每月福利',3,['灵石 23,000','粉钻 80']),
           ('尊享权益',8,['挚友1名','85折']),
           ('黑金专享',8,['返现15%','包场15首']),
           ('拍卖特权',5,['保密出价','拍卖7折'])]},
  {'id':'VIII','wealth':18000,'group':'至尊',
   'cats':[('每月福利',3,['灵石 30,000','粉钻 100']),
           ('尊享权益',8,['挚友2名','8折']),
           ('黑金专享',8,['返现20%','包场15首']),
           ('拍卖特权',5,['保密出价','拍卖6折'])]},
  {'id':'IX','wealth':21000,'group':'至尊',
   'cats':[('每月福利',3,['灵石 36,000','粉钻 150']),
           ('尊享权益',8,['挚友3名','8折']),
           ('黑金专享',8,['返现20%','包场30首']),
           ('拍卖特权',5,['保密出价','拍卖5折'])]},
]

# 卡片几何（卡片网格在标题与二维码之间垂直居中）
COLS=3; ROWS=3
MARGIN_X=60
GAP=28
CARD_W=(W-2*MARGIN_X-(COLS-1)*GAP)//COLS
CARD_H=430
GRID_H=ROWS*CARD_H+(ROWS-1)*GAP
HEADER_BOTTOM=dy+24
QR_PANEL_H=290
QR_BOTTOM_MARGIN=100
QR_TOP=H-QR_PANEL_H-QR_BOTTOM_MARGIN
GRID_TOP=HEADER_BOTTOM+((QR_TOP-HEADER_BOTTOM)-GRID_H)//2
GRID_BOTTOM=GRID_TOP+GRID_H

def card_pos(i):
    r,c=divmod(i,COLS)
    x=MARGIN_X+c*(CARD_W+GAP)
    y=GRID_TOP+r*(CARD_H+GAP)
    return x,y

def glass_card(x,y,w,h,i):
    """水晶凸起玻璃卡片：通透渐变 + 弧形穹顶高光 + 立体斜面描边 + 内外发光"""
    R=30  # 更大圆角，水晶圆润
    # 外层金色光晕（高等级更强，柔化）
    glow_alpha=int(32+i*13)
    if glow_alpha>0:
        glow=Image.new('RGBA',(w+28,h+28),(0,0,0,0))
        gd=ImageDraw.Draw(glow)
        gd.rounded_rectangle((8,8,w+20,h+20),radius=R+6,outline=(212,175,55,glow_alpha),width=5)
        glow=glow.filter(ImageFilter.GaussianBlur(12))
        canvas.alpha_composite(glow,(x-14,y-14))
    # 基础层：通透深色纵向渐变（水晶玻璃感，降低不透明度）
    base=Image.new('RGBA',(w,h),(0,0,0,0))
    bd=ImageDraw.Draw(base)
    for yy in range(h):
        tt=yy/max(h-1,1)
        a=int(190-tt*25)
        r=int(18+tt*16); g=int(12+tt*11); b=int(6+tt*9)
        bd.line([(0,yy),(w,yy)],fill=(r,g,b,a))
    # 弧形穹顶高光（水晶凸起的顶部反光，宽而柔和）
    hl=Image.new('RGBA',(w,h),(0,0,0,0))
    hd=ImageDraw.Draw(hl)
    for yy in range(int(h*0.5)):
        # 弧形：中间高两边低，模拟穹顶反光
        edge=yy/(h*0.5)
        curve=1-(edge-0.5)**2*2.2
        a=int(70*max(curve,0)*(1-edge)**1.2)
        hd.line([(0,yy),(w,yy)],fill=(255,246,205,a))
    # 斜向细光带（玻璃折射）
    for k in range(-h,w+h,4):
        hd.line([(k,0),(k+h//3,h//3)],fill=(255,250,215,6),width=1)
    base=Image.alpha_composite(base,hl)
    # 底部微弱金色内反光
    refl=Image.new('RGBA',(w,h),(0,0,0,0))
    rd=ImageDraw.Draw(refl)
    for yy in range(int(h*0.32)):
        tt=yy/(h*0.32)
        a=int(38*tt)
        rd.line([(0,h-yy),(w,h-yy)],fill=(212,175,55,a))
    base=Image.alpha_composite(base,refl)
    # 圆角遮罩
    mask=Image.new('L',(w,h),0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,w,h),radius=R,fill=255)
    base.putalpha(mask)
    canvas.alpha_composite(base,(x,y))
    # 立体斜面描边（水晶凸起：上亮下暗，3D 边缘）
    border=Image.new('RGBA',(w,h),(0,0,0,0))
    bdr=ImageDraw.Draw(border)
    for yy in range(h):
        tt=yy/max(h-1,1)
        a=int(235-tt*100)
        bdr.line([(0,yy),(w,yy)],fill=(255,238,168,a) if tt<0.5 else (110,82,18,a))
    ring=Image.new('L',(w,h),0)
    ImageDraw.Draw(ring).rounded_rectangle((0,0,w,h),radius=R,fill=0,outline=255,width=3)
    border.putalpha(ring)
    canvas.alpha_composite(border,(x,y))
    # 顶部细亮线（凸起高光棱）
    topedge=Image.new('RGBA',(w,h),(0,0,0,0))
    te=ImageDraw.Draw(topedge)
    te.rounded_rectangle((2,2,w-2,h-2),radius=R-1,outline=(255,248,214,90),width=1)
    topedge.putalpha(mask)
    canvas.alpha_composite(topedge,(x,y))
    # 底部内阴影（水晶下沉感）
    botsh=Image.new('RGBA',(w,h),(0,0,0,0))
    bs=ImageDraw.Draw(botsh)
    for yy in range(int(h*0.25)):
        tt=yy/(h*0.25)
        a=int(45*(1-tt))
        bs.line([(0,h-1-yy),(w,h-1-yy)],fill=(0,0,0,a))
    botsh.putalpha(mask)
    canvas.alpha_composite(botsh,(x,y))
    # 内发光（顶部一圈暖光）
    inner=Image.new('RGBA',(w,h),(0,0,0,0))
    idr=ImageDraw.Draw(inner)
    idr.rounded_rectangle((5,5,w-5,h-5),radius=R-3,outline=(255,242,185,35),width=1)
    inner.putalpha(mask)
    canvas.alpha_composite(inner,(x,y))

for i,t in enumerate(TIERS):
    x,y=card_pos(i)
    cx=x+CARD_W//2
    glass_card(x,y,CARD_W,CARD_H,i)
    if i==8:
        badge='至 尊'
        bf=CJK(15,'Bold')
        bw,bh=tsize(badge,bf)
        rrect((cx-bw//2-10,y-12,cx+bw//2+10,y+12),8,fill=(212,175,55,255))
        txt(cx,y,badge,bf,(10,7,3),'mm')

    # 头部：黑金 Ⅰ（大字体饱满 + 金色描边）
    tier_title=f'黑金 {t["id"]}'
    ttf=CJK(56,'Black')
    draw.text((cx,y+30),tier_title,font=ttf,fill=(0,0,0,0),anchor='ma',stroke_width=2,stroke_fill=(110,82,18,220))
    gold_text(cx,y+28,tier_title,ttf,'ma')
    _,gnh=tsize(tier_title,ttf)
    # 财富值（金色大字）
    txt(cx,y+28+gnh+8,f'财富值 {t["wealth"]:,}',CJK(23,'Bold'),GOLD_HI,'ma',shadow=True)
    # 分隔线
    divy=y+28+gnh+8+32
    draw.line([(x+28,divy),(x+CARD_W-28,divy)],fill=(212,175,55,140),width=1)
    draw.ellipse([(cx-4,divy-4),(cx+4,divy+4)],fill=(212,175,55,220))

    # 四大类权益（均匀分布）
    cat_count=len(t['cats'])
    avail_h=y+CARD_H-divy-20
    per_h=avail_h//cat_count
    by2=divy+14
    for ci,(cat_name,count,reps) in enumerate(t['cats']):
        cy=divy+14+ci*per_h
        # 大类行：✓ 大类名 (N项)
        if count>0:
            txt(x+22,cy,'✓',SANS(21,'Bold'),GOLD_HI,'la')
            txt(x+48,cy,cat_name,SANS(21,'Bold'),GOLD,'la')
            txt(x+CARD_W-22,cy,f'{count}项',SANS(15,'Medium'),GOLD_HI,'ra')
        else:
            txt(x+22,cy,'—',SANS(21,'Regular'),DIM,'la')
            txt(x+48,cy,cat_name,SANS(21,'Medium'),DIM,'la')
            txt(x+CARD_W-22,cy,'—',SANS(15,'Regular'),DIM,'ra')
        _,bh1=tsize(cat_name,SANS(21,'Bold'))
        # 代表权益（小字）
        rep='  ·  '.join(reps)
        txt(x+48,cy+bh1+5,rep,SANS(15,'Medium'),CREAM,'la',shadow=True)

# ===== 底部二维码区域 =====
qr_panel_h=QR_PANEL_H
qr_top=QR_TOP

# ===== 装饰分隔（卡片与二维码之间）=====
mid_y=(GRID_BOTTOM+qr_top)//2
draw.line([(CX-200,mid_y),(CX-34,mid_y)],fill=(212,175,55,150),width=1)
draw.line([(CX+34,mid_y),(CX+200,mid_y)],fill=(212,175,55,150),width=1)
draw.polygon([(CX,mid_y-9),(CX+9,mid_y),(CX,mid_y+9),(CX-9,mid_y)],fill=(212,175,55,210))
motto='NOBILITAS · AURUM · NIGRA'
txt(CX,mid_y+32,motto,LATIN(20,'sans'),MUTED,'ma')

# 二维码面板（深色玻璃 + 金色渐变描边）
panel_x1,panel_x2=W//2-360,W//2+360
panel=Image.new('RGBA',(panel_x2-panel_x1,qr_panel_h),(0,0,0,0))
pd=ImageDraw.Draw(panel)
for yy in range(qr_panel_h):
    tt=yy/max(qr_panel_h-1,1)
    a=int(185-tt*25)
    pd.line([(0,yy),(panel_x2-panel_x1,yy)],fill=(14,9,4,a))
pmask=Image.new('L',(panel_x2-panel_x1,qr_panel_h),0)
ImageDraw.Draw(pmask).rounded_rectangle((0,0,panel_x2-panel_x1,qr_panel_h),radius=20,fill=255)
panel.putalpha(pmask)
canvas.alpha_composite(panel,(panel_x1,qr_top))
# 面板金色描边
pbdr=Image.new('RGBA',(panel_x2-panel_x1,qr_panel_h),(0,0,0,0))
pbd=ImageDraw.Draw(pbdr)
for yy in range(qr_panel_h):
    tt=yy/max(qr_panel_h-1,1)
    pbd.line([(0,yy),(panel_x2-panel_x1,yy)],fill=(255,232,150,int(200-tt*80)))
pring=Image.new('L',(panel_x2-panel_x1,qr_panel_h),0)
ImageDraw.Draw(pring).rounded_rectangle((0,0,panel_x2-panel_x1,qr_panel_h),radius=20,outline=255,width=2)
pbdr.putalpha(pring)
canvas.alpha_composite(pbdr,(panel_x1,qr_top))

# 美化二维码：白色圆角底 + 金色渐变描边 + 外发光（放大）
qr_size=200
qr_img=Image.open(QR).convert('RGBA').resize((qr_size,qr_size),Image.LANCZOS)
pad=18
qb_w=qr_size+2*pad
qcx=W//2-120; qcy=qr_top+(qr_panel_h-qb_w)//2
# 二维码外发光
qrglow=Image.new('RGBA',(qb_w+36,qb_w+36),(0,0,0,0))
ImageDraw.Draw(qrglow).rounded_rectangle((18,18,qb_w+18,qb_w+18),radius=24,outline=(212,175,55,170),width=7)
qrglow=qrglow.filter(ImageFilter.GaussianBlur(12))
canvas.alpha_composite(qrglow,(int(qcx-qb_w//2-18),int(qcy-18)))
# 白色圆角底 + 金色渐变描边
qbg=Image.new('RGBA',(qb_w,qb_w),(0,0,0,0))
qbd=ImageDraw.Draw(qbg)
for yy in range(qb_w):
    tt=yy/max(qb_w-1,1)
    qbd.line([(0,yy),(qb_w,yy)],fill=(252,246,228,255))
qmask=Image.new('L',(qb_w,qb_w),0)
ImageDraw.Draw(qmask).rounded_rectangle((0,0,qb_w,qb_w),radius=20,fill=255)
qbg.putalpha(qmask)
canvas.alpha_composite(qbg,(qcx-qb_w//2,qcy))
# 二维码图案
canvas.alpha_composite(qr_img,(int(qcx-qr_size//2),int(qcy+pad)))
# 金色渐变描边
qbrd=Image.new('RGBA',(qb_w,qb_w),(0,0,0,0))
qbdd=ImageDraw.Draw(qbrd)
for yy in range(qb_w):
    tt=yy/max(qb_w-1,1)
    qbdd.line([(0,yy),(qb_w,yy)],fill=(255,232,150,255) if tt<0.5 else (150,110,25,255))
qbring=Image.new('L',(qb_w,qb_w),0)
ImageDraw.Draw(qbring).rounded_rectangle((0,0,qb_w,qb_w),radius=20,outline=255,width=3)
qbrd.putalpha(qbring)
canvas.alpha_composite(qbrd,(qcx-qb_w//2,qcy))

# 右侧文字（放大）
tx=W//2+40
txt(tx,qr_top+qr_panel_h//2-44,'扫码查看',CJK(34,'Bold'),GOLD,'la')
txt(tx,qr_top+qr_panel_h//2+2,'完整九阶权益',CJK(26,'Medium'),CREAM,'la')
txt(tx,qr_top+qr_panel_h//2+42,'zhaomivip.github.io',LATIN(20,'sans'),MUTED,'la')

# 整体金边（外框+内细线，双层优雅）
PAD=42
rrect([(PAD,PAD),(W-PAD,H-PAD)],r=18,outline=(212,175,55,170),w=2)
rrect([(PAD+7,PAD+7),(W-PAD-7,H-PAD-7)],r=14,outline=(212,175,55,70),w=1)

# 四角装饰
def corner(cx,cy,sx,sy):
    draw.line([(cx,cy),(cx+sx,cy)],fill=(212,175,55,220),width=2)
    draw.line([(cx,cy),(cx,cy+sy)],fill=(212,175,55,220),width=2)
corner(90,90,40,40); corner(W-90,90,-40,40); corner(90,H-90,40,-40); corner(W-90,H-90,-40,-40)

# 暗角
vig=Image.new('L',(W,H),0); vd=ImageDraw.Draw(vig)
vd.ellipse([-200,-200,W+200,H+200],fill=255)
vig=vig.filter(ImageFilter.GaussianBlur(180))
dark=Image.new('RGBA',(W,H),(0,0,0,90))
canvas=Image.composite(canvas,dark,vig).convert('RGB')
canvas.save(OUT,quality=92)
print('poster saved:',OUT,canvas.size)
print(f'ratio {W/H:.4f} = 9/21 = {9/21:.4f}')
print(f'card {CARD_W}x{CARD_H}, qr_panel {qr_panel_h}')
