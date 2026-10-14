# Cephe 1914: C++ modülü (gameplay ajanı)

Sözleşme: `Docs/cephe1914-teknik.md`. Bu belge `Source/Cephe1914` modülünün haritası, derleme adımları ve bilinen risklerdir. Not: kod Linux'ta yazıldı, hiç derlenmedi.

## Sınıf haritası (`Source/Cephe1914/`)

| Dosya | İçerik |
|---|---|
| `Core/CepheTypes.h` | `EMapMode`, `ESide`, `ETerrain`, `FProvinceRow`, `FNationRow`, `CepheMap` (dünya ölçeği, UV↔dünya) |
| `Core/CepheData.*` | JSON yükleyiciler: `LoadFronts/Rails/Armies/Adjacency` (`Content/Map/Raw`) |
| `Core/CepheUtil.*` | sessiz asset yükleme, `TintSlot`, `BuildSplineStrip` (USplineComponent + USplineMeshComponent) |
| `Map/ProvinceMapSubsystem.*` | ID dokusu CPU'da, DataTable'lar, 1024×4 arama dokusu, seçim/hover/mod, delegeler |
| `Map/ProvinceMapActor.*` | levha mesh'i, `MID` parametreleri, imleç→levha ışını, hover |
| `Map/FrontLineActor.*`, `Map/RailNetworkActor.*` | JSON'dan spline şeritler |
| `Map/ArmyCounterActor.*`, `Map/ArmyManager.*` | ordu işareti (blok + organizasyon çubuğu), `armies.json`'dan spawn |
| `Camera/StrategyCameraPawn.*` | SpringArm + Camera, WASD/ok, kenar kaydırma, 3 seviye zoom, Q/E |
| `Game/CepheInput.*` | Enhanced Input eylemleri ve eşleme bağlamı (asset yok) |
| `Game/CepheGameMode.*` | varsayılan sınıflar; BeginPlay'de eksik aktörleri (levha, cephe, demiryolu, ordu yöneticisi) spawn eder |
| `Game/CephePlayerController.*` | imleç, tıklama, 1-4 katman, Boşluk, +/-, F1-F6 (`OnMenuKey`) |
| `Game/CepheClock.*` | `UTickableWorldSubsystem`: 14 Kasım 1914 başlangıç, hız 0-4, saatlik tık |
| `Game/CepheHUD.*`, `UI/SCepheHUD.*` | Slate arayüz (üst şerit, sol menü, telgraf, seçim paneli, katman düğmeleri) |

Arama dokusu: sütun = bölge kimliği (< 1024). Ülke indeksi = `DT_Nations` satır sırası + 1 (0 = yok). Satır 0 renkleri dokuya sRGB kapalı yazıldığı için doğrusal değer olduğu gibi kodlanır (`ToFColor(false)`).

## Beklenen asset yolları (level ajanı bunları üretmeli veya `AProvinceMapActor` özelliklerinden değiştirmeli)

- `/Game/Map/DT_Provinces`, `/Game/Map/DT_Nations` (sözleşme)
- `/Game/Map/Meshes/SM_MapBoard`, `SM_TrenchStrip`, `SM_RailStrip`, `SM_ArmyCounter` (sözleşme; yoksa levha düzleme, ordu bloğu küpe düşer, şeritler çizilmez)
- Sözleşmede olmayan, varsayım: `/Game/Map/M_ProvinceMap` (malzeme), `/Game/Map/T_ProvinceId`, `T_Heightmap`, `T_Paper` (dokular), isteğe bağlı `/Game/Map/M_Strip` ve `/Game/Map/M_CounterColor` ("Color" vektör parametreli, şeritler için "Used with Spline Meshes" açık)
- Harita: `/Game/Map/Map_Europe1914` (`Config/DefaultEngine.ini` varsayılan harita)

## Derleme (Windows, VS 2022)

1. Unreal Engine 5.4 (veya 5.5) kur; Visual Studio 2022'de "Game development with C++" iş yükü, MSVC v143 ve Windows SDK.
2. `Cephe1914.uproject` dosyasına sağ tık → "Generate Visual Studio project files" (`EngineAssociation` farklıysa sürüm seçtirir).
3. `Cephe1914.sln` aç, yapılandırma `Development Editor`, platform `Win64`, hedef `Cephe1914Editor` → Build. Ya da `.uproject`'i çift tıkla, modül derlensin diye "Yes" de.
4. Paketleme: `Map/Raw` `DefaultGame.ini` içinde `DirectoriesToAlwaysStageAsUFS` olarak ekli ("Additional Non-Asset Directories to Package").

## İlk açılışta

1. Editör açılınca Output Log'da `LogCephe` hatalarına bak (yüklenemeyen asset/JSON uyarıları orada).
2. Level ajanının betiği `Scripts/level/build_map_level.py`'yi editörde çalıştır (ham dosyaları içe aktarır, `M_ProvinceMap`, DataTable'lar ve `Map_Europe1914` kurulur).
3. Betik `M_ProvinceMap` içinde `IdTex, LookupTex, HeightTex, PaperTex, MapTexelSize, BorderColor, NationBorderColor, SeaColor, HillshadeStrength, MapMode` parametrelerini üretmeli; doku yolları yukarıdaki varsayımla uyuşmuyorsa `AProvinceMapActor` özelliklerinden düzelt.
4. Oynat (PIE): GameMode `/Script/Cephe1914.CepheGameMode` olarak ayarlı; haritada aktör yoksa GameMode kendisi üretir.

Kontroller: WASD/ok = kaydır, tekerlek = zoom (3 seviye), Q/E = döndür, sol tık = seç, 1-4 = katman, Boşluk = duraklat, +/- = hız, F1-F6 = menü.

## Bilinen riskler

- Hiç derlenmedi: ilk derlemede küçük hatalar beklenir (aşağıdaki liste en olasılar).
- `FProvinceRow.Population/Industry` `float` (CSV'de tam sayı da kayan da gelse okunur); sözleşme türü belirtmiyor.
- Hover/seçim, harita yüksekliğini hesaba katmadan `HoverPlaneZ` düzlemine ışın atar; yüksek rölyefte kamera eğikken birkaç piksel sapma olabilir. Cephe/demiryolu Z'si sabit ofsettir (rölyefi izlemez), `SM_MapBoard` yüksekliği/merkezi sözleşmedeki gibi (dünya orijini, ≤ 600 cm) varsayıldı.
- Ordu bloğu boyutu `SM_ArmyCounter` ölçüsüne göre `BlockSize/BarMaxLength` ile elle ayarlanır; ülke rengi malzeme slotu 1'e ("Color" parametresi) uygulanır.
- Üst şeritteki kaynak değerleri (insan gücü, sanayi...) yer tutucudur; ekonomi sistemi yok.
- Mono yazı tipi `Engine/Content/Slate/Fonts/DroidSansMono.ttf` dosyasından yüklenir, yoksa varsayılan yazıya düşer.
- Fare tekerleği `EKeys::MouseWheelAxis` + `Triggered` ile bir adım sayılır; bazı aygıtlarda kare başına birden fazla tetiklenebilir.
- Bölge sayısı 1023'ü aşarsa arama dokusu genişliği (1024) büyütülmelidir.
- Çok sayıda `USplineMeshComponent` (binlerce parça) oluşturulur; `MinStepCm` ile seyreltilir.
