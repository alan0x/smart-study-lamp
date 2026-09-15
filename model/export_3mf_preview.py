# Convert assembly_view_only.glb to a 3MF preview that keeps per-part names and
# colors (trimesh's own 3MF exporter drops them). Run from the repository root:
#   python model/export_3mf_preview.py
import zipfile
import trimesh
from xml.sax.saxutils import escape

scene = trimesh.load('assembly_view_only.glb')
items = []
for node in scene.graph.nodes_geometry:
    T, geom_name = scene.graph[node]
    g = scene.geometry[geom_name].copy()
    g.apply_transform(T)
    items.append((node, g))

def fmt(v):
    return ('%.4f' % v).rstrip('0').rstrip('.')

colors, objects, build = [], [], []
for i, (name, g) in enumerate(items, start=1):
    try:
        rgba = g.visual.face_colors[0]
    except Exception:
        rgba = (200, 200, 200, 255)
    colors.append('<base name="%s" displaycolor="#%02X%02X%02X%02X"/>' % (escape(name), *tuple(int(c) for c in rgba)))
    verts = ''.join('<vertex x="%s" y="%s" z="%s"/>' % (fmt(x), fmt(y), fmt(z)) for x, y, z in g.vertices)
    tris = ''.join('<triangle v1="%d" v2="%d" v3="%d"/>' % tuple(t) for t in g.faces)
    objects.append('<object id="%d" name="%s" type="model" pid="1" pindex="%d">'
                   '<mesh><vertices>%s</vertices><triangles>%s</triangles></mesh></object>'
                   % (i, escape(name), i - 1, verts, tris))
    build.append('<item objectid="%d"/>' % i)

model = ('<?xml version="1.0" encoding="UTF-8"?>'
 '<model unit="millimeter" xml:lang="en-US" '
 'xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
 'xmlns:m="http://schemas.microsoft.com/3dmanufacturing/material/2015/02">'
 '<metadata name="Application">smart-study-lamp</metadata>'
 '<metadata name="Title">Smart Study Lamp V3 - assembly preview (do not print)</metadata>'
 '<resources><basematerials id="1">%s</basematerials>%s</resources><build>%s</build></model>'
 % (''.join(colors), ''.join(objects), ''.join(build)))
content_types = ('<?xml version="1.0" encoding="UTF-8"?>'
 '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
 '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
 '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/></Types>')
rels = ('<?xml version="1.0" encoding="UTF-8"?>'
 '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
 '<Relationship Target="/3D/3dmodel.model" Id="rel0" '
 'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')

with zipfile.ZipFile('assembly_view_only.3mf', 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', content_types)
    z.writestr('_rels/.rels', rels)
    z.writestr('3D/3dmodel.model', model)

back = trimesh.load('assembly_view_only.3mf')
print('parts:', len(back.geometry), '| iPad present:', any('iPad' in n for n in back.geometry))
