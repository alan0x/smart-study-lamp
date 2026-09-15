import sys, pathlib, json, math, zipfile
sys.path.insert(0,str(pathlib.Path('work/pythonlibs').resolve()))
import numpy as np
import manifold3d as m
import trimesh
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager
font=pathlib.Path('C:/Windows/Fonts/msyh.ttc')
if font.exists():
    font_manager.fontManager.addfont(str(font));plt.rcParams['font.family']=font_manager.FontProperties(fname=str(font)).get_name()
plt.rcParams['axes.unicode_minus']=False
OUT=pathlib.Path('outputs/V3'); ST=OUT/'STL'; ST.mkdir(parents=True,exist_ok=True)
parts=[]; report=[]; solids={}; refs=[]
def box(size,at=(0,0,0)):return m.Manifold.cube(size,True).translate(at)
def cyl(r,h,at,axis='z'):
    s=m.Manifold.cylinder(h,r,r,40,True)
    if axis=='y':s=s.rotate((90,0,0))
    if axis=='x':s=s.rotate((0,90,0))
    return s.translate(at)
def rb(size,r,at=(0,0,0)):
    w,d,h=size
    s=box((w-2*r,d,h))+box((w,d-2*r,h))
    for x in [-w/2+r,w/2-r]:
        for y in [-d/2+r,d/2-r]:s+=cyl(r,h,(x,y,0))
    return s.translate(at)
def prism(poly,z,h):return m.CrossSection([poly]).extrude(h).translate((0,0,z))
def mesh(s):
    q=s.to_mesh();return trimesh.Trimesh(np.array(q.vert_properties)[:,:3],np.array(q.tri_verts),process=True)
def save(name,s,c='#d4dcd7',print_rotate=None):
    t=mesh(s);assert t.is_watertight and t.is_winding_consistent and t.volume>0,name
    assert len(t.split())==1,(name,'disconnected')
    p=mesh(s.rotate(print_rotate)) if print_rotate else t.copy()
    p.apply_translation(-p.bounds[0]);p.export(ST/(name+'.stl'))
    parts.append((name,t,c));solids[name]=s
    report.append(dict(part=name,print_bounds_mm=np.round(p.extents,2).tolist(),volume_cm3=round(t.volume/1000,2),watertight=True,connected_solids=1,triangles=len(t.faces)))
    return s
def ref(name,s,c):refs.append((name,mesh(s),c))

# Rearward +Y; table top Z=0. Bottom chassis is inset under a rounded removable shell.
base=rb((252,232,8),20,(0,0,4))-rb((108,108,12),12,(0,-20,4))
for x in [-60,60]:
    for y in [-74,34]:
        base+=box((10,14,22),(x,y,19))
        base+=box((3,14,26),(x+(6 if x>0 else -6),y,21))
# Spine socket is unchanged in position, with open cable space in front.
base+=rb((42,40,72),4,(0,96,44));base-=box((20.6,20.6,76),(0,99,48))
for z in [28,62]:base-=cyl(2.2,60,(0,96,z),'y')
for x in [-110,110]:
    for y in [-70,70]:
        base-=cyl(2.7,12,(x,y,4));base-=cyl(4.5,4,(x,y,2))
for x in [-118,118]:
    for y in [-100,100]:
        base+=box((12,12,6),(x,y,11));base-=cyl(1.7,20,(x,y,8));base-=cyl(3.2,3,(x,y,1.5))
base-=box((26,18,76),(0,77,46))
save('01_hidden_chassis',base,'#344945')

# Top and four sides envelop computer/ballast; 6 mm continuous shadow ventilation gap.
shell=rb((260,240,84),24,(0,0,56))-rb((252,232,90),20,(0,0,49))
# This inner cavity terminates at Z94: the continuous top skin is 4 mm thick.
# Open rear notch permits lifting shell without disassembling the lamp column.
shell-=box((46,70,100),(0,99,60))
# Generous front port recess and split rear cable windows avoid exact unsupported port geometry.
shell-=rb((120,22,50),7).rotate((90,0,0)).translate((0,-104,58))
for x in [-50,50]:shell-=rb((48,44,46),6).rotate((90,0,0)).translate((x,110,58))
# Underside accessible heat-set inserts; no fasteners on the top surface.
for x in [-118,118]:
    for y in [-100,100]:
        shell+=box((20,16,14),(x,y,21))
        shell-=cyl(2.6,6,(x,y,17));shell-=cyl(1.7,14,(x,y,21))
save('02_rounded_mac_shell',shell,print_rotate=(180,0,0))

def vertical(z0,z1,holes):
    s=rb((42,48,z1-z0),5,(0,90,(z0+z1)/2))-rb((34,40,z1-z0+2),2,(0,90,(z0+z1)/2))
    for z in holes:s-=cyl(2.2,60,(0,90,z),'y')
    return s
save('03_column_lower_240',vertical(80,320,[110,278,292])-box((16,12,12),(0,68,240)))
save('04_column_upper_220',vertical(320,540,[345,510])-box((26,14,12),(0,68,532)))
def arm(y0,y1,holes):
    # Rounded X/Z section, extrusion along Y.
    s=(rb((42,44,y1-y0),5)-rb((34,36,y1-y0+2),2)).rotate((90,0,0)).translate((0,(y0+y1)/2,545))
    for y in holes:s-=cyl(2.2,55,(0,y,545))
    return s
save('05_arm_rear_156',arm(-90,66,[45]),print_rotate=(90,0,0))
save('06_arm_front_165',arm(-255,-90,[-145,-245,-225])-box((14,12,14),(0,-210,525)),print_rotate=(90,0,0))
elbow=rb((48,54,44),6,(0,97,562))-rb((40,46,48),3,(0,97,562))
elbow-=box((44,24,44),(0,70,545))
for x in [-24,24]:elbow-=cyl(2.2,10,(x,99,550),'x')
save('07_corner_cover',elbow)

head=rb((320,68,22),10,(0,-235,512))-rb((312,60,24),6,(0,-235,507))
head+=box((36,44,6),(0,-235,520))
for y in [-245,-225]:head-=cyl(2.2,32,(0,y,518))
head-=box((14,12,30),(0,-210,518))
for x in [-130,130]:head-=cyl(1.7,12,(x,-235,520))
for x in [-30,30]:
    head+=box((12,16,5),(x,-274,519.5));head-=cyl(1.7,12,(x,-276,519.5))
save('08_rounded_LED_head',head,'#344945',print_rotate=(180,0,0))

# UGREEN body 59 wide x 35 face-height x 23 optical depth; lens points down.
camera=rb((74,50,29),5,(0,-308,502.5))-box((62,38,33),(0,-308,502.5))
# Short retaining lips touch only the outer face edge; pad before installation.
for x in [-29.5,29.5]:
    for y in [-319,-297]:camera+=box((5,6,3),(x,y,489.5))
for x in [-30,30]:
    camera+=box((12,18,5),(x,-279,514.5));camera-=cyl(1.7,12,(x,-276,514.5))
# Open top-control access on both face-height edges.
for y in [-331,-285]:camera-=box((24,12,19),(0,y,510.5))
for x in [-34,34]:camera-=cyl(1.7,36,(x,-313,504))
save('09_UGREEN_59x35x23_cradle',camera,'#344945')
cap=rb((74,50,4),5,(0,-308,519))-box((54,30,8),(0,-308,519))
for x in [-30,30]:cap-=box((14,18,8),(x,-276,519))
for x in [-34,34]:cap-=cyl(1.7,10,(x,-313,519))
save('10_camera_rear_keeper',cap,'#344945')

# Detachable vertical dovetail dock, hard bottom stop and removable transverse locking bolt.
female=box((54,20,70),(0,56,285))-prism([(-14,45),(14,45),(21,61),(-21,61)],256,66)
for z in [278,292]:
    female-=cyl(2.2,30,(0,56,z),'y')
    female-=cyl(4.1,4,(0,63,z),'y')
female-=cyl(2.2,70,(0,55,285),'x')
save('11_column_slide_dock',female,'#344945',print_rotate=(90,0,0))

def tilt(s):return s.rotate((-12,0,0)).translate((0,-8,195))
# Open T-frame: rear center spine + bottom crossbeam. All sides remain open.
frame=box((34,8,128),(0,4,64))+box((180,8,28),(0,4,14))
# Slots allow both lower feet to shift sideways.
for sign in [-1,1]:
    frame-=box((48,14,4.4),(sign*59,4,14))
    frame-=box((48,3,8.2),(sign*59,1.5,14))
    for x in [sign*35,sign*83]:
        frame-=cyl(2.2,14,(x,4,14),'y');frame-=cyl(4.1,3,(x,1.5,14),'y')
for z in [115,125]:
    frame-=cyl(2.2,14,(0,4,z),'y');frame-=cyl(4.1,3,(0,1.5,z),'y')
for x in [-20,20]:frame+=box((8,30,34),(x,19,85))
frame+=box((48,19,34),(0,24.5,85))
frame=tilt(frame)-box((100,50,200),(0,70.4,285))
frame+=box((24,14,26),(0,39,282))
male=prism([(-13,45.5),(13,45.5),(20.2,60.5),(-20.2,60.5)],256,54)
frame+=male;frame-=cyl(2.2,65,(0,55,285),'x')
save('12_open_screen_carrier',frame,print_rotate=(12,0,0))

def foot(x):
    s=box((36,6,28),(x,11.4,14))+box((36,33.4,5),(x,-2.3,-2.5))
    s+=box((36,3,10),(x,-17.5,5))
    s-=cyl(2.2,14,(x,11.4,14),'y')
    return tilt(s)
save('13_screen_lower_foot_left',foot(-55),print_rotate=(12,0,0))
save('14_screen_lower_foot_right',foot(55),print_rotate=(12,0,0))

JAW_H=134.8
jaw=box((30,6,130),(0,11.4,JAW_H-65))
jaw+=box((36,33.4,6),(0,-2.3,JAW_H+3))
jaw+=box((36,3,11),(0,-17.5,JAW_H+.5))
# One long slot accepts two separate M4 locks, preventing upper jaw rotation.
jaw-=box((4.4,12,110),(0,11.4,JAW_H-60))
for z in [JAW_H-115,JAW_H-5]:jaw-=cyl(2.2,12,(0,11.4,z),'y')
save('15_screen_sliding_upper_jaw',tilt(jaw),print_rotate=(12,0,0))

# One small fit coupon combines tube and slide interface tests, kept outside assembly.
coupon=rb((36,36,12),3)-box((20.6,20.6,16))
save('16_tube_fit_coupon',coupon,'#a78c66')
coupon2=box((54,20,14),(0,56,7))-prism([(-14,45),(14,45),(21,61),(-21,61)],-1,16)
save('17_slide_fit_coupon',coupon2,'#a78c66')
save('18_slide_male_fit_coupon',prism([(-13,45.5),(13,45.5),(20.2,60.5),(-20.2,60.5)],0,14),'#a78c66')

# References are NOT printable deliverables, but checked for mechanical interference.
ref('Mac_mini_envelope',rb((127,127,50),12,(0,-20,55)),'#909ca0')
ref('iPad_mini_envelope',tilt(box((195.4,6.3,134.8),(0,-5.15,67.4))),'#263d45')
ref('steel_spine',box((20,20,532),(0,99,274)),'#86999c')
ref('steel_arm',box((20,384,20),(0,-83,550)),'#86999c')
for x in [-110,110]:ref('ballast_'+str(x),box((30,180,20),(x,0,18)),'#737f7a')
ref('LED_aluminum_envelope',box((296,18,8),(0,-235,514)),'#fff0b0')
ref('UGREEN_case_envelope',box((59,35,23),(0,-308,502.5)),'#1d292b')
ref('lens_illustrative',cyl(8,3,(0,-308,489.5)),'#3e6970')

# Conservative cable/plug envelopes, used for interference checks below.
wire_probes=[
 ('base_entry',box((6,8,66),(-9,78,47))),
 ('column_cable',box((6,8,446),(-9,78,307))),
 ('arm_cable',box((6,328,8),(-9,-86,532))),
 ('LED_feed',box((8,6,20),(0,-210,526))),
 ('screen_exit',box((10,16,6),(0,66,240))),
 ('camera_USB_plug_allowance',box((14,12,28),(0,-308,530)))
]

# Accurate CPU depth rendering of actual triangle mesh, no generated mock-up imagery.
def render(items,az=-65,el=20,center=(0,-105,290),scale=1.3,W=850,H=1000):
    pix=np.full((H,W,3),[246,247,245],dtype=np.uint8);depth=np.full((H,W),-np.inf)
    az,el=np.radians([az,el]);d=np.array([np.cos(el)*np.cos(az),np.cos(el)*np.sin(az),np.sin(el)])
    right=np.array([-np.sin(az),np.cos(az),0]);up=np.cross(d,right)
    light=np.array([-.3,-.5,.8]);light/=np.linalg.norm(light)
    for name,t,col in items:
      for tri in t.triangles:
        v=np.array(tri)-center;p=np.column_stack((v@right*scale+W/2,-v@up*scale+H/2,v@d))
        x0=max(0,int(np.floor(p[:,0].min())));x1=min(W-1,int(np.ceil(p[:,0].max())))
        y0=max(0,int(np.floor(p[:,1].min())));y1=min(H-1,int(np.ceil(p[:,1].max())))
        if x1<x0 or y1<y0:continue
        xx,yy=np.meshgrid(np.arange(x0,x1+1)+.5,np.arange(y0,y1+1)+.5)
        a,b,c=p;den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-8:continue
        u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
        vv=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w=1-u-vv
        z=u*a[2]+vv*b[2]+w*c[2];sub=depth[y0:y1+1,x0:x1+1]
        mask=(u>=-1e-7)&(vv>=-1e-7)&(w>=-1e-7)&(z>sub)
        norm=np.cross(v[1]-v[0],v[2]-v[0]);norm/=max(np.linalg.norm(norm),1e-9)
        color=np.array(matplotlib.colors.to_rgb(col))*255*(.65+.35*max(0,np.dot(norm,light)))
        pix[y0:y1+1,x0:x1+1][mask]=color.astype(np.uint8);sub[mask]=z[mask]
    return pix

assembled=[p for p in parts if not p[0].startswith(('16','17','18'))]
fig=plt.figure(figsize=(16,10),facecolor='#f6f7f5')
ax=fig.add_axes([.02,.12,.46,.78]);ax.imshow(render(assembled+refs));ax.axis('off')
fig.text(.05,.95,'学习台灯  /  V3',fontsize=26,color='#273d37')
fig.text(.05,.905,'圆角包覆底座 · 可拆开放支架 · 一体式 USB 摄像头',fontsize=13,color='#64706a')
ax=fig.add_axes([.52,.49,.44,.35]);
baseitems=[p for p in assembled if p[0].startswith(('01','02'))]+[p for p in refs if 'Mac' in p[0] or 'ballast' in p[0]]
ax.imshow(render(baseitems,az=-60,el=24,center=(0,0,50),scale=1.85,W=850,H=400));ax.axis('off')
fig.text(.54,.845,'01  侧面与顶部包覆，底边留通风阴影缝',fontsize=13,color='#273d37')
screenitems=[p for p in assembled if p[0].startswith(('11','12','13','14','15'))]
ax=fig.add_axes([.52,.13,.44,.34]);ax.imshow(render(screenitems,az=-50,el=20,center=(0,24,267),scale=2.25,W=850,H=430));ax.axis('off')
fig.text(.54,.45,'02  开放托架：下托脚横移，上夹爪伸缩',fontsize=13,color='#273d37')
fig.text(.54,.095,'滑入式接口 + 横向锁紧螺栓，可整组取下',fontsize=12,color='#64706a')
fig.text(.05,.045,'结构样件 / 金属骨架与配重另配 / 摄像头按厂家外形尺寸预适配，尚需实物复核',fontsize=11,color='#64706a')
fig.savefig(OUT/'台灯V3_总览.png',dpi=150);plt.close(fig)

# Exploded mechanical detail, showing concealed ballast and independent detachable screen module.
fig,axs=plt.subplots(1,3,figsize=(18,7),facecolor='#f6f7f5')
expl=[]
for n,t,c in baseitems:
    tt=t.copy()
    if n.startswith('02'):tt.apply_translation((0,0,125))
    expl.append((n,tt,c))
axs[0].imshow(render(expl,az=-55,el=28,center=(0,0,100),scale=1.7,W=650,H=620));axs[0].set_title('底座：上罩可独立拆下',fontsize=15)
expl=[]
for n,t,c in screenitems:
    tt=t.copy()
    if not n.startswith('11'):tt.apply_translation((0,-60,65))
    expl.append((n,tt,c))
axs[1].imshow(render(expl,az=-40,el=18,center=(0,0,300),scale=2.4,W=650,H=620));axs[1].set_title('屏幕：先解锁，上提后取出',fontsize=15)
camitems=[p for p in assembled if p[0].startswith(('09','10'))]+[p for p in refs if 'UGREEN' in p[0] or 'lens' in p[0]]
expl=[]
for n,t,c in camitems:
    tt=t.copy()
    if n.startswith('10'):tt.apply_translation((0,0,23))
    expl.append((n,tt,c))
axs[2].imshow(render(expl,az=-60,el=-25,center=(0,-300,516),scale=5,W=650,H=620));axs[2].set_title('摄像头：保留成品金属外壳',fontsize=15)
for ax in axs:ax.axis('off');ax.set_facecolor('#f6f7f5')
fig.text(.06,.05,'拆装示意；紧固件、软垫、接线未显示。底座外壳保留背面灯柱让位缺口。',fontsize=12,color='#64706a')
fig.savefig(OUT/'台灯V3_拆装细节.png',dpi=150);plt.close(fig)

scene=trimesh.Scene()
for name,t,c in assembled+refs:
    v=t.copy();v.visual.face_colors=trimesh.visual.color.hex_to_rgba(c);scene.add_geometry(v,node_name=name)
scene.export(OUT/'assembly_view_only.glb')

# Pairwise volume intersections, excluding touching surfaces and explicit separate fit coupons.
def intersect(a,b):
    if not np.all(np.minimum(a.bounds[1],b.bounds[1])-np.maximum(a.bounds[0],b.bounds[0])>0.001):return 0
    aa=m.Manifold(m.Mesh(np.array(a.vertices,dtype=np.float32),np.array(a.faces,dtype=np.uint32)))
    bb=m.Manifold(m.Mesh(np.array(b.vertices,dtype=np.float32),np.array(b.faces,dtype=np.uint32)))
    return (aa^bb).volume()
clashes=[]
for i,(n,a,c) in enumerate(assembled):
    for nn,b,cc in assembled[i+1:]:
        vol=intersect(a,b)
        if vol>.1:clashes.append([n,nn,round(vol,3)])
device_clashes=[]
for n,a,c in assembled:
    for nn,b,cc in refs:
        if nn not in ['Mac_mini_envelope','iPad_mini_envelope','UGREEN_case_envelope'] and not nn.startswith('ballast'):continue
        vol=intersect(a,b)
        if vol>.1:device_clashes.append([n,nn,round(vol,3)])
motion_checks=[]
# Endpoints + intermediate jaw positions; verify the slide geometry throughout its travel.
for height in [130,150,175,200,220]:
    jt=mesh(tilt(jaw.translate((0,0,height-JAW_H))))
    v=intersect(jt,mesh(frame))+intersect(jt,mesh(female))
    motion_checks.append(dict(check='upper_jaw_at_'+str(height)+'mm',intersection_mm3=round(v,4)))
    assert v<.1,('jaw travel',height,v)
for dz in [0,10,30,50,66]:
    v=intersect(mesh(frame.translate((0,0,dz))),mesh(female))
    motion_checks.append(dict(check='carrier_lift_'+str(dz)+'mm',intersection_mm3=round(v,4)))
    assert v<.1,('slide lift',dz,v)
(OUT/'mesh_validation.json').write_text(json.dumps(dict(parts=report,printed_part_intersections_mm3=clashes,device_envelope_intersections_mm3=device_clashes,motion_checks=motion_checks),ensure_ascii=False,indent=2),encoding='utf-8')
print('CLASHES:',clashes);print('DEVICE CLASHES:',device_clashes)
assert not clashes,clashes
assert not device_clashes,device_clashes
print('PASS',len(parts),'watertight, single-component STL parts')

wire_checks=[]
for name,probe in wire_probes:
    for nn,s in list(solids.items())[:15]+[(n,None) for n,t,c in refs if n.startswith('steel')]:
        target=mesh(s) if s is not None else next(t for n,t,c in refs if n==nn)
        vol=intersect(mesh(probe),target)
        if vol>.1:wire_checks.append([name,nn,round(vol,3)])
(OUT/'wiring_validation.json').write_text(json.dumps({'probe_sizes_mm':{n:mesh(s).extents.tolist() for n,s in wire_probes},'collisions':wire_checks},indent=2),encoding='utf-8')
print('WIRE CLASHES',wire_checks)
assert not wire_checks,wire_checks


