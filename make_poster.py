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
    os.path.join(ASSETS,'fonts'),
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
ART_MAP={'xiaowei':'ZCOOLXiaoWei.ttf','kuaile':'ZCOOLKuaiLe.ttf'}
SCRIPT_MAP={'great':'GreatVibes-Regular.ttf','dance':'DancingScript-Bold.ttf'}

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
def ART(size,style='xiaowei'): return _load(size,ART_MAP,style)
def SCRIPT(size,style='great'): return _load(size,SCRIPT_MAP,style)

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

# ===== 卡片几何常量（提前定义，供标题区分割线估算使用）=====
COLS=3; ROWS=3
MARGIN_X=60
GAP=28
CARD_W=(W-2*MARGIN_X-(COLS-1)*GAP)//COLS
CARD_H=516
GRID_H=ROWS*CARD_H+(ROWS-1)*GAP
QR_PANEL_H=290

# ===== 标题区（艺术字体 + 分布填充与卡片间空隙）=====
ey='NOBILITAS · AURUM · NIGRA'
ef=LATIN(30,'display'); ew,eh=tsize(ey,ef)
ey_y=178
txt(CX,ey_y,ey,ef,GOLD,'ma')
draw.line([(CX-ew//2-50,ey_y+eh//2),(CX-ew//2-14,ey_y+eh//2)],fill=(212,175,55,200),width=2)
draw.line([(CX+ew//2+14,ey_y+eh//2),(CX+ew//2+50,ey_y+eh//2)],fill=(212,175,55,200),width=2)

title='着迷黑金贵族体系'
tf=ART(156,'xiaowei')   # 站酷小薇艺术字体（加大）
ty=ey_y+eh+200           # 再下移两个行高位置
SPACING=14
title_w=sum(tsize(ch,tf)[0] for ch in title)+SPACING*(len(title)-1)
tx0=CX-title_w//2
# 标题金色光晕
glow=Image.new('RGBA',(W,460),(0,0,0,0))
gd=ImageDraw.Draw(glow)
gx=tx0
for ch in title:
    cw,_=tsize(ch,tf)
    gd.text((gx,230-ty),ch,font=tf,fill=(212,175,55,140),anchor='la')
    gx+=cw+SPACING
glow=glow.filter(ImageFilter.GaussianBlur(28))
canvas.alpha_composite(glow,(0,ty-230))
# 逐字绘制：投影 + 金色描边 + 金色渐变填充
gx=tx0
for ch in title:
    cw,chh=tsize(ch,tf)
    ccx=gx+cw//2
    draw.text((ccx+4,ty+4),ch,font=tf,fill=(0,0,0,175),anchor='ma')
    draw.text((ccx,ty),ch,font=tf,fill=(255,238,168,0),anchor='ma',stroke_width=4,stroke_fill=(110,82,18,235))
    gold_text(ccx,ty,ch,tf,'ma')
    gx+=cw+SPACING

sub_left='九阶黑金'
sub_right='逐档尊贵'
sf=ART(46,'xiaowei')
sub_sp=10
# 计算两段宽度
lw=sum(tsize(ch,sf)[0] for ch in sub_left)+sub_sp*(len(sub_left)-1)
rw=sum(tsize(ch,sf)[0] for ch in sub_right)+sub_sp*(len(sub_right)-1)
gap=40  # 中间菱形间距
sub_total_w=lw+gap+rw
sx0=CX-sub_total_w//2
sub_y=ty+tsize(title,tf)[1]+34
# 左段
sx=sx0
for ch in sub_left:
    cw,_=tsize(ch,sf)
    gold_text(sx+cw//2,sub_y,ch,sf,'ma')
    sx+=cw+sub_sp
# 中间菱形（手绘，避免字体缺字）
dia_x=sx0+lw+gap//2
draw.polygon([(dia_x,sub_y-10),(dia_x+8,sub_y),(dia_x,sub_y+10),(dia_x-8,sub_y)],fill=(212,175,55,235))
# 右段
sx=sx0+lw+gap
for ch in sub_right:
    cw,_=tsize(ch,sf)
    gold_text(sx+cw//2,sub_y,ch,sf,'ma')
    sx+=cw+sub_sp

# 英文副标题：手写花体英文（Great Vibes），加大
lead='Black Gold Nobility · Nine Tiers'
lf=SCRIPT(72,'great')
ly=sub_y+tsize(sub_left,sf)[1]+36
txt(CX,ly,lead,lf,GOLD,'ma')
lead_h=tsize(lead,lf)[1]

# 标题分隔线：下移到英文花字与卡片之间的中间位置
# 两步估算：先用占位 dy 算出网格位置，再把分隔线放到英文与卡片的中点
_dy_est=ly+lead_h+36
_hb_est=_dy_est+16
_grid_top_est=_hb_est+((H-QR_PANEL_H-30-_hb_est)-GRID_H)//2
dy=(ly+lead_h//2+_grid_top_est)//2
# 标题分隔线（两端菱形端饰）
draw.line([(150,dy),(CX-16,dy)],fill=(212,175,55,130),width=1)
draw.line([(CX+16,dy),(W-150,dy)],fill=(212,175,55,130),width=1)
draw.polygon([(CX,dy-6),(CX+6,dy),(CX,dy+6),(CX-6,dy)],fill=(212,175,55,220))

# ===== 九档卡片（3x3）=====
# 每档按四大类提炼：(项数, [代表权益1, 代表权益2])
# 原则：每档尽量选上一档没有的、或数值比上一档更高的权益
TIERS=[
  {'id':'I','wealth':3000,'group':'初阶',
   'cats':[('每月福利',3,['灵石 4,000','粉钻 20']),
           ('尊享权益',4,['六字头衔','中级马甲']),
           ('黑金专享',3,['生日 1档','返现 10%']),
           ('拍卖特权',0,['—'])]},
  {'id':'II','wealth':4500,'group':'初阶',
   'cats':[('每月福利',3,['灵石 7,000','粉钻 30']),
           ('尊享权益',5,['永久无流放','95折']),
           ('黑金专享',3,['生日 2档','拍卖 95折']),
           ('拍卖特权',0,['—'])]},
  {'id':'III','wealth':6000,'group':'中阶',
   'cats':[('每月福利',3,['灵石 10,000','粉钻 40']),
           ('尊享权益',7,['个人认证卡','名人堂']),
           ('黑金专享',4,['生日 3档','拍卖 9折']),
           ('拍卖特权',3,['清单查阅','匿名出价'])]},
  {'id':'IV','wealth':8000,'group':'中阶',
   'cats':[('每月福利',3,['灵石 14,000','粉钻 50']),
           ('尊享权益',8,['专属 C 卡','9折']),
           ('黑金专享',4,['生日 4档','返现 10%']),
           ('拍卖特权',3,['清单查阅','匿名出价'])]},
  {'id':'V','wealth':10000,'group':'高级',
   'cats':[('每月福利',3,['灵石 17,000','粉钻 60']),
           ('尊享权益',8,['至尊一字','双人认证']),
           ('黑金专享',7,['专属俱乐部','CP 共享']),
           ('拍卖特权',4,['流拍内购','优先出价'])]},
  {'id':'VI','wealth':12000,'group':'高级',
   'cats':[('每月福利',3,['灵石 20,000','粉钻 70']),
           ('尊享权益',8,['挚友 1名','85折']),
           ('黑金专享',8,['生日电台','包场 15首']),
           ('拍卖特权',4,['流拍内购','保密名额'])]},
  {'id':'VII','wealth':15000,'group':'高级',
   'cats':[('每月福利',3,['灵石 23,000','粉钻 80']),
           ('尊享权益',8,['挚友 1名','85折']),
           ('黑金专享',8,['返现 15%','包场 15首']),
           ('拍卖特权',5,['保密出价','拍卖 7折'])]},
  {'id':'VIII','wealth':18000,'group':'至尊',
   'cats':[('每月福利',3,['灵石 30,000','粉钻 100']),
           ('尊享权益',8,['挚友 2名','8折']),
           ('黑金专享',8,['返现 20%','包场 15首']),
           ('拍卖特权',5,['保密出价','拍卖 6折'])]},
  {'id':'IX','wealth':21000,'group':'至尊',
   'cats':[('每月福利',3,['灵石 36,000','粉钻 150']),
           ('尊享权益',8,['挚友 3名','8折']),
           ('黑金专享',8,['返现 20%','包场 30首']),
           ('拍卖特权',5,['保密出价','拍卖 5折'])]},
]

# 卡片几何（卡片网格在标题与二维码之间垂直居中，二维码贴近卡片下方）
HEADER_BOTTOM=dy+16
# 先用底部估算位计算网格居中，再把二维码上移贴近卡片
_QR_EST=H-QR_PANEL_H-30
GRID_TOP=HEADER_BOTTOM+((_QR_EST-HEADER_BOTTOM)-GRID_H)//2
GRID_BOTTOM=GRID_TOP+GRID_H
QR_TOP=GRID_BOTTOM+55          # 二维码上移，紧贴卡片下方

def card_pos(i):
    r,c=divmod(i,COLS)
    x=MARGIN_X+c*(CARD_W+GAP)
    y=GRID_TOP+r*(CARD_H+GAP)
    return x,y

def glass_card(x,y,w,h,i):
    """半透明半黑色玻璃水晶卡片：深色玻璃底 + 白色水晶高光 + 水润光滑边缘 + 立体凸起"""
    R=34  # 大圆角，水滴圆润光滑

    # ===== 悬浮投影：完全在卡片下方外侧，模糊后切掉卡片区域内投影 =====
    sh=100
    shadow=Image.new('RGBA',(w+80,h+160),(0,0,0,0))
    sd=ImageDraw.Draw(shadow)
    sd.rounded_rectangle((40,h,w+40,h+sh),radius=R,fill=(0,0,0,90))
    shadow=shadow.filter(ImageFilter.GaussianBlur(22))
    smask=shadow.getchannel('A').copy()
    ImageDraw.Draw(smask).rectangle((0,0,w+80,h),fill=0)
    shadow.putalpha(smask)
    canvas.alpha_composite(shadow,(x-40,y))

    # 外层柔和白色光晕（高等级稍强，非金色，保持统一）
    glow_alpha=int(22+i*8)
    if glow_alpha>0:
        glow=Image.new('RGBA',(w+34,h+34),(0,0,0,0))
        gd=ImageDraw.Draw(glow)
        gd.rounded_rectangle((10,10,w+24,h+24),radius=R+7,outline=(220,225,235,glow_alpha),width=4)
        glow=glow.filter(ImageFilter.GaussianBlur(15))
        canvas.alpha_composite(glow,(x-17,y-17))

    # ===== 基础层：半透明半黑色深色玻璃（冷调深灰，背景微透，整体统一）=====
    base=Image.new('RGBA',(w,h),(0,0,0,0))
    bd=ImageDraw.Draw(base)
    for yy in range(h):
        tt=yy/max(h-1,1)
        # 深色玻璃：整体统一深灰，仅极轻微顶亮底暗
        a=int(96-tt*16)            # 半透明：顶部96，底部80
        r=int(28+tt*6); g=int(29+tt*6); b=int(33+tt*6)
        bd.line([(0,yy),(w,yy)],fill=(r,g,b,a))

    # ===== 水晶高光（极柔和灰白色，保持整体半黑色统一，仅微妙水润感）=====
    hl=Image.new('RGBA',(w,h),(0,0,0,0))
    hd=ImageDraw.Draw(hl)
    # 穹顶主高光：极淡顶部亮斑，向下弧形衰减（微妙凸起感）
    for yy in range(int(h*0.62)):
        edge=yy/(h*0.62)
        curve=1-(edge-0.24)**2*4.0
        a=int(72*max(curve,0)*(1-edge)**1.1)
        hd.line([(0,yy),(w,yy)],fill=(210,215,225,a))
    # 镜面反光带（极淡横向亮带，水润光滑）
    for yy in range(int(h*0.14)):
        tt=yy/(h*0.14)
        a=int(48*(1-tt)**2.6)
        hd.line([(w*0.10,yy+int(h*0.06)),(w*0.90,yy+int(h*0.06))],fill=(215,220,230,a))
    # 顶部棱线（极淡顶边聚光）
    for yy in range(int(h*0.03)):
        a=int(70*(1-yy/(h*0.03)))
        hd.line([(w*0.16,yy),(w*0.84,yy)],fill=(220,225,235,a))
    # 细密折射光带（极淡细线）
    for k in range(-h,w+h,4):
        hd.line([(k,0),(k+h//3,h//3)],fill=(210,215,225,3),width=1)
    base=Image.alpha_composite(base,hl)

    # 底部极微弱冷色反光
    refl=Image.new('RGBA',(w,h),(0,0,0,0))
    rd=ImageDraw.Draw(refl)
    for yy in range(int(h*0.35)):
        tt=yy/(h*0.35)
        a=int(22*tt)
        rd.line([(0,h-yy),(w,h-yy)],fill=(160,170,185,a))
    base=Image.alpha_composite(base,refl)

    # 圆角遮罩
    mask=Image.new('L',(w,h),0)
    ImageDraw.Draw(mask).rounded_rectangle((0,0,w,h),radius=R,fill=255)
    base.putalpha(mask)
    canvas.alpha_composite(base,(x,y))

    # ===== 立体棱边描边（上亮下暗，极淡，凸起感）=====
    border=Image.new('RGBA',(w,h),(0,0,0,0))
    bdr=ImageDraw.Draw(border)
    for yy in range(h):
        tt=yy/max(h-1,1)
        a=int(120-tt*70)
        bdr.line([(0,yy),(w,yy)],fill=(200,208,220,a) if tt<0.5 else (35,37,42,a))
    ring=Image.new('L',(w,h),0)
    ImageDraw.Draw(ring).rounded_rectangle((0,0,w,h),radius=R,fill=0,outline=255,width=3)
    border.putalpha(ring)
    canvas.alpha_composite(border,(x,y))

    # 顶部亮棱（极淡，水润光滑）
    topedge=Image.new('RGBA',(w,h),(0,0,0,0))
    te=ImageDraw.Draw(topedge)
    te.rounded_rectangle((2,2,w-2,h-2),radius=R-1,outline=(220,225,235,90),width=2)
    canvas.alpha_composite(topedge,(x,y))

    # 底部边缘微暗（凸起物底边阴影，仅边缘）
    botedge=Image.new('RGBA',(w,h),(0,0,0,0))
    be=ImageDraw.Draw(botedge)
    be.rounded_rectangle((2,2,w-2,h-2),radius=R-1,outline=(0,0,0,100),width=2)
    botmask=Image.new('L',(w,h),0)
    ImageDraw.Draw(botmask).rectangle((0,h//2,w,h),fill=255)
    botedge.putalpha(Image.composite(botedge.getchannel('A'),Image.new('L',(w,h),0),botmask))
    canvas.alpha_composite(botedge,(x,y))

    # 内圈细白边（玻璃内轮廓）
    inner=Image.new('RGBA',(w,h),(0,0,0,0))
    idr=ImageDraw.Draw(inner)
    idr.rounded_rectangle((5,5,w-5,h-5),radius=R-3,outline=(220,225,235,30),width=1)
    canvas.alpha_composite(inner,(x,y))

for i,t in enumerate(TIERS):
    x,y=card_pos(i)
    cx=x+CARD_W//2
    glass_card(x,y,CARD_W,CARD_H,i)

    # 头部：黑金 Ⅰ（大字体饱满 + 金色描边）
    tier_title=f'黑金 {t["id"]}'
    ttf=CJK(56,'Black')
    draw.text((cx,y+30),tier_title,font=ttf,fill=(0,0,0,0),anchor='ma',stroke_width=2,stroke_fill=(110,82,18,220))
    gold_text(cx,y+28,tier_title,ttf,'ma')
    _,gnh=tsize(tier_title,ttf)
    # 身价值（金色大字）
    txt(cx,y+28+gnh+8,f'身价值 {t["wealth"]:,}',CJK(23,'Bold'),GOLD_HI,'ma',shadow=True)
    # 分隔线
    divy=y+28+gnh+8+32
    draw.line([(x+28,divy),(x+CARD_W-28,divy)],fill=(212,175,55,140),width=1)
    draw.ellipse([(cx-4,divy-4),(cx+4,divy+4)],fill=(212,175,55,220))

    # 四大类权益（均匀分布、统一圆润字体、加大饱满）
    cat_count=len(t['cats'])
    avail_h=y+CARD_H-divy-16
    per_h=avail_h//cat_count
    cat_font=CJK(23,'Bold')      # 大类名加大
    cnt_font=CJK(15,'Bold')      # 项数
    rep_font=CJK(17,'Medium')    # 代表权益加大
    chk_font=CJK(22,'Bold')      # 对勾
    for ci,(cat_name,count,reps) in enumerate(t['cats']):
        cy=divy+14+ci*per_h
        # 大类行
        if count>0:
            txt(x+20,cy,'✓',chk_font,GOLD_HI,'la')
            txt(x+48,cy,cat_name,cat_font,GOLD,'la')
            txt(x+CARD_W-20,cy,f'{count}项',cnt_font,GOLD_HI,'ra')
        else:
            txt(x+20,cy,'—',chk_font,DIM,'la')
            txt(x+48,cy,cat_name,cat_font,DIM,'la')
            txt(x+CARD_W-20,cy,'—',cnt_font,DIM,'ra')
        _,bh1=tsize(cat_name,cat_font)
        # 代表权益（饱满分布）
        rep='  ·  '.join(reps)
        txt(x+48,cy+bh1+8,rep,rep_font,CREAM,'la',shadow=True)

# ===== 底部二维码区域 =====
qr_panel_h=QR_PANEL_H
qr_top=QR_TOP

# ===== 分割线（卡片与二维码之间）=====
div_y=GRID_BOTTOM+27
draw.line([(90,div_y),(CX-26,div_y)],fill=(212,175,55,220),width=2)
draw.line([(CX+26,div_y),(W-90,div_y)],fill=(212,175,55,220),width=2)
draw.polygon([(CX,div_y-9),(CX+9,div_y),(CX,div_y+9),(CX-9,div_y)],fill=(212,175,55,240))

# 二维码区域：去掉黑色底框，仅保留极淡金色描边作为结构
panel_x1,panel_x2=W//2-360,W//2+360
pbdr=Image.new('RGBA',(panel_x2-panel_x1,qr_panel_h),(0,0,0,0))
pbd=ImageDraw.Draw(pbdr)
for yy in range(qr_panel_h):
    tt=yy/max(qr_panel_h-1,1)
    pbd.line([(0,yy),(panel_x2-panel_x1,yy)],fill=(255,232,150,int(120-tt*60)))
pring=Image.new('L',(panel_x2-panel_x1,qr_panel_h),0)
ImageDraw.Draw(pring).rounded_rectangle((0,0,panel_x2-panel_x1,qr_panel_h),radius=20,outline=255,width=1)
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
txt(tx,qr_top+qr_panel_h//2-34,'扫码查看完整',CJK(32,'Bold'),GOLD,'la')
txt(tx,qr_top+qr_panel_h//2+10,'黑金贵族权益',CJK(32,'Bold'),GOLD,'la')

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
