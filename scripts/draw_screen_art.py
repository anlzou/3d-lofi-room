"""Original low-resolution screen artwork, no external game assets."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'blender/textures';out.mkdir(exist_ok=True)
im=Image.new('RGB',(256,192),'#29394e');d=ImageDraw.Draw(im)
for y in range(192):
    t=y/192;d.line((0,y,255,y),fill=(int(31+29*t),int(43+24*t),int(65+22*t)))
for x,y in [(12,33),(43,67),(79,24),(122,47),(205,27),(235,69),(183,84)]:d.rectangle((x,y,x+1,y+1),fill='#d9cdb1')
d.ellipse((174,31,206,63),fill='#e6cd92');d.ellipse((164,25,196,57),fill='#29394e')
for x,y,w,h in [(0,121,40,54),(43,108,33,67),(83,126,50,49),(143,96,32,79),(185,119,62,56)]:
    d.rectangle((x,y,x+w,y+h),fill='#40536a')
    for xx in range(x+6,x+w-3,10):
        for yy in range(y+8,y+h-3,13):d.rectangle((xx,yy,xx+3,yy+4),fill='#839091')
for x,y,w in [(0,167,83),(107,142,64),(204,160,52)]:
    d.rectangle((x,y,x+w,y+5),fill='#a4ad80');d.rectangle((x,y+6,x+w,191),fill='#805b53')
    for xx in range(x,x+w,14):d.line((xx,y+9,xx+8,y+9),fill='#b28b71')
# An original little courier crossing rooftops with a scarf.
d.rectangle((119,122,129,131),fill='#d8bc91');d.rectangle((117,119,131,123),fill='#c28165')
d.rectangle((120,132,130,139),fill='#82a6a1');d.rectangle((129,131,140,134),fill='#cc9574')
d.rectangle((119,139,122,142),fill='#ead8b5');d.rectangle((127,139,130,142),fill='#ead8b5')
d.point((128,126),fill='#253342')
for x,y in [(69,142),(91,124),(173,116)]:d.ellipse((x,y,x+5,y+5),outline='#e8b769',width=2)
d.rectangle((6,6,249,20),fill='#202d3e');d.text((12,9),'MOON HOP    001990     * * *',fill='#d9cdb1')
im.resize((512,384),Image.Resampling.NEAREST).save(out/'screen-crt-original.png')
im=Image.new('RGB',(256,192),'#9da99c');d=ImageDraw.Draw(im)
d.rectangle((0,0,255,13),fill='#e7e0c9');d.text((6,2),'File   Edit   Notes       17:20',fill='#354341')
d.rectangle((19,32,228,164),fill='#3d514b');d.rectangle((16,28,225,160),fill='#e6dfcb',outline='#42554d',width=2)
d.rectangle((18,30,223,43),fill='#c1c8b1');d.text((63,32),'Night notes',fill='#344a43')
d.text((28,56),'SEPTEMBER 1999',fill='#4e6358')
for y,w in [(80,149),(93,162),(106,117),(126,142)]:d.line((28,y,w,y),fill='#809181',width=2)
d.rectangle((28,142,31,149),fill='#4e6358')
im.resize((512,384),Image.Resampling.NEAREST).save(out/'screen-mac-original.png')
print('ORIGINAL_SCREEN_ART_OK')
atlas=Image.new('RGB',(768,384),'#ddd3b6')
for i,(title,bg,ink,accent) in enumerate([('NIGHT\nSHIFT','#dbc6a2','#3e5362','#b77455'),('MOON\nRADIO','#9babb0','#34424b','#d5b790'),('OFF\nLINE','#c28972','#473f52','#ddd0b4')]):
    card=Image.new('RGB',(256,384),bg);p=ImageDraw.Draw(card)
    bold=ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf',44);small=ImageFont.truetype('C:/Windows/Fonts/consola.ttf',12)
    p.rectangle((10,10,245,373),outline=ink,width=3)
    p.text((21,19),'VOL. 03   /   SEPTEMBER 1999',font=small,fill=ink)
    p.multiline_text((19,42),title,font=bold,fill=ink,spacing=-8)
    p.ellipse((77,153,223,299),fill=accent)
    for y in range(157,299,7):
        for x in range(77,223,7):
            if (x-150)**2+(y-226)**2<70**2:p.ellipse((x,y,x+2,y+2),fill=ink)
    p.polygon([(18,288),(65,207),(105,261),(153,230),(235,311),(235,327),(18,327)],fill=ink)
    p.text((20,338),'SMALL HOURS / BIG DREAMS',font=small,fill=ink)
    p.text((20,356),'ORIGINAL PRINT   NO. 0'+str(i+1),font=small,fill=ink)
    atlas.paste(card,(256*i,0))
atlas.save(out/'poster-atlas-original.png')
print('ORIGINAL_POSTER_ART_OK')
