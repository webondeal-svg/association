import os, sys, numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor, white
from reportlab.lib.utils import ImageReader

# Usage : python3 build.py sortie.pdf [fond_perdu_en_pt]   (3 mm = 8.504 pt)
D = os.path.dirname(os.path.abspath(__file__)) + '/'
FD = D + 'fonts/'
for n in ['Lato-Regular', 'Lato-Bold', 'Lato-Black', 'Playfair-Italic']:
    pdfmetrics.registerFont(TTFont(n, FD + n + '.ttf'))

RED = HexColor('#A3141E'); DARKRED = HexColor('#7A0C16'); INK = HexColor('#16181D')
NAVY = HexColor('#3B4566'); GREY = HexColor('#5B6275'); BG = HexColor('#F6F2F2')
PINK = HexColor('#F8E4E6'); LINE = HexColor('#E6DCDD')

W, H = 595.276, 841.89
BLEED = float(sys.argv[2]) if len(sys.argv) > 2 else 0
OUT = sys.argv[1]
PHOTO_H = 425

def Y(t): return H - t

# ---------- photo composite with left white fade ----------
def photo_layer():
    src = Image.open(D + 'photo-enfant.jpg').convert('RGB')
    top, bottom = -BLEED, PHOTO_H
    k = (bottom - top) / src.height            # pt per px
    face_px, face_pt = 1040, 470               # child's face centre
    off = face_pt - face_px * k               # page x of photo's left edge
    left, right = -BLEED, W + BLEED
    wpx = int(round((right - left) / k))
    canvas_img = Image.new('RGB', (wpx, src.height), 'white')
    canvas_img.paste(src, (int(round((off - left) / k)), 0))
    a = np.asarray(canvas_img).astype(float)
    xs = left + (np.arange(wpx) + .5) * k
    t = np.clip((xs - 250) / (400 - 250), 0, 1)
    t = t * t * (3 - 2 * t)                    # smoothstep
    a = a * t[None, :, None] + 255 * (1 - t[None, :, None])
    img = Image.fromarray(a.astype('uint8'))
    return ImageReader(img), left, top, right - left, bottom - top

def text(c, x, t, s, font, size, color, cs=0, anchor='l'):
    c.setFont(font, size); c.setFillColor(color)
    w = pdfmetrics.stringWidth(s, font, size) + cs * (len(s) - 1)
    if anchor == 'c': x -= w / 2
    if anchor == 'r': x -= w
    to = c.beginText(x, Y(t)); to.setFont(font, size); to.setCharSpace(cs); to.textOut(s); c.drawText(to)
    return w

def fit(s, font, size, maxw):
    while pdfmetrics.stringWidth(s, font, size) > maxw: size -= .1
    return size

c = canvas.Canvas(OUT, pagesize=(W + 2 * BLEED, H + 2 * BLEED), initialFontName='Lato-Regular', initialFontSize=10)
c.setTitle('Cœur et Rahma — Flyer dons'); c.setAuthor('Cœur et Rahma')
c.translate(BLEED, BLEED)

# backgrounds
c.setFillColor(white); c.rect(-BLEED, -BLEED, W + 2 * BLEED, H + 2 * BLEED, 0, 1)
img, x, t, w, h = photo_layer()
c.drawImage(img, x, Y(t + h), w, h)

# ---------- header: logo + brand ----------
LX = 40
logo = Image.open(D + 'logo.png'); lw = 92; lh = lw * logo.height / logo.width
c.drawImage(ImageReader(logo), LX, Y(22 + lh), lw, lh, mask='auto')
t0 = 22 + lh + 18
text(c, LX, t0, 'CŒUR ET RAHMA', 'Lato-Black', 15, INK, cs=0.3)
for i, l in enumerate(['ACTIONS HUMANITAIRES', 'EN FRANCE, AU MAROC', 'ET À L’INTERNATIONAL']):
    text(c, LX, t0 + 14 + i * 10, l, 'Lato-Bold', 6.8, NAVY, cs=1.1)
c.setFillColor(RED); c.rect(LX, Y(t0 + 44), 26, 2, 0, 1)

# headline
hs = 34; hb = t0 + 86
text(c, LX - 2, hb, 'ENSEMBLE,', 'Lato-Black', hs, INK)
text(c, LX - 2, hb + hs * 1.08, 'FAISONS', 'Lato-Black', hs, RED)
text(c, LX - 2, hb + hs * 2.16, 'LA DIFFÉRENCE.', 'Lato-Black', hs, RED)
sb = hb + hs * 2.16 + 18
c.setFillColor(RED); c.rect(LX, Y(sb), 40, 2, 0, 1)
for i, l in enumerate(['Chaque don peut devenir', 'une aide concrète pour une', 'personne qui en a besoin.']):
    text(c, LX, sb + 22 + i * 16, l, 'Lato-Regular', 12.5, GREY)
text(c, LX, sb + 22 + 2 * 16 + 24, 'SOLIDARITÉ  •  DIGNITÉ  •  OPPORTUNITÉS', 'Lato-Bold', 7, RED, cs=1.2)

# tagline on photo (solid label, not on the shirt stripes)
bx, by, bw, bh = W - 28 - 168, 350, 168, 58
c.saveState(); c.setFillColor(DARKRED); c.setFillAlpha(0.88)
c.roundRect(bx, Y(by + bh), bw, bh, 6, 0, 1); c.restoreState()
for i, l in enumerate(['DES ENFANTS AUJOURD’HUI,', 'UN MEILLEUR DEMAIN.']):
    text(c, bx + 12, by + 23 + i * 15, l, 'Lato-Bold', 9.5, white, cs=0.6)
c.setFillColor(white); c.rect(bx + 12, Y(by + 10), 22, 1.5, 0, 1)

# ---------- support section ----------
ST, SB = PHOTO_H, 670
c.setFillColor(BG); c.rect(-BLEED, Y(SB), W + 2 * BLEED, SB - ST, 0, 1)
M = 28
c.setFillColor(RED); c.rect(M, Y(ST + 54), 2.5, 38, 0, 1)
w1 = text(c, M + 12, ST + 38, 'SOUTENEZ ', 'Lato-Black', 22, RED)
text(c, M + 12 + w1, ST + 38, 'NOS ACTIONS', 'Lato-Black', 22, INK)
text(c, M + 12, ST + 54, '3 moyens simples de nous soutenir :', 'Lato-Regular', 11, GREY)

CT, CB = ST + 70, SB - 12
widths = [150, 219, 160]; gap = (W - 2 * M - sum(widths)) / 2
xs = [M, M + widths[0] + gap, M + widths[0] + widths[1] + 2 * gap]

def card(i, title):
    x, w = xs[i], widths[i]
    c.setFillColor(white); c.setStrokeColor(LINE); c.setLineWidth(.6)
    c.roundRect(x, Y(CB), w, CB - CT, 8, 1, 1)
    c.setFillColor(RED); c.circle(x + 16, Y(CT + 17), 8, 0, 1)
    text(c, x + 16, CT + 20.3, str(i + 1), 'Lato-Black', 9, white, anchor='c')
    text(c, x + 30, CT + 21, title, 'Lato-Black', 11.5, INK)
    return x, w

# 1 PayPal
x, w = card(0, 'Par PayPal')
q = 100
c.drawImage(ImageReader(D + 'qr-paypal.jpg'), x + (w - q) / 2, Y(CT + 34 + q), q, q)
text(c, x + w / 2, CT + 34 + q + 13, 'Scannez ce QR code', 'Lato-Regular', 8.5, GREY, anchor='c')
text(c, x + w / 2, CT + 34 + q + 24, 'pour faire un don en ligne.', 'Lato-Regular', 8.5, GREY, anchor='c')

# 2 Virement
x, w = card(1, 'Par virement bancaire')
# bank icon
ix, it = x + w - 34, CT + 8
c.setFillColor(RED); p = c.beginPath()
p.moveTo(ix, Y(it + 9)); p.lineTo(ix + 11, Y(it + 2)); p.lineTo(ix + 22, Y(it + 9)); p.close(); c.drawPath(p, 0, 1)
c.rect(ix + 1, Y(it + 11), 20, 1.6, 0, 1)
for k in range(3): c.rect(ix + 3.5 + k * 6.2, Y(it + 20), 2.6, 8.2, 0, 1)
c.rect(ix, Y(it + 23), 22, 2.2, 0, 1)
rows = [('Titulaire', 'CŒUR ET RAHMA'), ('IBAN', 'FR76 3008 7338 5600 0213 8700 129'),
        ('BIC', 'CMCIFRPP'), ('RIB', '30087 33856 00021387001 29')]
c.setFillColor(PINK); c.roundRect(x + 10, Y(CB - 12), w - 20, CB - 12 - (CT + 40), 5, 0, 1)
vx = x + 54; vs = min(fit(v, 'Lato-Bold', 9, x + w - 18 - vx) for _, v in rows)
for i, (k_, v) in enumerate(rows):
    tt = CT + 64 + i * 23
    text(c, x + 18, tt, k_, 'Lato-Regular', 8, GREY)
    text(c, vx, tt, v, 'Lato-Bold', vs, INK)

# 3 Chèque
x, w = card(2, 'Par chèque')
ix, it = x + w - 36, CT + 9
c.setStrokeColor(RED); c.setLineWidth(1.3); c.roundRect(ix, Y(it + 15), 24, 15, 2, 1, 0)
c.setLineWidth(1); c.line(ix + 4, Y(it + 5), ix + 13, Y(it + 5)); c.line(ix + 4, Y(it + 10), ix + 20, Y(it + 10))
tt = CT + 52
text(c, x + 14, tt, 'À l’ordre de :', 'Lato-Regular', 8.5, GREY)
text(c, x + 14, tt + 13, 'Mr ES-ESEDDIK', 'Lato-Black', 10, INK)
text(c, x + 14, tt + 40, 'À envoyer à :', 'Lato-Regular', 8.5, GREY)
for i, l in enumerate(['2 rue des Aulnes', 'Résidence Bois Briard', '77680 Roissy-en-Brie']):
    text(c, x + 14, tt + 54 + i * 13, l, 'Lato-Bold', 9, INK)

# ---------- actions row ----------
AT = SB + 26
labels = ['AIDE ALIMENTAIRE', 'SOUTIEN AUX ENFANTS', 'ACTIONS SOLIDAIRES']
colw = (W - 2 * M) / 3
def icon(i, cx, cy):
    c.setStrokeColor(RED); c.setFillColor(RED); c.setLineWidth(1.3)
    if i == 0:   # bowl + steam
        p = c.beginPath(); p.moveTo(cx - 8, cy + 1); p.lineTo(cx + 8, cy + 1)
        p.curveTo(cx + 8, cy - 7, cx - 8, cy - 7, cx - 8, cy + 1); c.drawPath(p, 1, 1)
        c.line(cx - 10, cy + 1, cx + 10, cy + 1)
        for dx in (-4, 0, 4):
            p = c.beginPath(); p.moveTo(cx + dx, cy + 4); p.curveTo(cx + dx + 2, cy + 6, cx + dx - 2, cy + 8, cx + dx, cy + 10); c.drawPath(p, 1, 0)
    elif i == 1:  # adult + child
        c.circle(cx - 3.5, cy + 5, 3, 0, 1); c.circle(cx + 5.5, cy + 2, 2.3, 0, 1)
        p = c.beginPath(); p.moveTo(cx - 9.5, cy - 8); p.curveTo(cx - 9.5, cy + 2, cx + 2.5, cy + 2, cx + 2.5, cy - 8); p.close(); c.drawPath(p, 0, 1)
        p = c.beginPath(); p.moveTo(cx + 1.5, cy - 8); p.curveTo(cx + 1.5, cy - 1, cx + 9.5, cy - 1, cx + 9.5, cy - 8); p.close(); c.drawPath(p, 0, 1)
    else:        # heart
        p = c.beginPath(); p.moveTo(cx, cy - 8)
        p.curveTo(cx - 12, cy, cx - 7, cy + 10, cx, cy + 4)
        p.curveTo(cx + 7, cy + 10, cx + 12, cy, cx, cy - 8); c.drawPath(p, 0, 1)
ext = []
for i, l in enumerate(labels):
    x0 = M + i * colw
    lw_ = pdfmetrics.stringWidth(l, 'Lato-Bold', 9) + 0.8 * (len(l) - 1)
    gx = x0 + (colw - (36 + 10 + lw_)) / 2
    ext.append((gx, gx + 46 + lw_))
    c.setFillColor(PINK); c.circle(gx + 18, Y(AT), 18, 0, 1)
    icon(i, gx + 18, Y(AT))
    text(c, gx + 46, AT + 3.2, l, 'Lato-Bold', 9, INK, cs=0.8)
for i in (1, 2):
    sx = (ext[i - 1][1] + ext[i][0]) / 2
    c.setStrokeColor(LINE); c.setLineWidth(.8); c.line(sx, Y(AT - 14), sx, Y(AT + 14))

# ---------- footer ----------
FT = AT + 30
c.setFillColor(DARKRED); c.rect(-BLEED, -BLEED, W + 2 * BLEED, H - FT + BLEED, 0, 1)
fh = H - FT
qx, qw = 330, W - M - 330
qt, qb = FT + 16, H - 16
c.setFillColor(white); c.roundRect(qx, Y(qb), qw, qb - qt, 8, 0, 1)
qc = qx + qw / 2; mid = (qt + qb) / 2
text(c, qc, mid - 9, '« Allah aide Son serviteur', 'Playfair-Italic', 12, INK, anchor='c')
text(c, qc, mid + 7, 'tant que celui-ci aide son frère. »', 'Playfair-Italic', 12, INK, anchor='c')
c.setFillColor(RED); c.rect(qc - 12, Y(mid + 15), 24, 1.5, 0, 1)
text(c, qc, mid + 27, 'Sahih Muslim, 2699a', 'Playfair-Italic', 8.5, NAVY, anchor='c')

ct = FT + 30
# mail icon
c.setStrokeColor(white); c.setLineWidth(1)
c.rect(M, Y(ct + 1), 13, 9, 1, 0); c.line(M, Y(ct - 8), M + 6.5, Y(ct - 3.5)); c.line(M + 13, Y(ct - 8), M + 6.5, Y(ct - 3.5))
text(c, M + 20, ct, 'coeur.rahma@hotmail.com', 'Lato-Regular', 10.5, white)
pt = ct + 20
# phone icon (handset)
c.setFillColor(white); p = c.beginPath()
px, py = M + 1, Y(pt)
p.moveTo(px, py + 6); p.curveTo(px, py - 1, px + 5, py - 3, px + 11, py - 3)
p.lineTo(px + 11, py + 1); p.lineTo(px + 8, py + 1); p.curveTo(px + 6, py + 1, px + 4, py + 3, px + 4, py + 6); p.lineTo(px + 4, py + 9); p.lineTo(px, py + 9); p.close(); c.drawPath(p, 0, 1)
text(c, M + 20, pt, '06 23 02 80 92', 'Lato-Regular', 10.5, white)
c.setFillColor(white); c.rect(M, Y(pt + 15), 26, 1.5, 0, 1)
text(c, M, pt + 33, 'UN PETIT GESTE. UNE GRANDE DIFFÉRENCE.', 'Lato-Bold', 9.5, white, cs=0.8)

c.showPage(); c.save()
print('ok', OUT, 'footer h', fh)
