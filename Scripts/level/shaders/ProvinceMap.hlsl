// ProvinceMap.hlsl - M_ProvinceMap Custom (HLSL) dugumunun govdesi (Cephe 1914).
// build_map_level.py bu dosyayi okuyup Custom dugume koyar. Fonksiyon govdesidir: "return" ile biter.
//
// Custom dugum girisleri (adlar birebir ayni olmali):
//   UV (float2), IdTex, LookupTex, HeightTex, PaperTex (Texture2D nesneleri; <ad>Sampler otomatik),
//   TexelSize (float4, xy = 1/4096, 1/3112), BorderColor (rgba, a = opaklik),
//   NationBorderColor (rgba, a = opaklik), SeaColor (rgb), HillshadeStrength (float), MapMode (float)
// Cikis: float4 (rgb = taban renk, a = 1).
//
// Arama dokusu (1024 x 4): satir 0 = goruntu rengi; satir 1: R sahip, G kontrol, B taraf;
// satir 2: R secili, G ustunde, B isgal, A kale; satir 3: R siper*51, G arazi*51.

#define LOOKUP(i, row) LookupTex.Load(int3(min((i), 1023), (row), 0))

int2 dim = int2(round(1.0 / TexelSize.x), round(1.0 / TexelSize.y));
int2 px = clamp(int2(floor(UV * float2(dim))), int2(0, 0), dim - int2(1, 1));

// --- Kimlik cozumu: id = round(R*255) + round(G*255)*256 (nokta ornekleme) ---
float4 idc = IdTex.Load(int3(px, 0));
int id = (int)round(idc.r * 255.0) + (int)round(idc.g * 255.0) * 256;
bool sea = (id == 0);

float4 row1 = LOOKUP(id, 1) * 255.0;
float4 row2 = LOOKUP(id, 2);
int owner = (int)round(row1.r);
bool selected = row2.r > 0.5;
bool hovered = row2.g > 0.5;
bool occupied = row2.b > 0.5;

// --- Komsu 4 piksel: bolge sinirinin, ulke sinirinin ve kiyinin tespiti ---
const int2 dirs4[4] = { int2(1, 0), int2(-1, 0), int2(0, 1), int2(0, -1) };
float regionEdge = 0.0;
float nationEdge = 0.0;
float coastEdge = 0.0;

[unroll]
for (int r = 1; r <= 3; r++)
{
    [unroll]
    for (int k = 0; k < 4; k++)
    {
        int2 np = clamp(px + dirs4[k] * r, int2(0, 0), dim - int2(1, 1));
        float4 nc = IdTex.Load(int3(np, 0));
        int nid = (int)round(nc.r * 255.0) + (int)round(nc.g * 255.0) * 256;
        bool nsea = (nid == 0);
        if (nid != id)
        {
            if (r == 1) regionEdge = 1.0;                       // ince bolge siniri
            if (nsea != sea) { if (r <= 2) coastEdge = 1.0; }   // kiyi cizgisi
            else if (!sea)
            {
                int nowner = (int)round(LOOKUP(nid, 1).r * 255.0);
                if (nowner != owner) nationEdge = 1.0;          // kalin ulke siniri (3 piksele kadar)
            }
        }
    }
}

// --- Taban renk ---
float3 col;
if (sea)
{
    col = SeaColor.rgb;
    // Kiyi taramasi: 8 yonde 10 ve 22 piksel uzakta kara ara, bantta cizgi desenini ciz
    const int2 dirs8[8] = { int2(1,0), int2(-1,0), int2(0,1), int2(0,-1), int2(1,1), int2(-1,1), int2(1,-1), int2(-1,-1) };
    float nearHit = 0.0;
    float farHit = 0.0;
    [unroll]
    for (int d = 0; d < 8; d++)
    {
        int2 p1 = clamp(px + dirs8[d] * 10, int2(0, 0), dim - int2(1, 1));
        int2 p2 = clamp(px + dirs8[d] * 22, int2(0, 0), dim - int2(1, 1));
        float4 c1 = IdTex.Load(int3(p1, 0));
        float4 c2 = IdTex.Load(int3(p2, 0));
        if (c1.r + c1.g > 0.0) nearHit = 1.0;
        if (c2.r + c2.g > 0.0) farHit = 1.0;
    }
    float band = max(nearHit, farHit * 0.6);
    float stripe = step(0.5, frac((float)(px.x + px.y) * 0.125));   // capraz tarama
    col = lerp(col, col * 0.78, band * stripe);
}
else
{
    col = LOOKUP(id, 0).rgb;   // satir 0 = goruntu rengi (MapMode ne olursa olsun, C++ gunceller)
}

// --- Tepe golgesi (heightmap, merkezi farklar) ---
if (!sea)
{
    float2 d = TexelSize.xy * 2.0;
    float hx1 = HeightTex.SampleLevel(HeightTexSampler, UV + float2(d.x, 0), 0).r;
    float hx0 = HeightTex.SampleLevel(HeightTexSampler, UV - float2(d.x, 0), 0).r;
    float hy1 = HeightTex.SampleLevel(HeightTexSampler, UV + float2(0, d.y), 0).r;
    float hy0 = HeightTex.SampleLevel(HeightTexSampler, UV - float2(0, d.y), 0).r;
    float3 n = normalize(float3(-(hx1 - hx0) * 90.0, -(hy1 - hy0) * 90.0, 1.0));   // UV y asagi
    float3 L = normalize(float3(-0.6, -0.6, 0.55));                                // kuzeybati isik
    float shade = dot(n, L) - L.z / length(L);
    float strength = HillshadeStrength * (MapMode > 1.5 && MapMode < 2.5 ? 1.6 : 1.0); // arazi modunda guclu
    col *= saturate(1.0 + shade * strength);
}

// --- Isgal: capraz koyu tarama (isgalci rengi icin ayri yol yok) ---
if (occupied && !sea)
{
    float hatch = step(0.7, frac((float)(px.x - px.y) * (1.0 / 14.0)));
    col = lerp(col, col * 0.35, hatch);
}

// --- Hover / secim ---
if (hovered && !sea) col = lerp(col, float3(1.0, 0.97, 0.85), 0.22);
if (selected && !sea) col = lerp(col, float3(1.0, 0.92, 0.6), 0.30);

// --- Kagit dokusu carpimi ---
float3 paper = PaperTex.Sample(PaperTexSampler, UV * float2(8.0, 6.0)).rgb;
col *= lerp(float3(1, 1, 1), saturate(paper * 1.12), 0.65);

// --- Murekkep cizgiler ---
col = lerp(col, BorderColor.rgb, regionEdge * BorderColor.a);
col = lerp(col, BorderColor.rgb * 0.8, coastEdge * 0.85);
col = lerp(col, NationBorderColor.rgb, nationEdge * NationBorderColor.a);
if (selected && regionEdge > 0.5) col = lerp(col, float3(0.95, 0.75, 0.15), 0.9);

return float4(col, 1.0);
