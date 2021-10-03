import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib

income_statistic_old = pd.read_csv("Finanzierungskonzept_alt.csv").set_index(['Einkommensart']).transpose()
income_statistic_new = pd.read_csv("Finanzierungskonzept_neu.csv").set_index(['Einkommensart']).transpose()

# define figure
fig, ax = plt.subplots(1, figsize=(10, 50))
# Set the tick labels font
for label in (ax.get_xticklabels() + ax.get_yticklabels()):
    label.set_fontname('Arial')
    label.set_fontsize(7)

colors = {'Netto': '#ff7f00', 'Sozialleistungen': '#b3cde3', 'Sozialversicherung': '#fbb4ae', 'Steuern': '#fed9a6',
          'Grundeinkommen': '#377eb8', 'Energiegeld': '#006600'}
N = len(income_statistic_old)
ind = np.arange(N)  # the x locations for the groups


# plot bars
bottom = len(income_statistic_old) * [0]
for idx, name in enumerate(income_statistic_old.columns):
    plt.bar(ind, income_statistic_old[name], bottom=bottom, color=colors[name], width=0.24, zorder=3)
    bottom = bottom + income_statistic_old[name]

width = 0.3      # the width of the bars
bottom = len(income_statistic_new) * [0]
for idx, name in enumerate(income_statistic_new.columns):
    extra_width = 0
    x_trans = 0
    skip_bottom = False
    if name == 'Energiegeld':
        x_trans = -0.06
        extra_width = -0.12
        skip_bottom = True
    if name == 'Steuern' or name == 'Sozialversicherung':
        x_trans = 0.06
        extra_width = -0.12
        if name == 'Steuern':
            skip_bottom = True
    plt.bar(ind+width+x_trans, income_statistic_new[name], bottom=bottom, color=colors[name], width=0.24+extra_width,
            zorder=3)
    if not skip_bottom:
        bottom = bottom + income_statistic_new[name]

names_of_values = list(np.repeat(income_statistic_old.columns, len(income_statistic_old.index)))
names_of_values += names_of_values
list_values = [income_statistic_old.to_numpy().transpose(), income_statistic_new.to_numpy().transpose()]
list_values = [item for sublist in list_values for item in sublist]
list_values = [str(item)+' €' for sublist in list_values for item in sublist]
for i, rect in enumerate(ax.patches):
    h = rect.get_height() / 2.
    w = rect.get_width() / 2.
    x, y = rect.get_xy()
    if h != 0:
        value = list_values[i]
        if names_of_values[i] == 'Energiegeld':
            x_trans = -0.03
        elif names_of_values[i] == 'Steuern' and i > 36 or names_of_values[i] == 'Sozialversicherung' and i > 36:
            x_trans = 0.08
        else:
            x_trans = 0
        ax.text(x+w+x_trans, y+h, value, horizontalalignment='center', verticalalignment='center', fontsize=6)

ax.set_xticks(ind + width / 2)
plt.xticks(ind + width / 2, income_statistic_old.index)
# title, legend, labels
plt.title('Einkommensverteilung [links: alt | rechts: neu] \n', loc='left')
plt.legend(income_statistic_new.columns, bbox_to_anchor=([0.75, 1, 0, 0]), ncol=3,
           frameon=False)
plt.xlabel('\n Einkommenstyp')

#plt.tight_layout()

# remove spines
ax.spines['right'].set_visible(False)
ax.spines['left'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.spines['bottom'].set_visible(False)
ax.grid(b=True, linestyle='-', zorder=0, axis='y')

fig.savefig('Einkommensverteilung_BarCharts.png')

