# Cephe 1914: harita veri hattı ve Blender varlıkları

Sözleşme: `Docs/cephe1914-teknik.md` ("Veri hattı", "Blender"). Bu belge uygulamanın özeti ve bilinen sınırlarıdır.

## Çalıştırma (repo kökünden, Python 3.13)

```
pip install numpy scipy pillow shapely "geopandas<1" bpy   # bpy: Blender 5.x modülü
python3 Scripts/assets/make_map_data.py              # tüm Content/Map/Raw çıktıları + önizlemeler (~45 sn)
python3 Scripts/assets/make_map_data.py --previews   # yalnızca önizlemeler (ham veri hazırsa)
python3 Scripts/assets/build_table_assets.py         # FBX + 3 render (~4 dk, Cycles CPU)
python3 Scripts/assets/build_table_assets.py --fbx-only
python3 Scripts/assets/build_table_assets.py --render-only a   # a: masa genel, b: Batı Cephesi, c: ürünler
```

Dosyalar: `make_map_data.py` (ana betik), `map_seeds.py` (bölge tohumları, ordular, demiryolları), `map_relief.py` (dağ sıraları, plato, şelf), `build_table_assets.py` (Blender). `_seed_gen_reference.py` yalnızca başlangıç referansıdır.

## Çıktılar (`Content/Map/Raw/`)

| Dosya | Boyut / içerik |
|---|---|
| `province_id.png` | 4096 x 3112 RGB8, `id = R + 256*G`, B = 0, 0 = deniz; **431 kara bölgesi**, kenar yumuşatma yok |
| `heightmap.png` | 4096 x 3112, 16-bit gri; 8192 = kıyı, kara ≥ 8232, en yüksek ~65432, deniz < 8168 |
| `paper.png` | 1024 x 1024 RGB8, döşenebilir (periyodik FFT gürültüsü + sarmal lif çizgileri) |
| `provinces.csv` | 431 satır; `Population` **bin kişi**, `Industry` 0-10, `Terrain` heightmap ile tutarlı (Plains 202, Hills 116, Mountains 77, Forest 30, Marsh 6), 22 kale, 35 işgalli bölge |
| `nations.csv` | 23 ülke, doğrusal renk |
| `adjacency.json` | 1094 kara komşuluğu `[a, b, sınır pikseli]` |
| `fronts.json` | 100 çizgi (UV), siper: Batı 4-5, Sırp 2, Doğu 1-2, Kafkas/Osmanlı 1 |
| `rails.json` | 29 hat (şehir merkezleri arası, Catmull-Rom ile yumuşatılmış) |
| `armies.json` | 31 ordu (Kasım 1914) |
| `preview_{political,alliance,terrain,front}.png` | 4096 x 3112 (ham); 1600 px kopyaları `Docs/img/cephe1914/` altında |
| `FBX/SM_*.fbx` | MapBoard, WarTable, ArmyCounter, FortMarker, TrenchStrip, RailStrip, CommandPin |

Renderlar: `Docs/img/cephe1914/render_masa_genel.png`, `render_bati_cephesi.png`, `render_urunler.png` (1600 x 900; her biri ~75 sn, 56-64 örnek, denoise açık).

## Yöntem

- Kara: Natural Earth 110m ülke poligonları rasterize edilir, kıyı gauss + fraktal gürültüyle yumuşatılır (110m köşeliliğini azaltmak için).
- Bölge ataması: her kara pikseli kendi **grubundaki** en yakın tohuma gider; piksel koordinatı ve tohumlar aynı domain-warp alanıyla bükülür (organik sınır; tohum kendi pikselini kaybetmez). Gruplar: bugünkü sınırı kullanan ülkeler (FRA, ESP, POR, SWI, NED, BEL, LUX, ITA, DEN, NOR, SWE, GBR+İrlanda, GRE, kolonyal parçalar) ayrı; Orta/Doğu Avrupa, Balkanlar, Rusya, Osmanlı ortak `POOL`. 1914 istisnaları: bugünkü Fransa'daki Elsass-Lothringen, bugünkü İtalya'daki Trentino/Güney Tirol ve Gorizia-Trieste `POOL`'a verilir. Aynı kara parçası şartı için 8-bağlantılı kara bileşeni kullanılır; tohumsuz adalar grubun en yakın tohumuna gider.
- Heightmap: dağ sıraları (Alpler, Pireneler, Karpatlar, Dinar, Balkan/Rodop, Apeninler, İskandinav, Kafkaslar, Toroslar, Karadeniz dağları, Atlas, İskoç, Masif Santral, Vosges/Kara Orman, Bohemya çevresi, Ardenler alçak vb.) çizgi + gauss profil + fBm; plato kabarıkları; kıyıya doğru alçalma; denizde şelf bölgeli negatif derinlik. Arazi sütunu: bölge ortalama yükseklik/sapmasından, tohumdaki eğilimle (Orman/Bataklık/Dağ) birleştirilir.
- Cephe çizgileri: İtilaf-İttifak kontrollü komşu bölgelerin ortak sınır piksel kenarları zincirlenir, yeniden örneklenir, yumuşatılır, sadeleştirilir.
- Blender: model metre ile kurulur (levha 409.6 x 311.2 m, 512 x 389 hücre, 200 070 köşe, yer değiştirme en çok 600 cm). FBX `FBX_SCALE_UNITS` ile `UnitScaleFactor=100` yazar; köşeler metre, Unreal santimetreye çevirir: levha 40960 x 31120 cm (dosyadan doğrulandı). Blender +Y = Unreal -Y; Blender V = 1 - Unreal V, böylece doku sol üst (0,0) = dünya (-20480, -15560).
- Ölçüler (cm): ArmyCounter 640 x 360 x 212 (taban z=0, malzeme slotları: 0 Wood, 1 Flag/üst yüz, UV 0..1), FortMarker ~508 x 508 x 530 (0 Stone, 1 Roof), TrenchStrip X 0..100, Y ±32 (0 Earth, 1 Sandbag; dişli kenar +Y), RailStrip X 0..100, Y ±18, CommandPin 92 x 92 x 241 (uç z=0), WarTable 46000 x 35000 (üst yüzey z = -30 cm, levha üstünde).

## Bilinen sınırlar

- 110m verisi: kıyılar kaba (Fyn adası, Baltık/Ege küçük adaları yok), ülke sınırları düz parçalı; iç bölge sınırları organik.
- Libya şeridi kapsam dışı bırakıldı (lat 33 sınırı); Kuzey Schleswig (Danimarka) ve Batı Trakya (Yunanistan) bugünkü sınırla işlendi.
- Sanayi/nüfus tahminidir; nüfus bin kişi (alan x tahmini yoğunluk + büyük şehir eklemesi).
- Orman/Bataklık sınıfları tohum eğilimine bağlı (toplam 36), gerçek bitki örtüsü modellenmedi.
- Rölyef sentetik; dağ yükseklikleri 4900 m'de kırpılır (Elbrus/Ağrı). Levha heightmap'i dünyada 6 m'ye kadar çıkar.
- Cephe çizgileri bölge çifti başına ayrı polylinedir (bir cephe çok parçadan oluşur); uç noktaları kavuşur.
- Render ölçekleri gösterim içindir (blok/kale/siper şeritleri okunsun diye 1x-5x büyütüldü); oyun içi ölçek gameplay ajanına bağlı.
- Sözleşmeye eklenenler: `map_seeds.py`, `map_relief.py` yardımcı modülleri; `Docs/img/cephe1914/preview_*.png` 1600 px kopyaları.
