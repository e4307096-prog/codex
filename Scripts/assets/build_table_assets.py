# -*- coding: utf-8 -*-
"""Cephe 1914: masa üstü harita varlıkları (Blender, bpy, başsız) ve render önizlemeleri.

Çalıştırma (repo kökünden, önce make_map_data.py çalışmış olmalı):
    python3 Scripts/assets/build_table_assets.py              # FBX + renderlar
    python3 Scripts/assets/build_table_assets.py --fbx-only
    python3 Scripts/assets/build_table_assets.py --render-only [a|b|c]
    python3 Scripts/assets/build_table_assets.py --quick      # düşük çözünürlük/örnek (hızlı deneme)

Birim notu: model Blender'da METRE ile kurulur (levha 409.6 x 311.2 m); FBX dışa aktarımı
`apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', global_scale=1` ile UnitScaleFactor=100 yazar
(köşe değerleri metre, dosya birimi 100 cm); Unreal bunu santimetreye çevirir -> levha 40960 x 31120 cm.
Eksenler: Blender +X = Unreal +X, Blender +Y = Unreal -Y (içe aktarmada), +Z yukarı.
UV: Blender V = 1 - Unreal V; dokunun sol üst köşesi (0,0) Unreal dünyasında (-20480, -15560) noktasına düşer.
"""
import json, math, os, sys, time
import numpy as np
from PIL import Image
import bpy, bmesh
from mathutils import Vector, Matrix, Euler

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..'))
RAW = os.path.join(ROOT, 'Content', 'Map', 'Raw')
FBXDIR = os.path.join(RAW, 'FBX')
IMG = os.path.join(ROOT, 'Docs', 'img', 'cephe1914')
Image.MAX_IMAGE_PIXELS = None
U = 0.01  # cm -> m
BW, BH = 409.6, 311.2  # levha (m)
GX, GY = 512, 389      # ızgara hücresi
MAXH_CM = 600.0
QUICK = '--quick' in sys.argv


def log(msg, t0=[time.time()]):
    print('[%6.1fs] %s' % (time.time() - t0[0], msg), flush=True)


# ------------------------------------------------------------------ genel yardımcılar
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.unit_settings.system = 'METRIC'
    sc.unit_settings.scale_length = 1.0
    return sc


def mat(name, color, rough=0.6, metal=0.0, tex=None):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metal
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    if tex:
        t = nt.nodes.new('ShaderNodeTexImage')
        t.image = tex
        t.interpolation = 'Linear'
        nt.links.new(t.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = (*color, 1.0)
    return m


def wood_mat(name, c1, c2, rough=0.5, scale=3.0):
    """Prosedürel ahşap (yalnızca render için; FBX'e düz malzeme gider)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputMaterial')
    bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
    bsdf.inputs['Roughness'].default_value = rough
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale * 0.12, scale * 0.12)
    wv = nt.nodes.new('ShaderNodeTexWave')
    wv.wave_type = 'BANDS'
    wv.inputs['Scale'].default_value = 3.0
    wv.inputs['Distortion'].default_value = 6.0
    wv.inputs['Detail'].default_value = 3.0
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (*c1, 1)
    ramp.color_ramp.elements[1].color = (*c2, 1)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    nt.links.new(mp.outputs['Vector'], wv.inputs['Vector'])
    nt.links.new(wv.outputs['Fac'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return m


def new_bm():
    return bmesh.new()


def add_box(bm, size, center, bevel=0.0, seg=2, mi=0, rot_z=0.0):
    """size/center cm cinsinden."""
    r = bmesh.ops.create_cube(bm, size=1.0)
    verts = r['verts']
    for v in verts:
        v.co = Vector((v.co.x * size[0] * U, v.co.y * size[1] * U, v.co.z * size[2] * U))
    if rot_z:
        bmesh.ops.rotate(bm, verts=verts, cent=(0, 0, 0), matrix=Matrix.Rotation(rot_z, 3, 'Z'))
    bmesh.ops.translate(bm, verts=verts, vec=(center[0] * U, center[1] * U, center[2] * U))
    faces = list({f for v in verts for f in v.link_faces})
    for f in faces:
        f.material_index = mi
    if bevel > 0:
        edges = list({e for v in verts for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=edges, offset=bevel * U, offset_type='OFFSET', segments=seg, profile=0.5, affect='EDGES', clamp_overlap=True)
    return verts


def add_cyl(bm, r1, r2, h, center, seg=24, bevel=0.0, mi=0, bseg=2, cap=True):
    r = bmesh.ops.create_cone(bm, cap_ends=cap, cap_tris=False, segments=seg, radius1=r1 * U, radius2=r2 * U, depth=h * U)
    verts = r['verts']
    bmesh.ops.translate(bm, verts=verts, vec=(center[0] * U, center[1] * U, center[2] * U))
    for f in {f for v in verts for f in v.link_faces}:
        f.material_index = mi
    if bevel > 0:
        edges = list({e for v in verts for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=edges, offset=bevel * U, offset_type='OFFSET', segments=bseg, profile=0.5, affect='EDGES', clamp_overlap=True)
    return verts


def add_sphere(bm, radius, center, mi=0, seg=24):
    r = bmesh.ops.create_uvsphere(bm, u_segments=seg, v_segments=seg // 2, radius=radius * U)
    verts = r['verts']
    bmesh.ops.translate(bm, verts=verts, vec=(center[0] * U, center[1] * U, center[2] * U))
    for f in {f for v in verts for f in v.link_faces}:
        f.material_index = mi
    return verts


def box_uv(bm, scale_cm=100.0):
    uvl = bm.loops.layers.uv.verify()
    for f in bm.faces:
        n = f.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for l in f.loops:
            c = l.vert.co / U / scale_cm
            uv = (c.y, c.z) if ax == 0 else (c.x, c.z) if ax == 1 else (c.x, c.y)
            l[uvl].uv = uv


def finish_obj(name, bm, mats, smooth=True, uv_fn=None):
    (uv_fn or box_uv)(bm)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    if smooth:
        for p in me.polygons:
            p.use_smooth = True
    for m in mats:
        me.materials.append(m)
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    return ob


# ------------------------------------------------------------------ varlıklar
def mats_basic():
    return dict(
        Wood=mat('Wood', (0.46, 0.29, 0.15), 0.55),
        WoodDark=mat('WoodDark', (0.22, 0.12, 0.07), 0.5),
        Flag=mat('Flag', (0.75, 0.75, 0.72), 0.8),
        Stone=mat('Stone', (0.62, 0.60, 0.55), 0.8),
        Roof=mat('Roof', (0.55, 0.22, 0.15), 0.7),
        Earth=mat('Earth', (0.30, 0.22, 0.14), 0.95),
        Sandbag=mat('Sandbag', (0.58, 0.52, 0.36), 0.95),
        Ballast=mat('Ballast', (0.34, 0.33, 0.31), 0.95),
        Steel=mat('Steel', (0.42, 0.42, 0.44), 0.4, 0.9),
        PinHead=mat('PinHead', (0.72, 0.08, 0.06), 0.3),
        Brass=mat('Brass', (0.72, 0.55, 0.2), 0.3, 1.0),
        MapSurface=mat('M_MapBoard', (0.8, 0.8, 0.75), 0.9),
    )


def build_map_board(M, hm):
    """Yer değiştirilmiş levha: hm = heightmap (uint16, H x W)."""
    from scipy import ndimage as ndi
    xs = np.linspace(-BW / 2, BW / 2, GX + 1)
    ys = np.linspace(-BH / 2, BH / 2, GY + 1)
    X, Y = np.meshgrid(xs, ys)  # (GY+1, GX+1)
    h, w = hm.shape
    px = (X / BW + 0.5) * (w - 1)
    py = (0.5 - Y / BH) * (h - 1)
    v = ndi.map_coordinates(hm.astype(np.float32), [py, px], order=1)
    cm = np.where(v >= 8192, (v - 8192) / (65535 - 8192) * MAXH_CM, (v - 8192) / 8192.0 * 20.0)
    Z = cm * U
    verts = np.stack([X, Y, Z], -1).reshape(-1, 3).astype(np.float32)
    nx = GX + 1
    idx = np.arange((GX + 1) * (GY + 1)).reshape(GY + 1, nx)
    quads = np.stack([idx[:-1, :-1], idx[:-1, 1:], idx[1:, 1:], idx[1:, :-1]], -1).reshape(-1, 4)
    me = bpy.data.meshes.new('SM_MapBoard')
    me.vertices.add(len(verts))
    me.vertices.foreach_set('co', verts.ravel())
    nl = len(quads) * 4
    me.loops.add(nl)
    me.loops.foreach_set('vertex_index', quads.ravel().astype(np.int32))
    me.polygons.add(len(quads))
    me.polygons.foreach_set('loop_start', np.arange(0, nl, 4, dtype=np.int32))
    me.polygons.foreach_set('loop_total', np.full(len(quads), 4, np.int32))
    me.update(calc_edges=True)
    uvl = me.uv_layers.new(name='UVMap')
    vi = np.empty(nl, np.int32)
    me.loops.foreach_get('vertex_index', vi)
    u = (verts[vi, 0] + BW / 2) / BW
    vv = (verts[vi, 1] + BH / 2) / BH
    uvl.data.foreach_set('uv', np.stack([u, vv], -1).ravel().astype(np.float32))
    for p in me.polygons:
        p.use_smooth = True
    me.materials.append(M['MapSurface'])
    me.validate()
    ob = bpy.data.objects.new('SM_MapBoard', me)
    bpy.context.scene.collection.objects.link(ob)
    return ob, (xs, ys, Z)


def build_war_table(M):
    bm = new_bm()
    TW, TD = 46000, 35000
    top = -30.0  # üst yüzey z (cm): levha (deniz en çok -20 cm) bunun üstünde durur
    add_box(bm, (TW, TD, 1800), (0, 0, top - 900), bevel=500, seg=3, mi=0)
    # levhayı çerçeveleyen çıta (içi boş)
    fw, fh = 900, 450
    ox, oy = 40960 / 2 + fw / 2, 31120 / 2 + fw / 2
    add_box(bm, (40960 + 2 * fw, fw, fh), (0, oy, top + fh / 2), bevel=120, mi=1)
    add_box(bm, (40960 + 2 * fw, fw, fh), (0, -oy, top + fh / 2), bevel=120, mi=1)
    add_box(bm, (fw, 31120, fh), (ox, 0, top + fh / 2), bevel=120, mi=1)
    add_box(bm, (fw, 31120, fh), (-ox, 0, top + fh / 2), bevel=120, mi=1)
    # etek
    add_box(bm, (TW - 4000, 1400, 1800), (0, TD / 2 - 2200, top - 2700), bevel=250, mi=1)
    add_box(bm, (TW - 4000, 1400, 1800), (0, -TD / 2 + 2200, top - 2700), bevel=250, mi=1)
    add_box(bm, (1400, TD - 4000, 1800), (TW / 2 - 2200, 0, top - 2700), bevel=250, mi=1)
    add_box(bm, (1400, TD - 4000, 1800), (-TW / 2 + 2200, 0, top - 2700), bevel=250, mi=1)
    # ayaklar: yuvarlatılmış, aşağı doğru daralan
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (TW / 2 - 2600), sy * (TD / 2 - 2600)
            add_cyl(bm, 1700, 1200, 10500, (cx, cy, top - 1800 - 5250), seg=20, bevel=300, mi=1)
            add_cyl(bm, 2100, 2100, 700, (cx, cy, top - 1800 - 350), seg=20, bevel=200, mi=1)
            add_cyl(bm, 1500, 1500, 600, (cx, cy, top - 1800 - 10500 - 300), seg=20, bevel=200, mi=1)
    return finish_obj('SM_WarTable', bm, [M['Wood'], M['WoodDark']])


def build_army_counter(M):
    bm = new_bm()
    add_box(bm, (600, 360, 200), (0, 0, 100), bevel=40, seg=3, mi=0)
    # üst yüz: bayrak/sembol için ayrı slot (0..1 UV)
    add_box(bm, (540, 300, 14), (0, 0, 200 + 5), bevel=8, seg=1, mi=1)
    # ön yönü belli eden küçük kama (ahşap)
    add_box(bm, (60, 280, 40), (300 + 10, 0, 60), bevel=14, seg=2, mi=0)

    def uv(bm_):
        box_uv(bm_)
        uvl = bm_.loops.layers.uv.verify()
        for f in bm_.faces:
            if f.material_index == 1 and f.normal.z > 0.9:
                for l in f.loops:
                    c = l.vert.co / U
                    l[uvl].uv = ((c.x + 270) / 540.0, (c.y + 150) / 300.0)
    return finish_obj('SM_ArmyCounter', bm, [M['Wood'], M['Flag']], uv_fn=uv)


def build_fort_marker(M):
    bm = new_bm()
    add_cyl(bm, 260, 240, 70, (0, 0, 35), seg=28, bevel=18, mi=0)
    add_cyl(bm, 170, 150, 260, (0, 0, 70 + 130), seg=28, bevel=14, mi=0)
    add_cyl(bm, 205, 205, 40, (0, 0, 350), seg=28, bevel=12, mi=0)
    for k in range(8):
        a = k * math.pi / 4
        add_box(bm, (58, 74, 80), (math.cos(a) * 180, math.sin(a) * 180, 370 + 40), bevel=10, mi=0, rot_z=a)
    add_cyl(bm, 8, 8, 160, (0, 0, 370 + 80), seg=10, mi=1)
    add_box(bm, (70, 4, 44), (38, 0, 370 + 130), bevel=1, seg=1, mi=1)
    return finish_obj('SM_FortMarker', bm, [M['Stone'], M['Roof']])


def build_trench_strip(M):
    """X: 0..100 cm, Y: -30..+30 cm, Z: 0..~10 cm. Dişli kenar +Y tarafında, çuval siperi -Y tarafında."""
    bm = new_bm()
    # zigzag zemin
    pts = [(0, -30), (100, -30), (100, 22)]
    for k in range(5):
        xr = 100 - k * 20
        pts += [(xr - 10, 34), (xr - 20, 22)]
    verts = [bm.verts.new((x * U, y * U, 0)) for x, y in pts]
    f = bm.faces.new(verts)
    f.material_index = 0
    r = bmesh.ops.extrude_face_region(bm, geom=[f])
    ev = [e for e in r['geom'] if isinstance(e, bmesh.types.BMVert)]
    bmesh.ops.translate(bm, verts=ev, vec=(0, 0, 4 * U))
    # kanal: ortada koyu çukur
    add_box(bm, (100, 24, 1.5), (50, 2, 4.2), mi=0)
    # çuval sırası (-Y tarafı)
    for k in range(5):
        add_box(bm, (17, 11, 8), (10 + k * 20, -22, 8), bevel=3, seg=2, mi=1)
    for k in range(4):
        add_box(bm, (17, 10, 7), (20 + k * 20, -22, 15), bevel=3, seg=2, mi=1)
    # dişlerin üstüne küçük çuvallar
    for k in range(5):
        add_box(bm, (9, 7, 5), (10 + k * 20, 29, 6.5), bevel=2, seg=2, mi=1)
    return finish_obj('SM_TrenchStrip', bm, [M['Earth'], M['Sandbag']])


def build_rail_strip(M):
    """X: 0..100 cm, Y: -18..18, Z: 0..~6."""
    bm = new_bm()
    add_box(bm, (100, 36, 2.5), (50, 0, 1.25), bevel=0.8, seg=1, mi=0)
    for k in range(8):
        add_box(bm, (5, 32, 2.2), (6.25 + k * 12.5, 0, 3.6), bevel=0.7, seg=1, mi=1)
    for sy in (-9, 9):
        add_box(bm, (100, 2.4, 3.2), (50, sy, 6.3), bevel=0.6, seg=1, mi=2)
    return finish_obj('SM_RailStrip', bm, [M['Ballast'], M['Wood'], M['Steel']])


def build_command_pin(M):
    bm = new_bm()
    add_cyl(bm, 1.2, 12, 100, (0, 0, 50), seg=14, mi=1)        # iğne (uç aşağıda)
    add_cyl(bm, 22, 22, 14, (0, 0, 104), seg=20, bevel=3, mi=1)
    add_cyl(bm, 10, 10, 50, (0, 0, 135), seg=16, bevel=2, mi=1)
    add_sphere(bm, 46, (0, 0, 195), mi=0)
    return finish_obj('SM_CommandPin', bm, [M['PinHead'], M['Brass']])


# ------------------------------------------------------------------ dışa aktarma
def export_fbx(ob, path):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    ob.select_set(True)
    bpy.context.view_layer.objects.active = ob
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, object_types={'MESH'}, global_scale=1.0, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Z', axis_up='Y', bake_space_transform=False,
                             mesh_smooth_type='FACE', add_leaf_bones=False, use_mesh_modifiers=True, path_mode='AUTO', batch_mode='OFF')


def verify_fbx(path):
    try:
        from io_scene_fbx import parse_fbx
        root, ver = parse_fbx.parse(path)
        info = {'ver': ver}
        for el in root.elems:
            if el.id == b'GlobalSettings':
                for p in el.elems[1].elems:
                    if p.props[0] == b'UnitScaleFactor':
                        info['UnitScaleFactor'] = p.props[4]
        vmax = None
        for el in root.elems:
            if el.id == b'Objects':
                for g in el.elems:
                    if g.id == b'Geometry':
                        for c in g.elems:
                            if c.id == b'Vertices':
                                a = np.array(c.props[0])
                                a = a.reshape(-1, 3)
                                info['bbox_file'] = [round(float(x), 2) for x in (a.max(0) - a.min(0))]
                                info['nverts'] = len(a)
        if 'bbox_file' in info:
            info['bbox_cm'] = [round(x * info.get('UnitScaleFactor', 1.0), 1) for x in info['bbox_file']]
        return info
    except Exception as e:
        return {'err': str(e)}


def build_and_export():
    os.makedirs(FBXDIR, exist_ok=True)
    hm = np.array(Image.open(os.path.join(RAW, 'heightmap.png'))).astype(np.uint16)
    reset_scene()
    M = mats_basic()
    objs = {}
    ob, _ = build_map_board(M, hm)
    objs['SM_MapBoard'] = ob
    objs['SM_WarTable'] = build_war_table(M)
    objs['SM_ArmyCounter'] = build_army_counter(M)
    objs['SM_FortMarker'] = build_fort_marker(M)
    objs['SM_TrenchStrip'] = build_trench_strip(M)
    objs['SM_RailStrip'] = build_rail_strip(M)
    objs['SM_CommandPin'] = build_command_pin(M)
    for name, o in objs.items():
        # her FBX'te yalnızca kendisi: diğerlerini gizle
        p = os.path.join(FBXDIR, name + '.fbx')
        export_fbx(o, p)
        info = verify_fbx(p)
        d = o.dimensions
        log('%s.fbx %.1f KB  blender m: %.2f x %.2f x %.2f  %s' % (name, os.path.getsize(p) / 1024, d.x, d.y, d.z, info))


# ------------------------------------------------------------------ render sahneleri
def set_render(sc, w=1600, h=900, samples=48):
    if QUICK:
        w, h, samples = 800, 450, 12
    sc.render.engine = 'CYCLES'
    sc.cycles.device = 'CPU'
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    try:
        sc.cycles.denoiser = 'OPENIMAGEDENOISE'
    except Exception:
        pass
    sc.cycles.max_bounces = 4
    sc.cycles.diffuse_bounces = 2
    sc.cycles.glossy_bounces = 2
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_depth = '8'
    sc.render.threads_mode = 'AUTO'
    try:
        sc.cycles.use_adaptive_sampling = True
        sc.cycles.adaptive_threshold = 0.03
    except Exception:
        pass


def set_world(sc, top=(0.55, 0.62, 0.68), bottom=(0.16, 0.15, 0.14), strength=0.9):
    w = bpy.data.worlds.new('W')
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new('ShaderNodeOutputWorld')
    bg = nt.nodes.new('ShaderNodeBackground')
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    ramp = nt.nodes.new('ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*bottom, 1)
    ramp.color_ramp.elements[1].position = 0.55
    ramp.color_ramp.elements[1].color = (*top, 1)
    mr = nt.nodes.new('ShaderNodeMapRange')
    mr.inputs['From Min'].default_value = -1
    mr.inputs['From Max'].default_value = 1
    nt.links.new(tc.outputs['Generated'], sep.inputs['Vector'])
    # Generated 0..1: Z bileşeni
    nt.links.new(sep.outputs['Z'], ramp.inputs['Fac'])
    nt.links.new(ramp.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = strength
    nt.links.new(bg.outputs['Background'], out.inputs['Surface'])


def sun(sc, loc_rot, energy=3.0, angle=0.05, color=(1.0, 0.94, 0.85)):
    ld = bpy.data.lights.new('Sun', 'SUN')
    ld.energy = energy
    ld.angle = angle
    ld.color = color
    ob = bpy.data.objects.new('Sun', ld)
    ob.rotation_euler = Euler(loc_rot, 'XYZ')
    sc.collection.objects.link(ob)
    return ob


def area_light(sc, loc, target, size, energy, color=(1, 1, 1)):
    ld = bpy.data.lights.new('Area', 'AREA')
    ld.energy = energy
    ld.size = size
    ld.color = color
    ob = bpy.data.objects.new('Area', ld)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(ob)
    return ob


def camera(sc, loc, target, lens=35, fstop=None, focus=None, shift_y=0.0):
    cd = bpy.data.cameras.new('Cam')
    cd.lens = lens
    cd.clip_start = 0.05
    cd.clip_end = 3000
    cd.sensor_width = 36
    cd.shift_y = shift_y
    if fstop:
        cd.dof.use_dof = True
        cd.dof.aperture_fstop = fstop
        cd.dof.focus_distance = focus or (Vector(target) - Vector(loc)).length
    ob = bpy.data.objects.new('Cam', cd)
    ob.location = loc
    d = Vector(target) - Vector(loc)
    ob.rotation_euler = d.to_track_quat('-Z', 'Y').to_euler()
    sc.collection.objects.link(ob)
    sc.camera = ob
    return ob


def uv_to_board(u, v_img):
    """UV (sol üst orijin) -> levha x,y (m)."""
    return (u - 0.5) * BW, (0.5 - v_img) * BH


def lonlat_uv(lon, lat):
    return (lon + 11.0) / 57.0, (62.0 - lat) / 29.0


class Height:
    def __init__(self, hm):
        self.hm = hm
        self.h, self.w = hm.shape

    def at(self, x, y):
        px = int(min(max((x / BW + 0.5) * (self.w - 1), 0), self.w - 1))
        py = int(min(max((0.5 - y / BH) * (self.h - 1), 0), self.h - 1))
        v = float(self.hm[py, px])
        return ((v - 8192) / (65535 - 8192) * MAXH_CM if v >= 8192 else (v - 8192) / 8192.0 * 20.0) * U


def instance(sc, src, name, loc, rot_z=0.0, scale=1.0, mats=None):
    ob = bpy.data.objects.new(name, src.data)
    ob.location = loc
    ob.rotation_euler = (0, 0, rot_z)
    ob.scale = (scale, scale, scale)
    sc.collection.objects.link(ob)
    if mats:
        for i, m in enumerate(mats):
            if m is not None:
                ob.material_slots[i].link = 'OBJECT'
                ob.material_slots[i].material = m
    return ob


def srgb_to_lin(c):
    c = np.asarray(c, float) / 255.0
    return tuple(np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4))


NATION_RGB = dict(FRA=(112, 148, 190), GBR=(214, 140, 150), RUS=(118, 154, 104), BEL=(226, 204, 96), GER=(122, 126, 124),
                  AUH=(214, 176, 78), OTT=(172, 146, 98), SER=(168, 84, 96))


def build_render_world(which):
    """Ortak: masa + levha (düz/yer değiştirilmiş) + malzemeler. Dönüş: sc, objs, Height"""
    hm = np.array(Image.open(os.path.join(RAW, 'heightmap.png'))).astype(np.uint16)
    sc = reset_scene()
    M = mats_basic()
    prev = bpy.data.images.load(os.path.join(RAW, 'preview_political.png'))
    prev.colorspace_settings.name = 'sRGB'
    board_mat = mat('BoardMat', None, 0.85, 0.0, tex=prev)
    board_mat.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = 0.8
    ob, _ = build_map_board(M, hm)
    ob.data.materials[0] = board_mat
    table = build_war_table(M)
    table.data.materials[0] = wood_mat('TableWood', (0.22, 0.12, 0.06), (0.40, 0.24, 0.12), 0.45, 0.8)
    table.data.materials[1] = wood_mat('FrameWood', (0.14, 0.07, 0.035), (0.30, 0.16, 0.08), 0.4, 1.2)
    return sc, M, Height(hm)


def render(sc, name):
    os.makedirs(IMG, exist_ok=True)
    path = os.path.join(IMG, 'render_%s.png' % name)
    sc.render.filepath = path
    t = time.time()
    bpy.ops.render.render(write_still=True)
    dt = time.time() - t
    log('render_%s.png: %.0f s' % (name, dt))
    return dt


def make_props_for_render(M):
    counter = build_army_counter(M)
    fort = build_fort_marker(M)
    trench = build_trench_strip(M)
    rail = build_rail_strip(M)
    pin = build_command_pin(M)
    for o in (counter, fort, trench, rail, pin):
        o.hide_render = True
        o.location = (0, 0, -500)
    # render için daha güzel malzemeler
    counter.data.materials[0] = wood_mat('CWood', (0.45, 0.28, 0.13), (0.62, 0.40, 0.20), 0.45, 4.0)
    fort.data.materials[0] = mat('FStone', (0.68, 0.64, 0.56), 0.75)
    fort.data.materials[1] = mat('FRoof', (0.60, 0.14, 0.10), 0.6)
    return counter, fort, trench, rail, pin


def flag_mat(code):
    c = NATION_RGB[code]
    return mat('Flag_' + code, srgb_to_lin(c), 0.75)


def place_front_strips(sc, trench, hobj, fronts, box, scale=2.0, step=1.0, levels=(4, 5), germ_dir=None):
    """Cephe çizgisi boyunca SM_TrenchStrip örnekleri. germ_dir: dişli (+Y) kenarın bakacağı yön (düşman tarafı)."""
    n = 0
    for fr in fronts:
        if fr['trench'] not in levels:
            continue
        pts = np.array([uv_to_board(u, v) for u, v in fr['points']])
        cx, cy = pts[len(pts) // 2]
        if not (box[0] <= cx <= box[2] and box[1] <= cy <= box[3]):
            continue
        # 0.5 m aralıkla yeniden örnekle + hafif yumuşatma
        c0 = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(pts, axis=0).T))])
        if c0[-1] < 0.8:
            continue
        tt = np.arange(0, c0[-1], 0.5)
        pts = np.stack([np.interp(tt, c0, pts[:, 0]), np.interp(tt, c0, pts[:, 1])], 1)
        k = 4
        sm = pts.copy()
        for i in range(len(pts)):
            sm[i] = pts[max(0, i - k):i + k + 1].mean(0)
        seg = np.hypot(*np.diff(sm, axis=0).T)
        cum = np.concatenate([[0], np.cumsum(seg)])
        L = cum[-1]
        cnt = max(1, int(round(L / (step * scale))))
        for kk in range(cnt):
            t = (kk + 0.5) * L / cnt
            i = int(min(np.searchsorted(cum, t, side='right') - 1, len(seg) - 1))
            f = (t - cum[i]) / max(seg[i], 1e-9)
            pos = sm[i] + (sm[i + 1] - sm[i]) * f
            j0, j1 = max(0, i - 5), min(len(sm) - 1, i + 6)
            d = sm[j1] - sm[j0]
            ang = math.atan2(d[1], d[0])
            if germ_dir is not None:
                left = Vector((-math.sin(ang), math.cos(ang), 0))
                if left.dot(germ_dir) < 0:
                    ang += math.pi
            z = hobj.at(pos[0], pos[1])
            instance(sc, trench, 'trench', (pos[0], pos[1], z + 0.01), ang, scale)
            n += 1
    return n


def render_a():
    sc, M, hobj = build_render_world('a')
    counter, fort, trench, rail, pin = make_props_for_render(M)
    armies = json.load(open(os.path.join(RAW, 'armies.json'), encoding='utf-8'))
    provs = {}
    import csv
    for r in csv.DictReader(open(os.path.join(RAW, 'provinces.csv'), encoding='utf-8')):
        provs[int(r['Id'])] = r
    S = 5.5
    picks = ['Fransız 5. Ordu', 'Fransız 2. Ordu', 'Alman 6. Ordu', 'Alman 5. Ordu', 'Britanya Seferi Kuvvetleri', 'Rus 2. Ordu', 'Alman 8. Ordu',
             'Avusturya 1. Ordu', 'Rus 3. Ordu', 'Sırp 1. Ordu', 'Osmanlı 3. Ordu', 'Rus Kafkas Ordusu']
    for a in armies:
        if a['name'] in picks:
            p = provs[a['province']]
            x, y = uv_to_board(float(p['CentroidU']), float(p['CentroidV']))
            z = hobj.at(x, y)
            ang = math.radians(20 if a['nation'] in ('FRA', 'GBR', 'BEL', 'RUS', 'SER') else 200)
            ob = instance(sc, counter, a['name'], (x, y, z), ang, S, mats=[None, flag_mat(a['nation'])])
    for r in provs.values():
        if r['Fort'] == 'True' and r['Name'] in ('Verdun', 'Przemyśl', 'Königsberg', 'Erzurum', 'Edirne'):
            x, y = uv_to_board(float(r['CentroidU']), float(r['CentroidV']))
            instance(sc, fort, 'fort_' + r['Name'], (x, y, hobj.at(x, y)), 0, S)
    # cephe şeritleri (abartılı ölçek)
    fronts = json.load(open(os.path.join(RAW, 'fronts.json')))
    n = place_front_strips(sc, trench, hobj, fronts, (-1e9, -1e9, 1e9, 1e9), scale=4.0, step=1.0, levels=(1, 2, 4, 5))
    log('şerit: %d' % n)
    set_world(sc, (0.74, 0.80, 0.86), (0.2, 0.18, 0.16), 1.0)
    sun(sc, (math.radians(52), math.radians(8), math.radians(-32)), 2.4, 0.03)
    area_light(sc, (0, -300, 500), (0, 0, 0), 300, 4.0e5, (1, 0.97, 0.92))
    # zemin
    bpy.ops.mesh.primitive_plane_add(size=6000, location=(0, 0, -129.2))
    fl = bpy.context.active_object
    fl.data.materials.append(mat('Floor', (0.10, 0.09, 0.085), 0.9))
    camera(sc, (0, -392, 262), (0, -8, 0), lens=34, fstop=None)
    set_render(sc, 1600, 900, 48)
    return render(sc, 'masa_genel')


def render_b():
    sc, M, hobj = build_render_world('b')
    counter, fort, trench, rail, pin = make_props_for_render(M)
    fronts = json.load(open(os.path.join(RAW, 'fronts.json')))
    # Flandre (2.9, 50.9) - Verdun (5.4, 49.2)
    f0 = uv_to_board(*lonlat_uv(2.9, 50.9))
    f1 = uv_to_board(*lonlat_uv(5.4, 49.2))
    mid = ((f0[0] + f1[0]) / 2, (f0[1] + f1[1]) / 2)
    _d = Vector((f1[0] - f0[0], f1[1] - f0[1], 0)).normalized()
    nrm0 = Vector((-_d.y, _d.x, 0))
    if nrm0.dot(Vector((-1, -1, 0))) < 0:
        nrm0 = -nrm0
    n = place_front_strips(sc, trench, hobj, fronts, (mid[0] - 40, mid[1] - 40, mid[0] + 40, mid[1] + 40), scale=2.6, step=1.0, levels=(4, 5), germ_dir=-nrm0)
    log('şerit: %d' % n)
    rails = json.load(open(os.path.join(RAW, 'rails.json'), encoding='utf-8'))
    nr = 0
    for r in rails:
        if r['name'] not in ('Paris-Verdun-Metz', 'Paris-Lille', 'Paris-Nancy'):
            continue
        poly = np.array([uv_to_board(u, v) for u, v in r['points']])
        seg = np.hypot(*np.diff(poly, axis=0).T)
        cum = np.concatenate([[0], np.cumsum(seg)])
        t = 0.0
        sc_r = 3.0
        while t < cum[-1] - 1e-6:
            i = min(np.searchsorted(cum, t, side='right') - 1, len(seg) - 1)
            f = (t - cum[i]) / max(seg[i], 1e-9)
            pos = poly[i] + (poly[i + 1] - poly[i]) * f
            if abs(pos[0] - mid[0]) < 48 and abs(pos[1] - mid[1]) < 48:
                ang = math.atan2(poly[i + 1][1] - poly[i][1], poly[i + 1][0] - poly[i][0])
                instance(sc, rail, 'rail', (pos[0], pos[1], hobj.at(pos[0], pos[1]) + 0.01), ang, sc_r)
                nr += 1
            t += 1.0 * sc_r
    log('ray: %d' % nr)
    dirv = Vector((f1[0] - f0[0], f1[1] - f0[1], 0)).normalized()
    nrm = Vector((-dirv.y, dirv.x, 0))
    if nrm.dot(Vector((-1, -1, 0))) < 0:
        nrm = -nrm  # Fransız tarafı (güneybatı)
    # ordu blokları: cephe hattının iki yanında, düşmana dönük
    for k, (t, side, code) in enumerate(((-0.30, 1, 'FRA'), (0.05, 1, 'GBR'), (0.38, 1, 'FRA'), (-0.18, -1, 'GER'), (0.2, -1, 'GER'), (0.45, -1, 'GER'))):
        base = Vector((mid[0], mid[1], 0)) + dirv * (t * 62) + nrm * (side * 8.0)
        face = -nrm * side
        ang = math.atan2(face.y, face.x) + (0.12 if k % 2 else -0.1)
        instance(sc, counter, 'army%d' % k, (base.x, base.y, hobj.at(base.x, base.y)), ang, 0.9, mats=[None, flag_mat(code)])
    import csv
    provs = {r['Name']: r for r in csv.DictReader(open(os.path.join(RAW, 'provinces.csv'), encoding='utf-8'))}
    vp = provs['Verdun']
    x, y = uv_to_board(float(vp['CentroidU']), float(vp['CentroidV']))
    instance(sc, fort, 'fort', (x - 4, y - 5, hobj.at(x, y)), 0, 1.1)
    set_world(sc, (0.72, 0.78, 0.84), (0.22, 0.2, 0.18), 1.0)
    sun(sc, (math.radians(58), math.radians(0), math.radians(-60)), 2.6, 0.03)
    target = Vector((mid[0], mid[1], 0.4)) + dirv * 2
    cam_loc = target + nrm * 30 + dirv * -10 + Vector((0, 0, 13))
    camera(sc, cam_loc, target, lens=32, fstop=4.0, focus=(target - cam_loc).length * 1.02)
    set_render(sc, 1600, 900, 56)
    return render(sc, 'bati_cephesi')


def render_c():
    sc = reset_scene()
    M = mats_basic()
    counter, fort, trench, rail, pin = make_props_for_render(M)
    for o in (counter, fort, trench, rail, pin):
        o.hide_render = False
    counter.data.materials[1] = mat('FlagC', srgb_to_lin(NATION_RGB['FRA']), 0.7)
    desk = bpy.data.objects.new('desk', bpy.data.meshes.new('desk'))
    bm = bmesh.new()
    add_box(bm, (6000, 3600, 120), (0, 0, -60), bevel=20, seg=2, mi=0)
    bm.to_mesh(desk.data)
    bm.free()
    desk.data.materials.append(wood_mat('DeskWood', (0.34, 0.20, 0.10), (0.5, 0.31, 0.16), 0.5, 0.5))
    sc.collection.objects.link(desk)
    counter.location = (-5.0, 0.4, 0)
    counter.rotation_euler = (0, 0, math.radians(-18))
    counter2 = instance(sc, counter, 'c2', (-2.3, 4.0, 0), math.radians(12), 1.0, mats=[None, mat('FlagG', srgb_to_lin(NATION_RGB['GER']), 0.7)])
    counter3 = instance(sc, counter, 'c3', (-2.0, -3.4, 0), math.radians(5), 1.0, mats=[None, mat('FlagR', srgb_to_lin(NATION_RGB['RUS']), 0.7)])
    fort.location = (4.4, -0.6, 0)
    pin.location = (1.0, 0.2, 0)
    pin.rotation_euler = (0, 0, 0.3)
    for k in range(3):
        instance(sc, trench, 't%d' % k, (-7.5 + k * 2.5, -7.8, 0), 0, 2.5)
        instance(sc, rail, 'r%d' % k, (1.0 + k * 2.5, -7.8, 0), 0, 2.5)
    for o in (counter, fort, pin):
        o.hide_render = False
    set_world(sc, (0.80, 0.84, 0.88), (0.35, 0.32, 0.28), 1.0)
    sun(sc, (math.radians(50), math.radians(10), math.radians(-38)), 2.0, 0.05)
    area_light(sc, (6, -12, 12), (0, 0, 1), 10, 500, (1.0, 0.95, 0.88))
    camera(sc, (-3.0, -31.0, 15.0), (0.0, -0.4, 1.5), lens=50, fstop=5.6, focus=34.5)
    set_render(sc, 1600, 900, 64)
    return render(sc, 'urunler')


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if '--render-only' not in sys.argv:
        build_and_export()
    if '--fbx-only' in sys.argv:
        return
    which = args or ['a', 'b', 'c']
    times = {}
    if 'a' in which:
        times['a'] = render_a()
    if 'b' in which:
        times['b'] = render_b()
    if 'c' in which:
        times['c'] = render_c()
    log('render süreleri: %s' % times)


if __name__ == '__main__':
    main()
