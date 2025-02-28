import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro, ttest_ind, zscore, mannwhitneyu
import glob
from pathlib import Path
import os

# Function to extract energy consumption
def get_energy_consumption(file_path):
    df = pd.read_csv(file_path)
    
    # Ensure the required column exists
    if "PACKAGE_ENERGY (J)" not in df.columns:
        raise ValueError(f"Missing 'package energy (J)' column in {file_path}")
    
    # Compute energy consumption as the difference between first and last row
    energy_consumption = df["PACKAGE_ENERGY (J)"].iloc[-1] - df["PACKAGE_ENERGY (J)"].iloc[0]
    return energy_consumption

# Load all runs for each Python version
def load_experiment_results(folder_path):
    files = glob.glob(os.path.join(folder_path, "*.csv"))
    energy_values = [get_energy_consumption(file) for file in files]
    return np.array(energy_values)

def remove_outliers(data):
    z_scores = np.abs(zscore(data))
    filtered_data = data[z_scores < 3]  # Keep values within 3 standard deviations
    return filtered_data

def cohen_d(x, y):
    return (np.mean(x) - np.mean(y)) / np.sqrt((np.std(x, ddof=1) ** 2 + np.std(y, ddof=1) ** 2) / 2)

def plot_median_difference(energy_311, energy_314):
    # Compute medians and interquartile ranges (IQR)
    median_311 = np.median(energy_311)
    median_314 = np.median(energy_314)
    
    iqr_311 = np.percentile(energy_311, 75) - np.percentile(energy_311, 25)
    iqr_314 = np.percentile(energy_314, 75) - np.percentile(energy_314, 25)

    print(f'Python 3.11 median: {median_311}')
    print(f'Python 3.14 median: {median_314}')

    median_diff = median_314 - median_311
    percent_change = (median_diff / median_311) * 100

    print(f"Median Difference: {median_diff:.2f} J")
    print(f"Percent Change: {percent_change:.2f}%")

    # Create the bar plot with IQR as error bars
    plt.figure(figsize=(10, 6))
    bars = plt.bar(
        ["Python 3.11", "Python 3.14"], 
        [median_311, median_314], 
        yerr=[iqr_311 / 2, iqr_314 / 2],  # Half of IQR as error bars
        capsize=5, 
        color=["blue", "orange"]
    )

    # Add labels and title
    plt.ylabel("Median Energy Consumption (J)")
    plt.title("Median Energy Consumption Comparison (Python 3.11 vs 3.14)")

    # Show grid for better readability
    plt.grid(True)

    # Tight layout for spacing
    plt.tight_layout()

    # Save and show the plot
    plt.savefig("median_energy_comparison.png", dpi=300)
    plt.show()

def plot_mean_difference(energy_311, energy_314):
    # Compute means and standard deviations
    mean_311 = np.mean(energy_311)
    mean_314 = np.mean(energy_314)
    std_311 = np.std(energy_311)
    std_314 = np.std(energy_314)

    print(f'Python 3.11 mean: {mean_311}')
    print(f'Python 3.14 mean: {mean_314}')

    mean_diff = mean_314 - mean_311

    # Compute percentage change (relative to Python 3.11)
    percent_change = (mean_diff / mean_311) * 100
    print(f"Mean Difference: {mean_diff:.2f} J")
    print(f"Percent Change: {percent_change:.2f}%")

    # Compute the standard error of the mean (SEM)
    sem_311 = std_311 / np.sqrt(len(energy_311))
    sem_314 = std_314 / np.sqrt(len(energy_314))

    print(f'Python 3.11 SEM: {sem_311}')
    print(f'Python 3.14 SEM: {sem_314}')
    # Create the bar plot
    plt.figure(figsize=(10, 6))  # Increase figure size to avoid crowding
    bars = plt.bar(
        ["Python 3.11", "Python 3.14"], 
        [mean_311, mean_314], 
        yerr=[sem_311, sem_314], 
        capsize=5, 
        color=["blue", "orange"]
    )

    # Add labels and title
    plt.ylabel("Mean Energy Consumption (J)")
    plt.title("Mean Energy Consumption Comparison (Python 3.11 vs 3.14)")

    # Annotate the bars with the exact values, with an offset to avoid overlap with error bars
    for bar in bars:
        yval = bar.get_height()
        print(yval)
        # Add a vertical offset (adjust this as needed) to move the text above the error bars
        #plt.text(bar.get_x() + bar.get_width() / 2, yval + 0.05, f'{yval:.2f}', ha='center', va='bottom', fontsize=12)

    # Adjust y-axis limits to avoid zoomed-in look
    plt.ylim(min(mean_311, mean_314) - 1, max(mean_311, mean_314) + 1)  # Adjust this range as needed

    # Show grid for better clarity
    plt.grid(True)

    # Tight layout for proper spacing
    plt.tight_layout()

    # Save and show the plot
    plt.savefig("mean_energy_comparison.png", dpi=300)
    plt.show()

def process_results(python_311_folder, python_314_folder):
    # Load results
    energy_311 = load_experiment_results(python_311_folder)
    energy_314 = load_experiment_results(python_314_folder)

    # Remove outliers
    energy_311 = remove_outliers(energy_311)
    energy_314 = remove_outliers(energy_314)

    plot_median_difference(energy_311, energy_314)

    # Normality Test (Shapiro-Wilk)
    shapiro_311 = shapiro(energy_311)
    shapiro_314 = shapiro(energy_314)

    print(f"Shapiro-Wilk test for Python 3.11: W={shapiro_311.statistic}, p={shapiro_311.pvalue}")
    print(f"Shapiro-Wilk test for Python 3.14: W={shapiro_314.statistic}, p={shapiro_314.pvalue}")

    # Visualization (Violin + Box Plot)
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=[energy_311, energy_314], inner="box", palette=["blue", "orange"])
    plt.xticks([0, 1], ["Python 3.11", "Python 3.14"])
    plt.ylabel("Energy Consumption (J)")
    plt.title("Energy Consumption Comparison (Python 3.11 vs 3.14)")
    plt.grid()

    # Save or Show the plot
    plt.savefig("energy_comparison.png", dpi=300)
    plt.show()

    # **Statistical Analysis**
    if shapiro_311.pvalue > 0.05 and shapiro_314.pvalue > 0.05:
        # If both are normal, use Welch’s t-test
        _, p_value = ttest_ind(energy_311, energy_314, equal_var=False, alternative='two-sided')
        test_used = "Welch's t-test"
    else:
        # If at least one is non-normal, use Mann-Whitney U test
        U1, p_value = mannwhitneyu(energy_311, energy_314, alternative='two-sided')
        test_used = "Mann-Whitney U test"

    print(f"\n{test_used} results: p-value = {p_value}")

    # Interpretation
    alpha = 0.05
    if p_value < alpha:
        print("Significant difference detected between Python 3.11 and 3.14 energy consumption.")
    else:
        print("No significant difference detected between Python 3.11 and 3.14 energy consumption.")

    print(f'Median Python 3.11: {np.median(energy_311)}')
    print(f'Median Python 3.14: {np.median(energy_314)}')
    # **Effect Size Calculations**
    median_diff = np.median(energy_311) - np.median(energy_314)
    print(f"Median Difference: {median_diff:.2f} J")

    # **Percentage of pairs supporting a conclusion**
    N1, N2 = len(energy_311), len(energy_314)
    percentage_pairs = U1 / (N1 * N2)
    print(f"Percentage of Pairs Supporting Conclusion: {percentage_pairs * 100:.2f}%")

    # **Common Language Effect Size (CLES)**
    CLES = percentage_pairs  # Equivalent to ΔM
    print(f"Common Language Effect Size (CLES): {CLES:.4f}")

    # **Cohen's d Effect Size (if normal)**
    if test_used == "Welch's t-test":
        d = cohen_d(energy_311, energy_314)
        print(f"Cohen's d effect size: {d:.4f}")

if __name__ == "__main__":
    PROJECT_ROOT = Path(__file__).resolve().parent
    output_dir = PROJECT_ROOT / "energy_results"
    os.makedirs(output_dir, exist_ok=True)

    # Define subdirectories for Python versions
    python311_dir = output_dir / "python3.11_runs"
    python314_dir = output_dir / "python3.14_runs"
    process_results(python311_dir, python314_dir)