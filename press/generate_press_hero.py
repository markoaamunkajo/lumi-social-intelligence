from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math, os, random
W,H = 1920,1080
img = Image.new('RGBA',(W,H),(5,12,25,255))
p = img.load()
# soft radial/linear background
for y in range(H):
    for x in range(W):
        nx=x/W; ny=y/H
        d=math.hypot((nx-0.68)/0.72,(ny-0.50)/0.66)
        glow=max(0,1-d)
        d2=math.hypot((nx-0.70)/0.25,(ny-0.52)/0.25)
        warm=max(0,1-d2)
        base=(6,15,31)
        blue=(190,232,255)
        gold=(255,232,170)
        a=min(0.68, glow*0.82)
        b=min(0.35, warm*0.45)
        r=int(base[0]*(1-a)+blue[0]*a); g=int(base[1]*(1-a)+blue[1]*a); bcol=int(base[2]*(1-a)+blue[2]*a)
        r=int(r*(1-b)+gold[0]*b); g=int(g*(1-b)+gold[1]*b); bcol=int(bcol*(1-b)+gold[2]*b)
        p[x,y]=(r,g,bcol,255)
# overlays
canvas=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(canvas)
# subtle arcs
for off, alpha in [(0,45),(260,30),(-230,26)]:
    d.arc((-160+off,80,1520+off,1120),200,350,fill=(220,247,255,alpha),width=3)
    d.arc((740+off,-120,2020+off,1140),20,160,fill=(220,247,255,alpha),width=3)
# orbital center
cx,cy=1310,535
for rx,ry,rot,col,width in [(365,150,-18,(248,216,137,160),7),(305,125,22,(222,247,255,120),5),(230,90,63,(143,180,255,120),4)]:
    pts=[]
    for i in range(361):
        t=math.radians(i); x=rx*math.cos(t); y=ry*math.sin(t); rr=math.radians(rot)
        pts.append((cx+x*math.cos(rr)-y*math.sin(rr), cy+x*math.sin(rr)+y*math.cos(rr)))
    d.line(pts,fill=col,width=width,joint='curve')
# dashed path
for phase in [0, 180]:
    pts=[]
    for i in range(0,361,4):
        t=math.radians(i); x=430*math.cos(t); y=190*math.sin(t); rr=math.radians(10)
        pts.append((cx+x*math.cos(rr)-y*math.sin(rr),cy+x*math.sin(rr)+y*math.cos(rr)))
    for i in range(0,len(pts)-4,8): d.line(pts[i:i+4],fill=(248,216,137,135),width=3)
# core glow
for r,a,c in [(190,42,(255,240,180)),(115,80,(255,240,190)),(68,120,(255,250,230))]:
    d.ellipse((cx-r,cy-r,cx+r,cy+r),fill=(*c,a))
d.ellipse((cx-26,cy-26,cx+26,cy+26),fill=(255,255,255,245))
# nodes
for x,y,r in [(1080,440,12),(1570,360,9),(1178,725,8),(1658,710,13)]:
    d.ellipse((x-r,y-r,x+r,y+r),fill=(255,246,216,230),outline=(232,251,255,230),width=3)
# floating cards
for x,y,w,h in [(1120,190,238,92),(1460,690,268,104)]:
    d.rounded_rectangle((x,y,x+w,y+h),radius=24,fill=(235,251,255,185),outline=(232,251,255,90),width=2)
d.line([(1150,237),(1170,257),(1215,207)],fill=(255,225,156,255),width=8,joint='curve')
d.rounded_rectangle((1235,222,1318,231),4,fill=(245,255,255,170)); d.rounded_rectangle((1235,243,1292,251),4,fill=(198,235,255,130))
d.ellipse((1488,718,1536,766),fill=(255,230,167,210)); d.line([(1500,742),(1510,752),(1534,720)],fill=(20,40,70,245),width=6,joint='curve')
d.rounded_rectangle((1555,724,1682,733),4,fill=(245,255,255,170)); d.rounded_rectangle((1555,750,1641,758),4,fill=(198,235,255,130))
# human / social arcs bottom
for box,col,wid in [((1100,800,1460,1060),(255,231,172,170),34),((1290,825,1600,1070),(210,240,255,170),30),((1200,890,1560,1010),(255,255,255,80),20)]:
    d.arc(box,205,335,fill=col,width=wid)
canvas=canvas.filter(ImageFilter.GaussianBlur(0.1))
img=Image.alpha_composite(img,canvas)
# typography
text=ImageDraw.Draw(img)
def font(size,bold=False):
    candidates=[
      '/System/Library/Fonts/Supplemental/Arial Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Arial.ttf',
      '/System/Library/Fonts/Supplemental/Helvetica.ttf',
      '/Library/Fonts/Arial.ttf'
    ]
    for c in candidates:
        if c and os.path.exists(c): return ImageFont.truetype(c,size)
    return ImageFont.load_default()
title=font(78,True); sub=font(31); small=font(22,True)
text.text((116,190),'Lumi Social',font=title,fill=(247,251,255,255))
text.text((116,274),'Intelligence',font=title,fill=(247,251,255,255))
text.text((120,385),'Agents that remember carefully,',font=sub,fill=(207,228,247,255))
text.text((120,429),'read the room better,',font=sub,fill=(207,228,247,255))
text.text((120,473),'and know when not to act.',font=sub,fill=(207,228,247,255))
text.line((120,557,640,557),fill=(248,216,137,200),width=2)
text.text((120,590),'Governed reflection • Review • Consent • Repair',font=small,fill=(234,248,255,255))
# vignette
v=Image.new('L',(W,H),0); vd=ImageDraw.Draw(v); vd.rectangle((0,0,W,H),fill=0)
# save
out='/Users/markoaamunkajo/Documents/lumi-social-intelligence/press/lumi-social-intelligence-press-hero-16x9.png'
img.convert('RGB').save(out,quality=95)
print(out)
