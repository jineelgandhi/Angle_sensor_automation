import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


class CurveFit:
    def __init__(self, csv_path: str):
        self.csv = pd.read_csv(csv_path)
        self.a_y_m = 0.0
        self.a_x_m = 0.0
        self.o_x_m = 0.0
        self.o_y_m = 0.0
        self.phi_x_m = 0.0
        self.phi_y_m = 0.0
        self.f_x_m = 0.0
        self.f_y_m = 0.0
        self.theta_rad = []

    def calculate_curve_fit(self, plot_graph: bool = False):

        # 1. Calculate Differential Signals
        X_COS_DIFF = self.csv['COS_P'] - self.csv['COS_N']
        Y_SIN_DIFF = self.csv['SIN_P'] - self.csv['SIN_N']

        # 2. Encoder dgree angle calculation
        cumulative_angle = np.cumsum(self.csv['encoder']) / 40000 * 360  # 40000 = 1 revolution
        # Convert to radians because sine and cosine models prefer radians
        self.theta_rad = np.deg2rad(cumulative_angle)

        # 3. Initial Guesses
        initial_guess_sin = [np.std(Y_SIN_DIFF), 1/(2*np.pi), 0, np.mean(Y_SIN_DIFF)]
        initial_guess_cos = [np.std(X_COS_DIFF), 1/(2*np.pi), 0, np.mean(X_COS_DIFF)]

        def sine_model(theta, A, freq, phase, offset):
            return A * np.sin(2 * np.pi * freq * (theta + phase)) + offset

        def cosine_model(theta, A, freq, phase, offset):
            return A * np.cos(2 * np.pi * freq * (theta + phase)) + offset

        # 4. Curve Fit SIN Signal
        params_sin, _ = curve_fit(sine_model, self.theta_rad, Y_SIN_DIFF, p0=initial_guess_sin)
        self.a_y_m, self.f_y_m, phase_y, self.o_y_m = params_sin

        # 5. Curve Fit COS Signal
        params_cos, _ = curve_fit(cosine_model, self.theta_rad, X_COS_DIFF, p0=initial_guess_cos)
        self.a_x_m, self.f_x_m, phase_x, self.o_x_m = params_cos

        # Convert phases from radians to degrees
        self.phi_y_m = np.rad2deg(phase_y)
        self.phi_x_m = np.rad2deg(phase_x)

        if plot_graph:
            plt.figure(figsize=(14, 6))
            plt.subplot(2, 1, 1)
            plt.plot(np.rad2deg(self.theta_rad), Y_SIN_DIFF, label='Raw SIN', alpha=0.7)
            plt.plot(np.rad2deg(self.theta_rad), sine_model(
                self.theta_rad, *params_sin), label='Fitted SIN', linestyle='--')
            plt.xlabel('Angle (degrees)')
            plt.ylabel('SIN_P - SIN_N')
            plt.title('SIN Differential Signal and Fit')
            plt.legend()
            plt.subplot(2, 1, 2)
            plt.plot(np.rad2deg(self.theta_rad), X_COS_DIFF, label='Raw COS', alpha=0.7)
            plt.plot(np.rad2deg(self.theta_rad), cosine_model(
                self.theta_rad, *params_cos), label='Fitted COS', linestyle='--')
            plt.xlabel('Angle (degrees)')
            plt.ylabel('COS_P - COS_N')
            plt.title('COS Differential Signal and Fit')
            plt.legend()
            plt.tight_layout()
            plt.show()

    def print_calibration_values(self):
        print(f"o_x_m = {self.o_x_m},")
        print(f"o_y_m = {self.o_y_m},")
        print(f"a_x_m = {self.a_x_m},")
        print(f"a_y_m = {self.a_y_m},")
        print(f"phi_x_m = {self.phi_x_m},")
        print(f"phi_y_m = {self.phi_y_m}")


if __name__ == "__main__":
    csv_path = "Book1.csv"
    curve_fitting = CurveFit(csv_path=csv_path)
    curve_fitting.calculate_curve_fit(plot_graph=True)
    curve_fitting.print_calibration_values()
