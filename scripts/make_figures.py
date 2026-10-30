"""Figures 2 to 5 and 9 to 11 of the paper from the notebook outputs.

Usage: python make_figures.py <folder with the result folders> <output folder>
"""
import sys, os
import numpy as np, pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import dates as mdates, rcParams
from matplotlib.patches import FancyBboxPatch, Rectangle

R, OUT = sys.argv[1], sys.argv[2]
ORIG_LST = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'lst_original_points.csv.gz')
os.makedirs(OUT, exist_ok=True)
rcParams.update({"font.family": "serif", "mathtext.fontset": "dejavuserif", "font.size": 9.5, "axes.linewidth": 0.8, "savefig.dpi": 300,
                 "axes.spines.top": False, "axes.spines.right": False})
OB = pd.to_datetime(['2019-06-22', '2020-05-29', '2021-05-15', '2022-05-07'])
C_RF, C_TAB, C_FUS, C_T, C_V, C_W = '#b84a2f', '#3a6ea5', '#111111', '#2e6b8a', '#d1711e', '#4d8f5b'

def mark(ax, lo=None, hi=None):
    for o in OB:
        if (lo is None or o >= lo) and (hi is None or o <= hi):
            ax.axvspan(o, o + pd.Timedelta(days=30), color='#f2c14e', alpha=0.28, lw=0, zorder=0)
            ax.axvline(o, color='0.35', ls='--', lw=0.9, zorder=1)

def save(fig, name):
    fig.savefig(f'{OUT}/{name}.png', bbox_inches='tight'); fig.savefig(f'{OUT}/{name}.pdf', bbox_inches='tight'); plt.close(fig)
    print('saved', name)

# ---------- Fig. 2: data footprints ----------
LAKE = (36.36061, 74.56276)
fig, ax = plt.subplots(figsize=(7.2, 5.0))
def box(x0, x1, y0, y1, **kw):
    ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, fill=False, **kw))
box(74.499, 74.621, 36.300, 36.401, ec='0.45', lw=1.2, ls='-', label='Sentinel-2 export area')
dlat, dlon = 2.5 / 111.2, 2.5 / (111.32 * np.cos(np.radians(LAKE[0])))
box(LAKE[1] - dlon, LAKE[1] + dlon, LAKE[0] - dlat, LAKE[0] + dlat, ec=C_RF, lw=2.0, label='RiskFlow window (5 x 5 km)')
box(74.54, 74.63, 36.34, 36.41, ec=C_V, lw=1.6, ls='--', label='ITS_LIVE velocity box (tongue and ice dam)')
gl = LAKE[0] + (np.arange(8) - 3.5) * 0.01; gn = LAKE[1] + (np.arange(8) - 3.5) * 0.0125
GX, GY = np.meshgrid(gn, gl)
ax.plot(GX.ravel(), GY.ravel(), 's', ms=3.2, mfc='none', mec=C_T, mew=0.9, label='MODIS lake grid (64 pixels)')
O = pd.read_csv(ORIG_LST, usecols=['Latitude', 'Longitude']).drop_duplicates()
ax.plot(O.Longitude, O.Latitude, '.', ms=3, c='0.3', label='original MODIS points (9 pixels)')
ax.plot(LAKE[1], LAKE[0], '*', ms=14, mfc='#f2c14e', mec='k', mew=0.8, label='ice-dammed lake', zorder=5)
ax.plot(74.595, 36.298, 'v', ms=7, mfc='w', mec='k', label='Hassanabad (Karakoram Highway)', zorder=5)
ax.set_xlim(74.47, 74.66); ax.set_ylim(36.28, 36.50)
ax.set_aspect(1 / np.cos(np.radians(LAKE[0])))
ax.set_xlabel('Longitude (°E)'); ax.set_ylabel('Latitude (°N)')
x0, y0 = 74.480, 36.288; km = 5 / (111.32 * np.cos(np.radians(36.3)))
ax.plot([x0, x0 + km], [y0, y0], c='k', lw=2.5); ax.text(x0 + km / 2, y0 + 0.003, '5 km', ha='center', fontsize=8)
ax.annotate('N', xy=(74.645, 36.495), xytext=(74.645, 36.468), ha='center', va='top', fontsize=9,
            arrowprops=dict(arrowstyle='-|>', color='k', lw=1))
ax.annotate('original MODIS points\n(about 14 km north-west)', xy=(74.4955, 36.472), xytext=(74.505, 36.488), fontsize=7.2,
            va='center', arrowprops=dict(arrowstyle='-', color='0.4', lw=0.7))
ax.legend(fontsize=7.4, loc='upper left', bbox_to_anchor=(1.02, 1.0), frameon=True, framealpha=0.95, edgecolor='0.8')
ax.grid(True, lw=0.3, color='0.9')
save(fig, 'fig02_data_footprints')

# ---------- Fig. 3: velocity context ----------
V = pd.read_csv(f'{R}/TerraFlow_Shisper/terraflow_daily_for_fusion.csv', parse_dates=['date'])
V['fast'] = V.n_pixels * V.frac_over_300
M = V.set_index('date').median_observed.resample('MS').median()
Y = V.groupby(V.date.dt.year).agg(readings=('n_pixels', 'sum'), fast=('fast', 'sum'))
Y['share'] = 100 * Y.fast / Y.readings
fig, ax = plt.subplots(2, 1, figsize=(7.2, 4.6), sharex=False, gridspec_kw=dict(hspace=0.35))
ax[0].plot(M.index, M.values, c='k', lw=0.9)
ax[0].axvspan(pd.Timestamp('2017-01-01'), pd.Timestamp('2019-12-31'), color='0.88', zorder=0)
ax[0].text(pd.Timestamp('2016-09-01'), 0.97, 'surge\n2017 to 2019', transform=ax[0].get_xaxis_transform(), ha='center',
           va='top', fontsize=7.5, color='0.35')
mark(ax[0])
ax[0].set_ylabel('median daily maximum\nspeed (m yr$^{-1}$)'); ax[0].set_yscale('log')
ax[0].set_xlim(pd.Timestamp('1991-01-01'), pd.Timestamp('2025-12-31'))
ax[0].text(0.005, 1.02, '(a)', transform=ax[0].transAxes, fontweight='bold')
yy = Y[Y.index >= 1991]
ax[1].bar(yy.index, yy.share, color=['#b84a2f' if 2017 <= y <= 2019 else '0.55' for y in yy.index], width=0.8)
ax[1].set_ylabel('readings above\n300 m yr$^{-1}$ (%)'); ax[1].set_xlim(1990.4, 2025.6)
for o in OB:
    ax[1].axvline(o.year + (o.dayofyear - 1) / 365.25, color='0.35', ls='--', lw=0.9)
ax[1].text(0.005, 1.02, '(b)', transform=ax[1].transAxes, fontweight='bold')
for a in ax:
    a.grid(True, axis='y', lw=0.3, color='0.9')
save(fig, 'fig03_velocity_context')

# ---------- Fig. 4: framework and module architectures ----------
fig, ax = plt.subplots(figsize=(7.4, 4.4)); ax.set_xlim(0, 100); ax.set_ylim(0, 62); ax.axis('off')
def node(x, y, w, h, title, body, fc, tsize=7.6, bsize=6.4):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.3,rounding_size=1.0', fc=fc, ec='0.25', lw=0.8))
    if title:
        ax.text(x + w / 2, y + h - 1.4, title, ha='center', va='top', fontsize=tsize, fontweight='bold')
    ax.text(x + w / 2, y + (h - 4.6 if title else h / 2), body, ha='center', va='top' if title else 'center',
            fontsize=bsize, linespacing=1.3)
def arrow(x0, y0, x1, y1):
    ax.annotate('', xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle='-|>', color='0.25', lw=0.9, shrinkA=0, shrinkB=0))
rows = [(45, 'Sentinel-2 L2A', '6 bands, 5 x 5 km\nwindow at the lake,\n128 x 128 pixels', 'RiskFlow (CNN)',
         'conv 32 and 64 (3 x 3),\nmax-pooling, dense 64,\nsigmoid output', 'scene probability\n(post-outburst)', '#dbe7f3'),
        (26, 'ITS_LIVE v2', 'image-pair velocities\nover the tongue\nand the ice dam', 'TerraFlow (Transformer)',
         '4 layers, 8 heads, width 256;\nlast 32 observed days\nto the next one', 'velocity anomaly\n(30 days, 90th pct.)', '#fbe3cf'),
        (7, 'MODIS MOD11A1', 'daytime LST on an\n8 x 8 km grid\ncentred on the lake', 'TempFlow (BiLSTM)',
         'BiLSTM 128, LSTM 64,\nLSTM 32; 30-day\ncontext to next day', 'temperature anomaly\n(30 days, median)', '#f6d8d8')]
for y, t1, b1, t2, b2, b3, fc in rows:
    node(0.5, y, 20, 12, t1, b1, '#f2f2f2'); node(24, y, 26, 12, t2, b2, fc); node(53.5, y, 17.5, 12, None, b3, 'white', bsize=6.6)
    arrow(20.8, y + 6, 23.7, y + 6); arrow(50.3, y + 6, 53.2, y + 6)
node(75, 13, 24.5, 14, 'Tabular stream', 'daily logistic regression\nof the two anomalies', '#e8e8e8')
arrow(71.3, 32, 74.7, 24.5); arrow(71.3, 13, 74.7, 17)
node(75, 40, 24.5, 19, 'FusionFlow', 'logit p = logit p$_{\\rm vis}$ + logit p$_{\\rm tab}$\nalert if p $\\geq$ 0.5\n\ncompared with RiskFlow\nalone, the agreement rule\nand the either-stream rule', '#e8e8e8')
arrow(71.3, 51, 74.7, 51); arrow(87.25, 27.3, 87.25, 39.7)
save(fig, 'fig04_framework')

# ---------- Fig. 5: RiskFlow, every scene predicted by a model that never saw its year ----------
L = pd.read_csv(f'{R}/RiskFlow_Shisper/riskflow_predictions.csv', parse_dates=['date']).sort_values('date')
L['rule'] = L.water_rule == 1
g = L.label == 1
fig, ax = plt.subplots(2, 1, figsize=(7.4, 4.8), sharex=True, gridspec_kw=dict(hspace=0.12, height_ratios=[1.3, 1]))
ax[0].scatter(L.date[~g], L.p_loyo[~g], s=10, c=C_TAB, alpha=0.8, label='normal scene', zorder=3)
ax[0].errorbar(L.date[g], L.p_loyo[g], yerr=[L.p_loyo[g] - L.p_loyo_min[g], L.p_loyo_max[g] - L.p_loyo[g]],
               fmt='^', ms=6, c=C_RF, ecolor=C_RF, elinewidth=0.8, capsize=2, label='post-outburst scene (5-seed range)', zorder=4)
ax[0].axhline(0.5, c='0.4', ls=':', lw=1); ax[0].set_ylim(-0.04, 1.04); ax[0].set_ylabel('RiskFlow probability')
ax[0].legend(fontsize=7.5, loc='upper right', bbox_to_anchor=(1.0, 1.0), frameon=True, framealpha=0.95, edgecolor='0.8')
ax[1].scatter(L.date, L.water_km2, s=9, c='0.45', label='water within 1.5 km of the lake', zorder=3)
ax[1].scatter(L.date[L.rule], L.water_km2[L.rule], s=40, facecolors='none', edgecolors=C_W, lw=1.1, label='flagged by the water-index rule', zorder=4)
ax[1].scatter(L.date[g], L.water_km2[g], s=22, marker='^', c=C_RF, zorder=5, label='post-outburst scene')
ax[1].axhline(0.05, c=C_W, ls=':', lw=0.9); ax[1].axhline(0.02, c=C_W, ls='--', lw=0.9)
ax[1].set_ylabel('water area (km$^2$)'); ax[1].set_ylim(-0.015, 0.44)
ax[1].legend(fontsize=7.2, ncol=3, loc='upper center', frameon=True, framealpha=0.95, edgecolor='0.8')
for a in ax:
    mark(a); a.grid(True, axis='y', lw=0.3, color='0.9')
ax[0].text(0.005, 1.02, '(a)', transform=ax[0].transAxes, fontweight='bold'); ax[1].text(0.005, 1.02, '(b)', transform=ax[1].transAxes, fontweight='bold')
save(fig, 'fig05_riskflow_loyo')

# ---------- Fig. 9: TempFlow by lead time at both sites ----------
LK = pd.read_csv(f'{R}/TempFlow_Shisper/tempflow_leadtime.csv')
OR = pd.read_csv(f'{R}/TempFlow_original/tempflow_leadtime.csv')
fig, ax = plt.subplots(1, 2, figsize=(7.4, 3.0), gridspec_kw=dict(wspace=0.28))
for a, T, title in [(ax[0], LK, '(a) lake grid (64 pixels at the lake)'), (ax[1], OR, '(b) original points (14 km north-west)')]:
    best = T[(T.tempflow < T.persistence) & (T.tempflow < T.climatology_pixel)].lead_days
    for h in best:
        a.axvspan(h - 0.5, h + 0.5, color='0.92', zorder=0)
    a.plot(T.lead_days, T.climatology_pixel, color='#d1711e', ls=':', lw=1.8, marker='^', ms=5, label='climatology (seasonal cycle)')
    a.plot(T.lead_days, T.persistence, color=C_TAB, ls='--', lw=1.6, marker='s', ms=4.5, label='persistence (last value)')
    a.plot(T.lead_days, T.tempflow, color='#111111', lw=2.0, marker='o', ms=5, label='TempFlow')
    a.set_xticks([1, 2, 3, 4]); a.set_xlim(0.5, 4.5); a.set_xlabel('forecast lead time (days)'); a.set_title(title, fontsize=9, loc='left')
    a.grid(True, axis='y', lw=0.3, color='0.88')
ax[0].set_ylabel('mean absolute error (K)'); ax[1].legend(fontsize=7.3, loc='lower right', frameon=True, framealpha=0.95, edgecolor='0.8')
save(fig, 'fig09_tempflow_leadtime')

# ---------- Figs. 10 and 11: FusionFlow ----------
D = pd.read_csv(f'{R}/FusionFlow_Shisper/fusion_daily.csv', parse_dates=['date'])
S = pd.read_csv(f'{R}/FusionFlow_Shisper/fusion_scenes.csv', parse_dates=['date'])
lo, hi = pd.Timestamp('2022-03-01'), pd.Timestamp('2022-08-31')
d22, s22 = D[(D.date >= lo) & (D.date <= hi)], S[(S.date >= lo) & (S.date <= hi)]
fig, ax = plt.subplots(3, 1, figsize=(7.0, 6.2), sharex=True, gridspec_kw=dict(hspace=0.12))
ax[0].plot(d22.date, d22.vel_anom, c='k', lw=1.1); ax[0].set_ylabel('velocity anomaly\n(log ratio, 90th pct.)')
ax[1].plot(d22.date, d22.temp_anom, c=C_T, lw=1.1); ax[1].axhline(0, c='0.6', lw=0.8); ax[1].set_ylabel('temperature\nanomaly (K)')
ax[2].plot(d22.date, d22.p_tab_main, c=C_TAB, lw=1.1, label='tabular stream (daily)')
ax[2].plot(s22.date, s22.p_rf_main, '^', c=C_RF, ms=6.5, label='RiskFlow (scene)')
ax[2].plot(s22.date, s22.p_fusion_main, 'o', mfc='none', mec=C_FUS, ms=8.5, mew=1.3, label='FusionFlow (scene)')
ax[2].axhline(0.5, c='0.4', ls=':', lw=1); ax[2].set_ylim(-0.03, 1.03); ax[2].set_ylabel('probability')
ax[2].legend(fontsize=7.5, loc='upper right', frameon=True, framealpha=0.95, edgecolor='0.8')
for k, a in enumerate(ax):
    mark(a, lo, hi); a.grid(True, axis='y', lw=0.3, color='0.9')
    a.text(0.005, 1.02, f'({"abc"[k]})', transform=a.transAxes, fontweight='bold')
ax[2].xaxis.set_major_locator(mdates.MonthLocator()); ax[2].xaxis.set_major_formatter(mdates.DateFormatter('%b 2022'))
save(fig, 'fig11_fusion_2022')

fig, ax = plt.subplots(2, 1, figsize=(7.4, 4.6), sharex=True, gridspec_kw=dict(hspace=0.12))
ax[0].plot(D.date, D.p_tab_loyo, c=C_TAB, lw=0.8); ax[0].axhline(0.5, c='0.4', ls=':', lw=1)
ax[0].axvline(pd.Timestamp('2022-12-31'), c=C_T, ls=':', lw=1.1)
ax[0].text(pd.Timestamp('2023-01-20'), 0.97, 'temperature\nstream ends', transform=ax[0].get_xaxis_transform(), fontsize=7, color=C_T, va='top')
ax[0].set_ylabel('tabular stream\n(daily)'); ax[0].set_ylim(-0.03, 1.03)
gg = S.label == 1
ax[1].scatter(S.date[~gg], S.p_rf_loyo[~gg], s=9, c='#9db4cf', label='RiskFlow, normal scene', zorder=3)
ax[1].scatter(S.date[~gg], S.p_fusion_loyo[~gg], s=11, facecolors='none', edgecolors='0.3', lw=0.6, label='FusionFlow, normal scene', zorder=3)
ax[1].scatter(S.date[gg], S.p_rf_loyo[gg], s=42, marker='^', c=C_RF, label='RiskFlow, post-outburst scene', zorder=4)
ax[1].scatter(S.date[gg], S.p_fusion_loyo[gg], s=70, facecolors='none', edgecolors='k', lw=1.3, label='FusionFlow, post-outburst scene', zorder=4)
ax[1].axhline(0.5, c='0.4', ls=':', lw=1); ax[1].set_ylim(-0.03, 1.03); ax[1].set_ylabel('probability (scene)')
ax[1].legend(fontsize=7, ncol=1, loc='center right', bbox_to_anchor=(1.0, 0.6), frameon=True, framealpha=0.95, edgecolor='0.8')
for k, a in enumerate(ax):
    mark(a); a.grid(True, axis='y', lw=0.3, color='0.9'); a.text(0.005, 1.02, f'({"ab"[k]})', transform=a.transAxes, fontweight='bold')
save(fig, 'fig10_fusion_timeline')
