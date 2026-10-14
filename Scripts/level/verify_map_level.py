"""Cephe 1914: harita seviyesini dogrular, sonucu Saved/cephe-verify.json'a yazar.

  UnrealEditor-Cmd Cephe1914.uproject -run=pythonscript -script="Scripts/level/verify_map_level.py"
"""
import csv
import json
import os

import unreal

PROJECT_DIR = unreal.Paths.project_dir()
RAW_DIR = os.path.join(PROJECT_DIR, "Content", "Map", "Raw")
OUT = os.path.join(unreal.Paths.project_saved_dir(), "cephe-verify.json")
MAP_PATH = "/Game/Maps/Map_Europe1914"

eal = unreal.EditorAssetLibrary
mel = unreal.MaterialEditingLibrary
results = {}


def check(name, ok, detail=""):
    results[name] = {"ok": bool(ok), "detail": str(detail)}


def csv_rows(fname):
    with open(os.path.join(RAW_DIR, fname), "r", encoding="utf-8-sig", newline="") as f:
        return max(0, sum(1 for _ in csv.reader(f)) - 1)


def main():
    try:
        lvl = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
        check("level_load", lvl.load_level(MAP_PATH), MAP_PATH)

        actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
        classes = [a.get_class().get_name() for a in actors]
        for cname in ("ProvinceMapActor", "FrontLineActor", "RailNetworkActor", "DirectionalLight",
                      "SkyLight", "ExponentialHeightFog", "PostProcessVolume", "PlayerStart"):
            check("actor_" + cname, cname in classes)
        labels = [a.get_actor_label() for a in actors]
        check("actor_WarTable", "WarTable" in labels)

        world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
        gm = world.get_world_settings().get_editor_property("default_game_mode")
        check("gamemode", gm is not None and "CepheGameMode" in gm.get_name(), gm)

        # Malzeme parametreleri
        mat = eal.load_asset("/Game/Map/Materials/M_ProvinceMap")
        check("mat_M_ProvinceMap", mat is not None)
        if mat:
            tex = [str(n) for n in mel.get_texture_parameter_names(mat)]
            sca = [str(n) for n in mel.get_scalar_parameter_names(mat)]
            vec = [str(n) for n in mel.get_vector_parameter_names(mat)]
            for n in ("IdTex", "LookupTex", "HeightTex", "PaperTex"):
                check("param_tex_" + n, n in tex)
            for n in ("HillshadeStrength", "MapMode"):
                check("param_scalar_" + n, n in sca)
            for n in ("MapTexelSize", "BorderColor", "NationBorderColor", "SeaColor"):
                check("param_vector_" + n, n in vec)
        for mname, params in (("M_TrenchStrip", ("Color", "Intensity")), ("M_ArmyCounter", ("NationColor",)),
                              ("M_Rail", ("Color",))):
            m = eal.load_asset("/Game/Map/Materials/" + mname)
            check("mat_" + mname, m is not None)
            if m and params:
                allp = [str(n) for n in (list(mel.get_scalar_parameter_names(m))
                                         + list(mel.get_vector_parameter_names(m)))]
                for p in params:
                    check("param_%s_%s" % (mname, p), p in allp)

        # Dokular
        for t in ("T_ProvinceId", "T_Height", "T_Paper"):
            check("tex_" + t, eal.does_asset_exist("/Game/Map/Textures/" + t))
        pid = eal.load_asset("/Game/Map/Textures/T_ProvinceId")
        if pid:
            check("tex_id_nearest", pid.get_editor_property("filter") == unreal.TextureFilter.TF_NEAREST)
            check("tex_id_srgb_off", not pid.get_editor_property("srgb"))

        # DataTable satir sayilari (CSV ile karsilastir)
        for dt_name, csv_name in (("DT_Provinces", "provinces.csv"), ("DT_Nations", "nations.csv")):
            dt = eal.load_asset("/Game/Map/" + dt_name)
            expected = csv_rows(csv_name)
            got = len(unreal.DataTableFunctionLibrary.get_data_table_row_names(dt)) if dt else -1
            check("dt_" + dt_name, dt is not None and got == expected and got > 0,
                  "satir=%s beklenen=%s" % (got, expected))
    except Exception as exc:  # noqa: BLE001
        check("exception", False, exc)

    all_ok = all(v["ok"] for v in results.values())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"ok": all_ok, "checks": results}, f, indent=2, ensure_ascii=False)
    unreal.log("CEPHE_VERIFY_%s -> %s" % ("OK" if all_ok else "FAIL", OUT))


main()
