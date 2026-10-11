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
tf=CJK(134,'Black')
ty=ey_y+eh+20
gold_text(CX,ty,title,tf,'ma')

sub='九阶黑金 · 逐档尊享'
sf=CJK(36,'SemiBold'); sw,sh=tsize(sub,sf)
gold_text(CX,ty+tsize(title,tf)[1]+14,sub,sf,'ma')

lead='BLACK GOLD NOBILITY · NINE TIERS'
lf=LATIN(22,'sans')
ly=ty+tsize(title,tf)[1]+14+sh+18
txt(CX,ly,lead,lf,MUTED,'ma')

dy=ly+36
draw.line([(150,dy),(W-150,dy)],fill=(212,175,55,120),width=1)
draw.ellipse([(CX-5,dy-5),(CX+5,dy+5)],outline=(212,175,55,200),width=2)

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

# 卡片几何（固定卡片高度，更紧凑）
GRID_TOP=dy+40
COLS=3; ROWS=3
MARGIN_X=60
GAP=22
CARD_W=(W-2*MARGIN_X-(COLS-1)*GAP)//COLS
CARD_H=430
GRID_BOTTOM=GRID_TOP+ROWS*CARD_H+(ROWS-1)*GAP

def card_pos(i):
    r,c=divmod(i,COLS)
    x=MARGIN_X+c*(CARD_W+GAP)
    y=GRID_TOP+r*(CARD_H+GAP)
    return x,y

def glass_card(x,y,w,h,i):
    """绘制玻璃拟态卡片：半透明深色渐变 + 顶部高光 + 立体边框 + 外发光"""
    # 外发光（高等级更强）
    glow_alpha=int(30+i*14)
    if glow_alpha>0:
        rrect((x-7,y-7,x+w+7,y+h+7),22,outline=(212,175,55,glow_alpha),w=3)
    # 基础层：半透明深色渐变
    base=Image.new('RGBA',(w,h),(0,0,0,0))
    bd=ImageDraw.Draw(base)
    for yy in range(h):
        tt=yy/max(h-1,1)
        a=int(200-tt*35)
        r=int(22+tt*10); g=int(16+tt*7); b=int(9+tt*5)
        bd.line([(0,yy),(w,yy)],fill=(r,g,b,a))
    # 顶部高光带（玻璃反光，更亮）
    highlight=Image.new('RGBA',(w,h),(0,0,0,0))
    hd=ImageDraw.Draw(highlight)
    for yy in range(h//2):
        tt=yy/(h//2)
        a=int(70*(1-tt))
        hd.line([(0,yy),(w,yy)],fill=(255,242,195,a))
    # 斜向光带（更粗）
    for k in range(0,w,2):
        hd.line([(k,0),(k+h//3,h//3)],fill=(255,246,205,6),width=1)
    base=Image.alpha_composite(base,highlight)
    # 应用圆角遮罩
    mask=Image.new('L',(w,h),0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,w,h),radius=18,fill=255)
    base.putalpha(mask)
    canvas.alpha_composite(base,(x,y))
    # 立体边框：上左亮、下右暗
    bd2=ImageDraw.Draw(canvas,'RGBA')
    bd2.arc((x+2,y+2,x+w-2,y+h-2),180,360,fill=(255,238,170,210),width=2)
    bd2.arc((x+2,y+2,x+w-2,y+h-2),0,180,fill=(60,44,14,180),width=2)
    bd2.rounded_rectangle((x+1,y+1,x+w-1,y+h-1),radius=17,outline=(212,175,55,150),width=1)

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

    # 头部：黑金 Ⅰ（大字体饱满）
    gold_text(cx,y+28,f'黑金 {t["id"]}',CJK(56,'Black'),'ma')
    _,gnh=tsize(f'黑金 {t["id"]}',CJK(56,'Black'))
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

# ===== 底部二维码（放大）=====
qr_panel_h=200
qr_top=H-qr_panel_h-120

# ===== 装饰分隔（卡片与二维码之间的留白点缀）=====
mid_y=(GRID_BOTTOM+qr_top)//2
draw.line([(CX-200,mid_y),(CX-34,mid_y)],fill=(212,175,55,150),width=1)
draw.line([(CX+34,mid_y),(CX+200,mid_y)],fill=(212,175,55,150),width=1)
draw.polygon([(CX,mid_y-9),(CX+9,mid_y),(CX,mid_y+9),(CX-9,mid_y)],fill=(212,175,55,210))
motto='NOBILITAS · AURUM · NIGRA'
txt(CX,mid_y+32,motto,LATIN(20,'sans'),MUTED,'ma')

rrect((W//2-300,qr_top,W//2+300,qr_top+qr_panel_h),14,fill=(12,8,4,180),outline=(212,175,55,160),w=2)
qr_size=150
qr_img=Image.open(QR).convert('RGBA').resize((qr_size,qr_size),Image.LANCZOS)
qcx=W//2-90; qcy=qr_top+(qr_panel_h-qr_size)//2
rrect((qcx-qr_size//2-10,qcy-10,qcx+qr_size//2+10,qcy+qr_size+10),8,fill=(248,240,216))
canvas.alpha_composite(qr_img,(int(qcx-qr_size//2),int(qcy)))
rrect((qcx-qr_size//2-10,qcy-10,qcx+qr_size//2+10,qcy+qr_size+10),8,outline=(212,175,55,255),w=2)
tx=W//2+28
txt(tx,qr_top+qr_panel_h//2-30,'扫码查看',CJK(26,'Bold'),GOLD,'la')
txt(tx,qr_top+qr_panel_h//2+6,'完整九阶权益',CJK(20,'Medium'),CREAM,'la')
txt(tx,qr_top+qr_panel_h//2+36,'zhaomivip.github.io',LATIN(16,'sans'),MUTED,'la')

# 四角装饰
def corner(cx,cy,sx,sy):
    draw.line([(cx,cy),(cx+sx,cy)],fill=(212,175,55,200),width=2)
    draw.line([(cx,cy),(cx,cy+sy)],fill=(212,175,55,200),width=2)
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
