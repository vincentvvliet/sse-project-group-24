import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import shapiro, ttest_ind, mannwhitneyu
import glob
import os
import re
from pathlib import Path


def cohen_d(x, y):
    """Compute Cohen's d for two independent samples."""
    return (np.mean(x) - np.mean(y)) / np.sqrt(
        (np.std(x, ddof=1) ** 2 + np.std(y, ddof=1) ** 2) / 2
    )

def perform_stat_tests(energy_311, energy_314, alpha=0.05):
    """Runs normality checks, picks an appropriate test, prints results & effect sizes."""
    # Normality test
    shapiro_311 = shapiro(energy_311)
    shapiro_314 = shapiro(energy_314)
    print(f"Shapiro-Wilk for Python 3.11: W={shapiro_311.statistic:.3f}, p={shapiro_311.pvalue:.4f}")
    print(f"Shapiro-Wilk for Python 3.14: W={shapiro_314.statistic:.3f}, p={shapiro_314.pvalue:.4f}")

    # Decide test based on normality
    if shapiro_311.pvalue > alpha and shapiro_314.pvalue > alpha:
        print("Both samples appear normally distributed; using Welch's t-test.")
        stat, p_value = ttest_ind(energy_311, energy_314, equal_var=False)
        test_used = "Welch's t-test"
    else:
        print("At least one sample not normal; using Mann-Whitney U test.")
        stat, p_value = mannwhitneyu(energy_311, energy_314, alternative='two-sided')
        test_used = "Mann-Whitney U test"

    print(f"{test_used} statistic={stat:.3f}, p-value={p_value:.4f}")

    if p_value < alpha:
        print("Significant difference detected between Python 3.11 and 3.14.")
    else:
        print("No significant difference detected between Python 3.11 and 3.14.")

    
    median_311 = np.median(energy_311)
    median_314 = np.median(energy_314)
    print(f"Median Python 3.11: {median_311:.2f}")
    print(f"Median Python 3.14: {median_314:.2f}")
    print(f"Median difference: {median_314 - median_311:.2f} J")

    if test_used == "Mann-Whitney U test":
        N1, N2 = len(energy_311), len(energy_314)
        percentage_pairs = stat / (N1 * N2)
        print(f"Percentage of pairs supporting difference: {percentage_pairs*100:.2f}%")
        print(f"Common Language Effect Size (CLES): {percentage_pairs:.3f}")

    # If t-test, we can compute Cohen's d
    if test_used == "Welch's t-test":
        d = cohen_d(energy_311, energy_314)
        print(f"Cohen's d = {d:.3f}")

# Function to extract execution time from summary text file
def get_execution_time(summary_file):
    try:
        with open(summary_file, "r") as file:
            content = file.read()
        match = re.search(r"Energy consumption in joules: .* for (\d+\.\d+) sec of execution", content)
        if match:
            return float(match.group(1))
        else:
            raise ValueError(f"Execution time not found in {summary_file}")
    except Exception as e:
        print(f"Error reading {summary_file}: {e}")
        return None

# Function to extract system power and compute energy consumption
def get_energy_consumption(csv_file, summary_file):
    df = pd.read_csv(csv_file)
    if "SYSTEM_POWER (Watts)" not in df.columns:
        raise ValueError(f"Missing 'SYSTEM_POWER (Watts)' column in {csv_file}")
    
    avg_power = df["SYSTEM_POWER (Watts)"].mean()
    execution_time = get_execution_time(summary_file)
    if execution_time is None:
        return None
    return avg_power * execution_time

# Load experiment results based on mode
def load_experiment_results(folder_path, mode):
    csv_files = glob.glob(os.path.join(folder_path, f"*_python*_{mode}_*.csv"))
    if not csv_files:
        print(f"Warning: No CSV files found for {mode} in {folder_path}")
        return np.array([])
    
    energy_values = []
    for csv_file in csv_files:
        base_name = os.path.basename(csv_file)
        # Extract the specific part needed for the summary file
        csv_name_pattern = re.search(r"(matrix_benchmark\.py_python3\.\d+_\w+_run\d+)\.csv", base_name)
        
        if csv_name_pattern:
            summary_filename = f"energybridge_output_{csv_name_pattern.group(1)}.txt"
            summary_file = os.path.join(folder_path, summary_filename)
            
            if os.path.exists(summary_file):
                energy = get_energy_consumption(csv_file, summary_file)
                if energy is not None:
                    energy_values.append(energy)
                else:
                    print(f"Warning: Energy computation failed for {csv_file}")
            else:
                print(f"Warning: Summary file missing for {csv_file}. Expected: {summary_file}")
        else:
            print(f"Warning: Could not parse CSV filename pattern: {base_name}")
    
    if not energy_values:
        print(f"Warning: No valid energy values computed for {mode} in {folder_path}")
    return np.array(energy_values)

def remove_outliers(data, z_threshold=3):
    if len(data) < 3:  
        return data
    z_scores = np.abs((data - np.mean(data)) / np.std(data))
    return data[z_scores < z_threshold]

def plot_violin_comparison(energy_311, energy_314, title, filename):
    """Violin + box plot."""
    plt.figure(figsize=(10, 6))
    sns.violinplot(data=[energy_311, energy_314], inner="box", palette=["blue", "orange"])
    plt.xticks([0, 1], ["Python 3.11", "Python 3.14"])
    plt.ylabel("Energy Consumption (J)")
    plt.title(title)
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    
    # Print quick summary in console
    print(f"\n{title}")
    print(f"Python 3.11: {len(energy_311)} measurements")
    print(f"  Mean: {np.mean(energy_311):.2f}J, Median: {np.median(energy_311):.2f}J")
    print(f"  Min: {np.min(energy_311):.2f}J, Max: {np.max(energy_311):.2f}J")
    
    print(f"Python 3.14: {len(energy_314)} measurements")
    print(f"  Mean: {np.mean(energy_314):.2f}J, Median: {np.median(energy_314):.2f}J")
    print(f"  Min: {np.min(energy_314):.2f}J, Max: {np.max(energy_314):.2f}J")
    
    mean_diff_percent = (
        (np.mean(energy_314) - np.mean(energy_311))
        / np.mean(energy_311)
        * 100
    )
    median_diff_percent = (
        (np.median(energy_314) - np.median(energy_311))
        / np.median(energy_311)
        * 100
    )
    print(f"Difference: Mean: {mean_diff_percent:.2f}%, Median: {median_diff_percent:.2f}%")
    plt.show()

def plot_mean_bar_comparison(energy_311, energy_314, title, filename):
    """Creates a bar chart showing mean + SEM for each Python version."""
    mean_311 = np.mean(energy_311)
    mean_314 = np.mean(energy_314)
    sem_311 = np.std(energy_311, ddof=1) / np.sqrt(len(energy_311))
    sem_314 = np.std(energy_314, ddof=1) / np.sqrt(len(energy_314))
    
    plt.figure(figsize=(10, 6))
    plt.bar(["Python 3.11", "Python 3.14"],
            [mean_311, mean_314],
            yerr=[sem_311, sem_314],
            capsize=5, 
            color=["blue", "orange"],
            alpha=0.8)
    plt.ylabel("Mean Energy Consumption (J)")
    plt.title(title)
    plt.grid(True, axis='y')
    plt.tight_layout()
    plt.savefig(filename, dpi=300)
    plt.show()
    
   
    print(f"\n{title}")
    print(f"Python 3.11: mean={mean_311:.2f} J, SEM={sem_311:.2f}")
    print(f"Python 3.14: mean={mean_314:.2f} J, SEM={sem_314:.2f}")

def process_results(python_311_folder, python_314_folder):
    """Main routine: load data, remove outliers, produce violin + bar plots + stats."""
    print(f"Python 3.11 folder: {python_311_folder}")
    print(f"Python 3.14 folder: {python_314_folder}")
    print(f"Python 3.11 folder exists: {os.path.exists(python_311_folder)}")
    print(f"Python 3.14 folder exists: {os.path.exists(python_314_folder)}")
    
    for mode in ["normal", "optimized"]:
        print(f"\nProcessing {mode} mode...")
        energy_311 = load_experiment_results(python_311_folder, mode)
        energy_314 = load_experiment_results(python_314_folder, mode)
        
        print(f"Found {len(energy_311)} energy values for Python 3.11 ({mode})")
        print(f"Found {len(energy_314)} energy values for Python 3.14 ({mode})")
        
        energy_311 = remove_outliers(energy_311)
        energy_314 = remove_outliers(energy_314)
        
        print(f"After outlier removal: {len(energy_311)} for Python 3.11, {len(energy_314)} for Python 3.14")
        
        if len(energy_311) == 0 or len(energy_314) == 0:
            print(f"Skipping {mode} comparison due to insufficient data")
            continue
        
       
        violin_title = f"Energy Consumption: Python 3.11 ({mode}) vs Python 3.14 ({mode})"
        violin_filename = f"violin_energy_comparison_{mode}.png"
        plot_violin_comparison(energy_311, energy_314, violin_title, violin_filename)

       
        bar_title = f"Mean Energy Consumption Comparison (Python 3.11 {mode} vs Python 3.14 {mode})"
        bar_filename = f"mean_energy_comparison_{mode}.png"
        plot_mean_bar_comparison(energy_311, energy_314, bar_title, bar_filename)

     
        print("\nStatistical Analysis:")
        perform_stat_tests(energy_311, energy_314)


PROJECT_ROOT = Path(__file__).resolve().parent
output_dir = PROJECT_ROOT / "results"
os.makedirs(output_dir, exist_ok=True)

python311_dir = output_dir / "Python3.11"
python314_dir = output_dir / "Python3.14"

# Check if directories exist
if not os.path.exists(python311_dir):
    print(f"Warning: Directory {python311_dir} does not exist")
if not os.path.exists(python314_dir):
    print(f"Warning: Directory {python314_dir} does not exist")

process_results(python311_dir, python314_dir)
