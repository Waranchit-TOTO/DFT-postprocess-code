import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from matplotlib.lines import Line2D
import sys 
import re 

fig_name = '101D_fatbands.png'
title_name = '101D, fat-bands'

fermi = -5.599590

k_labels = [
            (0.000000, 'X'),
            (0.144983, r'$\Gamma$'),
            (0.261655, 'Y')]
x_max = 0.261655

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["Times New Roman"] + plt.rcParams["font.serif"]
plt.rcParams["font.weight"] = "bold"
plt.rcParams["mathtext.fontset"] = "stix"

axis_label_font = {
    'fontsize': 18,
    'fontweight': 'bold',
    'fontfamily': 'serif',
}

tick_label_font = {
    'fontsize': 18,
    'fontweight': 'bold',
    'fontfamily': 'serif',
}

def read_data(filename):
    with open(filename, 'r') as f :
        f.readline()
        tmp = f.readline()
        tmp = tmp.split()

        nband=int(tmp[-3])
        nspin=int(tmp[-2])
        nk=int(tmp[-1])

        print( f' read from {filename}/ nband, nspin, nk: {nband} {nspin} {nk}')

    data=np.loadtxt(filename)
    data=data.reshape(nband, nk, -1)
    return data


"""
def read_fermi(filename):
    temlate='siesta:         Fermi'
    with open(filename, 'r') as g :
        data=g.read()

    for match in re.finditer(temlate, data):
        ind_start=match.start()
        ind_end=ind_start+100
        text=data[ind_start:ind_end].split('\n')[0].split()
        fermi=float(text[-1])
        print(f'fermi energy is read from {filename} as {fermi}')

    return fermi
"""



#fermi=read_fermi('../RUN_device.out')


#files_to_plot=sys.argv[1:]

files_to_plot=['O_2p.dat' , 'O_2s.dat', 'Sn_5s.dat', 'Sn_5p.dat', 'Sn_4d.dat']

#files_to_plot=['O_2s.dat', 'Sn_4d.dat' ]

#cmaps = ['Blues','magma', 'Reds', 'viridis', 'cividis', 'plasma', 'inferno']

color = ['Reds', 'Blues', 'Greens', 'Purples', 'Oranges']
plot_mode = 'combined'  # 'separate'

"""if not files_to_plot:
    raise SystemExit('Usage: python plot-fatbands.py <orbital_1.dat> <orbital_2.dat> ...')
"""

n_orb = len(files_to_plot)

def make_axes(plot_mode, n_orb):
    if plot_mode == 'combined':
        fig, ax = plt.subplots(1, 1, figsize=(4.2, 8.0))
        return fig, [ax]

    fig, axes = plt.subplots(
        1,
        n_orb,
        figsize=(3.6 * n_orb, 7.5),
        sharey=True,
        squeeze=False,
    )
    return fig, list(axes[0])

tmp = []
def plot_orbital(ax, data, cmap_name, draw_band_lines=True):
    nband, nk, _ = data.shape
    weight_max=np.max(np.abs(data[:, :, 2]))
    print(f'weight max : {weight_max}')
    tmp.append(weight_max)

    for iband in range(nband) :
        kaxis=data[iband, :, 0]
        eigen=data[iband, :, 1] - fermi
        weight=np.abs(data[iband, :, 2])/weight_max

        if draw_band_lines:
            ax.plot(
                kaxis,
                eigen,
                c='black',
                lw=0.2,
                zorder=1,
            )

        ax.scatter(
            kaxis,
            eigen,
            c=weight,
            alpha= weight/(np.max(tmp)),
            s=180*np.sqrt(weight), #1*100*weight**2, 
            vmin=0,
            vmax= 0.6, #1, #0.6,
            cmap=cmap_name,
            edgecolors='black',
            linewidths=0.15,
            zorder=3,
        )


if plot_mode not in {'separate', 'combined'}:
    raise SystemExit("plot_mode must be 'separate' or 'combined'")

fig, axes = make_axes(plot_mode, n_orb)
legend_handles = []
legend_fontsize = 16
legend_markersize = 14

for j, filename in enumerate(files_to_plot):
    data=read_data(filename)
    orbital_name = Path(filename).stem
    legend_label = orbital_name.replace('_', '-')
    cmap_name = color[j % len(color)]

    if plot_mode == 'combined':
        ax = axes[0]
        plot_orbital(ax, data, cmap_name, draw_band_lines=(j == 0))
        legend_handles.append(
            Line2D(
                [0],
                [0],
                marker='o',
                linestyle='',
                markersize=legend_markersize,
                markerfacecolor=plt.get_cmap(cmap_name)(0.75),
                markeredgecolor='black',
                markeredgewidth=0.6,
                label=legend_label,
                
            )
        )
    else:
        ax = axes[j]
        plot_orbital(ax, data, cmap_name)
        ax.set_title(orbital_name, fontsize=14, fontweight='bold')

# ---------------------------- formatting 

k_values = [label[0] for label in k_labels]
k_names = [label[1] for label in k_labels]
for ax in axes:
    for k_val in k_values:
        ax.axvline(x=k_val, color='black', linestyle='-', linewidth=1.2, alpha=1)
    ax.set_xticks(k_values)
    ax.set_xticklabels(k_names, **tick_label_font)

    ax.axhline(y=0, color='r', linestyle='--', linewidth=1)
    ax.set_ylim(-2,2)
    #ax.set_ylim(-2.0,2.0)
    ax.set_xlim(0,x_max)
    ax.tick_params(axis='y', labelsize=tick_label_font['fontsize'])
    for label in ax.get_yticklabels():
        label.set_fontweight(tick_label_font['fontweight'])
        label.set_fontfamily(tick_label_font['fontfamily'])
    ax.grid(True, alpha=0.3, axis='y')

#axes[0].set_ylabel('Energy - $E_F$ (eV)', **axis_label_font) # using ** to unpack the dictionary for font properties

if plot_mode == 'combined':
    axes[0].set_title(title_name, fontsize=20, fontweight='bold')
    axes[0].legend(handles=legend_handles, loc='upper right', fontsize=legend_fontsize, frameon=True)

plt.tight_layout()
plt.savefig(fig_name, dpi=300, bbox_inches='tight')

plt.show()













