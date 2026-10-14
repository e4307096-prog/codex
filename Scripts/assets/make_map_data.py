# -*- coding: utf-8 -*-
"""Cephe 1914: harita ham verisini üretir (Content/Map/Raw/*).

Çalıştırma (repo kökünden):
    python3 Scripts/assets/make_map_data.py             # her şey
    python3 Scripts/assets/make_map_data.py --previews  # yalnızca önizlemeler (ham veri hazırsa)

Bağımlılıklar: numpy, scipy, pillow, shapely, geopandas<1.
Sözleşme: Docs/cephe1914-teknik.md ("Veri hattı").
"""
import csv, json, math, os, sys, time, warnings
warnings.filterwarnings('ignore')
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
RAW = os.path.join(ROOT, 'Content', 'Map', 'Raw')
IMG = os.path.join(ROOT, 'Docs', 'img', 'cephe1914')
sys.path.insert(0, HERE)
from map_seeds import SECTIONS, ARMIES, RAILS
from map_relief import RIDGES, PLATEAUS, SHELVES

W, H = 4096, 3112
LON0, LON1, LAT0, LAT1, LATC = -11.0, 46.0, 33.0, 62.0, 48.0
Image.MAX_IMAGE_PIXELS = None


def T(msg, t0=[time.time()]):
    print('[%6.1fs] %s' % (time.time() - t0[0], msg), flush=True)


# ---- projeksiyon: x = (lon+11)*cos48, y = 62-lat; kapsama göre piksele ölçeklenir
def lonlat_to_px(lon, lat):
    return (np.asarray(lon) - LON0) / (LON1 - LON0) * W, (LAT1 - np.asarray(lat)) / (LAT1 - LAT0) * H


def px_to_lonlat(x, y):
    return LON0 + np.asarray(x) / W * (LON1 - LON0), LAT1 - np.asarray(y) / H * (LAT1 - LAT0)


# ---- ülke tablosu
NATIONS = {  # kod: (ad, taraf, sRGB renk (dönem haritası, solgun))
    'FRA': ('Fransa', 'Entente', (112, 148, 190)),
    'GBR': ('Britanya', 'Entente', (214, 140, 150)),
    'RUS': ('Rus İmparatorluğu', 'Entente', (118, 154, 104)),
    'BEL': ('Belçika', 'Entente', (226, 204, 96)),
    'SER': ('Sırbistan', 'Entente', (168, 84, 96)),
    'MNT': ('Karadağ', 'Entente', (150, 96, 112)),
    'GER': ('Alman İmparatorluğu', 'Central', (122, 126, 124)),
    'AUH': ('Avusturya-Macaristan', 'Central', (214, 176, 78)),
    'OTT': ('Osmanlı Devleti', 'Central', (172, 146, 98)),
    'ITA': ('İtalya', 'Neutral', (128, 176, 164)),
    'ROM': ('Romanya', 'Neutral', (176, 128, 156)),
    'BUL': ('Bulgaristan', 'Neutral', (160, 192, 120)),
    'GRE': ('Yunanistan', 'Neutral', (156, 194, 218)),
    'ALB': ('Arnavutluk', 'Neutral', (196, 120, 100)),
    'SWI': ('İsviçre', 'Neutral', (206, 206, 200)),
    'ESP': ('İspanya', 'Neutral', (218, 184, 138)),
    'POR': ('Portekiz', 'Neutral', (186, 156, 176)),
    'NED': ('Hollanda', 'Neutral', (220, 158, 100)),
    'LUX': ('Lüksemburg', 'Neutral', (176, 176, 176)),
    'DEN': ('Danimarka', 'Neutral', (196, 118, 118)),
    'NOR': ('Norveç', 'Neutral', (136, 128, 176)),
    'SWE': ('İsveç', 'Neutral', (146, 176, 208)),
    'PER': ('İran', 'Neutral', (196, 182, 146)),
}
# ülke kodu -> nüfus yoğunluğu (kişi/km2, 1914 tahmini taban)
DENS = dict(GBR=120, FRA=72, BEL=230, LUX=100, NED=180, GER=105, AUH=75, SER=55, MNT=25, ITA=125, SWI=85, ESP=40, POR=60,
            DEN=65, NOR=8, SWE=12, RUS=34, ROM=48, BUL=46, GRE=42, ALB=26, OTT=22, PER=8)
GROUP_OF_COUNTRY = {}
for n in ['France']:
    GROUP_OF_COUNTRY[n] = 'FRA'
for n in ['Algeria', 'Tunisia', 'Morocco']:
    GROUP_OF_COUNTRY[n] = 'FRA_COL'
for n in ['United Kingdom', 'Ireland']:
    GROUP_OF_COUNTRY[n] = 'GBR'
for n in ['Cyprus', 'N. Cyprus']:
    GROUP_OF_COUNTRY[n] = 'GBR_COL'
for n, g in [('Belgium', 'BEL'), ('Luxembourg', 'LUX'), ('Netherlands', 'NED'), ('Italy', 'ITA'), ('Switzerland', 'SWI'),
             ('Spain', 'ESP'), ('Portugal', 'POR'), ('Denmark', 'DEN'), ('Norway', 'NOR'), ('Sweden', 'SWE'),
             ('Greece', 'GRE'), ('Iran', 'PER')]:
    GROUP_OF_COUNTRY[n] = g
# 1914'te bugünkü sınırın dışında kalan parçalar: grup POOL'a aktarılır (Elsass-Lothringen, Güney Tirol/Trentino, Gorizia/Trieste)
AL_POLY = [(5.95, 49.6), (5.95, 48.95), (6.3, 48.75), (6.7, 48.65), (6.95, 48.45), (7.0, 48.3), (7.1, 48.1), (6.98, 47.85),
           (6.9, 47.55), (7.2, 47.4), (8.3, 47.4), (8.3, 49.7)]
TN_POLY = [(10.4, 45.78), (10.9, 45.80), (11.2, 45.95), (11.7, 46.05), (12.0, 46.3), (12.5, 46.6), (12.5, 47.3), (10.4, 47.3)]
TS_POLY = [(13.5, 45.3), (14.3, 45.3), (14.3, 46.7), (13.35, 46.7), (13.35, 46.2), (13.5, 45.95)]


def noise(shape, beta, seed):
    """Periyodik, 1/f^beta güç spektrumlu gürültü, ortalama 0, std 1."""
    rng = np.random.default_rng(seed)
    F = np.fft.rfft2(rng.standard_normal(shape))
    fy = np.fft.fftfreq(shape[0])[:, None]
    fx = np.fft.rfftfreq(shape[1])[None, :]
    k = np.sqrt(fx * fx + fy * fy)
    k[0, 0] = 1.0
    F *= k ** (-beta / 2.0)
    F[0, 0] = 0
    n = np.fft.irfft2(F, s=shape)
    return ((n - n.mean()) / n.std()).astype(np.float32)


def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


def parse_seeds():
    seeds = []
    for owner, group, text in SECTIONS:
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split(';')
            name, lon, lat = parts[0], float(parts[1]), float(parts[2])
            fl = {}
            if len(parts) > 3:
                for tok in parts[3].split(','):
                    tok = tok.strip()
                    if '=' in tok:
                        k, v = tok.split('=')
                        fl[k] = v
                    elif tok:
                        fl[tok] = True
            seeds.append(dict(name=name, lon=lon, lat=lat, owner=owner, group=group, ctrl=fl.get('occ', owner),
                              tag=fl.get('t'), fort=bool(fl.get('fort')), ind=fl.get('i'), city=float(fl.get('c', 0))))
    return seeds


def poly_mask(pts):
    im = Image.new('L', (W, H), 0)
    xy = [tuple(float(v) for v in lonlat_to_px(lo, la)) for lo, la in pts]
    ImageDraw.Draw(im).polygon(xy, fill=1)
    return np.array(im, bool)


def rasterize_countries():
    import geopandas as gpd
    from shapely.geometry import box
    w = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    clip = box(LON0 - 1, LAT0 - 1, LON1 + 1, LAT1 + 1)
    im = Image.new('L', (W, H), 0)
    dr = ImageDraw.Draw(im)
    names = {}
    idx = 0
    for _, row in w.iterrows():
        if row['name'] == 'Libya':  # kapsamda yalnızca ince bir şerit; dışarıda bırakılır
            continue
        g = row.geometry.buffer(0).intersection(clip)
        if g.is_empty:
            continue
        idx += 1
        names[idx] = row['name']
        polys = [g] if g.geom_type == 'Polygon' else [p for p in getattr(g, 'geoms', []) if p.geom_type == 'Polygon']
        for p in polys:
            xs, ys = lonlat_to_px(*np.array(p.exterior.coords).T)
            xy = list(zip(xs.tolist(), ys.tolist()))
            dr.polygon(xy, fill=idx)
    return np.array(im), names


# ------------------------------------------------------------------ bölge ataması
def build_provinces():
    T('ülkeler rasterize ediliyor')
    cidx, cnames = rasterize_countries()
    land = cidx > 0
    seeds = parse_seeds()
    groups = []
    for s in seeds:
        if s['group'] not in groups:
            groups.append(s['group'])
    if 'POOL' not in groups:
        groups.append('POOL')
    gid = {g: i + 1 for i, g in enumerate(groups)}
    grp = np.zeros((H, W), np.uint8)
    lut = np.zeros(256, np.uint8)
    for i, n in cnames.items():
        g = GROUP_OF_COUNTRY.get(n, 'POOL')
        lut[i] = gid.get(g, gid['POOL'])
    grp = lut[cidx]
    # 1914 sınır istisnaları
    fr = np.zeros(256, bool)
    for i, n in cnames.items():
        if n == 'France':
            fr[i] = True
    grp[fr[cidx] & poly_mask(AL_POLY)] = gid['POOL']
    it = np.zeros(256, bool)
    for i, n in cnames.items():
        if n == 'Italy':
            it[i] = True
    grp[it[cidx] & (poly_mask(TN_POLY) | poly_mask(TS_POLY))] = gid['POOL']
    T('kara pikseli: %d' % land.sum())

    comp, ncomp = ndi.label(land, structure=np.ones((3, 3)))
    # tohum konumlarını kendi grubunun karasına tuttur
    for s in seeds:
        x, y = lonlat_to_px(s['lon'], s['lat'])
        s['x0'], s['y0'] = float(x), float(y)
    gtrees = {}
    for g in groups:
        ys, xs = np.nonzero(grp[::2, ::2] == gid[g])
        if len(ys) == 0:
            continue
        pts = np.stack([xs * 2.0, ys * 2.0], 1)
        gtrees[g] = (cKDTree(pts), pts)
    for s in seeds:
        if s['group'] not in gtrees:
            raise SystemExit('grup karasız: %s (%s)' % (s['group'], s['name']))
        tr, pts = gtrees[s['group']]
        d, j = tr.query([s['x0'], s['y0']])
        s['x'], s['y'] = float(pts[j][0]), float(pts[j][1])
        s['snap'] = float(d)
        s['comp'] = int(comp[int(s['y']), int(s['x'])])
        if d > 25:
            print('  uyarı: tohum kıyıya/ülkeye %.0f px taşındı: %s' % (d, s['name']))

    T('domain-warp gürültüsü')
    lw, lh = W // 4, H // 4
    wx = ndi.zoom(noise((lh, lw), 2.8, 11), 4, order=1)
    wy = ndi.zoom(noise((lh, lw), 2.8, 12), 4, order=1)
    wx2 = noise((H // 2, W // 2), 2.2, 13)
    wy2 = noise((H // 2, W // 2), 2.2, 14)
    wx2 = np.kron(wx2, np.ones((2, 2), np.float32))
    wy2 = np.kron(wy2, np.ones((2, 2), np.float32))
    DX = (wx * 22 + wx2 * 7).astype(np.float32)
    DY = (wy * 22 + wy2 * 7).astype(np.float32)
    del wx, wy, wx2, wy2

    A = np.zeros((H, W), np.uint16)
    for g in groups:
        sl = [i for i, s in enumerate(seeds) if s['group'] == g]
        gm = grp == gid[g]
        ys, xs = np.nonzero(gm)
        if len(ys) == 0:
            continue
        cl = comp[ys, xs]
        qx = xs + DX[ys, xs]
        qy = ys + DY[ys, xs]
        out = np.zeros(len(ys), np.int32)
        order = np.argsort(cl, kind='stable')
        cls = cl[order]
        bounds = np.flatnonzero(np.diff(cls)) + 1
        starts = np.concatenate([[0], bounds])
        ends = np.concatenate([bounds, [len(cls)]])
        allpts = np.array([[seeds[i]['x'], seeds[i]['y']] for i in sl])
        alltree = cKDTree(allpts)
        for st, en in zip(starts, ends):
            sel = order[st:en]
            c = cls[st]
            ins = [k for k, i in enumerate(sl) if seeds[i]['comp'] == c]
            if ins:
                tr = cKDTree(allpts[ins])
                _, j = tr.query(np.stack([qx[sel], qy[sel]], 1))
                out[sel] = np.array(ins)[j]
            else:
                _, j = alltree.query(np.stack([qx[sel], qy[sel]], 1))
                out[sel] = j
        gl = np.array(sl)
        A[ys, xs] = gl[out] + 1  # geçici kimlik = tohum sırası + 1
        T('grup %s: %d bölge, %d piksel' % (g, len(sl), len(ys)))
    del DX, DY
    # boş kalan tohumları at, kimlikleri yeniden numarala
    cnt = np.bincount(A.ravel(), minlength=len(seeds) + 1)
    keep = [i for i in range(len(seeds)) if cnt[i + 1] > 0]
    remap = np.zeros(len(seeds) + 2, np.uint16)
    for new, i in enumerate(keep):
        remap[i + 1] = new + 1
    A = remap[A]
    provs = []
    for new, i in enumerate(keep):
        s = seeds[i]
        s['id'] = new + 1
        provs.append(s)
    dropped = [seeds[i]['name'] for i in range(len(seeds)) if i not in keep]
    if dropped:
        print('  piksel almayan tohumlar atıldı:', dropped)
    return A, provs, land, cidx, cnames


# ------------------------------------------------------------------ yükseklik
def build_heightmap(land):
    T('heightmap: gürültü ve sıralar')
    lw, lh = W // 4, H // 4
    X = np.arange(lw)[None, :] / (lw / (LON1 - LON0)) + LON0
    Y = LAT1 - np.arange(lh)[:, None] / (lh / (LAT1 - LAT0))
    base_n = noise((lh, lw), 3.0, 21)
    h = 45 + 55 * (base_n * 0.5 + 0.5).clip(0, 1) * 1.5
    h = h.astype(np.float32)
    for lon, lat, rx, ry, hh in PLATEAUS:
        g = np.exp(-(((X - lon) / rx) ** 2 + ((Y - lat) / ry) ** 2))
        h = np.maximum(h, h * 0.4 + hh * g * (0.85 + 0.15 * base_n))
    mod = noise((lh, lw), 2.4, 22)
    ppd_y = lh / (LAT1 - LAT0)
    ridge = np.zeros((lh, lw), np.float32)
    for name, pts, peak, hw in RIDGES:
        if len(pts) < 2 or peak <= 0:
            continue
        im = Image.new('L', (lw, lh), 255)
        xy = [tuple(float(v) for v in ((lo - LON0) / (LON1 - LON0) * lw, (LAT1 - la) / (LAT1 - LAT0) * lh)) for lo, la in pts]
        ImageDraw.Draw(im).line(xy, fill=0, width=1)
        mask = np.array(im) > 0
        # yalnızca yakın bölgede mesafe hesapla
        ys, xs = np.nonzero(~mask)
        y0, y1 = max(0, int(np.min(np.array(xy)[:, 1]) - 6 * hw * ppd_y)), min(lh, int(np.max(np.array(xy)[:, 1]) + 6 * hw * ppd_y))
        x0, x1 = max(0, int(np.min(np.array(xy)[:, 0]) - 6 * hw * ppd_y)), min(lw, int(np.max(np.array(xy)[:, 0]) + 6 * hw * ppd_y))
        sub = mask[y0:y1, x0:x1]
        if sub.all():
            continue
        d = ndi.distance_transform_edt(sub)
        prof = peak * np.exp(-(d / (hw * ppd_y)) ** 2) * np.clip(0.85 + 0.28 * mod[y0:y1, x0:x1], 0.5, 1.3)
        ridge[y0:y1, x0:x1] = np.maximum(ridge[y0:y1, x0:x1], prof.astype(np.float32))
    h = np.maximum(h, ridge + h * 0.3)
    hf = ndi.zoom(h, 4, order=3).astype(np.float32)
    del h, ridge
    T('heightmap: ince detay')
    n1 = noise((H, W), 2.3, 23)
    rid = 1 - np.abs(n1) / 1.8
    n2 = noise((H, W), 1.6, 24)
    hf = hf + np.clip(hf / 800.0, 0, 1.3) * 320 * (rid - 0.45) + 10 * n2
    del n1, rid, n2
    dland = ndi.distance_transform_edt(land).astype(np.float32)
    cf = 0.3 + 0.7 * smoothstep(dland / 34.0)
    hf = np.clip(hf, 8, 4900) * cf
    hf = np.maximum(hf, 6)
    # deniz derinliği
    sea = ~land
    dsea = ndi.distance_transform_edt(sea).astype(np.float32)
    depth = 3000 * (1 - np.exp(-dsea / 170.0)) + 8
    lw2, lh2 = W // 8, H // 8
    X2 = np.arange(lw2)[None, :] / (lw2 / (LON1 - LON0)) + LON0
    Y2 = LAT1 - np.arange(lh2)[:, None] / (lh2 / (LAT1 - LAT0))
    sh = np.zeros((lh2, lw2), np.float32)
    for lon, lat, rx, ry in SHELVES:
        sh = np.maximum(sh, smoothstep(1.6 - np.sqrt(((X2 - lon) / rx) ** 2 + ((Y2 - lat) / ry) ** 2)))
    sh = ndi.zoom(sh, 8, order=1)
    depth = depth * (1 - sh) + np.minimum(depth, 130) * sh
    depth += 25 * noise((H // 4, W // 4), 2.5, 25).repeat(4, 0).repeat(4, 1) * (dsea > 8)
    depth = np.clip(depth, 4, 3000)
    hm = np.where(land, 8192 + 40 + hf * (57200.0 / 4900.0), 8192 - 24 - depth * 2.7)
    hm = np.clip(hm, 0, 65535).astype(np.uint16)
    return hm, hf, dland, dsea


# ------------------------------------------------------------------ yazım yardımcıları
def srgb_to_lin(c):
    c = np.asarray(c, np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def side_of(code):
    return NATIONS[code][1]


def trench_level(ca, cb, lon, lat):
    codes = {ca, cb}
    if 'SER' in codes or 'MNT' in codes:
        return 2
    if codes & {'FRA', 'BEL', 'GBR'}:
        return 5 if (lat >= 49.9 and lon < 5.5) or (lat >= 50.8) else 4
    if 'OTT' in codes:
        return 1
    return 2 if (lon < 25.5 and lat > 49.0) else 1


def chains_from_edges(edges):
    adj = {}
    for a, b in edges:
        adj.setdefault(a, []).append(b)
        adj.setdefault(b, []).append(a)
    seen = set()
    out = []

    def walk(start, nxt):
        path = [start, nxt]
        seen.add((start, nxt)); seen.add((nxt, start))
        prev, cur = start, nxt
        while len(adj[cur]) == 2:
            n = adj[cur][0] if adj[cur][0] != prev else adj[cur][1]
            if (cur, n) in seen:
                break
            seen.add((cur, n)); seen.add((n, cur))
            path.append(n)
            prev, cur = cur, n
        return path
    for v in list(adj):
        if len(adj[v]) != 2:
            for n in adj[v]:
                if (v, n) not in seen:
                    out.append(walk(v, n))
    for v in list(adj):
        for n in adj[v]:
            if (v, n) not in seen:
                out.append(walk(v, n))
    return out


def smooth_chain(path):
    from shapely.geometry import LineString
    pts = np.array(path, float)
    if len(pts) < 3:
        return pts
    ls = LineString(pts)
    n = max(3, int(ls.length / 5))
    res = np.array([ls.interpolate(i / (n - 1), normalized=True).coords[0] for i in range(n)])
    k = 4
    sm = res.copy()
    for i in range(1, n - 1):
        a, b = max(0, i - k), min(n, i + k + 1)
        sm[i] = res[a:b].mean(0)
    from shapely.geometry import LineString as LS
    sm = np.array(LS(sm).simplify(0.7).coords)
    return sm


def make_fronts(A, provs):
    ctrl = {p['id']: p['ctrl'] for p in provs}
    side = np.zeros(len(provs) + 1, np.int8)
    for p in provs:
        side[p['id']] = {'Entente': 1, 'Central': 2}.get(side_of(p['ctrl']), 0)
    res = []
    edges = {}
    ah, bh = A[:, :-1], A[:, 1:]
    m = (ah != bh) & (ah > 0) & (bh > 0) & (side[ah] > 0) & (side[bh] > 0) & (side[ah] != side[bh])
    ys, xs = np.nonzero(m)
    for y, x in zip(ys.tolist(), xs.tolist()):
        a, b = int(ah[y, x]), int(bh[y, x])
        k = (a, b) if a < b else (b, a)
        edges.setdefault(k, []).append(((x + 1, y), (x + 1, y + 1)))
    av, bv = A[:-1, :], A[1:, :]
    m = (av != bv) & (av > 0) & (bv > 0) & (side[av] > 0) & (side[bv] > 0) & (side[av] != side[bv])
    ys, xs = np.nonzero(m)
    for y, x in zip(ys.tolist(), xs.tolist()):
        a, b = int(av[y, x]), int(bv[y, x])
        k = (a, b) if a < b else (b, a)
        edges.setdefault(k, []).append(((x, y + 1), (x + 1, y + 1)))
    for (a, b), el in sorted(edges.items()):
        for ch in chains_from_edges(el):
            if len(ch) < 12:
                continue
            sm = smooth_chain(ch)
            mid = sm[len(sm) // 2]
            lon, lat = px_to_lonlat(mid[0], mid[1])
            lvl = trench_level(ctrl[a], ctrl[b], float(lon), float(lat))
            pts = [[round(float(x) / W, 5), round(float(y) / H, 5)] for x, y in sm]
            res.append(dict(a=a, b=b, trench=lvl, points=pts))
    return res


def catmull(points, n=8):
    p = [points[0]] + points + [points[-1]]
    out = []
    for i in range(1, len(p) - 2):
        p0, p1, p2, p3 = (np.array(v, float) for v in p[i - 1:i + 3])
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(np.array(points[-1], float))
    return out


def write_tables(A, provs, hf, land):
    T('tablolar')
    n = len(provs)
    ids = A.ravel()
    rows = np.repeat(np.arange(H), W)
    lat_row = LAT1 - (np.arange(H) + 0.5) / H * (LAT1 - LAT0)
    areaw = (1.0361 * 1.5473 * np.cos(np.radians(lat_row))).astype(np.float64)
    area = np.bincount(ids, weights=np.repeat(areaw, W), minlength=n + 1)
    hv = hf.ravel()
    sumh = np.bincount(ids, weights=hv, minlength=n + 1)
    cnt = np.bincount(ids, minlength=n + 1).astype(np.float64)
    meanh = sumh / np.maximum(cnt, 1)
    sumh2 = np.bincount(ids, weights=hv.astype(np.float64) ** 2, minlength=n + 1)
    stdh = np.sqrt(np.maximum(sumh2 / np.maximum(cnt, 1) - meanh ** 2, 0))
    # centroid: kütle merkezi; bölge dışına düşerse en yakın bölge pikseli
    ys, xs = np.mgrid[0:H, 0:W]
    sx = np.bincount(ids, weights=xs.ravel(), minlength=n + 1) / np.maximum(cnt, 1)
    sy = np.bincount(ids, weights=ys.ravel(), minlength=n + 1) / np.maximum(cnt, 1)
    del ys, xs
    rng = np.random.default_rng(5)
    rows_out = []
    for p in provs:
        i = p['id']
        cx, cy = sx[i], sy[i]
        xi, yi = int(round(min(max(cx, 0), W - 1))), int(round(min(max(cy, 0), H - 1)))
        if A[yi, xi] != i:
            pxs, pys = np.nonzero(A[max(0, yi - 300):yi + 300, max(0, xi - 300):xi + 300].T == i)
            if len(pxs):
                d = (pxs + max(0, xi - 300) - cx) ** 2 + (pys + max(0, yi - 300) - cy) ** 2
                j = np.argmin(d)
                cx, cy = pxs[j] + max(0, xi - 300), pys[j] + max(0, yi - 300)
            else:
                cx, cy = p['x'], p['y']
        p['cu'], p['cv'] = (cx + 0.5) / W, (cy + 0.5) / H
        p['area'] = area[i]
        p['meanh'] = meanh[i]
        # arazi
        mh, sd = meanh[i], stdh[i]
        tag = p['tag']
        if mh > 950 or (mh > 650 and sd > 330):
            terr = 'Mountains'
        elif mh > 420 or sd > 190:
            terr = 'Hills'
        else:
            terr = 'Plains'
        if tag == 'M' and terr != 'Mountains':
            terr = 'Mountains' if mh > 600 else 'Hills'
        elif tag == 'H' and terr == 'Plains':
            terr = 'Hills'
        elif tag == 'F' and terr == 'Plains':
            terr = 'Forest'
        elif tag == 'S' and terr == 'Plains':
            terr = 'Marsh'
        elif tag == 'F' and terr == 'Hills' and mh < 500:
            terr = 'Forest'
        p['terrain'] = terr
        # sanayi / nüfus
        o = p['owner']
        ind = int(p['ind']) if p['ind'] is not None else {'GBR': 3, 'FRA': 2, 'BEL': 4, 'LUX': 6, 'NED': 3, 'GER': 3, 'AUH': 2, 'ITA': 2, 'SWI': 3,
                                                           'SWE': 2, 'DEN': 2}.get(o, 1)
        if p['group'] == 'FRA_COL' or p['group'] == 'ITA_COL':
            ind = 0
        if o == 'OTT':
            ind = int(p['ind']) if p['ind'] is not None else 0
        p['industry'] = int(min(10, max(0, ind)))
        lon0, lat0 = px_to_lonlat(cx, cy)
        dens = DENS[o] * (0.55 + 0.13 * p['industry'])
        if o == 'RUS':
            if 18 < lon0 < 25.5 and 49 < lat0 < 55:
                dens *= 2.4
            elif lat0 > 58.5:
                dens *= 0.28
            elif 24 < lon0 < 40 and 46 < lat0 < 52:
                dens *= 1.5
            elif lon0 > 36 and 53 < lat0 < 58:
                dens *= 1.4
            elif lon0 > 41 and lat0 < 44:
                dens *= 0.7
            elif lon0 < 31 and lat0 > 55:
                dens *= 0.6
        if o == 'OTT' and (lon0 > 39 or lat0 < 36.5):
            dens *= 0.5
        if o == 'FRA' and p['group'] == 'FRA_COL':
            dens = 14
        if terr == 'Mountains':
            dens *= 0.45
        elif terr in ('Hills', 'Marsh'):
            dens *= 0.8
        elif terr == 'Forest':
            dens *= 0.75
        pop = area[i] * dens / 1000.0 * float(rng.uniform(0.9, 1.1)) + p['city']
        p['pop'] = int(max(5, round(pop)))
    # CSV
    with open(os.path.join(RAW, 'provinces.csv'), 'w', newline='', encoding='utf-8') as f:
        wr = csv.writer(f, lineterminator='\n')
        wr.writerow(['---', 'Id', 'Name', 'Owner', 'Controller', 'Terrain', 'Fort', 'Population', 'Industry', 'CentroidU', 'CentroidV'])
        for p in provs:
            wr.writerow(['P%d' % p['id'], p['id'], p['name'], p['owner'], p['ctrl'], p['terrain'], 'True' if p['fort'] else 'False',
                         p['pop'], p['industry'], '%.5f' % p['cu'], '%.5f' % p['cv']])
    used = sorted({p['owner'] for p in provs} | {p['ctrl'] for p in provs})
    with open(os.path.join(RAW, 'nations.csv'), 'w', newline='', encoding='utf-8') as f:
        wr = csv.writer(f, lineterminator='\n')
        wr.writerow(['---', 'Code', 'Name', 'Side', 'Color'])
        for c in used:
            r, g, b = srgb_to_lin(NATIONS[c][2])
            wr.writerow([c, c, NATIONS[c][0], NATIONS[c][1], '(R=%.4f,G=%.4f,B=%.4f,A=1.0)' % (r, g, b)])
    # komşuluk
    keys = []
    for a, b in ((A[:, :-1], A[:, 1:]), (A[:-1, :], A[1:, :])):
        m = (a != b) & (a > 0) & (b > 0)
        aa, bb = a[m].astype(np.int64), b[m].astype(np.int64)
        keys.append(np.minimum(aa, bb) * 65536 + np.maximum(aa, bb))
    keys = np.concatenate(keys)
    u, c = np.unique(keys, return_counts=True)
    adj = [[int(k // 65536), int(k % 65536), int(v)] for k, v in zip(u, c)]
    json.dump(adj, open(os.path.join(RAW, 'adjacency.json'), 'w'), separators=(',', ':'))
    T('komşuluk: %d çift' % len(adj))
    fronts = make_fronts(A, provs)
    json.dump(fronts, open(os.path.join(RAW, 'fronts.json'), 'w'), separators=(',', ':'))
    T('cepheler: %d çizgi' % len(fronts))
    # demiryolları
    byname = {p['name']: p for p in provs}
    rails = []
    for name, cities in RAILS:
        pts = []
        for c in cities:
            if c not in byname:
                raise SystemExit('demiryolu şehri yok: %s (%s)' % (c, name))
            pts.append((byname[c]['x'] / W, byname[c]['y'] / H))
        sm = catmull(pts, 8) if len(pts) > 2 else pts
        rails.append(dict(name=name, points=[[round(float(x), 5), round(float(y), 5)] for x, y in sm]))
    json.dump(rails, open(os.path.join(RAW, 'rails.json'), 'w'), ensure_ascii=False, separators=(',', ':'))
    armies = []
    for name, nat, prov, div, org in ARMIES:
        if prov not in byname:
            raise SystemExit('ordu bölgesi yok: %s' % prov)
        armies.append(dict(name=name, nation=nat, province=byname[prov]['id'], divisions=div, organization=org))
    json.dump(armies, open(os.path.join(RAW, 'armies.json'), 'w'), ensure_ascii=False, indent=0)
    return fronts


def make_paper():
    n = 1024
    base = np.array([218, 219, 200], np.float32)
    img = np.ones((n, n, 3), np.float32) * base
    low = noise((n, n), 3.2, 31)
    mid = noise((n, n), 1.6, 32)
    hi = noise((n, n), 0.6, 33)
    v = 1 + 0.035 * low + 0.02 * mid + 0.012 * hi
    # lif çizgileri (sarmalı)
    fib = Image.new('L', (n, n), 0)
    dr = ImageDraw.Draw(fib)
    rng = np.random.default_rng(34)
    for _ in range(2600):
        x, y = rng.uniform(0, n, 2)
        a = rng.uniform(0, math.pi)
        l = rng.uniform(5, 22)
        dx, dy = math.cos(a) * l, math.sin(a) * l
        shade = int(rng.integers(30, 90))
        for ox in (-n, 0, n):
            for oy in (-n, 0, n):
                dr.line([(x + ox, y + oy), (x + dx + ox, y + dy + oy)], fill=shade, width=1)
    fibn = np.array(fib, np.float32) / 255.0
    fibn = ndi.gaussian_filter(fibn, 0.6, mode='wrap')
    v = v + 0.35 * fibn * (rng.random((n, n)) > 0.5)
    # lekeler
    st = noise((n, n), 2.6, 35)
    stain = np.clip((st - 1.2) * 0.12, 0, 0.12)
    img = img * v[..., None] * (1 - stain[..., None] * np.array([0.4, 0.7, 1.0]))
    img = img + rng.normal(0, 1.2, img.shape)
    Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).save(os.path.join(RAW, 'paper.png'))


# ------------------------------------------------------------------ önizleme
def hillshade(hm_m, exag=6.0):
    z = ndi.gaussian_filter(hm_m, 1.2) / 1000.0 / 1.036
    gy, gx = np.gradient(z)
    nx, ny = -gx * exag, -gy * exag
    inv = 1.0 / np.sqrt(nx * nx + ny * ny + 1)
    L = np.array([-0.55, -0.55, 0.65])
    L = L / np.linalg.norm(L)
    s = (nx * L[0] + ny * L[1] + L[2]) * inv
    return s.astype(np.float32)


LABELS = {  # kod: (metin, lon, lat, boy px, harf aralığı)
    'FRA': ('FRANSA', 2.4, 46.6, 60, 14), 'GBR': ('BRİTANYA', -1.4, 53.0, 40, 8), 'GER': ('ALMANYA', 10.9, 51.0, 66, 14),
    'AUH': ('AVUSTURYA-MACARİSTAN', 19.5, 47.35, 38, 8), 'RUS': ('RUSYA', 33.5, 55.5, 150, 30), 'OTT': ('OSMANLI DEVLETİ', 34.5, 39.1, 62, 14),
    'ITA': ('İTALYA', 12.3, 42.6, 36, 9), 'ESP': ('İSPANYA', -4.0, 40.0, 58, 12), 'POR': ('PORTEKİZ', -8.3, 39.5, 22, 4),
    'SWI': ('İSVİÇRE', 8.2, 46.85, 17, 3), 'NED': ('HOLLANDA', 5.4, 52.3, 17, 3), 'BEL': ('BELÇİKA', 4.5, 50.6, 15, 2),
    'DEN': ('DANİMARKA', 9.5, 56.1, 17, 3), 'NOR': ('NORVEÇ', 8.6, 60.9, 40, 9), 'SWE': ('İSVEÇ', 15.0, 59.6, 42, 12),
    'ROM': ('ROMANYA', 25.3, 45.7, 38, 8), 'BUL': ('BULGARİSTAN', 25.6, 42.9, 24, 4), 'GRE': ('YUNANİSTAN', 22.3, 39.2, 22, 3),
    'SER': ('SIRBİSTAN', 20.7, 43.9, 19, 3), 'ALB': ('ARN.', 19.9, 41.3, 14, 1), 'MNT': ('', 19, 42.7, 10, 1),
}


def build_lookups(provs):
    n = len(provs)
    owner = np.zeros(n + 1, 'U3'); ctrl = np.zeros(n + 1, 'U3')
    for p in provs:
        owner[p['id']] = p['owner']; ctrl[p['id']] = p['ctrl']
    return owner, ctrl


def shifted_or(m, r=1):
    o = m.copy()
    for k in range(1, r + 1):
        o[:, k:] |= m[:, :-k]
        o[k:, :] |= m[:-k, :]
    return o


def render_preview(mode, A, provs, hm, fronts, paper, dland, dsea):
    n = len(provs)
    land = A > 0
    h_m = np.where(hm > 8192, (hm.astype(np.float32) - 8232) * 4900.0 / 57200.0, 0).clip(0, None)
    sh = hillshade(h_m)
    sea = (180, 198, 198) if mode != 'terrain' else (176, 194, 196)
    LUT = np.zeros((n + 1, 3), np.float32)
    HAT = np.zeros((n + 1, 3), np.float32)
    OCC = np.zeros(n + 1, bool)
    rng = np.random.default_rng(3)
    jit = 1 + rng.uniform(-0.045, 0.045, n + 1)
    TERR = dict(Plains=(212, 214, 176), Forest=(142, 170, 122), Hills=(200, 180, 134), Mountains=(176, 152, 128), Marsh=(152, 180, 168))
    SIDEC = dict(Entente=(112, 150, 196), Central=(206, 156, 108), Neutral=(210, 204, 182))
    for p in provs:
        i = p['id']
        if mode == 'political' or mode == 'front':
            c = np.array(NATIONS[p['owner']][2], np.float32)
            hc = np.array(NATIONS[p['ctrl']][2], np.float32)
        elif mode == 'alliance':
            c = np.array(SIDEC[side_of(p['owner'])], np.float32)
            hc = np.array(SIDEC[side_of(p['ctrl'])], np.float32)
        else:
            c = np.array(TERR[p['terrain']], np.float32)
            hc = c
        if mode == 'front':
            c = c * 0.62 + np.array([214, 210, 190], np.float32) * 0.38
        LUT[i] = c * jit[i]
        HAT[i] = hc * 0.72
        OCC[i] = p['owner'] != p['ctrl'] and mode != 'terrain'
    img = LUT[A]
    img[~land] = sea
    # hillshade
    strength = 1.5 if mode == 'terrain' else 0.8
    f = 1 + strength * (sh - sh[land].mean()) * 1.1
    f = np.where(land, f, 1.0)
    img *= f[..., None]
    # işgal çizgileri
    yy, xx = np.mgrid[0:H, 0:W]
    stripe = (((xx + yy) % 14) < 4) & OCC[A]
    img[stripe] = img[stripe] * 0.35 + HAT[A][stripe] * 0.65
    del yy, xx, stripe
    # deniz kıyı taraması
    for d0, a in ((4, .45), (10, .35), (18, .28), (28, .2), (40, .14)):
        m = (np.abs(dsea - d0) < 0.9) & (~land)
        img[m] = img[m] * (1 - a) + np.array([92, 120, 126], np.float32) * a
    # sınırlar
    owner, ctrl = build_lookups(provs)
    ow = np.zeros(n + 1, np.int16)
    codes = {c: k + 1 for k, c in enumerate(sorted(NATIONS))}
    for p in provs:
        ow[p['id']] = codes[p['owner']]
    own = ow[A]
    pb = np.zeros((H, W), bool)
    nb = np.zeros((H, W), bool)
    for sl_a, sl_b, tgt in ((np.s_[:, :-1], np.s_[:, 1:], np.s_[:, :-1]), (np.s_[:-1, :], np.s_[1:, :], np.s_[:-1, :])):
        a, b = A[sl_a], A[sl_b]
        m = (a != b) & (a > 0) & (b > 0)
        pb[tgt] |= m
        nb[tgt] |= m & (own[sl_a] != own[sl_b])
    pb = shifted_or(pb, 1)
    nb = shifted_or(nb, 2)
    if mode != 'terrain':
        pbm = pb & ~nb
        img[pbm] = img[pbm] * 0.62 + np.array([84, 80, 66], np.float32) * 0.38
        img[nb] = img[nb] * 0.25 + np.array([62, 56, 46], np.float32) * 0.75
    else:
        img[pb] = img[pb] * 0.85 + np.array([84, 80, 66], np.float32) * 0.15
    coast = land & (dsea < 0) if False else None
    cm = shifted_or(land ^ ndi.binary_erosion(land), 1)
    img[cm & land] = img[cm & land] * 0.45 + np.array([60, 66, 70], np.float32) * 0.55
    # kâğıt
    pap = np.tile(paper, (H // paper.shape[0] + 1, W // paper.shape[1] + 1, 1))[:H, :W]
    pap = pap / pap.reshape(-1, 3).mean(0)
    img = img * (0.5 + 0.5 * pap)
    # vinyet
    vy = np.linspace(-1, 1, H)[:, None]
    vx = np.linspace(-1, 1, W)[None, :]
    vig = 1 - 0.10 * np.clip(vx ** 2 + vy ** 2 - 0.5, 0, 2)
    img *= vig[..., None]
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    dr = ImageDraw.Draw(im, 'RGBA')
    # ülke adları
    if mode in ('political', 'alliance', 'front'):
        lay = Image.new('L', (W, H), 0)
        ld = ImageDraw.Draw(lay)
        fpath = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
        for code, (txt, lo, la, sz, sp) in LABELS.items():
            if not txt:
                continue
            font = ImageFont.truetype(fpath, sz)
            widths = [ld.textlength(ch, font=font) + sp for ch in txt]
            tw = sum(widths)
            cx, cy = lonlat_to_px(lo, la)
            x = cx - tw / 2
            for ch, wd in zip(txt, widths):
                ld.text((x, cy - sz * 0.6), ch, font=font, fill=255)
                x += wd
        la_ = np.array(lay, np.float32)[..., None] / 255.0 * (0.5 if mode != 'front' else 0.35)
        arr = np.array(im, np.float32)
        arr = arr * (1 - la_) + np.array([58, 54, 46], np.float32) * la_
        im = Image.fromarray(arr.astype(np.uint8))
        dr = ImageDraw.Draw(im, 'RGBA')
    # cepheler
    ctrlside = {p['id']: side_of(p['ctrl']) for p in provs}
    wlvl = {0: 4, 1: 6, 2: 7, 3: 8, 4: 9, 5: 11}
    for fr in fronts:
        pts = [(u * W, v * H) for u, v in fr['points']]
        lvl = fr['trench']
        wd = wlvl[lvl] if mode == 'front' else max(3, wlvl[lvl] - 2)
        if mode == 'terrain':
            continue
        dr.line(pts, fill=(176, 28, 28, 235), width=wd, joint='curve')
        # dişler: Merkez kontrolündeki tarafa bakar
        tooth = 5 + lvl * 2
        step = 3.0 * tooth if lvl > 0 else 999
        acc = 0.0
        for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
            seg = math.hypot(x1 - x0, y1 - y0)
            if seg < 1e-6:
                continue
            ux, uy = (x1 - x0) / seg, (y1 - y0) / seg
            nx, ny = -uy, ux
            t = step - acc
            while t < seg:
                px, py = x0 + ux * t, y0 + uy * t
                for sgn in (1, -1):
                    sx, sy = px + nx * sgn * 6, py + ny * sgn * 6
                    ix, iy = int(min(max(sx, 0), W - 1)), int(min(max(sy, 0), H - 1))
                    pid = int(A[iy, ix])
                    if pid and ctrlside.get(pid) == 'Central':
                        base = tooth
                        tip = (px + nx * sgn * (wd / 2 + tooth), py + ny * sgn * (wd / 2 + tooth))
                        b1 = (px - ux * base * 0.6 + nx * sgn * wd / 2, py - uy * base * 0.6 + ny * sgn * wd / 2)
                        b2 = (px + ux * base * 0.6 + nx * sgn * wd / 2, py + uy * base * 0.6 + ny * sgn * wd / 2)
                        dr.polygon([b1, tip, b2], fill=(176, 28, 28, 235))
                t += step
            acc = (acc + seg) % step if step < 900 else 0
    # kaleler
    for p in provs:
        if not p['fort']:
            continue
        cx, cy = p['cu'] * W, p['cv'] * H
        R = 17
        star = []
        for k in range(10):
            r = R if k % 2 == 0 else R * 0.42
            a = -math.pi / 2 + k * math.pi / 5
            star.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        dr.polygon(star, fill=(30, 28, 26, 255), outline=(236, 232, 214, 255))
    return im


def previews(A, provs, hm, fronts, dland, dsea):
    T('önizlemeler')
    paper = np.array(Image.open(os.path.join(RAW, 'paper.png')).convert('RGB'), np.float32)
    os.makedirs(IMG, exist_ok=True)
    for mode in ('political', 'alliance', 'terrain', 'front'):
        im = render_preview(mode, A, provs, hm, fronts, paper, dland, dsea)
        im.save(os.path.join(RAW, 'preview_%s.png' % mode), optimize=False, compress_level=3)
        im.resize((1600, int(round(1600 * H / W))), Image.LANCZOS).save(os.path.join(IMG, 'preview_%s.png' % mode), compress_level=6)
        T('  preview_%s.png' % mode)


def main():
    os.makedirs(RAW, exist_ok=True)
    os.makedirs(IMG, exist_ok=True)
    if '--previews' in sys.argv:
        A = np.array(Image.open(os.path.join(RAW, 'province_id.png')))
        A = (A[..., 0].astype(np.uint16) + A[..., 1].astype(np.uint16) * 256)
        hm = np.array(Image.open(os.path.join(RAW, 'heightmap.png'))).astype(np.uint16)
        import csv as _csv
        provs = []
        seeds = {s['name']: s for s in parse_seeds()}
        with open(os.path.join(RAW, 'provinces.csv'), encoding='utf-8') as f:
            for r in _csv.DictReader(f):
                s = dict(seeds.get(r['Name'], {}))
                s.update(id=int(r['Id']), name=r['Name'], owner=r['Owner'], ctrl=r['Controller'], terrain=r['Terrain'], fort=r['Fort'] == 'True',
                         cu=float(r['CentroidU']), cv=float(r['CentroidV']))
                provs.append(s)
        fronts = json.load(open(os.path.join(RAW, 'fronts.json')))
        land = A > 0
        dsea = ndi.distance_transform_edt(~land).astype(np.float32)
        previews(A, provs, hm, fronts, None, dsea)
        return
    A, provs, land, cidx, cnames = build_provinces()
    rgb = np.zeros((H, W, 3), np.uint8)
    rgb[..., 0] = (A & 255).astype(np.uint8)
    rgb[..., 1] = (A >> 8).astype(np.uint8)
    Image.fromarray(rgb).save(os.path.join(RAW, 'province_id.png'), compress_level=6)
    del rgb
    T('province_id.png yazıldı, %d bölge' % len(provs))
    hm, hf, dland, dsea = build_heightmap(land)
    Image.fromarray(hm).save(os.path.join(RAW, 'heightmap.png'), compress_level=6)
    T('heightmap.png yazıldı')
    fronts = write_tables(A, provs, hf, land)
    make_paper()
    T('paper.png yazıldı')
    previews(A, provs, hm, fronts, dland, dsea)
    # özet
    ar = np.array([p['area'] for p in provs])
    print('bölge sayısı %d; alan km2 min/medyan/maks: %d / %d / %d' % (len(provs), ar.min(), np.median(ar), ar.max()))
    json.dump(dict(provinces=len(provs)), open(os.path.join(RAW, '_summary.json'), 'w'))
    os.remove(os.path.join(RAW, '_summary.json'))


if __name__ == '__main__':
    main()
