# "Yankı" hikâyesi için gerekli mekanikler

Kaynak: `e4307096-prog/SpaceRepair` → `Docs/story-arc.md` (kopyası: [story-arc.md](story-arc.md)).
Mevcut durum, SpaceRepair'deki betiklerden ve dokümanlardan okundu (Unreal 5.8.3; oyun mantığı Blueprint'te, `Scripts/build_*.py` ile üretiliyor). Bu belgede Unreal'da çalıştırılarak doğrulanmış bir şey yok.

## Özet

Bölüm 1 (Tahliye) oyunda. Sonraki bölümler için gereken mekaniklerin yaklaşık yarısında temel parça zaten var ve genişletilmesi yeterli. Gerçekten yeni olan altı sistem var:
1. Çok haritalı yapı
2. Kalıcı kayıt (SaveGame)
3. Veriyle çalışan diyalog
4. Yankı (hayalet tekrarı)
5. Envanter ve onarım ilerlemesi
6. Seçimli final

## Mevcut temel (yeniden kullanılacak)

| Sistem | Nerede | Hikâyede ne işe yarar |
|---|---|---|
| Kontrol noktası + `BP_RunState` (GameInstance) | `route_system.py`, `build_run_state.py` | Döngü / "yeniden dene"; harita değişse de durum korunur |
| Ölüm nedenleri 1-5 + Olay Raporu | `death_sequence.py` | Eski Üs'teki "7 kaza kaydı" için veri kaynağı |
| Daktilo diyalog kutusu (konuşan, ses, satır) | `finale_sequence.py` | Köy diyaloglarının iskeleti (şu an satırlar koda gömülü) |
| Taş Dede (`BP_StoneElder`, fener, yürüme/eğilme modları) | `build_stone_elder.py` | Kor Köyü'nün ilk NPC'si |
| Sığınak modu (MissionStage 3: oksijen sabit, 22 °C, levye kapalı) | `build_first_contact.py` | Kor Köyü "güvenli merkez" |
| Bayılma post-process'i (`Faint01`: bulanıklık, renk kaybı) | `build_faint_fx.py` | "Unutturan" çekirgenin HUD/hedef bulanıklığı |
| Mino darbesi (C, 650 cm, 15 sn bekleme) | `combat_system.py` | Kristal rezonans bulmacaları |
| Levye + kilit (3 vuruş, gürültü avcıları çeker) | `combat_system.py`, `build_lock_system.py` | Kristal kapılar |
| Kart alma (süzülen, ışıklı alınabilir obje) | `build_keycard.py` | Gemi parçalarının alınması |
| Kristal Çekirge (algı, hız, ısırık, sersemleme) | `build_hunter_behavior.py`, `build_crystal_hopper.py` | Büyük çekirgeler (ölçek/parametre) |
| İnsansı figür (beliren, kaybolan) | `generate_base_presence_mesh.py`, `build_first_contact.py` | Eski astronot figürleri |
| Astronot TTS sesi, Mino bip sesleri | `make_astronaut_voice*.py`, `make_mino_voice.py` | Telsiz kaydı ("Kapıyı açma"), Mino itirafı |

## Bölüm bölüm gereken mekanikler

### Bölüm 2: Kor Köyü
- **Yeni harita + geçiş:** Final siyah ekranla bitiyor ("Kor Köyü'nde uyanacaksın…"). Şu an tek harita var (`Deck01`). Yeni bir harita (ör. `Village01`) açılmalı ve `BP_RunState` üzerinden can, tayın, Mino durumu gibi değerler taşınmalı. Uyanış sahnesi de buraya.
- **Güvenli bölge:** Sığınak mantığı (MissionStage 3) bölge hacmine bağlanmalı. İçeride ölüm, soğuk ve oksijen tüketimi olmayacak.
- **Diyalog sistemi:** `finale_sequence.py`'deki kutu genelleştirilmeli. Satırlar DataTable'a (veya Python sözlüğü → DataTable) taşınmalı, NPC'ye E ile konuşma eklenmeli. 3-4 yerli için seçenek gerekmez, doğrusal satırlar yeterli. "Dönen" satırı zaten finalde var.
- **NPC'ler:** `BP_StoneElder` şablon olarak kullanılabilir. 2-3 yerli için farklı malzeme ya da parça gerekir (`generate_native_concepts.py` konseptleri hazır). Boşta durma ve konuşma modu yeterli.
- **Kask parçası:** Bir NPC'nin boynunda statik mesh. Mekanik değil, sahne detayı. Yakınlaşınca kısa bir astronot repliği tetiklenebilir.
- **Parça haritası / görev listesi:** `route_system.py` hedef satırı genişletilmeli: 3 parça (güç hücresi, seyir çekirdeği, basınç valfi) ve her birinin durumu.
- **Telsiz kaydı:** Tetik hacmi + bozulmuş astronot sesi (TTS + telsiz filtresi) + altyazı. Tek seferlik bayrak `RunState`'te tutulmalı.
- **Mino ve çocuklar:** Mino takip modlarına bir "oyna" modu eklenmeli (hedef çocuk, daire çizerek uçma). Kristal yakınında gözlerin titremesi, huzursuzluk için.

### Bölüm 3: Kristal Mağaraları
- **Kristal kapı:** İki tip. (a) Levye kilidi (mevcut sistem, yeni mesh). (b) Rezonans kapısı. Mino darbesi şu an yalnızca avcıları sersemletiyor ve sadece dışarıda (MissionStage 1-2) çalışıyor. Yarıçapındaki "rezonans" actor'larına da olay göndermeli ve mağarada da çalışmalı.
- **Rezonans bulmacası:** En basit hali: N kristali bekleme süresi içinde sırayla darbe menziline al. Kristal başına "şarjlı" süre ve hepsi yanınca kapı açılır.
- **Büyük çekirge:** Mevcut avcı Blueprint'i ölçek, can ve sersemleme süresi parametreleriyle türetilmeli. İsırınca oksijen emme zaten tasarımda var.
- **Unutturan etkisi:** Isırık veya yakınlık `Faint01` benzeri kısa bir bulanıklık versin. Hedef satırı birkaç saniye "???" ile karışık gösterilsin. HUD'da bayrak + süre yeterli.
- **Yankılar (yeni, en zor parça):**
  - Kayıt: Oyuncunun konumu ve yönü saniyede 5-10 kez bir halka belleğe yazılır. Ölümde son ~5 sn ölüm noktası ve nedeniyle birlikte saklanır.
  - Oynatma: Yarı saydam astronot klonu (aynı mesh + fresnel/translucent malzeme). Kayıttaki noktalar arasında aradeğerle kaydırılır, ölüm animasyonu nedene göre seçilir.
  - "Bazen yanlış yola çeker": Tasarımcının elle yerleştirdiği sahte yankılar (önceden kaydedilmiş yol). Gerçek ölümlerle karıştırılır.
  - Yankının bıraktığı eşya: Ölüm noktasında alınabilir obje (kasa içeriği sistemi).
  - Kalıcılık: Oturum içi için `BP_RunState` yeter. Oyun kapatılıp açılınca da sürecekse SaveGame gerekir (aşağıda).

### Bölüm 4: Eski Üs
- **Üs iç kısmının açılması:** Şu an görünmez duvarlarla kapalı (`probe_gate_bypass.py`). Hikâye bayrağına göre duvarlar kalkmalı ya da ayrı harita yapılmalı.
- **İzleyen figürler:** Mevcut figür davranışı genişletilmeli: oyuncuya dönük durur, X cm yaklaşınca solarak kaybolur, başka bir noktada yeniden belirir.
- **Kaza kayıtları bilgisayarı:** E ile açılan bir UI paneli. 7 kayıt: bir kısmı sabit metin, bir kısmı oyuncunun gerçek ölüm nedenleri (`DeathCause` geçmişi). Bunun için ölüm geçmişi listesi kalıcı kayıtta tutulmalı.
- **Notlar:** Okunabilir el yazısı notlar (`make_human_notes.ps1` dokuları var) + E ile yakın plan metin.
- **Telsiz kaynağı:** Bölüm 2'deki kaydın orijinali. Aynı ses dosyası, bozulmasız hali.

### Bölüm 5: Kristalin Kalbi
- **Reaktör ortamı:** Mevcut reaktör montajı (`generate_reactor_assembly.py`) kristalle kaplanmış hali.
- **Mino itirafı:** Diyalog sistemi + Mino ses klipleri. Mino'nun "hafıza" değeri (ör. ölüm sayısıyla azalan) itiraf metnini etkileyebilir.
- **Seçim UI'ı:** İki seçenekli karar ekranı. Sonuç bayrağı kalıcı kayda yazılmalı.
  - Döngüyü kır: reaktör kapanır, çekirgeler sakinleşir (avcı davranışında "sakin" modu), Mino fabrika ayarı (yeni tanışma diyaloğu), son sahne.
  - Döngüde kal: oyun başa döner, oyuncunun yazdığı ya da seçtiği "sonraki sen" notu kaydedilir. Yeni oyunda bu not ve yankı görünür (New Game+).

## Ortak altyapı (önce bunlar)

1. **SaveGame:** Projede yok (`BP_RunState` yalnızca oturum boyunca yaşıyor). Gerekenler: ölüm geçmişi (neden, yer, süre), yankı kayıtları, toplanan parçalar, hikâye bayrakları (telsiz duyuldu, Dönen sahnesi, seçim), döngü sayısı. Blueprint `SaveGame` sınıfı + `SaveGameToSlot`/`LoadGameFromSlot`.
2. **Çok harita:** `OpenLevel` zaten kullanılıyor. `RunState`'e "hedef harita + giriş noktası" eklenmeli.
3. **Hikâye bayrakları:** Tek yerde (RunState + SaveGame) isimli bool/int alanlar. Tetik hacimleri bunlara yazsın.
4. **Diyalog verisi:** Konuşan, metin, ses, koşul bayrağı. Tüm NPC ve telsiz satırları buradan.
5. **Envanter / onarım:** 3 parça için 3 bool + köyde ilerleme göstergesi. Genel bir envanter şart değil.

## Önerilen sıra

Story-arc'taki "sıradaki dilim" ile uyumlu:

1. SaveGame + hikâye bayrakları + harita geçişi
2. Diyalog verisi (finale kutusunu genelleştir)
3. Kor Köyü dilimi: alan, ışık, 3 yerli, "Dönen", kask parçası, parça haritası, telsiz
4. Kristal kapı + Mino rezonansı + büyük çekirge
5. Yankı sistemi (önce oturum içi, sonra kalıcı)
6. Eski Üs (figürler, kayıt bilgisayarı, notlar)
7. Final + seçim + New Game+

## Riskler ve açık sorular

- Yankı sistemi Blueprint'i Python'la üretmek açısından en ağır iş: kayıt dizisi, aradeğerleme ve klon actor gerekiyor. C++ ile yazmak daha temiz olabilir, ama proje şu an saf Blueprint.
- Unreal kilidi: SpaceRepair'in kuralına göre aynı anda tek `UnrealEditor` açık olabilir. Harita ve Blueprint üreten işler paralel yürüyemez. Paralel gidebilenler: Blender modelleri (yerliler, kristaller, büyük çekirge), diyalog metinleri, ses üretimi.
- "Döngüde kal" sonunda oyuncunun not yazması metin girişi ister. Basitlik için hazır not seçenekleri önerilir.
- Kor Köyü yeraltında. Işık bütçesi (kristal emissive + çok noktasal ışık) performansı etkileyebilir, Lumen ayarlarını kontrol etmek gerekir.
