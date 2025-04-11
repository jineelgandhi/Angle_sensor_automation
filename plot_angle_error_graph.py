import pandas as pd
import matplotlib.pyplot as plt


def plot_angle_error_vs_theta(path, cycle_number):

    df = pd.read_csv(path)
    cycle_to_plot = cycle_number

    # Filter for selected cycle
    df_cycle = df[df['cycle'] == cycle_to_plot]

    # Plotting angle error vs theta for selected cycle
    plt.figure(figsize=(12, 7))
    plt.plot(df_cycle['theta'], df_cycle['angle_error'], marker='o', linestyle='-')
    plt.title(f'Angle Error vs Theta (Cycle {cycle_to_plot})')
    plt.xlabel('Theta (Degrees)')
    plt.ylabel('Angle Error (Degrees)')
    plt.grid(True)
    plt.show()


if __name__ == "__main__":
    plot_angle_error_vs_theta("measurement_log_20250408_125915_new.csv", 1)
