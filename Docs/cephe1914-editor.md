# Cephe 1914: editor betikleri

Sozlesme: `Docs/cephe1914-teknik.md`. Bu betikler Linux konteynerinde calistirilamadi; yalnizca `py_compile` ile sozdizimi dogrulandi.

## Calistirma sirasi
1. Ham veri hatti ciktilari `Content/Map/Raw/` altinda olmali (PNG, CSV, `FBX/*.fbx`).
2. C++ modulunu derle (Cephe1914 editor hedefi). `ProvinceRow`, `NationRow`, `ProvinceMapActor`, `FrontLineActor`, `RailNetworkActor`, `CepheGameMode` siniflari yuklenmeden betik DataTable ve aktor adimlarinda hata verir.
3. Harita kurulumu:
   `UnrealEditor-Cmd.exe Cephe1914.uproject -run=pythonscript -script="Scripts/level/build_map_level.py"`
   (veya editorde Tools > Execute Python Script). Sonda logda `CEPHE_MAP_READY` aranir; hata olursa `CEPHE_MAP_FAILED` ve izleme yazilir.
4. Dogrulama:
   `UnrealEditor-Cmd.exe Cephe1914.uproject -run=pythonscript -script="Scripts/level/verify_map_level.py"`
   Sonuc: `Saved/cephe-verify.json` (`ok` + her kontrol icin ayrinti).

Betik idempotent: dokular/FBX yeniden alinir, malzemeler bastan kurulur, DataTable'lar silinip yeniden olusur, seviyedeki `Cephe1914Build` etiketli aktorler silinip yeniden yerlestirilir. HLSL `Scripts/level/shaders/ProvinceMap.hlsl` dosyasindan okunur; shader'i degistirince betigi yeniden calistirmak yeterli.

## Bilinen riskler (dogrulanmadi)
- UE Python API adlari surume gore degisir; emin olunmayanlar: `MaterialExpressionCustom.inputs` atamasi (`CustomInput`) ve `connect_material_expressions` ile Custom giris adlari; `TextureObjectParameter.sampler_type` enum degerleri (`SAMPLERTYPE_LINEAR_GRAYSCALE`); `DataTableFunctionLibrary.fill_data_table_from_csv_file` donus tipi; `LevelEditorSubsystem.new_level` yeni seviyeyi kaydedip kaydetmedigi; PostProcessVolume `settings` override alanlari; ProvinceMapActor'un malzeme ozellik adi (betik `map_material` vb. dener, yoksa uyarir).
- `TC_VECTOR_DISPLACEMENTMAP` ile ID dokusunun gercekten sikistirilmamis 8-bit olarak kaldigi editorde Texture > Details'ten kontrol edilmeli; degilse `TC_EDITOR_ICON` denenir. Heightmap icin `TC_GRAYSCALE` (G16) secildi; `TC_HDR` float16'ya cevirip hassasiyet kaybettirir.
- 4096 x 3112 ID dokusu `Load` ile okunur (ornekleyici yok); HLSL'de `Texture2D.Load` ve `SampleLevel` Custom dugumde derlenmezse `<Ad>Sampler` adlari kontrol edilmeli.
- Arama dokusu girisine C++ calisirken dinamik malzemeyle `LookupTex` verilir; statik varsayilan T_ProvinceId'dir (yalnizca derleme icin).
- `SM_WarTable` yuksekligi (`TABLE_Z = -40`) mesh sinirlarina gore elle ayarlanir.
- `Map/Raw` paketleme dizini ayari en iyi gayretle yazilir; olmazsa Project Settings > Packaging > Additional Non-Asset Directories to Package'a elle `Map/Raw` eklenir.
- Isik degerleri (yogunluk, renk) gorsel olarak ayar ister; Lumen acikken DirectionalLight hareketli yapilmistir.
