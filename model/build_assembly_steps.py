# Step-by-step assembly illustration for lamp V3. Reuses assembly geometry and
# the CPU renderer from build_lamp_v3.py; run from the repository root:
#   python model/build_assembly_steps.py
import pathlib, importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

spec = importlib.util.spec_from_file_location('lamp', pathlib.Path(__file__).with_name('build_lamp_v3.py'))
lamp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lamp)

ALL = dict((n, (t, c)) for n, t, c in lamp.parts + lamp.refs)
CTX = '#a8b0aa'  # grey for already-installed context parts

def pick(names, offsets=None, ctx=(), colors=None):
    items = []
    for n in ctx:
        t, c = ALL[n]
        items.append((n, t.copy(), CTX))
    for n in names:
        t, c = ALL[n]
        t = t.copy()
        if offsets and n in offsets:
            t.apply_translation(offsets[n])
        items.append((n, t, (colors or {}).get(n, c)))
    return items

probes = dict(lamp.wire_probes)
def wires(*names):
    return [(n, lamp.mesh(probes[n]), '#e07020') for n in names]

W, H = 640, 520
PANELS = [
    dict(title='1  打印与试配验证',
         lines=['先打 16 / 17 / 18 试片：验证方管孔与滑轨间隙',
                '再打 11–15 支架试装设备；09 / 10 待摄像头到货确认',
                'PETG / ASA，0.2 mm 层高，5–6 道外壁，承力处局部实心'],
         items=pick(['16_tube_fit_coupon', '17_slide_fit_coupon', '18_slide_male_fit_coupon']),
         view=dict(az=-60, el=25, center=(0, 32, 8), scale=5.5)),
    dict(title='2  金属骨架与预穿线',
         lines=['20×20×1.5 钢方管焊成倒 L，验焊、去毛刺、清焊瘤',
                '先穿线后组装（橙色为线束通道示意）',
                '立管插入底架插座：M4×50 ×2（Z=28 / 62，配防压套）'],
         items=pick(['01_hidden_chassis', 'steel_spine', 'steel_arm'])
               + wires('base_entry', 'column_cable', 'arm_cable'),
         view=dict(az=-80, el=12, center=(0, 40, 280), scale=0.9)),
    dict(title='3  底座装配',
         lines=['M5×35 ×4 固定两块钢配重（底面头部凹位）',
                '放入 Mac mini：托点承托，底面中央保持开放',
                '罩上 02 外罩：底面 M3×16 ×4 + M3 热熔嵌件'],
         items=pick(['ballast_-110', 'ballast_110', 'Mac_mini_envelope',
                     '02_rounded_mac_shell'],
                    offsets={'02_rounded_mac_shell': (0, 0, 55)},
                    ctx=('01_hidden_chassis', 'steel_spine'),
                    colors={'Mac_mini_envelope': '#7d94a8'}),
         view=dict(az=-60, el=25, center=(0, 0, 75), scale=1.9)),
    dict(title='4  灯柱与灯臂套壳',
         lines=['03 / 04 / 05 / 06 / 07 依次套上金属管，穿 M4 螺栓',
                '11 连接座一并安装：低圆头 M4×65 ×2（Z=278 / 292）',
                '共 8 处穿管孔位，均配防压套，规格见紧固件表'],
         items=pick(['03_column_lower_240', '04_column_upper_220',
                     '05_arm_rear_156', '06_arm_front_165', '07_corner_cover',
                     '11_column_slide_dock'],
                    ctx=('01_hidden_chassis', 'steel_spine', 'steel_arm')),
         view=dict(az=-75, el=15, center=(0, -10, 310), scale=1.08)),
    dict(title='5  灯头与摄像头',
         lines=['08 灯头：M4×60 ×2（Y=-245 / -225，沿 Z）',
                'LED 铝槽 M3 ×2，长度按实物确认；灯条先穿线',
                '09 承座 M3×16 ×2 → 装摄像头 → 10 压盖 M3×40 ×2，加软垫'],
         items=pick(['08_rounded_LED_head', 'LED_aluminum_envelope',
                     '09_UGREEN_59x35x23_cradle', 'UGREEN_case_envelope',
                     'lens_illustrative', '10_camera_rear_keeper'],
                    offsets={'LED_aluminum_envelope': (0, 0, -20),
                             '09_UGREEN_59x35x23_cradle': (0, 0, -22),
                             'UGREEN_case_envelope': (0, 0, -22),
                             'lens_illustrative': (0, 0, -22),
                             '10_camera_rear_keeper': (0, -18, -44)},
                    ctx=('06_arm_front_165',)),
         view=dict(az=-50, el=18, center=(0, -262, 495), scale=2.8)),
    dict(title='6  屏幕模块',
         lines=['托脚 / 夹爪调松 → 垫软垫 → 装设备 → 轻压锁紧（M4×25 ×4）',
                '整组滑入 11 母座到底，装横向锁紧螺栓：M4×70 手拧 + 蝶形螺母',
                '拆卸反向：先卸锁紧螺栓，托住设备，上提约 66 mm 取出'],
         items=pick(['12_open_screen_carrier', '13_screen_lower_foot_left',
                     '14_screen_lower_foot_right', '15_screen_sliding_upper_jaw',
                     'iPad_Pro_11_envelope'],
                    ctx=('03_column_lower_240', '11_column_slide_dock')),
         view=dict(az=125, el=15, center=(0, 35, 270), scale=2.2)),
]

fig = plt.figure(figsize=(19, 12), facecolor='#f6f7f5')
for i, p in enumerate(PANELS):
    col, row = i % 3, i // 3
    x = 0.015 + col * 0.333
    y = 0.60 - row * 0.455
    ax = fig.add_axes([x, y, 0.315, 0.28])
    v = p['view']
    ax.imshow(lamp.render(p['items'], az=v['az'], el=v['el'], center=v['center'],
                          scale=v['scale'], W=W, H=H))
    ax.axis('off')
    tx = x + 0.005
    fig.text(tx, y - 0.012, p['title'], fontsize=16, color='#273d37',
             fontweight='bold', va='top')
    fig.text(tx, y - 0.052, '\n'.join(p['lines']), fontsize=11, color='#4a5a52',
             va='top', linespacing=1.55)

fig.text(0.03, 0.975, '学习台灯 V3 · 分步装配示意', fontsize=26, color='#273d37')
fig.text(0.03, 0.945, '灰色为已装就位的上下文零件；示意为装配顺序，紧固件、软垫、线缆未全部按比例显示，完整规格见《设计与打印说明》',
         fontsize=12, color='#64706a')
out = pathlib.Path('renders/台灯V3_分步装配.png')
fig.savefig(out, dpi=100)
print('saved', out)
