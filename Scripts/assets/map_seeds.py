# -*- coding: utf-8 -*-
"""Cephe 1914 bölge tohumları (Kasım 1914).

Satır biçimi:  Ad;boylam;enlem;bayraklar
Bayraklar (virgülle): t=M|H|F|S (Dağ/Tepe/Orman/Bataklık eğilimi), occ=KOD (işgalci),
fort, i=0..10 (sanayi), c=bin (büyük şehir nüfus eklemesi).
Bölümler: (sahip ülke, maske grubu, metin). Grup, "bugünkü sınır" kuralını uygular:
yalnızca o grubun kara pikselleri o bölümün tohumlarına gider. POOL = Orta/Doğu Avrupa,
Balkanlar, Rusya ve Osmanlı'nın ortak havuzu.
"""

SECTIONS = [
# ------------------------------------------------------------------ BRİTANYA
('GBR', 'GBR', """
Londra;-0.12;51.5;i=9,c=6500
Kent;0.9;51.2
Sussex;-0.4;50.9
Hampshire;-1.4;51.0
Devon;-3.7;50.7
Cornwall;-4.9;50.4
Bristol;-2.6;51.45;i=6,c=500
Güney Galler;-3.2;51.6;i=7
Orta Galler;-3.7;52.4;t=H
Kuzey Galler;-3.9;53.0;t=H
Oxford;-1.25;51.8
Doğu Anglia;1.0;52.7
Cambridge;0.1;52.2
Birmingham;-1.9;52.5;i=9,c=1500
Nottingham;-1.15;52.95;i=7
Lincolnshire;-0.3;53.2
Liverpool;-2.99;53.4;i=8,c=1000
Manchester;-2.25;53.55;i=9,c=2000
Sheffield;-1.47;53.38;i=9,c=500
Leeds;-1.55;53.85;i=8,c=500
Hull;-0.3;53.75;i=5
Cumbria;-3.0;54.5;t=H
Newcastle;-1.6;54.95;i=8,c=500
Glasgow;-4.25;55.85;i=8,c=1100
Edinburgh;-3.2;55.95;i=5,c=300
Güney İskoçya;-3.5;55.3;t=H
Aberdeen;-2.1;57.15
İskoç Dağları;-4.9;56.9;t=M
Inverness;-4.2;57.5;t=M
Dublin;-6.3;53.35;c=400
Cork;-8.5;51.9
Galway;-9.0;53.3
Limerick;-8.6;52.7
Donegal;-7.9;54.8;t=H
Belfast;-5.9;54.6;i=7,c=300
Orta İrlanda;-7.5;53.0
""".strip()),
('GBR', 'GBR_COL', """
Kıbrıs;33.2;35.1
""".strip()),
# ------------------------------------------------------------------ FRANSA
('FRA', 'FRA', """
Paris;2.35;48.85;i=8,c=3500
Meaux;2.95;48.95
Melun;3.0;48.5
Chartres;1.5;48.45
Orléans;1.9;47.9;i=3
Dunkerque;2.3;50.95;i=3
Boulogne;1.65;50.6
Béthune;2.45;50.55;i=6
Arras;2.8;50.25;i=4
Lille;3.06;50.63;occ=GER,i=9,c=700
Valenciennes;3.55;50.36;occ=GER,i=8
Cambrai;3.25;50.17;occ=GER,i=4
Amiens;2.3;49.9;i=4
Abbeville;1.85;50.1
Roye;2.78;49.7;occ=GER
Saint-Quentin;3.3;49.85;occ=GER,i=5
Vervins;3.95;49.85;occ=GER
Compiègne;2.85;49.42
Soissons;3.33;49.38
Laon;3.62;49.56;occ=GER
Reims;4.03;49.25;i=4
Rethel;4.37;49.5;occ=GER
Charleville;4.72;49.77;occ=GER,t=F,i=5
Argonne;5.05;49.35;occ=GER,t=F
Montmédy;5.4;49.52;occ=GER,t=F
Longwy-Briey;5.8;49.4;occ=GER,i=9
Verdun;5.38;49.16;fort,t=H
Châlons;4.37;48.95
Sainte-Menehould;4.9;49.0;t=F
Bar-le-Duc;5.16;48.77
Saint-Mihiel;5.55;48.88;occ=GER,t=H
Toul;5.8;48.65;fort
Nancy;6.35;48.7;i=7,c=120
Lunéville;6.55;48.55
Épinal;6.45;48.17;fort,t=H
Saint-Dié;6.95;48.28;t=M
Vesoul;6.15;47.62
Belfort;6.75;47.58;fort,t=H
Besançon;6.02;47.24;i=4
Jura;5.9;46.55;t=M
Chaumont;5.14;48.11
Troyes;4.08;48.3;i=3
Dijon;5.04;47.32
Auxerre;3.57;47.8
Nevers;3.16;47.0
Bourges;2.4;47.08
Rouen;1.1;49.44;i=5,c=120
Le Havre;0.1;49.5;i=4
Caen;-0.37;49.18
Cherbourg;-1.6;49.63
Alençon;0.1;48.43
Le Mans;0.2;47.98
Rennes;-1.68;48.11
Brest;-4.5;48.4
Vannes;-2.8;47.65
Nantes;-1.55;47.2;i=4
Angers;-0.55;47.47
Tours;0.7;47.4
Poitiers;0.35;46.58
La Rochelle;-1.15;46.15
Limoges;1.26;45.83
Périgueux;0.72;45.18
Bordeaux;-0.58;44.84;c=200
Bayonne;-1.47;43.5
Pau;-0.1;43.2;t=M
Toulouse;1.44;43.6;i=4
Cahors;1.44;44.45
Foix;1.6;42.95;t=M
Perpignan;2.9;42.7
Montpellier;3.88;43.6
Avignon;4.8;43.95
Marsilya;5.37;43.3;i=6,c=500
Nice;7.0;43.8;t=H
Grenoble;5.72;45.19;t=M,i=4
Savoie;6.4;45.4;t=M
Lyon;4.83;45.76;i=7,c=400
Saint-Étienne;4.39;45.43;i=8
Mâcon;4.8;46.3
Clermont-Ferrand;3.08;45.78;t=H
Masif Santral;2.9;44.7;t=M
Korsika;9.1;42.1;t=M
""".strip()),
('FRA', 'FRA_COL', """
Cezayir;3.05;36.75;c=200
Oran;-0.64;35.7
Konstantin;6.6;36.35
Sétif;5.4;36.2;t=H
Tunus;10.0;36.6;c=100
Sfaks;10.7;34.7
Rabat;-6.8;34.0
Fes;-5.0;34.0;t=H
""".strip()),
# ------------------------------------------------------------------ BELÇİKA
('BEL', 'BEL', """
Yser;2.85;51.05;i=2
Ypres;2.95;50.8;i=2
Brugge;3.22;51.2;occ=GER
Gent;3.72;51.05;occ=GER,i=6
Kortrijk;3.4;50.8;occ=GER,i=6
Mons;3.95;50.45;occ=GER,i=7
Charleroi;4.45;50.4;occ=GER,i=9
Namur;4.87;50.47;occ=GER,fort,i=5
Liège;5.57;50.63;occ=GER,fort,i=9,c=250
Anvers;4.4;51.22;occ=GER,fort,i=6,c=300
Brüksel;4.35;50.85;occ=GER,i=6,c=700
Limburg;5.33;50.95;occ=GER
Ardenler;5.3;50.2;occ=GER,t=H
Arlon;5.55;49.8;occ=GER,t=F
""".strip()),
('LUX', 'LUX', """
Lüksemburg;6.13;49.61;occ=GER,i=8
""".strip()),
('NED', 'NED', """
Amsterdam;4.9;52.37;i=4,c=600
Rotterdam;4.48;51.92;i=6,c=450
Zeeland;3.9;51.5
Brabant;5.2;51.5
Limburg (Hollanda);5.75;51.1;i=4
Arnhem;5.9;52.0
Zwolle;6.1;52.55
Groningen;6.57;53.2
Friesland;5.8;53.1
""".strip()),
# ------------------------------------------------------------------ ALMANYA
('GER', 'POOL', """
Aachen;6.08;50.77;i=6
Köln;6.96;50.94;i=8,c=600
Ruhr;7.4;51.5;i=10,c=3000
Münster;7.63;51.96
Ostfriesland;7.6;53.2
Bremen;8.8;53.1;i=4,c=250
Hamburg;10.0;53.55;i=8,c=1000
Kiel;9.7;54.5;i=4
Lübeck;10.8;53.85
Rostock;12.1;54.1
Stettin;14.55;53.43;i=5
Stolp;17.0;54.45
Danzig;18.65;54.35;i=5,c=100
Thorn;18.2;53.1;fort
Posen;16.93;52.41;i=3
Königsberg;20.5;54.7;fort,i=4
Allenstein;20.5;53.8;t=S
Gumbinnen;22.2;54.65
Lyck;22.3;53.85;t=S
Berlin;13.4;52.52;i=9,c=3000
Frankfurt (Oder);14.5;52.3
Magdeburg;11.6;52.1;i=5
Hannover;9.73;52.37;i=6
Kassel;9.5;51.3;t=H,i=5
Harz;10.6;51.75;t=H
Leipzig;12.37;51.34;i=8,c=300
Dresden;13.74;51.05;i=8,c=300
Chemnitz;12.9;50.8;t=H,i=9
Erfurt;11.03;50.98;i=4
Frankfurt;8.68;50.11;i=7,c=200
Saar;7.0;49.3;i=9
Pfalz;7.9;49.4;i=5
Karlsruhe;8.4;49.0;i=5
Stuttgart;9.18;48.78;i=6
Kara Orman;8.2;48.0;t=F
Ulm;10.0;48.4;t=H
Augsburg;10.7;48.3
Münih;11.58;48.14;i=6,c=500
Nürnberg;11.08;49.45;i=7
Würzburg;9.93;49.8
Regensburg;12.1;49.0;t=F
Görlitz;14.95;51.2;i=5
Glogau;16.1;51.7
Breslau;17.04;51.11;i=6,c=400
Oppeln;17.9;50.7;i=5
Yukarı Silezya;18.9;50.3;i=10,c=300
Metz;6.17;49.12;fort,i=7
Thionville;6.2;49.4;i=9
Sarrebourg;7.05;48.73
Strasbourg;7.75;48.58;fort,i=5,c=150
Colmar;7.36;48.08;i=4
Mulhouse;7.5;47.72;i=7
Thann;7.1;47.8;occ=FRA,t=H,i=3
""".strip()),
# ------------------------------------------------------------------ AVUSTURYA-MACARİSTAN
('AUH', 'POOL', """
Viyana;16.37;48.21;i=7,c=2100
Linz;14.3;48.3;i=4
Salzburg;13.05;47.8;t=M
Innsbruck;11.4;47.2;t=M
Graz;15.45;47.07;t=H,i=4
Klagenfurt;14.3;46.6;t=M
Laibach;14.5;46.05;t=H
Trieste;13.77;45.65;i=5,c=150
Pola;13.9;44.9;fort
Fiume;14.55;45.3
Zagreb;15.98;45.81;c=100
Osijek;18.7;45.55
Sarajevo;18.4;43.85;t=M
Hersek;17.8;43.3;t=M
Banja Luka;17.2;44.75;t=H
Zara;15.3;44.1;t=M
Spalato;16.5;43.5;t=M
Kotor;18.7;42.5;t=M
Prag;14.42;50.08;i=8,c=600
Pilsen;13.4;49.75;i=9
Reichenberg;15.0;50.75;i=8
Hradec Králové;15.8;50.2;i=5
Budweis;14.5;48.95
Brünn;16.6;49.2;i=7
Olmütz;17.25;49.6;i=4
Mährisch-Ostrau;18.3;49.85;i=9
Pressburg;17.1;48.15;i=4
Zvolen;19.15;48.58;t=H
Kaschau;21.25;48.72
Budapeşte;19.04;47.5;i=6,c=1000
Győr;17.65;47.7
Szombathely;16.6;47.2
Pécs;18.23;46.07
Szeged;20.15;46.25
Kecskemét;19.7;46.9
Miskolc;20.78;48.1;i=6
Debrecen;21.63;47.53
Nagyvárad;21.92;47.05
Temeşvar;21.23;45.75;i=3
Voyvodina;19.85;45.25
Klausenburg;23.6;46.77;t=H
Hermannstadt;24.15;45.8;t=M
Brașov;25.6;45.65;t=M
Maramureș;23.9;47.8;t=M
Ruthenia;22.7;48.4;t=M
Krakov;19.94;50.06;fort,i=5,c=150
Nowy Sącz;20.7;49.62;t=H
Tarnów;20.98;50.01
Rzeszów;21.9;50.04
Przemyśl;22.77;49.78;fort
Karpatlar;22.2;49.3;t=M
Sambor;23.5;49.4;occ=RUS,t=H
Lemberg;24.03;49.84;occ=RUS,i=4,c=200
Brody;25.15;50.1;occ=RUS
Tarnopol;25.6;49.55;occ=RUS
Stanislau;24.7;48.9;occ=RUS,t=H
Bukovina;25.94;48.29;occ=RUS,t=H
""".strip()),
# ------------------------------------------------------------------ SIRBİSTAN / KARADAĞ
('SER', 'POOL', """
Belgrad;20.46;44.8;c=100
Mačva;19.7;44.65
Valjevo;19.9;44.2;t=H
Kragujevac;20.9;44.0;t=H
Niş;21.9;43.32;t=H
Priştine;21.17;42.67;t=H
Novi Pazar;20.5;43.15;t=M
Üsküp;21.43;42.0;t=H
Manastır;21.35;41.03;t=H
""".strip()),
('MNT', 'POOL', """
Cetinje;19.0;42.35;t=M
Pljevlja;19.4;43.3;t=M
""".strip()),
# ------------------------------------------------------------------ İTALYA
('ITA', 'ITA', """
Torino;7.69;45.07;i=7,c=300
Milano;9.19;45.46;i=8,c=700
Verona;11.0;45.45
Venedik;12.33;45.6;i=3
Udine;13.23;46.07;t=H
Genova;8.93;44.41;i=6,c=200
Bologna;11.34;44.49;i=3
Floransa;11.25;43.77;t=H
Perugia;12.4;43.1;t=H
Ancona;13.5;43.6
Roma;12.5;41.9;c=600
Abruzzo;13.9;42.2;t=M
Napoli;14.27;40.85;i=5,c=700
Foggia;15.5;41.45
Bari;16.87;41.12
Potenza;15.8;40.6;t=H
Kalabriya;16.2;39.0;t=M
Palermo;13.35;38.1;t=H
Sicilya;14.4;37.4;t=H
Sardinya;9.0;40.0;t=H
""".strip()),
('ITA', 'ITA_COL', """
Trablus;13.2;32.9
""".strip()),
# ------------------------------------------------------------------ İSVİÇRE
('SWI', 'SWI', """
Bern;7.45;46.9;t=H
Zürih;8.55;47.37;i=4
Cenevre;6.14;46.2
Valais;7.6;46.2;t=M
Graubünden;9.5;46.7;t=M
""".strip()),
# ------------------------------------------------------------------ İSPANYA
('ESP', 'ESP', """
Madrid;-3.7;40.4;c=600
Barselona;2.17;41.4;i=6,c=600
Sevilla;-5.98;37.4
Granada;-3.6;37.2;t=M
Valensiya;-0.4;39.5
Bilbao;-2.95;43.25;i=6
Asturias;-5.8;43.3;t=M,i=3
Galiçya;-8.4;42.9;t=H
Zaragoza;-0.9;41.65
Salamanca;-5.7;41.0
Extremadura;-6.5;39.0
Córdoba;-4.8;38.0
Murcia;-1.1;38.0
La Mancha;-2.2;39.2
Pamplona;-1.64;42.8;t=H
Lleida;0.6;41.7
Burgos;-3.7;42.35
""".strip()),
('POR', 'POR', """
Lizbon;-9.1;38.7;c=250
Porto;-8.6;41.15
Coimbra;-8.4;40.2
Alentejo;-7.9;38.0
Trás-os-Montes;-7.4;41.6;t=H
""".strip()),
# ------------------------------------------------------------------ İSKANDİNAVYA
('DEN', 'DEN', """
Kopenhag;12.57;55.68;i=5,c=450
Odense;10.4;55.4
Güney Jutland;9.3;55.5
Aarhus;10.2;56.15
Aalborg;9.9;57.05
""".strip()),
('NOR', 'NOR', """
Oslo;10.75;59.9;c=200
Bergen;5.3;60.4;t=M
Stavanger;6.0;58.9;t=H
Kristiansand;8.0;58.15;t=H
Hamar;11.0;61.0;t=F
Sogn;7.0;61.2;t=M
Hardanger;7.5;60.2;t=M
""".strip()),
('SWE', 'SWE', """
Stokholm;18.07;59.33;c=400
Uppsala;17.6;59.86
Gävle;17.15;60.7;t=F
Göteborg;11.97;57.7;i=5
Malmö;13.4;55.8
Småland;14.8;57.0;t=F
Linköping;15.6;58.4
Örebro;15.2;59.3
Värmland;13.5;59.4;t=F
Dalarna;14.8;61.2;t=F
""".strip()),
# ------------------------------------------------------------------ RUSYA
('RUS', 'POOL', """
Varşova;21.0;52.23;i=5,c=880
Łódź;19.46;51.76;i=8,c=300
Płock;19.7;52.55
Włocławek;19.07;52.65;occ=GER
Kalisz;18.1;51.77;occ=GER
Radom;21.15;51.4
Kielce;20.62;50.87;t=H
Zagłębie;19.3;50.4;i=9
Lublin;22.57;51.25
Siedlce;22.27;52.17
Łomża;22.08;53.18;t=S
Suwałki;22.93;54.1;t=F
Białystok;23.16;53.13;i=4
Brest-Litovsk;23.7;52.1;fort,t=S
Zamość;23.25;50.72
Grodno;23.83;53.68;fort,t=F
Kovno;23.9;54.9;fort
Vilna;25.28;54.69;t=F
Libau;21.0;56.5
Riga;24.1;56.95;i=6,c=300
Dvinsk;26.5;55.9;t=F
Livonya;25.0;57.6;t=F
Reval;24.75;59.44
Dorpat;26.7;58.4
Pskov;28.33;57.82;t=F
Petrograd;30.3;59.94;i=9,c=2200
Novgorod;31.3;58.5;t=F
Vyborg;28.7;60.7;t=F
Helsinki;25.0;60.2
Turku;22.3;60.45;t=F
Tampere;23.8;61.5;t=F
Savonlinna;28.9;61.8;t=F
Karelya;33.0;61.3;t=F
Vologda;39.9;59.2;t=F
Kuzey Rusya;36.5;60.9;t=F
Minsk;27.56;53.9;t=F
Vitebsk;30.2;55.19;t=F
Mogilev;30.35;53.9
Gomel;31.0;52.43
Pinsk;26.1;52.1;t=S
Mozır;29.2;51.9;t=S
Smolensk;32.05;54.78;t=F
Tver;35.9;56.86;t=F
Moskova;37.62;55.76;i=7,c=1700
Tula;37.6;54.2;i=5
Bryansk;34.4;53.25;t=F
Orel;36.07;52.97
Kursk;36.19;51.73
Ryazan;39.75;54.63
Vladimir;40.4;56.13;i=5
Yaroslavl;39.9;57.6;t=F,i=4
Kostroma;41.0;57.77;t=F
Nijni Novgorod;44.0;56.3;i=5
Penza;45.0;53.2
Tambov;41.45;52.7
Voronej;39.2;51.67
Kiev;30.52;50.45;i=4,c=500
Jitomir;28.66;50.25;t=F
Çernigov;31.3;51.5;t=F
Poltava;34.55;49.6
Harkov;36.23;49.99;i=6
Yekaterinoslav;35.04;48.46;i=7
Donbas;38.0;48.4;i=8
Mariupol;37.5;47.1;i=3
Rostov;39.7;47.23;i=4
Kuban;38.98;45.04
Stavropol;41.97;45.04
Terek;45.5;43.3;t=M
Tsaritsyn;44.5;48.7
Kırım;34.0;45.2
Sivastopol;33.5;44.6;fort,t=H
Odessa;30.73;46.6;i=5,c=450
Nikolayev;32.0;46.97;i=4
Besarabya;28.8;47.0
Podolya;26.6;48.7
Volhinya;26.25;50.6;t=F
Batum;41.6;41.65;t=M
Kutaisi;42.7;42.3;t=H
Tiflis;44.79;41.72;t=H
Erivan;44.5;40.2;t=M
Kars;43.1;40.6;fort,t=M
Ardahan;42.7;41.1;t=M
""".strip()),
# ------------------------------------------------------------------ DİĞERLERİ
('ROM', 'POOL', """
Bükreş;26.1;44.43;i=4,c=300
Ploiești;26.0;44.95;i=5
Pitești;24.87;44.86;t=H
Craiova;23.8;44.32
Iași;27.58;47.15
Bacău;26.9;46.57
Galați;28.05;45.43;i=3
Dobruca;28.4;44.4
""".strip()),
('BUL', 'POOL', """
Sofya;23.32;42.7;t=H
Filibe;24.75;42.15;t=H
Varna;27.9;43.2
Ruse;25.95;43.85
Pleven;24.6;43.4
Burgas;27.45;42.5
""".strip()),
('GRE', 'GRE', """
Atina;23.72;37.98;c=200
Selanik;22.94;40.64;c=150
Epir;20.85;39.67;t=M
Teselya;22.4;39.65
Mora;21.75;38.25;t=H
Sparta;22.4;37.1;t=H
Kavala;24.4;41.0;t=H
Girit;24.8;35.25;t=M
""".strip()),
('ALB', 'POOL', """
Iskodra;19.5;42.05;t=M
Tiran;19.8;41.33;t=H
Avlonya;19.5;40.45;t=H
""".strip()),
('OTT', 'POOL', """
İstanbul;29.0;41.0;i=3,c=1100
Edirne;26.55;41.67;fort
Tekirdağ;27.5;41.0
Çanakkale;26.5;40.1;fort,t=H
Bursa;29.06;40.19;i=2
Zonguldak;31.8;41.45;t=F,i=3
Balıkesir;28.0;39.6
İzmir;27.2;38.4;c=200
Aydın;28.0;37.6
Eskişehir;30.5;39.77
Antalya;30.7;37.0;t=M
Konya;32.48;37.87
Ankara;32.85;39.93
Kırşehir;34.2;39.15
Kastamonu;33.8;41.4;t=M
Samsun;36.33;41.28
Sivas;37.02;39.75;t=H
Kayseri;35.48;38.72
Adana;35.32;37.0
Antep;37.4;37.07
Halep;37.16;36.2;c=200
Malatya;38.3;38.35;t=H
Diyarbakır;40.23;37.91
Trabzon;39.72;41.0;t=M
Erzincan;39.5;39.75;t=M
Erzurum;41.27;39.9;fort,t=M
Muş;42.1;38.7;t=M
Van;43.38;38.5;t=M
Hakkari;43.7;37.5;t=M
Musul;43.13;36.34
Kerkük;44.4;35.47
Bağdat;44.4;33.3;c=200
Deyrizor;40.15;35.33
Şam;36.29;33.5;c=250
Lübnan;35.6;33.9;t=M
""".strip()),
('PER', 'PER', """
Batı İran;45.6;36.0;t=M
""".strip()),
]

# Kasım 1914 ordular: ad, ülke, bölge adı, tümen, organizasyon
ARMIES = [
    ('Fransız 1. Ordu', 'FRA', 'Épinal', 5, 0.70),
    ('Fransız 2. Ordu', 'FRA', 'Nancy', 6, 0.66),
    ('Fransız 3. Ordu', 'FRA', 'Verdun', 5, 0.68),
    ('Fransız 4. Ordu', 'FRA', 'Sainte-Menehould', 5, 0.64),
    ('Fransız 5. Ordu', 'FRA', 'Reims', 6, 0.62),
    ('Fransız 6. Ordu', 'FRA', 'Soissons', 5, 0.60),
    ('Fransız 10. Ordu', 'FRA', 'Arras', 7, 0.58),
    ('Britanya Seferi Kuvvetleri', 'GBR', 'Ypres', 6, 0.55),
    ('Hint Kolordusu', 'GBR', 'Béthune', 2, 0.52),
    ('Belçika Ordusu', 'BEL', 'Yser', 6, 0.42),
    ('Alman 6. Ordu', 'GER', 'Lille', 7, 0.66),
    ('Alman 4. Ordu', 'GER', 'Kortrijk', 8, 0.62),
    ('Alman 1. Ordu', 'GER', 'Roye', 6, 0.60),
    ('Alman 3. Ordu', 'GER', 'Rethel', 5, 0.64),
    ('Alman 5. Ordu', 'GER', 'Montmédy', 6, 0.68),
    ('Alman 7. Ordu', 'GER', 'Strasbourg', 4, 0.60),
    ('Alman 8. Ordu', 'GER', 'Allenstein', 5, 0.70),
    ('Alman 9. Ordu', 'GER', 'Thorn', 7, 0.66),
    ('Avusturya 1. Ordu', 'AUH', 'Krakov', 6, 0.55),
    ('Avusturya 3. Ordu', 'AUH', 'Przemyśl', 5, 0.40),
    ('Avusturya 4. Ordu', 'AUH', 'Tarnów', 5, 0.50),
    ('Avusturya Balkan Ordusu', 'AUH', 'Voyvodina', 7, 0.58),
    ('Rus 2. Ordu', 'RUS', 'Łódź', 8, 0.60),
    ('Rus 4. Ordu', 'RUS', 'Lublin', 6, 0.55),
    ('Rus 9. Ordu', 'RUS', 'Varşova', 7, 0.62),
    ('Rus 3. Ordu', 'RUS', 'Lemberg', 7, 0.58),
    ('Rus 8. Ordu', 'RUS', 'Stanislau', 6, 0.50),
    ('Rus Kafkas Ordusu', 'RUS', 'Tiflis', 5, 0.55),
    ('Sırp 1. Ordu', 'SER', 'Valjevo', 5, 0.48),
    ('Osmanlı 3. Ordu', 'OTT', 'Erzurum', 6, 0.50),
    ('Osmanlı 4. Ordu', 'OTT', 'Şam', 4, 0.45),
]

# Ana demiryolu hatları (bölge adları, merkezden merkeze)
RAILS = [
    ('Paris-Lille', ['Paris', 'Amiens', 'Arras', 'Lille']),
    ('Paris-Verdun-Metz', ['Paris', 'Meaux', 'Châlons', 'Verdun', 'Metz', 'Strasbourg']),
    ('Paris-Nancy', ['Paris', 'Troyes', 'Chaumont', 'Nancy']),
    ('Paris-Belfort', ['Paris', 'Troyes', 'Vesoul', 'Belfort']),
    ('Paris-Marsilya', ['Paris', 'Auxerre', 'Dijon', 'Lyon', 'Avignon', 'Marsilya']),
    ('Paris-Bordeaux', ['Paris', 'Orléans', 'Tours', 'Poitiers', 'Bordeaux']),
    ('Paris-Le Havre', ['Paris', 'Rouen', 'Le Havre']),
    ('Paris-Brest', ['Paris', 'Chartres', 'Le Mans', 'Rennes', 'Brest']),
    ('Londra-Glasgow', ['Londra', 'Birmingham', 'Manchester', 'Cumbria', 'Glasgow']),
    ('Londra-Edinburgh', ['Londra', 'Cambridge', 'Leeds', 'Newcastle', 'Edinburgh']),
    ('Londra-Bristol', ['Londra', 'Oxford', 'Bristol']),
    ('Köln-Berlin', ['Köln', 'Ruhr', 'Hannover', 'Magdeburg', 'Berlin']),
    ('Berlin-Hamburg', ['Berlin', 'Hamburg']),
    ('Köln-Münih-Viyana', ['Köln', 'Frankfurt', 'Nürnberg', 'Münih', 'Salzburg', 'Linz', 'Viyana']),
    ('Berlin-Varşova-Petrograd', ['Berlin', 'Frankfurt (Oder)', 'Posen', 'Kalisz', 'Łódź', 'Varşova', 'Białystok', 'Grodno', 'Vilna', 'Dvinsk', 'Pskov', 'Petrograd']),
    ('Varşova-Moskova', ['Varşova', 'Brest-Litovsk', 'Minsk', 'Smolensk', 'Moskova']),
    ('Moskova-Petrograd', ['Moskova', 'Tver', 'Novgorod', 'Petrograd']),
    ('Berlin-Belgrad-İstanbul', ['Berlin', 'Dresden', 'Prag', 'Viyana', 'Budapeşte', 'Belgrad', 'Niş', 'Sofya', 'Filibe', 'Edirne', 'İstanbul']),
    ('Moskova-Odessa', ['Moskova', 'Orel', 'Kursk', 'Kiev', 'Odessa']),
    ('Moskova-Rostov', ['Moskova', 'Tula', 'Voronej', 'Rostov']),
    ('Berlin-Krakov-Lemberg', ['Berlin', 'Breslau', 'Yukarı Silezya', 'Krakov', 'Przemyśl', 'Lemberg']),
    ('Viyana-Trieste', ['Viyana', 'Graz', 'Laibach', 'Trieste']),
    ('Milano-Napoli', ['Milano', 'Bologna', 'Floransa', 'Roma', 'Napoli']),
    ('Torino-Venedik', ['Torino', 'Milano', 'Verona', 'Venedik']),
    ('Madrid-Barselona', ['Madrid', 'Zaragoza', 'Barselona']),
    ('İstanbul-Bağdat', ['İstanbul', 'Eskişehir', 'Ankara', 'Konya', 'Adana', 'Halep', 'Musul', 'Bağdat']),
    ('Bükreş-Iași', ['Bükreş', 'Galați', 'Bacău', 'Iași']),
    ('Kiev-Lemberg', ['Kiev', 'Jitomir', 'Volhinya', 'Lemberg']),
    ('Lyon-Torino', ['Lyon', 'Savoie', 'Torino']),
]
