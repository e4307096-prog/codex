# Cephe 1914: harita teknik sözleşmesi

Ajanlar arası sözleşme. Dosya yolları, veri biçimleri, sınıf ve parametre adları buradan alınır; değiştiren önce bu belgeyi günceller. Tasarım: https://claude.ai/artifact/BDmqQQzaXEKVYd5iTANZyu (Cephe 1914 planı).

Hedef: Unreal Engine 5.4+ (C++), Blender 5.x (bpy). Senaryo: 14 Kasım 1914.

## Veri hattı (assets ajanı, `Scripts/assets/`)

Kaynak: Natural Earth 1:110m (geopandas `naturalearth_lowres`), elle tanımlı bölge tohumları (`Scripts/assets/_seed_gen_reference.py` başlangıç listesidir).

Projeksiyon: eşdikdörtgen, merkez enlem 48°: `x = (lon + 11) * cos(48°)`, `y = (62 - lat)`; kapsam lon -11..46, lat 33..62. Piksel ölçeği bu kapsama göre.

Çıktılar `Content/Map/Raw/` altında (ham dosyalar, `.uasset` değil):

| Dosya | Biçim | İçerik |
|---|---|---|
| `province_id.png` | 4096 × 3112, RGB8, sıkıştırmasız | Piksel = bölge kimliği: `id = R + G * 256`, `B = 0`. `id 0` = deniz. Kenar yumuşatma YOK (her piksel tam bir kimlik). |
| `heightmap.png` | 4096 × 3112, 16-bit gri | 0 = deniz tabanı (-), 8192 = kıyı (deniz seviyesi), 65535 = en yüksek dağ. Sentetik rölyef (dağ sıraları + gürültü). |
| `paper.png` | 1024 × 1024, RGB8, döşenebilir | Harita kâğıdı dokusu (lif, leke). |
| `provinces.csv` | UE DataTable CSV | Başlık: `---,Id,Name,Owner,Controller,Terrain,Fort,Population,Industry,CentroidU,CentroidV`. `---` sütunu satır adı = `P<Id>`. Owner/Controller: ülke kodu (`FRA`, `GER`...). Terrain: `Plains/Forest/Hills/Mountains/Marsh`. Fort: `True/False`. Centroid UV 0..1 (dokuya göre). |
| `nations.csv` | UE DataTable CSV | `---,Code,Name,Side,Color` (Side: `Entente/Central/Neutral`; Color: `(R=..,G=..,B=..,A=1.0)` doğrusal 0..1). |
| `adjacency.json` | JSON | `[[idA, idB, borderPixels], ...]` kara komşulukları. |
| `fronts.json` | JSON | `[{ "a": idA, "b": idB, "trench": 0-5, "points": [[u,v],...] }]` düşman kontrolündeki komşular arası sınır çizgileri (UV 0..1). |
| `rails.json` | JSON | `[{ "name": "...", "points": [[u,v],...] }]` |
| `armies.json` | JSON | `[{ "name": "5. Ordu", "nation": "FRA", "province": id, "divisions": 4, "organization": 0.68 }]` |
| `preview_*.png` | PNG | Unreal malzemesinin numpy ile taklidi (siyasi, ittifak, arazi, cephe): doğrulama ve kullanıcıya gösterim için. |

Kurallar:
- Batı Cephesi bölgesinde (lon -2..9, lat 47..52) bölgeler küçük, Rusya'da büyük. Toplam 300-450 kara bölgesi.
- Sınırlar organik: piksel atamasında gürültüyle bükülmüş koordinat (domain warp). 1914 sınırı bugünküyle aşağı yukarı aynı olan ülkelerde (Fransa, İspanya, Portekiz, İsviçre, Hollanda, Belçika, İtalya, Danimarka, Norveç, İsveç, Britanya+İrlanda, Yunanistan) bölge yalnızca o ülkenin bugünkü poligonu içinden tohum alır; Orta/Doğu Avrupa, Balkanlar ve Osmanlı tohumları birleşik bölgede paylaşır.
- Durum: Kasım 1914 (Belçika'nın çoğu ve Kuzey Fransa Alman işgalinde, Doğu Galiçya Rus işgalinde, İtalya/Romanya/Bulgaristan/Yunanistan tarafsız, Osmanlı İttifak'ta).

## Blender (assets ajanı)

`Scripts/assets/build_table_assets.py` (bpy, başsız). Çıktılar `Content/Map/Raw/FBX/`: `SM_MapBoard` (heightmap ile yer değiştirilmiş harita levhası, UV 0..1 = dokular), `SM_WarTable` (ahşap masa), `SM_ArmyCounter` (ahşap blok + üst yüzü bayrak/sembol için ayrı malzeme slotu), `SM_FortMarker`, `SM_TrenchStrip` (spline boyunca uzatılacak, X ekseninde 100 cm, tekrar eden dişli siper şeridi), `SM_RailStrip`, `SM_CommandPin`. Birim: santimetre, +X ileri, +Z yukarı. Render önizlemeleri `Docs/img/cephe1914/` (Cycles CPU).

## Unreal C++ (gameplay ajanı, `Source/`)

Proje: `Cephe1914.uproject` (repo kökü), modül `Cephe1914`.

Dünya ölçeği: harita levhası `40960 × 31120 cm` (1 piksel = 10 cm), merkez dünya orijininde, yükseklik en çok 600 cm. UV (0,0) sol üst = dünya (-20480, -15560).

| Sınıf | Görev |
|---|---|
| `UProvinceMapSubsystem` (UWorldSubsystem) | `province_id.png`'yi `FPaths::ProjectContentDir()/Map/Raw` altından IImageWrapper ile CPU'ya okur (seçim için), DataTable'ları ve JSON'ları yükler, `UTexture2D` arama dokusunu (1024 × 4, BGRA8) üretir ve harita moduna göre günceller. `GetProvinceAtWorld(FVector)`, `GetProvinceAtUV(FVector2D)`. |
| `AProvinceMapActor` | Harita levhası mesh'i + dinamik malzeme. Malzeme parametreleri aşağıda. Fareyle üstüne gelme ve seçimi yayınlar. |
| `AFrontLineActor` | `fronts.json`'dan spline + SplineMeshComponent; genişlik siper seviyesine göre. |
| `ARailNetworkActor` | `rails.json`'dan spline mesh. |
| `AArmyCounterActor` | Ordu işareti; ülke rengi, organizasyon çubuğu; tıklanabilir. |
| `AStrategyCameraPawn` | WASD, kenar kaydırma, tekerlek yakınlaştırma (3 seviye: strateji, bölge, taktik), Q/E döndürme, eğim yakınlaştırmayla değişir. Enhanced Input; eylemler C++'ta oluşturulur (asset gerekmez). |
| `ACepheGameMode`, `ACephePlayerController` | Fare imleci, tıklama, harita modu tuşları (1-4), hız (Boşluk, +/-). |
| `SCepheHUD` (Slate) + `ACepheHUD` | Tamamen C++ arayüz: üst şerit (bayrak, kaynaklar, tarih, hız), sol menü, telgraf akışı, seçim paneli, katman düğmeleri. UMG asset'i gerekmez. |

Arama dokusu (1024 × 4, nokta örnekleme, sRGB kapalı):
- Satır 0: görüntü rengi (harita moduna göre).
- Satır 1: R = sahip ülke indeksi, G = kontrol eden ülke indeksi, B = taraf (0 tarafsız, 1 İtilaf, 2 İttifak), A = 255.
- Satır 2: R = seçili (255/0), G = üstünde (255/0), B = işgal (255/0), A = kale.
- Satır 3: R = siper seviyesi × 51, G = arazi indeksi × 51, B/A boş.

Malzeme parametreleri (`M_ProvinceMap`): `IdTex`, `LookupTex`, `HeightTex`, `PaperTex`, `MapTexelSize` (Vector2: 1/4096, 1/3112), `BorderColor`, `NationBorderColor`, `SeaColor`, `HillshadeStrength`, `MapMode` (skaler 0-3). Sınırlar shader'da komşu piksel karşılaştırmasıyla; ülke sınırı satır 1 farklıysa kalın.

## Unreal editör betikleri (level ajanı, `Scripts/level/`)

`build_map_level.py` (UE editör Python): ham dosyaları içe alır (ID dokusu: `TC_VectorDisplacementmap`/sıkıştırmasız, sRGB kapalı, `TF_Nearest`, mip yok; heightmap: `TC_Grayscale` 16-bit), FBX'leri alır, `M_ProvinceMap` malzemesini MaterialEditingLibrary + Custom HLSL düğümüyle kurar, CSV'lerden DataTable'ları oluşturur (`DT_Provinces` → `FProvinceRow`, `DT_Nations` → `FNationRow`), `Map_Europe1914` haritasını kurar ve aktörleri yerleştirir. Proje ayarı: `Map/Raw` "Additional Non-Asset Directories to Package"e eklenir.

## Varlık yolları ve parametre adları (tek kaynak)

- Dokular `/Game/Map/Textures/`: `T_ProvinceId`, `T_Height`, `T_Paper`. Mesh'ler `/Game/Map/Meshes/`: `SM_MapBoard`, `SM_WarTable`, `SM_ArmyCounter`, `SM_TrenchStrip`, `SM_RailStrip` vb. DataTable'lar `/Game/Map/`: `DT_Provinces` (`/Script/Cephe1914.ProvinceRow`), `DT_Nations` (`/Script/Cephe1914.NationRow`). Harita `/Game/Maps/Map_Europe1914` (`Config/DefaultEngine.ini` ile aynı).
- Malzemeler `/Game/Map/Materials/`: `M_ProvinceMap` (yukarıdaki parametreler), `M_TrenchStrip` (`Color`, `Intensity`; `AFrontLineActor`), `M_Rail` (`Color`; `ARailNetworkActor`), `M_ArmyCounter` (`NationColor`; `AArmyCounterActor`, organizasyon çubuğu da bunu kullanır).
- `AProvinceMapActor` özellikleri: `MapMaterialAsset`, `IdTextureAsset`, `HeightTextureAsset`, `PaperTextureAsset`, `BoardMeshAsset` (varsayılanlar yukarıdaki yollardır; betik ayrıca `map_material_asset` atar).
- HLSL Custom düğüm giriş adı `TexelSize`, bağlandığı parametre `MapTexelSize`; diğer girişler parametrelerle aynı adlı. Arama dokusu `Texture2D.Load(int3(id, satır, 0))` ile okunur (örnekleyici yok, `y = satır`).

## Doğrulama

Bu konteynerde Unreal yok: C++ derlenmez, editör betikleri çalışmaz; yalnızca sözdizimi ve statik inceleme. Veri hattı ve Blender burada çalıştırılır ve önizlemeleri üretilir.
