import os
import pickle
import pandas as pd
from timeit import default_timer as timer
import sys
from pathlib import Path
import numpy as np
from matplotlib.ticker import AutoMinorLocator
from matplotlib.markers import MarkerStyle
import matplotlib.patches as mpatches
from functions_and_settings import pathlist, scantree
from scripts.custom_functions.general import path_join
import decimal
from settings_plot import *

prefix = "24"
data = {}
for path in pathlist:
    for entry in scantree(sys.argv[1] if len(sys.argv) > 1 else path):
        if entry.name.endswith("KGE_test-results.pkl") and entry.is_file():
            # print(entry.name, entry.path)
            if "lr_improve" not in entry.path:
                with open(entry.path, "rb") as f:
                    kge_list = pickle.load(f)
                    # data[entry.path] = kge_list
                    if len(kge_list) != 35:
                        print(len(kge_list))
                        print(entry.path)
                    else:
                        # if "(25)" in entry.path:
                        data[entry.path] = kge_list

# print(data)
df = pd.DataFrame(data)

means = df.mean(axis=0)
means = pd.DataFrame(means, columns=["mean"]).reset_index().rename(columns={"index": 'path'})
# means["modelBS"] = means.path.str.split("/").str[-6] + " - " + means.path.str.split("/").str[-3]
means["BS"] = means.path.str.split("/").str[-3].str.split().str[-1].astype(int)
means["model"] = means.path.str.split("/").str[-6]
means["epochs"] = means.path.str.split("/").str[-4].str.split().str[-1].astype(int)
means = means.replace({"model": {"CNN_Deep +ESF": "CNN +ESF", "CNN_Deep -SF": "CNN -SF"}})

means["modelBS"] = means.model + " BS=" + means.BS.astype(str)
means = means.query("BS==2048 | BS == 256")
means = means.dropna().reset_index().copy()
# print(means.query("epochs==88").to_string())

# filter df by unique model/batch size combinations with this line
means = means.sort_values('mean', ascending=False).drop_duplicates(["modelBS"])
pickle.dump(means, open(path_join([Path.cwd().parent.parent, "df_best_runs.pkl"]), "wb"))

print(means.to_string())

df = means.copy()

##########################
# prepare df for seaborn #
##########################

res_dict = {}
for row in df.itertuples():
    bs = row.BS
    res_file = os.path.join(Path(row.path).parent, "KGE_test-results.pkl")
    if os.path.isfile(os.path.abspath(res_file)):
        with open(res_file, "rb") as f:
            kge_list = pickle.load(f)
            res_dict[row.modelBS] = sorted(kge_list)

df = pd.DataFrame(res_dict)

# remove new tested model
drop_cols = []
for col in df.columns:
    if col.startswith("CNN_LSTM"):
        drop_cols.append(col)

df = df.drop(drop_cols, axis=1)

df["count"] = df.index + 1
df_melt = pd.melt(df, id_vars="count", value_vars=df.columns)

df_melt["features"] = np.where(df_melt.variable.str.contains("ESF"), "With Static Features", "Without Static Features")
df_melt.variable = df_melt.variable.str.replace('\+ESF', '', regex=True)
df_melt.variable = df_melt.variable.str.replace('\-SF', '', regex=True)

#################
# Plotting Part #
#################

# set line break for x ticks

df_melt["variable"] = df_melt.variable.str.replace("  ", "\n", regex=False)
fig = plt.figure(figsize=(20, 8))
ax = sns.violinplot(data=df_melt, x="variable", y="value", hue="features",
                    hue_order=["With Static Features", "Without Static Features"],
                    cut=0, inner="quartile", split=True)


means1 = df_melt[df_melt.features == "With Static Features"].groupby('variable', sort=False)['value'].mean()
means2 = df_melt[df_melt.features == "Without Static Features"].groupby('variable', sort=False)['value'].mean()
means1 = pd.DataFrame(means1)
means2 = pd.DataFrame(means2)
means1["group"] = "With Static Features"
means2["group"] = "Without Static Features"

means = pd.concat([means1, means2])
means["name"] = means.index.str.replace(r"\n", " - ", regex=False)

plt.draw()  # create plot to access elements with the next line
xtick_loc = {v.get_text(): v.get_position()[0] for v in ax.get_xticklabels()}  # get coordinates of quartile lines
ytick_loc = {'CNN\nBS=256': [1.02, 0.99], 'LSTM\nBS=256': [0.985, 0.97],
             'CNN\nBS=2048': [0.98, 1.01], 'GRU\nBS=256': [0.99, 0.99],
             'GRU\nBS=2048': [0.99, 1.01], 'LSTM\nBS=2048': [1.01, 0.99]}

for idx, row in enumerate(means.itertuples()):
    x = xtick_loc[row.Index]
    if row.group == "With Static Features":
        y = row.value * ytick_loc[row.Index][0]
        if decimal.Decimal(str(round(row.value, 2))).as_tuple().exponent == -2:
            ax.text(x - 0.20, y, round(row.value, 2), size=15, weight='bold', color="white")
        else:
            ax.text(x - 0.15, y, round(row.value, 2), size=15, weight='bold', color="white")
    else:
        y = row.value * ytick_loc[row.Index][1]
        ax.text(x + 0.04, y, round(row.value, 2), size=15, weight='bold', color="white", )
        # path_effects=[pe.withStroke(linewidth=2, foreground="black")])

# plotting the means with a dot
sns.stripplot(data=means, x="variable", y="value", hue="group", s=12, legend=None, jitter=False,
              linewidth=.7, edgecolor="white", ax=ax)

# this part was for the case when 2 means of one violin are equal
# sns.stripplot(data=means.query("name == 'CNN - BS=256'"), x="variable", y="value", s=12, legend=None, jitter=False,
#               ax=ax, marker=MarkerStyle("o", fillstyle="left"))
# sns.stripplot(data=means.query("name == 'CNN - BS=256'"), x="variable", y="value", s=12, legend=None, jitter=False,
#               linewidth=.7, marker="o", fc="none",
#               edgecolor="white", ax=ax, )

ax.set(ylim=(0, 1.1))
# Show the minor grid as well. Style it in very light gray as a thin, dotted line.
ax.yaxis.set_minor_locator(AutoMinorLocator(2))  # number of subdivisions between major ticks
ax.grid(which='minor', color='#7E7B7B', linestyle=':', linewidth=.35)

# legend
handles, labels = ax.get_legend_handles_labels()
handles.append(mpatches.Patch(color='none', linestyle="none", label="test"))
ax.legend(handles=handles, labels=labels)
sns.move_legend(ax, "upper center", bbox_to_anchor=(.5, 1.013), ncol=2, shadow=False, title=None, frameon=True)


ax.set_ylabel("KGE", labelpad=20, weight="bold")
ax.set_xlabel("Model architecture - batch size", labelpad=20, weight="bold")
fig.tight_layout()

sns.despine(right=True, left=True)

fig.savefig(os.path.join("../../results/Modelcomp-Static.vs.NoStatic-Violinplot%s.pdf" % prefix), format="pdf",
            bbox_inches="tight")
plt.close(fig)

# plt.show()
