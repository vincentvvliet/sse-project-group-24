import matplotlib.pyplot as plt
import pandas as pd
import os
import seaborn as sns
import numpy as np
import re


# The code in this file was taken from the EnergyDebug repository by @enriquebarba97,
# Slight modifications were made to fit this to our use case.
# For more information, please see the repository at: https://github.com/enriquebarba97/EnergyDebug
class ImageData:

    def __init__(self, name) -> None:
        self.name = name
        self.run_dfs = {}
        self.norm_dfs = {}


def energy_data(workload, images, measurement="CPU_POWER (Watts)", toplot=None, indices=None, xlim=None, ylim=None,
                hist_data=None):
    """
    Plot power usage and recover aggregated data
    With measurement, you can choose between CPU_POWER (Watts) and CPU_USAGE_0
    """
    dataframes = {}

    fig, ax = plt.subplots(figsize=[20, 12])

    if xlim is not None:
        ax.set_xlim(xlim[0], xlim[1])

    if ylim is not None:
        ax.set_ylim(ylim[0], ylim[1])

    data = {"Image": [], "Time (s)": [], "Energy (J)": []}

    for image in images:
        image_name = image.split("@")[0]
        # if image_name not in ["light", "node", "centos","debian"]:
        if toplot is None or len(toplot) == 0 or image_name in toplot:
            # if image_name in ["ubuntu", "ubuntupack", "alpinepack", "alpinemusl", "alpineglibc", "alpinejem"]:
            dataframes[image_name] = ImageData(image_name)
            image_path = os.path.join(data_path, image)
            files = next(os.walk(image_path))[2]
            files = [f for f in files if f.endswith(".tsv")]
            dfs = {file.split(".")[0]: pd.read_csv(os.path.join(image_path, file),
                                                   usecols=["Delta", "Time", "CORE0_ENERGY (J)", "USED_MEMORY",
                                                            "CPU_USAGE_0"]) for file in files}
            dataframes[image_name].run_dfs = dfs

            all_data = []
            for run in dfs:
                df = dfs[run]

                key = "PACAKGE_ENERGY (W)"
                if "CPU_ENERGY (J)" in df.columns:
                    key = "CPU_ENERGY (J)"
                if "CORE0_ENERGY (J)" in df.columns:
                    key = "CORE0_ENERGY (J)"
                if "PACKAGE_ENERGY (J)" in df.columns:
                    key = "PACKAGE_ENERGY (J)"
                if "SYSTEM_POWER (Watts)" in df.columns:
                    key = "SYSTEM_POWER (Watts)"

                # Collect total energy for violin plots
                if key != "CPU_POWER (Watts)" and key != "SYSTEM_POWER (Watts)":
                    df["Point"] = np.arange(df.shape[0])
                    data["Image"].append(image_name)
                    data["Time (s)"].append((df["Time"].iloc[-1] - df["Time"].iloc[0]) / 1000)
                    data["Energy (J)"].append(df[key].iloc[-1] - df[key].iloc[0])

                # Compute power and plot
                energy = df[key].copy().to_list()
                cpu_data = df["CPU_USAGE_0"].copy().to_list()
                memory_data = df["USED_MEMORY"].copy().to_list()

                current_data = []

                if key != "CPU_POWER (Watts)" and key != "SYSTEM_POWER (Watts)":
                    df[key + "_original"] = df[key].copy()
                    for i in range(0, len(energy)):
                        if i in df[key + "_original"] and i - 1 in df[key + "_original"]:
                            # diff with previous value and convert to watts
                            energy[i] = (energy[i] - df[key + "_original"][i - 1]) * (1000 / df["Delta"][i])
                        else:
                            energy[i] = 0
                    # data = data[1:-1]
                    for i in range(0, len(energy)):
                        current_data.append({"Time": i, "CPU_POWER (Watts)": energy[i], "CPU_USAGE_0": cpu_data[i],
                                             "USED_MEMORY": memory_data[i]})
                        all_data.append({"Time": i, "CPU_POWER (Watts)": energy[i], "CPU_USAGE_0": cpu_data[i],
                                         "USED_MEMORY": memory_data[i]})

                dataframes[image_name].norm_dfs[run] = pd.DataFrame(current_data)

            all_data = pd.DataFrame(all_data)
            dataframes[image_name].norm_dfs["median"] = all_data.groupby("Time").median().reset_index()

            plot = sns.lineplot(all_data, x="Time", y="CPU_POWER (Watts)", estimator=np.median,
                                errorbar=lambda x: (np.quantile(x, 0.25), np.quantile(x, 0.75)), ax=ax, legend=True,
                                label=image_name)
            # plot = sns.lineplot(all_data, x="Time", y="CPU_POWER (Watts)", estimator=np.median, ax=ax, errorbar=None, legend=True, label=image_name)

            if indices is not None:
                for index in indices:
                    ax.axvline(x=index, color='r', linestyle='--')

            ax.set_xlabel("Time (ms)", size=26)
            ax.set_ylabel("CPU Power (W)", size=26)

            # Change legend font size
            plt.setp(ax.get_legend().get_texts(), fontsize='24')

            plot.set_title(workload, size=28)

    if hist_data is not None:
        ax2 = ax.twinx()

        sns.histplot(data=hist_data, x="Time", hue="Function", weights="Duration", multiple="dodge", bins=indices,
                     ax=ax2)

        ax2.set_ylabel("Function runtime (ns)", size=26)

        ax.yaxis.get_offset_text().set_fontsize(22)

        # Change legend font size
        plt.setp(ax2.get_legend().get_title(), fontsize='24')
        plt.setp(ax2.get_legend().get_texts(), fontsize='24')

    # Set axes numbers size
    plt.xticks(fontsize=22)
    plt.yticks(fontsize=22)
    plt.show()
    return dataframes, pd.DataFrame(data)


workload = "Energy consumption"
data_path = "data/result.csv"
dataframes, aggregate = energy_data(workload, images)
