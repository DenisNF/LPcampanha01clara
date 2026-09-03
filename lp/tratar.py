"""
Tratamento das fotos de fundo — tonaliza para o marinho da marca sem
degradar a imagem. Para trocar as fotos, mude os caminhos em FONTES e rode:
    python3 tratar.py
"""
from PIL import Image, ImageEnhance, ImageFilter
import numpy as np

MARINHO = (13, 30, 47)

FONTES = {
    # saída            origem                                              gama  tint  largura
    "luzes":  ("/mnt/user-data/uploads/robynne-o-HOrhCnQsxnQ-unsplash.jpg", .72,  .55,  3200),
    "galpao": ("/mnt/user-data/uploads/pexels-daniel-andraski-197681005-12234108.jpg", .82, .5, 2800),
}

def tratar(caminho, gama, tint_forca, larg):
    im = Image.open(caminho).convert("RGB")
    # reduzir antes de tratar já suaviza o ruído (supersampling)
    im = im.resize((larg, int(larg*im.size[1]/im.size[0])), Image.LANCZOS)
    im = im.filter(ImageFilter.MedianFilter(size=3))     # tira granulado do escuro

    a = np.asarray(im, dtype=np.float32)/255.
    a = np.power(a, gama)                                 # levanta sombras sem estourar luz

    lum = a @ np.array([.299,.587,.114], dtype=np.float32)
    alvo = np.array(MARINHO, dtype=np.float32)/255.
    claro = np.clip(alvo*3.6, 0, 1)
    tint = alvo[None,None,:]*(1-lum[...,None]) + claro[None,None,:]*lum[...,None]
    a = a*(1-tint_forca) + tint*tint_forca

    a = np.clip(a, 0, 1)
    a = np.where(a > .72, .72 + (a-.72)*.55, a)           # segura as altas luzes

    im = Image.fromarray((np.clip(a,0,1)*255).astype(np.uint8))
    im = ImageEnhance.Contrast(im).enhance(1.06)
    return im.filter(ImageFilter.GaussianBlur(.5))

for nome, (src, gama, tf, larg) in FONTES.items():
    out = tratar(src, gama, tf, larg)
    out.save(f"img/{nome}.webp", "WEBP", quality=82, method=6)
    print(f"{nome}.webp  {out.size}")
