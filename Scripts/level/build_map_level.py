"""Cephe 1914: harita seviyesini kuran Unreal editor betigi (idempotent).

Calistirma:
  UnrealEditor-Cmd Cephe1914.uproject -run=pythonscript -script="Scripts/level/build_map_level.py"
  (veya editorde: Tools > Execute Python Script)
Onkosul: C++ modulu derlenmis olmali (ProvinceRow, NationRow, ProvinceMapActor... siniflari yuklu).
Not: Bu betik Linux'ta calistirilamadi; yalnizca py_compile ile dogrulandi.
"""
import os
import traceback

import unreal

# ----------------------------------------------------------------------------------------------
# Sabitler
# ----------------------------------------------------------------------------------------------
PROJECT_DIR = unreal.Paths.project_dir()
RAW_DIR = os.path.join(PROJECT_DIR, "Content", "Map", "Raw")
FBX_DIR = os.path.join(RAW_DIR, "FBX")
SHADER_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "shaders", "ProvinceMap.hlsl")

TEX_PATH = "/Game/Map/Textures"
MESH_PATH = "/Game/Map/Meshes"
MAT_PATH = "/Game/Map/Materials"
MAP_PATH = "/Game/Maps/Map_Europe1914"
BUILD_TAG = "Cephe1914Build"       # bu betigin yerlestirdigi aktorler; yeniden calismada silinip yeniden kurulur

TABLE_Z = -40.0                    # SM_WarTable ofseti (levhanin altina); mesh sinirina gore elle ayarlanabilir
TEXEL_SIZE = (1.0 / 4096.0, 1.0 / 3112.0)

mel = unreal.MaterialEditingLibrary
eal = unreal.EditorAssetLibrary
atools = unreal.AssetToolsHelpers.get_asset_tools()


def log(msg):
    unreal.log("[CepheMap] " + str(msg))


def warn(msg):
    unreal.log_warning("[CepheMap] " + str(msg))


def try_set(obj, prop, value):
    """set_editor_property, ozellik yoksa/uymuyorsa uyar ve devam et."""
    try:
        obj.set_editor_property(prop, value)
        return True
    except Exception as exc:  # noqa: BLE001
        warn("ozellik atanamadi %s.%s: %s" % (obj.get_name() if hasattr(obj, "get_name") else obj, prop, exc))
        return False


# ----------------------------------------------------------------------------------------------
# 1. Doku iceri alma
# ----------------------------------------------------------------------------------------------
def import_file(filename, dest_path, dest_name, options=None):
    task = unreal.AssetImportTask()
    task.set_editor_property("filename", filename)
    task.set_editor_property("destination_path", dest_path)
    task.set_editor_property("destination_name", dest_name)
    task.set_editor_property("replace_existing", True)
    task.set_editor_property("replace_existing_settings", True)
    task.set_editor_property("automated", True)
    task.set_editor_property("save", False)
    if options is not None:
        task.set_editor_property("options", options)
    atools.import_asset_tasks([task])
    paths = list(task.get_editor_property("imported_object_paths"))
    return paths


def import_textures():
    specs = [
        ("province_id.png", "T_ProvinceId"),
        ("heightmap.png", "T_Height"),
        ("paper.png", "T_Paper"),
    ]
    for fname, name in specs:
        src = os.path.join(RAW_DIR, fname)
        if not os.path.isfile(src):
            raise RuntimeError("ham dosya yok: " + src)
        import_file(src, TEX_PATH, name)
        tex = eal.load_asset("%s/%s" % (TEX_PATH, name))
        if tex is None:
            raise RuntimeError("doku icerigi alinamadi: " + name)

        if name == "T_ProvinceId":
            # ID dokusu: renk degeri VERIDIR; sikistirma/sRGB/filtre/mip dokunmamali.
            # TC_VECTOR_DISPLACEMENTMAP = sikistirilmamis 8-bit RGBA, dogrusal (DXT yok).
            try_set(tex, "compression_settings", unreal.TextureCompressionSettings.TC_VECTOR_DISPLACEMENTMAP)
            try_set(tex, "srgb", False)
            try_set(tex, "filter", unreal.TextureFilter.TF_NEAREST)
            try_set(tex, "mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
            try_set(tex, "lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
            try_set(tex, "never_stream", True)
            try_set(tex, "address_x", unreal.TextureAddress.TA_CLAMP)
            try_set(tex, "address_y", unreal.TextureAddress.TA_CLAMP)
        elif name == "T_Height":
            # 16-bit korumak icin TC_GRAYSCALE (G16 olarak kalir). TC_HDR float16'ya cevirir
            # (11 bit mantis) ve 65535 adimi tam tutamaz; bu yuzden Grayscale secildi.
            try_set(tex, "compression_settings", unreal.TextureCompressionSettings.TC_GRAYSCALE)
            try_set(tex, "srgb", False)
            try_set(tex, "filter", unreal.TextureFilter.TF_BILINEAR)
            try_set(tex, "mip_gen_settings", unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
            try_set(tex, "never_stream", True)
            try_set(tex, "address_x", unreal.TextureAddress.TA_CLAMP)
            try_set(tex, "address_y", unreal.TextureAddress.TA_CLAMP)
        else:  # T_Paper
            try_set(tex, "srgb", True)
            try_set(tex, "address_x", unreal.TextureAddress.TA_WRAP)
            try_set(tex, "address_y", unreal.TextureAddress.TA_WRAP)
            try_set(tex, "mip_gen_settings", unreal.TextureMipGenSettings.TMGS_FROM_TEXTURE_GROUP)
        eal.save_loaded_asset(tex)
        log("doku hazir: " + name)


# ----------------------------------------------------------------------------------------------
# 2. FBX iceri alma
# ----------------------------------------------------------------------------------------------
def make_fbx_options():
    opts = unreal.FbxImportUI()
    try_set(opts, "import_mesh", True)
    try_set(opts, "import_as_skeletal", False)
    try_set(opts, "import_materials", True)
    try_set(opts, "import_textures", False)
    try_set(opts, "import_animations", False)
    try_set(opts, "mesh_type_to_import", unreal.FBXImportType.FBXIT_STATIC_MESH)
    sm = opts.get_editor_property("static_mesh_import_data")
    try_set(sm, "combine_meshes", False)          # birlestirme yok
    try_set(sm, "auto_generate_collision", True)
    return opts


def import_fbx():
    if not os.path.isdir(FBX_DIR):
        warn("FBX klasoru yok: " + FBX_DIR)
        return
    for fname in sorted(os.listdir(FBX_DIR)):
        if not fname.lower().endswith(".fbx"):
            continue
        name = os.path.splitext(fname)[0]
        import_file(os.path.join(FBX_DIR, fname), MESH_PATH, name, make_fbx_options())
        mesh = eal.load_asset("%s/%s" % (MESH_PATH, name))
        if mesh is None:
            warn("FBX alinamadi: " + fname)
            continue
        if name == "SM_MapBoard":
            # Tiklama/izleme icin karmasik cokgen = basit cokgen
            try:
                body = mesh.get_editor_property("body_setup")
                body.set_editor_property("collision_trace_flag",
                                         unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
            except Exception as exc:  # noqa: BLE001
                warn("MapBoard cokgen carpisma ayari yapilamadi: %s" % exc)
        eal.save_loaded_asset(mesh)
        log("mesh hazir: " + name)


# ----------------------------------------------------------------------------------------------
# 3. Malzemeler
# ----------------------------------------------------------------------------------------------
def get_or_create_material(name):
    path = "%s/%s" % (MAT_PATH, name)
    if eal.does_asset_exist(path):
        mat = eal.load_asset(path)
        mel.delete_all_material_expressions(mat)   # idempotent: bastan kur
        return mat
    return atools.create_asset(name, MAT_PATH, unreal.Material, unreal.MaterialFactoryNew())


def node(mat, cls, x, y):
    return mel.create_material_expression(mat, cls, x, y)


def vec_param(mat, pname, value, x, y):
    n = node(mat, unreal.MaterialExpressionVectorParameter, x, y)
    n.set_editor_property("parameter_name", pname)
    n.set_editor_property("default_value", unreal.LinearColor(*value))
    return n


def scalar_param(mat, pname, value, x, y):
    n = node(mat, unreal.MaterialExpressionScalarParameter, x, y)
    n.set_editor_property("parameter_name", pname)
    n.set_editor_property("default_value", value)
    return n


def tex_param(mat, pname, texture, sampler_type, x, y):
    n = node(mat, unreal.MaterialExpressionTextureObjectParameter, x, y)
    n.set_editor_property("parameter_name", pname)
    n.set_editor_property("texture", texture)
    try_set(n, "sampler_type", sampler_type)
    return n


def build_province_material():
    mat = get_or_create_material("M_ProvinceMap")
    id_tex = eal.load_asset(TEX_PATH + "/T_ProvinceId")
    h_tex = eal.load_asset(TEX_PATH + "/T_Height")
    p_tex = eal.load_asset(TEX_PATH + "/T_Paper")
    ST = unreal.MaterialSamplerType

    n_id = tex_param(mat, "IdTex", id_tex, ST.SAMPLERTYPE_LINEAR_COLOR, -900, -300)
    # Arama dokusu C++ tarafindan calisirken verilir; varsayilan olarak ayni ayarlarda T_ProvinceId konur
    n_lk = tex_param(mat, "LookupTex", id_tex, ST.SAMPLERTYPE_LINEAR_COLOR, -900, -150)
    n_h = tex_param(mat, "HeightTex", h_tex, ST.SAMPLERTYPE_LINEAR_GRAYSCALE, -900, 0)
    n_p = tex_param(mat, "PaperTex", p_tex, ST.SAMPLERTYPE_COLOR, -900, 150)
    n_texel = vec_param(mat, "MapTexelSize", (TEXEL_SIZE[0], TEXEL_SIZE[1], 0.0, 0.0), -900, 300)
    n_border = vec_param(mat, "BorderColor", (0.18, 0.11, 0.07, 0.75), -900, 450)
    n_nborder = vec_param(mat, "NationBorderColor", (0.07, 0.04, 0.03, 1.0), -900, 600)
    n_sea = vec_param(mat, "SeaColor", (0.50, 0.60, 0.63, 1.0), -900, 750)
    n_hill = scalar_param(mat, "HillshadeStrength", 0.6, -900, 900)
    n_mode = scalar_param(mat, "MapMode", 0.0, -900, 1050)
    n_uv = node(mat, unreal.MaterialExpressionTextureCoordinate, -900, -450)

    with open(SHADER_FILE, "r", encoding="utf-8") as f:
        code = f.read()

    cust = node(mat, unreal.MaterialExpressionCustom, -300, 0)
    cust.set_editor_property("code", code)
    cust.set_editor_property("description", "ProvinceMap")
    cust.set_editor_property("output_type", unreal.CustomMaterialOutputType.CMOT_FLOAT4)
    input_names = ["UV", "IdTex", "LookupTex", "HeightTex", "PaperTex", "TexelSize",
                   "BorderColor", "NationBorderColor", "SeaColor", "HillshadeStrength", "MapMode"]
    inputs = []
    for nm in input_names:
        ci = unreal.CustomInput()
        ci.set_editor_property("input_name", nm)
        inputs.append(ci)
    cust.set_editor_property("inputs", inputs)

    links = [
        (n_uv, "UV"), (n_id, "IdTex"), (n_lk, "LookupTex"), (n_h, "HeightTex"), (n_p, "PaperTex"),
        (n_texel, "TexelSize"), (n_border, "BorderColor"), (n_nborder, "NationBorderColor"),
        (n_sea, "SeaColor"), (n_hill, "HillshadeStrength"), (n_mode, "MapMode"),
    ]
    for src, pin in links:
        if not mel.connect_material_expressions(src, "", cust, pin):
            warn("Custom girisi baglanamadi: " + pin)

    mel.connect_material_property(cust, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rough = node(mat, unreal.MaterialExpressionConstant, -300, 250)
    rough.set_editor_property("r", 0.95)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)

    mel.recompile_material(mat)
    eal.save_loaded_asset(mat)
    log("M_ProvinceMap kuruldu")
    return mat


def build_trench_material():
    mat = get_or_create_material("M_TrenchStrip")
    color = vec_param(mat, "Color", (0.55, 0.04, 0.03, 1.0), -600, 0)   # kirmizi murekkep
    inten = scalar_param(mat, "Intensity", 1.0, -600, 200)
    mul = node(mat, unreal.MaterialExpressionMultiply, -300, 0)
    mel.connect_material_expressions(color, "", mul, "A")
    mel.connect_material_expressions(inten, "", mul, "B")
    mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_BASE_COLOR)
    mel.connect_material_property(mul, "", unreal.MaterialProperty.MP_EMISSIVE_COLOR)
    rough = node(mat, unreal.MaterialExpressionConstant, -300, 250)
    rough.set_editor_property("r", 0.85)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    eal.save_loaded_asset(mat)
    return mat


def build_counter_material():
    mat = get_or_create_material("M_ArmyCounter")
    nation = vec_param(mat, "NationColor", (0.2, 0.2, 0.6, 1.0), -700, 0)
    wood = node(mat, unreal.MaterialExpressionConstant3Vector, -700, 200)
    wood.set_editor_property("constant", unreal.LinearColor(0.30, 0.17, 0.08, 1.0))
    alpha = node(mat, unreal.MaterialExpressionConstant, -700, 380)
    alpha.set_editor_property("r", 0.8)
    lerp = node(mat, unreal.MaterialExpressionLinearInterpolate, -350, 0)
    mel.connect_material_expressions(wood, "", lerp, "A")
    mel.connect_material_expressions(nation, "", lerp, "B")
    mel.connect_material_expressions(alpha, "", lerp, "Alpha")
    mel.connect_material_property(lerp, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rough = node(mat, unreal.MaterialExpressionConstant, -350, 250)
    rough.set_editor_property("r", 0.65)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    eal.save_loaded_asset(mat)
    return mat


def build_rail_material():
    mat = get_or_create_material("M_Rail")
    c = vec_param(mat, "Color", (0.05, 0.045, 0.04, 1.0), -400, 0)   # C++ RailColor ile boyanir
    mel.connect_material_property(c, "", unreal.MaterialProperty.MP_BASE_COLOR)
    rough = node(mat, unreal.MaterialExpressionConstant, -400, 200)
    rough.set_editor_property("r", 0.7)
    mel.connect_material_property(rough, "", unreal.MaterialProperty.MP_ROUGHNESS)
    mel.recompile_material(mat)
    eal.save_loaded_asset(mat)
    return mat


# ----------------------------------------------------------------------------------------------
# 4. CSV -> DataTable
# ----------------------------------------------------------------------------------------------
def build_datatable(asset_name, csv_name, struct_path):
    path = "/Game/Map/" + asset_name
    csv = os.path.join(RAW_DIR, csv_name)
    if not os.path.isfile(csv):
        raise RuntimeError("CSV yok: " + csv)
    struct = unreal.load_object(None, struct_path)
    if struct is None:
        raise RuntimeError("satir yapisi yuklenemedi (C++ derlendi mi?): " + struct_path)

    if eal.does_asset_exist(path):
        eal.delete_asset(path)   # yeniden olustur (idempotent)
    factory = unreal.DataTableFactory()
    factory.set_editor_property("struct", struct)
    dt = atools.create_asset(asset_name, "/Game/Map", unreal.DataTable, factory)
    if dt is None:
        raise RuntimeError("DataTable olusmadi: " + asset_name)
    result = unreal.DataTableFunctionLibrary.fill_data_table_from_csv_file(dt, csv)
    # Surume gore bool veya sorun listesi doner
    log("%s CSV sonucu: %s" % (asset_name, result))
    names = unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)
    log("%s satir sayisi: %d" % (asset_name, len(names)))
    eal.save_loaded_asset(dt)
    return dt


# ----------------------------------------------------------------------------------------------
# 5. Seviye
# ----------------------------------------------------------------------------------------------
def load_class(path):
    cls = unreal.load_class(None, path)
    if cls is None:
        warn("sinif yuklenemedi: " + path)
    return cls


def spawn(cls, loc=(0.0, 0.0, 0.0), rot=(0.0, 0.0, 0.0), label=None):
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actor = sub.spawn_actor_from_class(cls, unreal.Vector(*loc), unreal.Rotator(rot[0], rot[1], rot[2]))
    if actor is None:
        warn("aktor uretilemedi: %s" % cls)
        return None
    if label:
        actor.set_actor_label(label)
    tags = list(actor.get_editor_property("tags"))
    tags.append(BUILD_TAG)
    actor.set_editor_property("tags", tags)
    return actor


def clear_previous(world_actors):
    sub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    count = 0
    for a in world_actors:
        try:
            if BUILD_TAG in [str(t) for t in a.get_editor_property("tags")]:
                sub.destroy_actor(a)
                count += 1
        except Exception:  # noqa: BLE001
            pass
    if count:
        log("onceki calismadan %d aktor silindi" % count)


def build_level(board_mat):
    lvl = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    asub = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if eal.does_asset_exist(MAP_PATH):
        lvl.load_level(MAP_PATH)
        clear_previous(asub.get_all_level_actors())
    else:
        if not lvl.new_level(MAP_PATH):
            raise RuntimeError("seviye olusturulamadi: " + MAP_PATH)

    # Cephe aktorleri (C++)
    pm_cls = load_class("/Script/Cephe1914.ProvinceMapActor")
    fl_cls = load_class("/Script/Cephe1914.FrontLineActor")
    rn_cls = load_class("/Script/Cephe1914.RailNetworkActor")
    if pm_cls:
        pm = spawn(pm_cls, label="ProvinceMap")
        if pm and board_mat:
            # C++ varsayilanlari (MapMaterialAsset, IdTextureAsset, HeightTextureAsset, PaperTextureAsset,
            # BoardMeshAsset) bu betigin yollariyla ayni; TSoftObjectPtr ozelligi acikca da atanir.
            try_set(pm, "map_material_asset", unreal.SoftObjectPath(MAT_PATH + "/M_ProvinceMap.M_ProvinceMap"))
    if fl_cls:
        spawn(fl_cls, label="FrontLines")
    if rn_cls:
        spawn(rn_cls, label="RailNetwork")

    # Masa
    table = eal.load_asset(MESH_PATH + "/SM_WarTable")
    if table:
        t_actor = spawn(unreal.StaticMeshActor, (0.0, 0.0, TABLE_Z), label="WarTable")
        if t_actor:
            t_actor.static_mesh_component.set_static_mesh(table)

    # Isiklar: alcak, sicak lamba isigi
    sun = spawn(unreal.DirectionalLight, (0.0, 0.0, 2000.0), (-22.0, 215.0, 0.0), "LampLight")
    if sun:
        comp = sun.get_component_by_class(unreal.DirectionalLightComponent)
        try_set(comp, "intensity", 4.0)
        try_set(comp, "light_color", unreal.Color(255, 188, 120, 255))
        try_set(comp, "atmosphere_sun_light", False)
        try_set(comp, "mobility", unreal.ComponentMobility.MOVABLE)
    sky = spawn(unreal.SkyLight, (0.0, 0.0, 3000.0), label="SkyLight")
    if sky:
        comp = sky.get_component_by_class(unreal.SkyLightComponent)
        try_set(comp, "intensity", 0.35)
        try_set(comp, "real_time_capture", True)
        try_set(comp, "mobility", unreal.ComponentMobility.MOVABLE)
    fog = spawn(unreal.ExponentialHeightFog, (0.0, 0.0, 0.0), label="Fog")
    if fog:
        comp = fog.get_component_by_class(unreal.ExponentialHeightFogComponent)
        try_set(comp, "fog_density", 0.002)
        try_set(comp, "fog_inscattering_color", unreal.LinearColor(0.35, 0.28, 0.20, 1.0))
    ppv = spawn(unreal.PostProcessVolume, label="PostProcess")
    if ppv:
        try_set(ppv, "unbound", True)
        st = ppv.get_editor_property("settings")
        try_set(st, "override_vignette_intensity", True)
        try_set(st, "vignette_intensity", 0.45)
        try_set(st, "override_auto_exposure_method", True)
        try_set(st, "auto_exposure_method", unreal.AutoExposureMethod.AEM_MANUAL)
        try_set(st, "override_auto_exposure_bias", True)
        try_set(st, "auto_exposure_bias", 1.0)
        try_set(ppv, "settings", st)
    spawn(unreal.PlayerStart, (0.0, 0.0, 3000.0), (-60.0, 0.0, 0.0), "PlayerStart")

    # World Settings: GameMode
    gm_cls = load_class("/Script/Cephe1914.CepheGameMode")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if gm_cls and world:
        try_set(world.get_world_settings(), "default_game_mode", gm_cls)

    lvl.save_current_level()
    log("seviye kaydedildi: " + MAP_PATH)


def set_packaging():
    """Content/Map/Raw'i 'Additional Non-Asset Directories to Package' listesine ekle (en iyi gayret)."""
    try:
        s = unreal.get_default_object(unreal.ProjectPackagingSettings)
        dirs = list(s.get_editor_property("directories_to_always_stage_as_non_ufs"))
        existing = [d.get_editor_property("path") for d in dirs]
        if "Map/Raw" not in existing:
            dp = unreal.DirectoryPath()
            dp.set_editor_property("path", "Map/Raw")
            dirs.append(dp)
            s.set_editor_property("directories_to_always_stage_as_non_ufs", dirs)
            s.save_config()
        log("paketleme dizini tamam: Map/Raw")
    except Exception as exc:  # noqa: BLE001
        warn("paketleme ayari yapilamadi, elle ekleyin (Project Settings > Packaging): %s" % exc)


# ----------------------------------------------------------------------------------------------
def main():
    try:
        import_textures()
        import_fbx()
        board_mat = build_province_material()
        build_trench_material()
        build_counter_material()
        build_rail_material()
        build_datatable("DT_Provinces", "provinces.csv", "/Script/Cephe1914.ProvinceRow")
        build_datatable("DT_Nations", "nations.csv", "/Script/Cephe1914.NationRow")
        build_level(board_mat)
        set_packaging()
        unreal.log("CEPHE_MAP_READY")
    except Exception:  # noqa: BLE001
        unreal.log_error("CEPHE_MAP_FAILED\n" + traceback.format_exc())
        raise


main()
