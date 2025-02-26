import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# 1) Load the data
df = pd.read_csv("energy_results.csv")

# Suppose your columns are:
# ['Python Version', 'Joules', 'Energy_Time', 'Script_ExecTime']
# Make sure 'Joules' and 'Energy_Time' columns are numeric
# If needed, convert them:
df["Joules"] = pd.to_numeric(df["Joules"], errors="coerce")
df["Energy_Time"] = pd.to_numeric(df["Energy_Time"], errors="coerce")
df["Script_ExecTime"] = pd.to_numeric(df["Script_ExecTime"], errors="coerce")

# 2) Basic boxplot for Joules
plt.figure(figsize=(6, 5))
sns.boxplot(x="Python Version", y="Joules", data=df)
plt.title("Energy Consumption (Joules) by Python Version")
plt.savefig("boxplot_joules.png")
plt.show()

# 3) Violin plot for Joules
plt.figure(figsize=(6, 5))
sns.violinplot(x="Python Version", y="Joules", data=df, inner="quartile")
plt.title("Energy Consumption Distribution (Joules)")
plt.savefig("violin_joules.png")
plt.show()

# 4) Boxplot for Script Execution Time (if you have it in CSV)
plt.figure(figsize=(6, 5))
sns.boxplot(x="Python Version", y="Script_ExecTime", data=df)
plt.title("Script Execution Time (seconds) by Python Version")
plt.savefig("boxplot_exec_time.png")
plt.show()
