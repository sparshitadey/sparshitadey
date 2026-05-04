#!/usr/bin/env python3
"""
generate_oscillation.py
-----------------------
Animated SVG: neutrino oscillation along the SBN beamline.
Top section: P(nu_e) vs L/E theory curve.
Bottom section: animated beam particles BNB -> SBND -> ICARUS.
Vertical dashed lines connect detector positions between both panels.

Physics: two-flavour approximation
  P(nu_mu -> nu_e, L) = sin2(2*theta) * sin2(1.27 * Dm2 * L[km] / E[GeV])
"""

import math
import random
import os

# -----------------------------------------------
# Physics
# -----------------------------------------------
THETA      = math.pi / 8
DELTA_M2   = 3.0               # eV2 -- sterile neutrino benchmark (SBN sensitivity region)
ENERGY_GEV = 0.8               # representative BNB energy

L_SBND_M   = 110.0
L_ICARUS_M = 600.0

def osc_prob(L_m):
    L_km = L_m / 1000.0
    arg  = 1.27 * DELTA_M2 * L_km / ENERGY_GEV
    return math.sin(2 * THETA)**2 * math.sin(arg)**2

P_sbnd   = osc_prob(L_SBND_M)
P_icarus = osc_prob(L_ICARUS_M)

# -----------------------------------------------
# Canvas layout
# -----------------------------------------------
W = 800

# -- oscillation plot section (top) --
PLOT_TOP    = 10          # y start of plot area
PLOT_H      = 68          # height of plot area
PLOT_LEFT   = 44          # x left edge of plot (space for y-axis label)
PLOT_RIGHT  = W - 20      # x right edge of plot
PLOT_BOTTOM = PLOT_TOP + PLOT_H

# -- divider --
DIVIDER_Y   = PLOT_BOTTOM + 10

# -- beam section (bottom) --
BEAM_SECTION_TOP = DIVIDER_Y
BEAM_SECTION_H   = 210
H = BEAM_SECTION_TOP + BEAM_SECTION_H

BEAM_Y      = BEAM_SECTION_TOP + BEAM_SECTION_H // 2 - 10
BEAM_RADIUS = 10          # tighter beam
PARTICLE_R  = 2.5         # smaller particles

DET_W = 60
DET_H = 80
DET_W_SBND = 38
DET_H_SBND = 60

# -- x positions (same as before) --
X_SOURCE  = 60
X_SBND    = 160   # aligned to L/E scale of plot
X_ICARUS  = 680

# -- L/E axis mapping --
# X_SOURCE  -> L/E = 0
# X_ICARUS  -> L/E = L_ICARUS_M / 1000 / ENERGY_GEV  (exactly)
# extend plot right past ICARUS to show curve continuing
LE_ICARUS  = L_ICARUS_M / 1000.0 / ENERGY_GEV        # 0.75 km/GeV
LE_SBND    = L_SBND_M  / 1000.0 / ENERGY_GEV         # 0.1375 km/GeV
LE_MAX     = LE_ICARUS * (PLOT_RIGHT - PLOT_LEFT) / (X_ICARUS - PLOT_LEFT)

def le_to_x(le):
    """Map L/E value (km/GeV) to x pixel."""
    return PLOT_LEFT + (le / LE_MAX) * (PLOT_RIGHT - PLOT_LEFT)

def prob_to_y(p):
    """Map probability [0,1] to y pixel in plot area (flipped: 0 at bottom)."""
    P_MAX = 0.45
    return PLOT_BOTTOM - (p / P_MAX) * PLOT_H

# -----------------------------------------------
# Particles
# -----------------------------------------------
random.seed(42)
N_PER_ZONE   = 30
ANIM_DUR     = 3.2
SPEED_JITTER = 0.6

def make_particles(x_start, x_end, p_nue, n=N_PER_ZONE):
    out = []
    for i in range(n):
        is_nue  = random.random() < p_nue
        y_off   = random.uniform(-BEAM_RADIUS + 2, BEAM_RADIUS - 2)
        delay   = random.uniform(0, ANIM_DUR)
        dur     = ANIM_DUR + random.uniform(-SPEED_JITTER, SPEED_JITTER)
        opacity = random.uniform(0.55, 0.88)
        out.append({
            "x_start": x_start, "x_end": x_end,
            "y": BEAM_Y + y_off,
            "is_nue": is_nue, "delay": delay,
            "dur": dur, "opacity": opacity,
        })
    return out

zone1 = make_particles(X_SOURCE, X_SBND,   p_nue=P_sbnd * 0.3)
zone2 = make_particles(X_SBND,   X_ICARUS, p_nue=P_icarus)
all_particles = zone1 + zone2

# -----------------------------------------------
# Colours
# -----------------------------------------------
NUE_CORE = "#64b5f6"
NUE_GLOW = "#1565c0"
NUM_CORE = "#ff8a80"
NUM_GLOW = "#b71c1c"
BG       = "#0d1117"
BEAM_COL = "#1a2233"
SBND_COL = "#00bcd4"
ICAR_COL = "#ce93d8"
AXIS_COL = "#3d4450"
LABEL_COL= "#8b949e"
CURVE_COL= "#a8d8a8"    # soft green for oscillation curve

# -----------------------------------------------
# Build SVG
# -----------------------------------------------
lines = []
def w(s): lines.append(s)

w(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
  f'width="{W}" height="{H}" style="background:{BG}; border-radius:12px;">')

# ---- defs ----
w('<defs>')

for fid, std in [("glow-nue","3.0"),("glow-num","3.0"),
                  ("glow-sbnd","6"),("glow-icarus","6"),
                  ("glow-curve","3"),("glow-src","5")]:
    w(f'  <filter id="{fid}" x="-80%" y="-80%" width="260%" height="260%">'
      f'<feGaussianBlur stdDeviation="{std}" result="blur"/>'
      f'<feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>'
      f'</filter>')

w(f'''  <linearGradient id="beam-grad" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0%"   stop-color="{BEAM_COL}" stop-opacity="0"/>
    <stop offset="40%"  stop-color="{BEAM_COL}" stop-opacity="0.4"/>
    <stop offset="60%"  stop-color="{BEAM_COL}" stop-opacity="0.4"/>
    <stop offset="100%" stop-color="{BEAM_COL}" stop-opacity="0"/>
  </linearGradient>''')

for gid, core, glow in [("grad-nue", NUE_CORE, NUE_GLOW),
                          ("grad-num", NUM_CORE, NUM_GLOW)]:
    w(f'''  <radialGradient id="{gid}" cx="50%" cy="50%" r="50%">
    <stop offset="0%"   stop-color="{core}" stop-opacity="1"/>
    <stop offset="55%"  stop-color="{core}" stop-opacity="0.5"/>
    <stop offset="100%" stop-color="{glow}" stop-opacity="0"/>
  </radialGradient>''')

w('</defs>')

# ---- CSS ----
w('<style>')
w('''
  .beam-env   { animation: pulse-beam   4s   ease-in-out infinite alternate; }
  .det-sbnd   { animation: pulse-sbnd   3s   ease-in-out infinite alternate; }
  .det-icarus { animation: pulse-icarus 3.5s ease-in-out infinite alternate; }
  @keyframes pulse-beam   { from{opacity:0.5} to{opacity:0.8} }
  @keyframes pulse-sbnd   { from{opacity:0.3} to{opacity:0.55} }
  @keyframes pulse-icarus { from{opacity:0.25} to{opacity:0.5} }
''')
for idx, p in enumerate(all_particles):
    x0, x1, y = p["x_start"], p["x_end"], p["y"]
    op = p["opacity"]
    w(f'  @keyframes fly{idx} {{'
      f' 0%{{transform:translate({x0:.1f}px,{y:.1f}px);opacity:0}}'
      f' 8%{{transform:translate({x0:.1f}px,{y:.1f}px);opacity:{op:.2f}}}'
      f' 92%{{transform:translate({x1:.1f}px,{y:.1f}px);opacity:{op:.2f}}}'
      f' 100%{{transform:translate({x1:.1f}px,{y:.1f}px);opacity:0}} }}')
    w(f'  #p{idx}{{animation:fly{idx} {p["dur"]:.2f}s linear {p["delay"]:.2f}s infinite}}')
w('</style>')

# =============================================
# OSCILLATION PLOT (top section)
# =============================================

# -- plot background --
w(f'<rect x="{PLOT_LEFT}" y="{PLOT_TOP}" '
  f'width="{PLOT_RIGHT - PLOT_LEFT}" height="{PLOT_H}" '
  f'fill="{BG}" rx="3" opacity="0.5"/>')

# -- axes --
# x axis
w(f'<line x1="{PLOT_LEFT}" y1="{PLOT_BOTTOM}" x2="{PLOT_RIGHT}" y2="{PLOT_BOTTOM}" '
  f'stroke="{AXIS_COL}" stroke-width="1" opacity="0.8"/>')
# y axis
w(f'<line x1="{PLOT_LEFT}" y1="{PLOT_TOP}" x2="{PLOT_LEFT}" y2="{PLOT_BOTTOM}" '
  f'stroke="{AXIS_COL}" stroke-width="1" opacity="0.8"/>')

# -- y-axis ticks and labels --
for prob, label in [(0.0,"0"), (0.2,"0.2"), (0.4,"0.4")]:
    yp = prob_to_y(prob)
    if PLOT_TOP <= yp <= PLOT_BOTTOM:
        w(f'<line x1="{PLOT_LEFT-3}" y1="{yp:.1f}" x2="{PLOT_LEFT}" y2="{yp:.1f}" '
          f'stroke="{AXIS_COL}" stroke-width="1"/>')
        w(f'<text x="{PLOT_LEFT-5}" y="{yp+3:.1f}" text-anchor="end" '
          f'font-family="monospace" font-size="8" fill="{LABEL_COL}" opacity="0.7">{label}</text>')
        # gridline
        w(f'<line x1="{PLOT_LEFT}" y1="{yp:.1f}" x2="{PLOT_RIGHT}" y2="{yp:.1f}" '
          f'stroke="{AXIS_COL}" stroke-width="0.5" stroke-dasharray="3 4" opacity="0.3"/>')

# -- axis labels --
w(f'<text x="{(PLOT_LEFT + PLOT_RIGHT)//2}" y="{H - 6}" text-anchor="middle" '
  f'font-family="monospace" font-size="9" fill="{LABEL_COL}" opacity="0.6">'
  f'L/E  [km/GeV]</text>')

# Dm2 annotation in top-right of plot
w(f'<text x="{PLOT_RIGHT - 5}" y="{PLOT_TOP + 12}" text-anchor="end" '
  f'font-family="monospace" font-size="8" fill="{CURVE_COL}" opacity="0.6">'
  f'&#916;m&#178; = {DELTA_M2:.0f} eV&#178;</text>')
w(f'<text x="10" y="{(PLOT_TOP + PLOT_BOTTOM)//2}" text-anchor="middle" '
  f'font-family="monospace" font-size="8" fill="{LABEL_COL}" opacity="0.6" '
  f'transform="rotate(-90,10,{(PLOT_TOP + PLOT_BOTTOM)//2})">P(&#957;e)</text>')

# -- oscillation curve --
N_CURVE = 300
curve_pts = []
for i in range(N_CURVE + 1):
    le = LE_MAX * i / N_CURVE
    p  = osc_prob(le * 1000.0 * ENERGY_GEV)   # convert back to metres
    xp = le_to_x(le)
    yp = prob_to_y(p)
    curve_pts.append(f"{xp:.1f},{yp:.1f}")

# glow version of curve (slightly thicker, more transparent)
w(f'<polyline points="{" ".join(curve_pts)}" '
  f'fill="none" stroke="{CURVE_COL}" stroke-width="3" opacity="0.15" '
  f'filter="url(#glow-curve)"/>')
# main curve
w(f'<polyline points="{" ".join(curve_pts)}" '
  f'fill="none" stroke="{CURVE_COL}" stroke-width="1.5" opacity="0.8"/>')

# -- SBND and ICARUS markers on curve --
for L_m, col, name in [(L_SBND_M, SBND_COL, "SBND"),
                         (L_ICARUS_M, ICAR_COL, "ICARUS")]:
    le  = L_m / 1000.0 / ENERGY_GEV
    p   = osc_prob(L_m)
    xm  = le_to_x(le)
    ym  = prob_to_y(p)
    # dot on curve
    w(f'<circle cx="{xm:.1f}" cy="{ym:.1f}" r="3.5" fill="{col}" '
      f'opacity="0.9" filter="url(#glow-curve)"/>')

# =============================================
# DASHED VERTICAL CONNECTORS (plot -> beamline)
# =============================================
for L_m, x_det, col in [(L_SBND_M, X_SBND, SBND_COL),
                          (L_ICARUS_M, X_ICARUS, ICAR_COL)]:
    le  = L_m / 1000.0 / ENERGY_GEV
    xm  = le_to_x(le)
    p   = osc_prob(L_m)
    ym  = prob_to_y(p)

    # line from curve dot down to divider (in plot coords)
    w(f'<line x1="{xm:.1f}" y1="{ym:.1f}" x2="{xm:.1f}" y2="{DIVIDER_Y}" '
      f'stroke="{col}" stroke-width="1" stroke-dasharray="4 3" opacity="0.35"/>')

    # line from divider down to detector box top (in beam coords)
    det_top = BEAM_Y - DET_H // 2
    w(f'<line x1="{x_det}" y1="{DIVIDER_Y}" x2="{x_det}" y2="{det_top}" '
      f'stroke="{col}" stroke-width="1" stroke-dasharray="4 3" opacity="0.35"/>')

# =============================================
# DIVIDER LINE
# =============================================
w(f'<line x1="{PLOT_LEFT}" y1="{DIVIDER_Y}" x2="{PLOT_RIGHT}" y2="{DIVIDER_Y}" '
  f'stroke="{AXIS_COL}" stroke-width="0.8" stroke-dasharray="6 5" opacity="0.4"/>')

# =============================================
# BEAM SECTION (bottom)
# =============================================

# -- beam envelope --
w(f'<rect class="beam-env" x="{X_SOURCE}" y="{BEAM_Y - BEAM_RADIUS}" '
  f'width="{X_ICARUS + DET_W//2 - X_SOURCE}" height="{BEAM_RADIUS * 2}" rx="5" '
  f'fill="url(#beam-grad)"/>')

# -- beamline centre --
w(f'<line x1="{X_SOURCE}" y1="{BEAM_Y}" x2="{X_ICARUS + DET_W//2}" y2="{BEAM_Y}" '
  f'stroke="{BEAM_COL}" stroke-width="1" stroke-dasharray="5 4" opacity="0.35"/>')

# -- particles --
r_outer = PARTICLE_R * 2.5
for idx, p in enumerate(all_particles):
    gid = "grad-nue" if p["is_nue"] else "grad-num"
    fid = "glow-nue" if p["is_nue"] else "glow-num"
    col = NUE_CORE   if p["is_nue"] else NUM_CORE
    w(f'<g id="p{idx}">')
    w(f'  <circle cx="0" cy="0" r="{r_outer:.1f}" fill="url(#{gid})" '
      f'filter="url(#{fid})" opacity="0.5"/>')
    w(f'  <circle cx="0" cy="0" r="{PARTICLE_R}" fill="{col}" opacity="0.9"/>')
    w('</g>')

# -- detector boxes --
def draw_detector(x_centre, label, sublabel, accent, filt, dw=None, dh=None):
    dw = dw if dw is not None else DET_W
    dh = dh if dh is not None else DET_H
    x = x_centre - DET_W // 2
    y = BEAM_Y - DET_H // 2
    w(f'<rect x="{x-2}" y="{y-2}" width="{DET_W+4}" height="{DET_H+4}" rx="5" '
      f'fill="{accent}" opacity="0.10" filter="url(#{filt})"/>')
    cls = "det-sbnd" if "sbnd" in filt else "det-icarus"
    w(f'<rect class="{cls}" x="{x}" y="{y}" width="{DET_W}" height="{DET_H}" rx="4" '
      f'fill="{BG}" fill-opacity="0.35" stroke="{accent}" stroke-width="1.5" '
      f'stroke-opacity="0.7"/>')
    w(f'<text x="{x_centre}" y="{y + DET_H + 15}" text-anchor="middle" '
      f'font-family="monospace" font-size="12" font-weight="bold" fill="{accent}" '
      f'opacity="0.95">{label}</text>')
    w(f'<text x="{x_centre}" y="{y + DET_H + 28}" text-anchor="middle" '
      f'font-family="monospace" font-size="9" fill="{LABEL_COL}" opacity="0.6">'
      f'{sublabel}</text>')

draw_detector(X_SBND,   "SBND",   "L = 110 m", SBND_COL, "glow-sbnd", DET_W_SBND, DET_H_SBND)
draw_detector(X_ICARUS, "ICARUS", "L = 600 m", ICAR_COL, "glow-icarus")

# -- BNB source --
w(f'<circle cx="{X_SOURCE}" cy="{BEAM_Y}" r="6" fill="#ffd54f" opacity="0.85" '
  f'filter="url(#glow-src)"/>')
w(f'<text x="{X_SOURCE}" y="{BEAM_Y + 20}" text-anchor="middle" '
  f'font-family="monospace" font-size="10" fill="#ffd54f" opacity="0.8">BNB</text>')

# -- legend --
LX = X_SOURCE + 2
LY = H - 16
w(f'<circle cx="{LX+5}" cy="{LY}" r="3.5" fill="{NUM_CORE}" opacity="0.9" '
  f'filter="url(#glow-num)"/>')
w(f'<text x="{LX+13}" y="{LY+4}" font-family="monospace" font-size="9" '
  f'fill="{NUM_CORE}" opacity="0.85">&#957;&#956;</text>')
w(f'<circle cx="{LX+42}" cy="{LY}" r="3.5" fill="{NUE_CORE}" opacity="0.9" '
  f'filter="url(#glow-nue)"/>')
w(f'<text x="{LX+50}" y="{LY+4}" font-family="monospace" font-size="9" '
  f'fill="{NUE_CORE}" opacity="0.85">&#957;e</text>')

w('</svg>')

# -----------------------------------------------
# Write
# -----------------------------------------------
os.makedirs("dist", exist_ok=True)
output_path = "dist/neutrino_oscillation.svg"
with open(output_path, "w") as f:
    f.write("\n".join(lines))

print(f"Written {output_path}  ({W}x{H}px)")
print(f"  P(nu_e) at SBND   {L_SBND_M:.0f}m: {P_sbnd:.4f}")
print(f"  P(nu_e) at ICARUS {L_ICARUS_M:.0f}m: {P_icarus:.4f}")
