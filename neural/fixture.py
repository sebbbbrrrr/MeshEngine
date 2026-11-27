from PIL import Image, ImageDraw
from pathlib import Path
import sys
p=Path(sys.argv[1]); p.parent.mkdir(parents=True,exist_ok=True)
im=Image.new("RGB",(512,512),(128,128,128))
d=ImageDraw.Draw(im)
d.polygon([(100,160),(270,90),(410,175),(240,250)],fill=(224,224,224))
d.polygon([(100,160),(240,250),(240,420),(100,330)],fill=(170,170,170))
d.polygon([(240,250),(410,175),(410,345),(240,420)],fill=(90,90,90))
im.save(p)
