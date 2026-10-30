from pathlib import Path
import cv2, numpy as np, math, subprocess, imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont, ImageFilter
ROOT=Path(__file__).resolve().parent
SRC=Path(r'C:/Users/vedha/Downloads/lokantra-film.mp4')
OUT=ROOT/'lokantra-film-fixed.mp4'
FONT=Path('C:/Windows/Fonts')
def font(s,bold=False,mono=False):return ImageFont.truetype(str(FONT/('consola.ttf' if mono else 'arialbd.ttf' if bold else 'arial.ttf')),s)
F={k:font(*v) for k,v in {'reply':(36,True),'label':(22,False,True),'report':(32,True),'brand':(66,True),'hero':(88,True),'sub':(29,False),'url':(30,False,True),'small':(19,False,True)}.items()}
# Real project mark, preserved with original transparency.
emblem=Image.open(ROOT.parent/'static/image/lokantra_emblem.png').convert('RGBA');emblem.thumbnail((108,108),Image.Resampling.LANCZOS)
rng=np.random.default_rng(9)
pts=[]
for i in range(175):
 z=1-2*(i+.5)/175;a=i*2.3999632297;r=math.sqrt(1-z*z);pts.append((r*math.cos(a),z,r*math.sin(a)))
pts=np.array(pts);dist=np.linalg.norm(pts[:,None,:]-pts[None,:,:],axis=2);edges=np.argwhere((dist<.33)&(dist>.001));edges=edges[edges[:,0]<edges[:,1]]
# Low-contrast glow leaves type highly readable.
y,x=np.mgrid[0:1080,0:1920];g=np.exp(-(((x-1430)/510)**2+((y-530)/470)**2));bg=np.zeros((1080,1920,3),np.uint8)
for c,v in enumerate([7,22,26]):bg[:,:,c]=(g*v+np.array([3,5,9])[c]).astype(np.uint8)
base=Image.fromarray(bg)
def outro(t):
 im=base.copy();d=ImageDraw.Draw(im);a=(t-35.5)*.15;rot=np.array([[math.cos(a),0,math.sin(a)],[0,1,0],[-math.sin(a),0,math.cos(a)]])
 p=pts@rot.T;xy=p[:,:2]*335+np.array([1440,525])
 for i,j in edges:
  dep=(p[i,2]+p[j,2]+2)/4;co=(int(15+dep*10),int(30+dep*65),int(40+dep*75));d.line([tuple(xy[i]),tuple(xy[j])],fill=co,width=1)
 for i in np.argsort(p[:,2]):
  xx,yy=xy[i];dep=(p[i,2]+1)/2;r=2+dep*2;col=(145,222,53) if i%13==0 else (int(30+100*dep),int(90+145*dep),int(110+135*dep));d.ellipse((xx-r,yy-r,xx+r,yy+r),fill=col)
 # Central node with clean, subtle rings.
 d.ellipse((1372,457,1508,593),outline=(28,85,94),width=2);d.ellipse((1390,475,1490,575),fill=(5,19,25),outline=(69,191,204),width=2)
 d.ellipse((1428,513,1452,537),fill=(157,236,66))
 im.alpha_composite(emblem,(120,205)) if im.mode=='RGBA' else im.paste(emblem,(120,205),emblem)
 d=ImageDraw.Draw(im);d.text((246,224),'LOKĀNTRA',font=F['brand'],fill=(244,247,249))
 d.text((128,410),'Rehearse',font=F['hero'],fill=(244,247,249));d.text((128,508),'tomorrow.',font=F['hero'],fill=(106,228,219))
 d.text((132,642),'Swarm intelligence. Real-world decisions.',font=F['sub'],fill=(155,171,182))
 d.line((132,751,850,751),fill=(38,53,61),width=1)
 d.text((132,788),'lokantra.vercel.app',font=F['url'],fill=(230,240,244));d.line((794,817,818,793),fill=(151,228,70),width=3);d.line((798,793,818,793,818,813),fill=(151,228,70),width=3)
 d.text((1280,936),'EXPLORE POSSIBLE FUTURES',font=F['small'],fill=(112,144,153))
 fade=min(1,max(0,(t-35.5)/.22));return np.array(im)*fade

def fix(frame,t):
 rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
 if 24.2<=t<25.5:
  # Replace the reply including its original growing bubble and any overflow.
  alpha=min(1,float(rgb[575:610,842:1000].max())/180)
  rgb[535:770,790:1920]=0
  if alpha>0:
   layer=Image.new('RGB',(1130,235));d=ImageDraw.Draw(layer)
   d.rounded_rectangle((30,25,930,207),radius=30,fill=(30,30,32),outline=(53,53,56),width=1)
   d.text((61,48),'agent #0402',font=F['label'],fill=(177,177,183))
   lines=['Because TigerGraph node #402','breached critical liquidity.']
   count=max(0,int((t-24.23)*100));a=lines[0][:count];b=lines[1][:max(0,count-len(lines[0]))]
   d.text((61,84),a,font=F['reply'],fill=(245,245,247));d.text((61,129),b,font=F['reply'],fill=(245,245,247))
   rgb[535:770,790:1920]=(np.array(layer)*alpha).astype(np.uint8)
 if 28.3<=t<30:
  # Track the filename during the card entrance; inpaint only the original glyphs.
  crop=rgb[495:563,750:1202].copy();mask=(crop.min(axis=2)>55).astype(np.uint8)*255
  if mask.sum()>255*40:
   yy,xx=np.where(mask>0);level=min(1,float(np.percentile(crop[mask>0],95))/245)
   mask=cv2.dilate(mask,np.ones((5,5),np.uint8));weight=np.linspace(0,1,68)[:,None,None]; clean=((1-weight)*rgb[494:495,750:1202]+weight*rgb[563:564,750:1202]).astype(np.uint8)
   rgb[495:563,750:1202]=clean
   im=Image.fromarray(rgb);d=ImageDraw.Draw(im);d.text((778,514),'Prediction_Report.pdf',font=F['report'],fill=tuple([int(245*level)]*3));rgb=np.array(im)
 if t>=35.5:rgb=np.clip(outro(t),0,255).astype(np.uint8)
 return rgb

def preview():
 c=cv2.VideoCapture(str(SRC))
 for t in [25,29,37.5]:
  c.set(cv2.CAP_PROP_POS_MSEC,t*1000);ok,f=c.read();Image.fromarray(fix(f,t)).save(ROOT/f'fixed-{t}.png')
 c.release()
def render():
 exe=imageio_ffmpeg.get_ffmpeg_exe();cmd=[exe,'-y','-f','rawvideo','-vcodec','rawvideo','-s','1920x1080','-pix_fmt','rgb24','-r','60','-i','-','-i',str(SRC),'-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','17','-pix_fmt','yuv420p','-c:a','copy','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart',str(OUT)]
 log=open(ROOT/'render.log','w');p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log);c=cv2.VideoCapture(str(SRC));i=0
 try:
  while True:
   ok,f=c.read()
   if not ok:break
   p.stdin.write(fix(f,i/60).tobytes());i+=1
   if i%300==0:print(f'{i}/2280 frames',flush=True)
 finally:c.release();p.stdin.close()
 code=p.wait();log.close();assert code==0;print(OUT,flush=True)
if __name__=='__main__':
 import sys
 preview()
 if '--render' in sys.argv:render()
