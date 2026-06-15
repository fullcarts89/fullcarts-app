#!/usr/bin/env python3
"""Static PNG fallback renderer for the RundownChip overlay (when the env can't run
Remotion/Chromium). Mirrors src/compositions/RundownChip.tsx + src/lib/theme.ts.
Fonts: converts the repo woff2 -> ttf via fonttools (needs: pip install Pillow fonttools brotli)."""
import os
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont

HERE=os.path.dirname(os.path.abspath(__file__)); FONTS=os.path.join(HERE,"_fonts"); os.makedirs(FONTS,exist_ok=True)
ROOT=os.path.abspath(os.path.join(HERE,"..","public","fonts")); OUT=os.path.join(HERE,"4thjuly-overlays")
for src,dst in {"space-grotesk-latin-700-normal.woff2":"sg700.ttf","jetbrains-mono-latin-700-normal.woff2":"jb700.ttf","jetbrains-mono-latin-400-normal.woff2":"jb400.ttf"}.items():
    f=TTFont(os.path.join(ROOT,src)); f.flavor=None; f.save(os.path.join(FONTS,dst))

BG_SCRIM=(10,11,13,235); BORDER=(255,255,255,31); CREAM=(245,244,240,255); SECOND=(160,160,165,255); RED=(220,38,38,255)
W,H=1080,1920; CARD_L,CARD_R,CARD_BOTTOM=60,910,1470; PAD_X,PAD_Y,GAP,RANK_W,RADIUS=36,28,28,110,24
jb=lambda s: ImageFont.truetype(os.path.join(FONTS,"jb700.ttf"),s); jb4=lambda s: ImageFont.truetype(os.path.join(FONTS,"jb400.ttf"),s); sg=lambda s: ImageFont.truetype(os.path.join(FONTS,"sg700.ttf"),s)
fmt=lambda n: str(int(n)) if float(n)==int(n) else str(n)
def wbox(d,t,f): b=d.textbbox((0,0),t,font=f); return b[2]-b[0],b[3]-b[1],b[1]
ITEMS=[
 dict(rank=5,product="Bold Party Blend", b=15,a=13.5,unit="oz",pct="10",   slug="01_chexmix"),
 dict(rank=4,product="Hint of Lime",      b=13,a=11,  unit="oz",pct="15.4", slug="02_tostitos"),
 dict(rank=3,product="Beef Franks (each)",b=56,a=43,  unit="g", pct="23.2", slug="03_nathans"),
 dict(rank=2,product="Graham Crackers",   b=25.6,a=19.2,unit="oz",pct="25", slug="04_honeymaid"),
 dict(rank=1,product="Lay's Classic",     b=235,a=145,unit="g", pct="38.3", slug="05_lays"),
]
AW,AP=34,16
def arrow(d,x,cy):
    d.line([(x,cy),(x+AW,cy)],fill=SECOND,width=3); d.line([(x+AW-12,cy-9),(x+AW,cy),(x+AW-12,cy+9)],fill=SECOND,width=3,joint="curve")
def render(it):
    img=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(img)
    f_rank,f_size,f_badge=jb(96),jb4(30),jb(48)
    badge=f'−{it["pct"]}%'; bw,bh,_=wbox(d,badge,f_badge); badge_w,badge_h=bw+40,bh+20
    bx1=CARD_R-PAD_X; bx0=bx1-badge_w; tx=CARD_L+PAD_X+RANK_W+GAP; max_w=bx0-GAP-tx
    ps=44
    while ps>26:
        pw,ph,_=wbox(d,it["product"],sg(ps))
        if pw<=max_w: break
        ps-=2
    f_prod=sg(ps); pw,ph,_=wbox(d,it["product"],f_prod)
    before=fmt(it["b"]); after=f'{fmt(it["a"])} {it["unit"]}'; bw0,sh,_=wbox(d,before,f_size)
    text_h=ph+6+sh; card_h=max(96,text_h,badge_h)+PAD_Y*2; top=CARD_BOTTOM-card_h
    d.rounded_rectangle([CARD_L,top,CARD_R,CARD_BOTTOM],radius=RADIUS,fill=BG_SCRIM,outline=BORDER,width=1)
    rw,rh,roff=wbox(d,str(it["rank"]),f_rank); d.text((CARD_L+PAD_X+(RANK_W-rw)//2,top+(card_h-rh)//2-roff),str(it["rank"]),font=f_rank,fill=RED)
    by0=top+(card_h-badge_h)//2; d.rounded_rectangle([bx0,by0,bx1,by0+badge_h],radius=16,fill=RED)
    _,_,boff=wbox(d,badge,f_badge); d.text((bx0+(badge_w-bw)//2,by0+(badge_h-bh)//2-boff),badge,font=f_badge,fill=CREAM)
    ty=top+(card_h-text_h)//2; _,_,poff=wbox(d,it["product"],f_prod); d.text((tx,ty-poff),it["product"],font=f_prod,fill=CREAM)
    sy=ty+ph+6; _,_,soff=wbox(d,before,f_size); d.text((tx,sy-soff),before,font=f_size,fill=SECOND)
    arrow(d,tx+bw0+AP,sy+sh//2); d.text((tx+bw0+AP+AW+AP,sy-soff),after,font=f_size,fill=SECOND)
    img.save(os.path.join(OUT,f'{it["slug"]}.png')); print("rendered",it["slug"],f"({ps}px)")
for it in ITEMS: render(it)
