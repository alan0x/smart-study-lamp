# Exploded-view rendering for lamp V3. Reuses assembly geometry and the CPU
# renderer from build_lamp_v3.py; run from the repository root:
#   python model/build_exploded_view.py
import sys, pathlib, importlib.util
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

spec = importlib.util.spec_from_file_location('lamp', pathlib.Path(__file__).with_name('build_lamp_v3.py'))
lamp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lamp)

# Per-part explode offsets along natural assembly directions (mm).
# The welded steel L-frame (spine + arm) stays put as the backbone.
OFF = {
    '02_rounded_mac_shell': (0, 0, 150),
    '03_column_lower_240': (0, 0, 260),
    '04_column_upper_220': (0, 0, 380),
    '07_corner_cover': (0, 0, 500),
    '05_arm_rear_156': (0, 80, 0),
    '06_arm_front_165': (0, -80, 0),
    '08_rounded_LED_head': (0, 0, -130),
    'LED_aluminum_envelope': (0, 0, -180),
    '09_UGREEN_59x35x23_cradle': (0, 0, -280),
    'UGREEN_case_envelope': (0, 0, -280),
    'lens_illustrative': (0, 0, -280),
    '10_camera_rear_keeper': (0, 0, -340),
    '11_column_slide_dock': (0, -60, 60),
    '12_open_screen_carrier': (0, 0, 200),
    'iPad_mini_envelope': (0, -140, 200),
    '13_screen_lower_foot_left': (-130, -260, 100),
    '14_screen_lower_foot_right': (130, -260, 100),
    '15_screen_sliding_upper_jaw': (0, -420, 0),
}

items = []
for n, t, c in lamp.assembled + lamp.refs:
    tt = t.copy()
    tt.apply_translation(OFF.get(n, (0, 0, 0)))
    items.append((n, tt, c))

AZ, EL = -20, 15
CENTER = (0, -40, 530)
SCALE, W, H = 1.4, 1400, 1900
pix = lamp.render(items, az=AZ, el=EL, center=CENTER, scale=SCALE, W=W, H=H)

# Projection identical to lamp.render, used to anchor badges at part centroids.
az, el = np.radians([AZ, EL])
d = np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
right = np.array([-np.sin(az), np.cos(az), 0]); up = np.cross(d, right)
def project(v):
    p = (np.asarray(v, dtype=float) - CENTER)
    return (p @ right * SCALE + W / 2, -p @ up * SCALE + H / 2)

# Badge text and pixel offset from the projected centroid (tune visually).
BADGES = {
    '01_hidden_chassis': ('01', 0, 50), '02_rounded_mac_shell': ('02', -70, -20),
    '03_column_lower_240': ('03', 55, 0), '04_column_upper_220': ('04', -55, 0),
    '05_arm_rear_156': ('05', 0, -50), '06_arm_front_165': ('06', -60, 0),
    '07_corner_cover': ('07', 60, -10), '08_rounded_LED_head': ('08', -80, 10),
    '09_UGREEN_59x35x23_cradle': ('09', -60, 15), '10_camera_rear_keeper': ('10', 0, 55),
    '11_column_slide_dock': ('11', -45, -25), '12_open_screen_carrier': ('12', 70, 10),
    '13_screen_lower_foot_left': ('13', -50, 30), '14_screen_lower_foot_right': ('14', 50, 30),
    '15_screen_sliding_upper_jaw': ('15', -60, 0),
    'steel_spine': ('G', 30, -60), 'steel_arm': ('G', -30, -50),
    'ballast_-110': ('P', -40, 25), 'ballast_110': ('P', 40, 25),
    'Mac_mini_envelope': ('M', 0, 55), 'LED_aluminum_envelope': ('L', 60, 20),
    'UGREEN_case_envelope': ('C', -40, -45), 'iPad_mini_envelope': ('T', 50, -40),
}
meshes = dict((n, t) for n, t, c in items)

fig = plt.figure(figsize=(14, 19), facecolor='#f6f7f5')
ax = fig.add_axes([0, 0.06, 1, 0.9]); ax.imshow(pix); ax.set_xlim(0, W); ax.set_ylim(H, 0); ax.axis('off')
for n, (txt, dx, dy) in BADGES.items():
    x, y = project(meshes[n].centroid)
    ax.text(x + dx, y + dy, txt, fontsize=13, color='#273d37', ha='center', va='center',
            bbox=dict(boxstyle='circle,pad=0.28', fc='white', ec='#273d37', lw=0.9))

fig.text(0.05, 0.965, '学习台灯 V3 · 整灯爆炸图', fontsize=24, color='#273d37')
fig.text(0.05, 0.938, '打印件沿装配方向散开；钢骨架为焊接整体，保持原位', fontsize=13, color='#64706a')
legend1 = ('打印件：01 内底架 · 02 圆角外罩 · 03 下灯柱 · 04 上灯柱 · 05 后灯臂 · 06 前灯臂 · 07 转角罩 · 08 灯头\n'
           '09 摄像头承座 · 10 摄像头压盖 · 11 滑入连接座 · 12 屏幕载架 · 13/14 下托脚 · 15 上夹爪')
legend2 = '另购件：G 钢方管骨架（焊接倒 L）· M Mac mini · P 钢配重 ×2 · L LED 铝槽 · C 绿联摄像头 · T 平板（示例）'
fig.text(0.05, 0.045, legend1, fontsize=11.5, color='#273d37', va='bottom')
fig.text(0.05, 0.018, legend2, fontsize=11.5, color='#64706a', va='bottom')
out = pathlib.Path('renders/台灯V3_爆炸图.png')
fig.savefig(out, dpi=100)
print('saved', out)
