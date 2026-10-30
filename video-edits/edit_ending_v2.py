from pathlib import Path
import cv2,numpy as np,subprocess,imageio_ffmpeg
from PIL import Image,ImageDraw,ImageFont
from edit_film import fix,font,SRC,ROOT
OUT=ROOT/'lokantra-film-reference-ending.mp4'
# Use the clean opening frame of the supplied reference for its slow cinematic push-in.
hero=np.array(Image.open(ROOT/'ref-0.png').convert('RGB'))
# The first frame has faint incoming letters on the otherwise flat wall.
# Reconstruct that small wall region from the clean pixels above and below it.
y0,y1,x0,x1=350,665,110,1030
w=np.linspace(0,1,y1-y0)[:,None,None]
wall=((1-w)*hero[y0-1:y0,x0:x1]+w*hero[y1:y1+1,x0:x1]).astype(np.uint8)
hero[y0:y1,x0:x1]=wall
hero=Image.fromarray(hero)
mark=Image.open(ROOT.parent/'static/image/lokantra_emblem.png').convert('RGBA');mark.thumbnail((160,160),Image.Resampling.LANCZOS)
white=(245,245,247);cyan=(0,215,228)
head=font(120,True);sub=font(37);brand=font(128,True);tag=font(48);url=font(34);button=font(30,True)
def ease(x):x=max(0,min(1,x));return 1-(1-x)**3
def centered(d,y,text,ft,color):d.text(((1920-d.textlength(text,font=ft))/2,y),text,font=ft,fill=color)
def shot(s):
 z=1+.025*min(s/3.6,1);ww=int(1920/z);hh=int(1080/z);im=hero.crop(((1920-ww)//2,(1080-hh)//2,(1920+ww)//2,(1080+hh)//2)).resize((1920,1080),Image.Resampling.BICUBIC)
 overlay=Image.new('RGB',(1920,1080));d=ImageDraw.Draw(overlay);alpha=ease((s-.12)/.5);dy=int(24*(1-alpha))
 d.text((130,365+dy),'Predict',font=head,fill=white);d.text((130,500+dy),'the unseen.',font=head,fill=white)
 d.text((137,700),'Rehearse your next move.',font=sub,fill=(190,190,196))
 # Text-only overlay keeps the photograph intact.
 mask=overlay.convert('L').point(lambda p:int(p*alpha));im.paste(overlay,(0,0),mask)
 fade=min(1,s/.22,max(0,(3.65-s)/.2));return (np.array(im)*fade).astype(np.uint8)
def card(s):
 im=Image.new('RGB',(1920,1080));a=ease(s/.45);dy=int(24*(1-a));im.paste(mark,((1920-mark.width)//2,180+dy),mark)
 d=ImageDraw.Draw(im);centered(d,386+dy,'LOKĀNTRA',brand,white)
 centered(d,586+dy,'Simulate your next move.',tag,white)
 centered(d,719+dy,'lokantra.vercel.app',url,cyan)
 d.rounded_rectangle((745,827+dy,1175,911+dy),radius=42,fill=white)
 centered(d,850+dy,'Start Simulation  →',button,(9,9,12))
 return (np.array(im)*a).astype(np.uint8)
def ending(s):return shot(s) if s<3.65 else card(s-3.65)
for s in [1.5,5.5]:Image.fromarray(ending(s)).save(ROOT/f'revised-ending-{s}.png')
if __name__=='__main__':
 import sys
 if '--render' not in sys.argv:raise SystemExit()
 exe=imageio_ffmpeg.get_ffmpeg_exe();flt='[1:a]asplit=2[a][b];[a]atrim=0:35.5,asetpts=PTS-STARTPTS[a1];[b]atrim=29.5:38,asetpts=PTS-STARTPTS[b1];[a1][b1]acrossfade=d=0.5:c1=tri:c2=tri,afade=t=out:st=42.6:d=0.9[aout]'
 cmd=[exe,'-y','-f','rawvideo','-vcodec','rawvideo','-s','1920x1080','-pix_fmt','rgb24','-r','60','-i','-','-i',str(SRC),'-filter_complex',flt,'-map','0:v','-map','[aout]','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','aac','-b:a','256k','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart','-t','43.5',str(OUT)]
 log=open(ROOT/'render-v2.log','w');p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log);c=cv2.VideoCapture(str(SRC))
 try:
  for i in range(2610):
   t=i/60
   if i<2130:
    ok,f=c.read();assert ok;rgb=fix(f,t)
   else:rgb=ending(t-35.5)
   p.stdin.write(rgb.tobytes())
   if i%600==0:print(f'{i}/2610',flush=True)
 finally:c.release();p.stdin.close()
 assert p.wait()==0;log.close();print(OUT,flush=True)
