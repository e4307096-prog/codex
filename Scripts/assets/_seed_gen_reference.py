import json, math, warnings
warnings.filterwarnings('ignore')
import geopandas as gpd
from shapely.geometry import box, Point, MultiPoint, LineString, MultiLineString, Polygon, MultiPolygon
from shapely.ops import unary_union, voronoi_diagram, linemerge
from shapely import affinity

LON0, LON1, LAT0, LAT1, LATC = -11.0, 46.0, 33.0, 62.0, 48.0
K = 1100 / ((LON1 - LON0) * math.cos(math.radians(LATC)))
def proj(lon, lat): return ((lon - LON0) * math.cos(math.radians(LATC)) * K, (LAT1 - lat) * K)
W, H = proj(LON1, LAT0)

w = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
land = unary_union(list(w.geometry)).intersection(box(LON0, LAT0, LON1, LAT1))
land = affinity.affine_transform(land, [math.cos(math.radians(LATC)) * K, 0, 0, -K, -LON0 * math.cos(math.radians(LATC)) * K, LAT1 * K])
land = land.buffer(0)

E = {'FRA','GBR','RUS','BEL','SER','MNT'}; C = {'GER','AUH','OTT'}
P = []  # name, lon, lat, owner, occupier, terrain, trench, fort
def add(owner, rows):
    for r in rows:
        name, lon, lat = r[:3]; extra = r[3] if len(r) > 3 else {}
        P.append(dict(name=name, lon=lon, lat=lat, owner=owner, occ=extra.get('occ'), terrain=extra.get('t', 'Ova'), fort=extra.get('fort', False)))
add('GBR', [('Londra',-0.1,51.5),('Birmingham',-1.9,52.5),('Manchester',-2.2,53.5),('Newcastle',-1.6,55.0),('Glasgow',-4.25,55.9),('İskoç Dağları',-4.6,57.4,{'t':'Dağ'}),
            ('Plymouth',-4.1,50.5),('Galler',-3.6,52.2,{'t':'Tepe'}),('Dublin',-6.6,53.3),('Cork',-8.6,52.0),('Belfast',-6.3,54.6),('Kıbrıs',33.2,35.1)])
add('FRA', [('Paris',2.35,48.85),('Lille',3.06,50.63,{'occ':'GER'}),('Amiens',2.3,49.9),('Reims',4.03,49.25),('Verdun',5.38,49.16,{'fort':True,'t':'Tepe'}),('Nancy',6.18,48.69),
            ('Belfort',6.86,47.64,{'fort':True,'t':'Dağ'}),('Rouen',1.1,49.44),('Brest',-4.0,48.3),('Nantes',-1.55,47.2),('Orléans',1.9,47.9),('Dijon',5.04,47.32),('Lyon',4.83,45.76),
            ('Bordeaux',-0.58,44.84),('Toulouse',1.44,43.6),('Marsilya',5.37,43.5),('Alpler',6.4,44.9,{'t':'Dağ'}),('Clermont',3.08,45.78,{'t':'Tepe'}),('Limoges',1.26,45.83),
            ('Cezayir',3.06,36.0),('Oran',-0.64,35.0),('Tunus',9.6,35.6),('Fas',-5.5,34.0),('Korsika',9.1,42.1,{'t':'Dağ'}),('Charleville',4.72,49.77,{'occ':'GER','t':'Orman'})])
add('BEL', [('Brüksel',4.35,50.85,{'occ':'GER'}),('Anvers',4.4,51.22,{'occ':'GER'}),('Flandre',2.85,50.95),('Liège',5.57,50.5,{'occ':'GER','fort':True})])
add('NED', [('Amsterdam',4.9,52.37),('Groningen',6.57,53.1),('Brabant',5.2,51.6)])
add('GER', [('Berlin',13.4,52.52),('Hamburg',10.0,53.55),('Kiel',9.9,54.4),('Hannover',9.73,52.37),('Köln',6.96,50.94),('Ruhr',7.4,51.5),('Frankfurt',8.68,50.11),
            ('Metz',6.17,49.12,{'fort':True}),('Strasbourg',7.6,48.4,{'t':'Orman'}),('Stuttgart',9.18,48.78,{'t':'Orman'}),('Münih',11.58,48.14),('Nürnberg',11.08,49.45),('Dresden',13.74,51.05),
            ('Leipzig',12.37,51.34),('Breslau',17.04,51.11),('Posen',16.93,52.41),('Danzig',18.65,54.2),('Königsberg',20.8,54.6,{'fort':True}),('Stettin',14.55,53.43),('Bremen',8.6,53.0),
            ('Kassel',9.5,51.3,{'t':'Tepe'}),('Masurya',21.8,53.8,{'t':'Bataklık'})])
add('AUH', [('Viyana',16.37,48.21),('Prag',14.42,50.08),('Moravya',16.9,49.3),('Budapeşte',19.04,47.5),('Debrecen',21.63,47.53),('Erdel',23.9,46.6,{'t':'Dağ'}),('Zagreb',15.98,45.81),
            ('Trieste',13.77,45.75),('Tirol',11.4,47.1,{'t':'Dağ'}),('Saraybosna',18.2,44.0,{'t':'Dağ'}),('Krakov',19.94,50.06),('Przemyśl',22.77,49.78,{'fort':True}),
            ('Lemberg',24.03,49.84,{'occ':'RUS'}),('Bukovina',25.94,48.29,{'occ':'RUS','t':'Dağ'}),('Temeşvar',21.23,45.75),('Dalmaçya',16.6,43.6,{'t':'Dağ'}),('Karpatlar',22.3,48.8,{'t':'Dağ'}),
            ('Graz',15.4,47.1,{'t':'Dağ'})])
add('SER', [('Belgrad',20.46,44.8),('Niş',21.9,43.4,{'t':'Dağ'}),('Üsküp',21.43,41.9,{'t':'Dağ'})])
add('MNT', [('Karadağ',19.2,42.6,{'t':'Dağ'})])
add('ITA', [('Milano',9.19,45.46),('Torino',7.69,45.07),('Venedik',12.33,45.6),('Bologna',11.34,44.49),('Floransa',11.25,43.6,{'t':'Tepe'}),('Roma',12.5,41.9),('Napoli',14.27,40.85),
            ('Bari',16.6,41.0),('Kalabriya',16.2,39.0,{'t':'Dağ'}),('Sicilya',14.0,37.5),('Sardinya',9.0,40.0,{'t':'Tepe'})])
add('SWI', [('Bern',7.45,46.8,{'t':'Dağ'}),('Zürih',8.8,47.3,{'t':'Dağ'})])
add('ESP', [('Madrid',-3.7,40.4),('Barselona',1.6,41.7),('Sevilla',-5.5,37.5),('Bilbao',-3.0,43.0,{'t':'Dağ'}),('Valensiya',-0.7,39.3),('Zaragoza',-0.89,41.65),('Galiçya',-8.0,42.7),('Salamanca',-6.0,41.2)])
add('POR', [('Lizbon',-8.6,38.9),('Porto',-8.0,41.3)])
add('DEN', [('Kopenhag',12.0,55.5),('Jutland',9.2,56.2)])
add('NOR', [('Oslo',10.5,60.0,{'t':'Dağ'}),('Bergen',6.5,60.6,{'t':'Dağ'})])
add('SWE', [('Stokholm',17.0,59.6),('Göteborg',13.0,57.8,{'t':'Orman'}),('Malmö',13.5,55.9),('Dalarna',14.8,61.2,{'t':'Orman'})])
add('RUS', [('Varşova',21.01,52.23),('Łódź',19.46,51.76),('Lublin',22.57,51.25),('Grodno',23.83,53.68,{'fort':True}),('Vilna',25.28,54.69,{'t':'Orman'}),('Kovno',23.4,55.3),
            ('Riga',24.1,56.95),('Estonya',25.5,58.8),('Petrograd',30.3,59.94),('Pskov',28.33,57.82,{'t':'Orman'}),('Minsk',27.56,53.9,{'t':'Orman'}),('Pinsk',26.1,52.1,{'t':'Bataklık'}),
            ('Smolensk',32.05,54.78,{'t':'Orman'}),('Moskova',37.62,55.76),('Kiev',30.52,50.45),('Jitomir',28.66,50.25,{'t':'Orman'}),('Odessa',30.73,46.6),('Besarabya',28.6,47.3),
            ('Harkov',36.23,49.99),('Voronej',39.2,51.67),('Rostov',39.7,47.23),('Kırım',34.0,45.0),('Tiflis',44.79,41.72,{'t':'Dağ'}),('Kars',43.1,40.6,{'t':'Dağ','fort':True}),
            ('Finlandiya',25.0,61.0,{'t':'Orman'}),('Vitebsk',30.2,55.19,{'t':'Orman'}),('Kursk',36.19,51.73),('Yekaterinoslav',35.04,48.46),('Kuban',40.5,45.0),('Tsaritsyn',44.5,48.7),
            ('Tula',37.6,54.0),('Volhinya',25.3,50.9,{'t':'Orman'}),('Podolya',27.5,48.9),('Novgorod',31.3,58.5,{'t':'Orman'}),('Yaroslavl',39.9,57.6,{'t':'Orman'}),('Penza',44.0,53.2),
            ('Tambov',41.45,52.7),('Kafkasya',42.0,43.6,{'t':'Dağ'}),('Bakü yolu',45.5,41.0,{'t':'Dağ'})])
add('ROM', [('Bükreş',26.1,44.43),('Yaş',27.3,47.0),('Krayova',23.8,44.32),('Dobruca',28.4,44.3)])
add('BUL', [('Sofya',23.32,42.7,{'t':'Dağ'}),('Varna',27.4,43.2),('Filibe',25.0,42.15)])
add('GRE', [('Atina',22.7,38.0,{'t':'Tepe'}),('Selanik',22.94,40.64),('Yanya',20.95,39.67,{'t':'Dağ'}),('Girit',24.8,35.25,{'t':'Dağ'})])
add('ALB', [('Arnavutluk',20.0,41.0,{'t':'Dağ'})])
add('OTT', [('İstanbul',28.4,41.25),('Edirne',26.56,41.68,{'fort':True}),('Bursa',29.06,40.19),('İzmir',27.4,38.6),('Ankara',32.85,39.93),('Konya',32.48,37.87),('Antalya',30.71,36.9,{'t':'Dağ'}),
            ('Adana',35.32,37.0),('Kayseri',35.48,38.72),('Sivas',37.02,39.75),('Samsun',36.33,41.0),('Trabzon',39.72,40.8,{'t':'Dağ'}),('Erzurum',41.27,39.9,{'t':'Dağ','fort':True}),
            ('Van',43.38,38.5,{'t':'Dağ'}),('Diyarbakır',40.23,37.91),('Halep',37.16,36.2),('Şam',36.29,34.0),('Musul',43.13,36.34),('Kastamonu',33.8,41.4,{'t':'Dağ'}),('Malatya',38.3,38.4,{'t':'Dağ'}),
            ('Çanakkale',27.0,39.95,{'fort':True})])

NAMES = dict(GBR='Britanya',FRA='Fransa',BEL='Belçika',NED='Hollanda',GER='Alman İmparatorluğu',AUH='Avusturya-Macaristan',SER='Sırbistan',MNT='Karadağ',ITA='İtalya',SWI='İsviçre',
             ESP='İspanya',POR='Portekiz',DEN='Danimarka',NOR='Norveç',SWE='İsveç',RUS='Rus İmparatorluğu',ROM='Romanya',BUL='Bulgaristan',GRE='Yunanistan',ALB='Arnavutluk',OTT='Osmanlı Devleti')

pts = [Point(*proj(p['lon'], p['lat'])) for p in P]
for p, pt in zip(P, pts): p['x'], p['y'] = pt.x, pt.y
comps = list(land.geoms) if isinstance(land, MultiPolygon) else [land]
cells = [None] * len(P)
for comp in comps:
    if comp.area < 30: continue
    idx = [i for i, pt in enumerate(pts) if comp.buffer(2).contains(pt)]
    if not idx:
        # island without a seed: give it to the nearest province as an extra piece
        c = comp.representative_point(); j = min(range(len(P)), key=lambda i: pts[i].distance(c))
        cells[j] = comp if cells[j] is None else cells[j].union(comp); continue
    if len(idx) == 1:
        i = idx[0]; cells[i] = comp if cells[i] is None else cells[i].union(comp); continue
    vd = voronoi_diagram(MultiPoint([pts[i] for i in idx]), envelope=box(-200, -200, W + 200, H + 200))
    for poly in vd.geoms:
        for i in idx:
            if poly.contains(pts[i]):
                piece = poly.intersection(comp)
                cells[i] = piece if cells[i] is None else cells[i].union(piece)
                break
def ctrl(p): return p['occ'] or p['owner']
def side(n): return 'E' if n in E else 'C' if n in C else 'N'
def d_of(g):
    g = g.simplify(0.6)
    polys = [g] if isinstance(g, Polygon) else [x for x in getattr(g, 'geoms', []) if isinstance(x, Polygon)]
    out = []
    for pg in polys:
        for ring in [pg.exterior] + list(pg.interiors):
            cs = list(ring.coords)
            if len(cs) < 4: continue
            out.append('M' + 'L'.join('%.1f,%.1f' % c for c in cs[:-1]) + 'Z')
    return ''.join(out)
provs = []
for i, p in enumerate(P):
    if cells[i] is None or cells[i].is_empty: continue
    provs.append(dict(i=i, n=p['name'], o=p['owner'], c=ctrl(p), t=p['terrain'], f=p['fort'], x=round(p['x'], 1), y=round(p['y'], 1), d=d_of(cells[i])))
# front lines + trench level
fronts = []
WEST = {'FRA','BEL','GBR'}
for a in range(len(P)):
    for b in range(a + 1, len(P)):
        if cells[a] is None or cells[b] is None: continue
        sa, sb = side(ctrl(P[a])), side(ctrl(P[b]))
        if {sa, sb} != {'E', 'C'}: continue
        if pts[a].distance(pts[b]) > 260: continue
        shared = cells[a].boundary.intersection(cells[b].boundary)
        if shared.is_empty or shared.length < 3: continue
        if not isinstance(shared, (LineString, MultiLineString)):
            shared = MultiLineString([g for g in getattr(shared, 'geoms', []) if isinstance(g, LineString)])
            if shared.is_empty: continue
        m = linemerge(shared) if isinstance(shared, MultiLineString) else shared
        lines = [m] if isinstance(m, LineString) else list(m.geoms)
        ca, cb = ctrl(P[a]), ctrl(P[b])
        lvl = 4 if (ca in WEST or cb in WEST) else 2 if 'SER' in (ca, cb) or 'MNT' in (ca, cb) else 1 if 'OTT' in (ca, cb) else 2
        for ln in lines:
            fronts.append(dict(d='M' + 'L'.join('%.1f,%.1f' % c for c in ln.coords), l=lvl, a=P[a]['name'], b=P[b]['name']))
# railways (major lines, by name)
byname = {p['name']: (round(p['x'], 1), round(p['y'], 1)) for p in P}
RAIL = [('Paris','Amiens','Lille'),('Paris','Reims','Verdun','Metz','Strasbourg'),('Paris','Nancy','Belfort'),('Paris','Orléans','Bordeaux'),('Paris','Dijon','Lyon','Marsilya'),('Paris','Rouen'),
        ('Köln','Ruhr','Hannover','Berlin'),('Köln','Frankfurt','Nürnberg','Münih','Viyana'),('Berlin','Posen','Varşova','Grodno','Vilna','Petrograd'),('Berlin','Breslau','Krakov','Przemyśl','Lemberg','Kiev'),
        ('Berlin','Stettin','Danzig','Königsberg'),('Berlin','Leipzig','Dresden','Prag','Viyana','Budapeşte','Belgrad','Niş','Sofya','Filibe','Edirne','İstanbul'),('İstanbul','Ankara'),
        ('Varşova','Minsk','Smolensk','Moskova'),('Moskova','Petrograd'),('Moskova','Kursk','Harkov','Rostov','Kuban','Tiflis'),('Kiev','Odessa'),('Londra','Birmingham','Manchester','Glasgow'),
        ('Viyana','Trieste'),('Milano','Venedik'),('Milano','Bologna','Roma','Napoli'),('Madrid','Zaragoza','Barselona'),('Hamburg','Berlin'),('Konya','Adana','Halep','Şam'),('Bursa','İstanbul')]
rails = ['M' + 'L'.join('%.1f,%.1f' % byname[n] for n in r) for r in RAIL]
coast = d_of(land)
json.dump(dict(W=round(W), H=round(H), provs=provs, fronts=fronts, rails=rails, land=coast, names=NAMES, E=sorted(E), C=sorted(C)),
          open('/tmp/claude-0/-home-user/a85a4fd9-0c65-56d9-87f7-804b7b5854df/scratchpad/ww1/map.json', 'w'), ensure_ascii=False, separators=(',', ':'))
print(len(provs), 'provinces', len(fronts), 'front segs', round(W), round(H))
missing = [P[i]['name'] for i in range(len(P)) if cells[i] is None]
print('no cell:', missing)
