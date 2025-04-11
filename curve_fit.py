import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# --- 1. Load Data ---
# Assume you have the data saved as 'anglesensor_readings.csv'
data = pd.read_csv('Book1.csv')

# --- 2. Calculate Differential Signals ---
X_COS_DIFF = data['COS_P'] - data['COS_N']
Y_SIN_DIFF = data['SIN_P'] - data['SIN_N']

# --- 3. Create Cumulative Angle Axis ---
# Cumulative sum of ENCODER steps, scaled to degrees (Encoder step per degree)
# Thesis assumes ENC counts correspond to fine angle steps, use cumulative
cumulative_angle = np.cumsum(data['encoder']) / 40000 * 360  # 40000 = 1 revolution

# Convert to radians because sine and cosine models prefer radians
theta_rad = np.deg2rad(cumulative_angle)

# --- 4. Define Fitting Functions ---


def sine_model(theta, A, freq, phase, offset):
    return A * np.sin(2 * np.pi * freq * (theta + phase)) + offset


def cosine_model(theta, A, freq, phase, offset):
    return A * np.cos(2 * np.pi * freq * (theta + phase)) + offset


# --- 5. Initial Guesses ---
initial_guess_sin = [np.std(Y_SIN_DIFF), 1/(2*np.pi), 0, np.mean(Y_SIN_DIFF)]
initial_guess_cos = [np.std(X_COS_DIFF), 1/(2*np.pi), 0, np.mean(X_COS_DIFF)]

# --- 6. Curve Fit SIN Signal ---
params_sin, _ = curve_fit(sine_model, theta_rad, Y_SIN_DIFF, p0=initial_guess_sin)
A_sin, freq_sin, phase_sin, offset_sin = params_sin

# --- 7. Curve Fit COS Signal ---
params_cos, _ = curve_fit(cosine_model, theta_rad, X_COS_DIFF, p0=initial_guess_cos)
A_cos, freq_cos, phase_cos, offset_cos = params_cos

# Convert phases from radians to degrees
phase_sin_deg = np.rad2deg(phase_sin)
phase_cos_deg = np.rad2deg(phase_cos)

# --- 8. Print Calibration Results ---
print("\nCalibration Results (following thesis exactly):")
print(
    f"SIN - Amplitude: {A_sin:.3f}, Frequency: {freq_sin:.6f}, Phase: {phase_sin_deg:.3f} deg, Offset: {offset_sin:.3f}")
print(
    f"COS - Amplitude: {A_cos:.3f}, Frequency: {freq_cos:.6f}, Phase: {phase_cos_deg:.3f} deg, Offset: {offset_cos:.3f}")

# --- 9. Optional: Plot Raw vs Fitted Curves ---
plt.figure(figsize=(14, 6))

plt.subplot(2, 1, 1)
plt.plot(np.rad2deg(theta_rad), Y_SIN_DIFF, label='Raw SIN', alpha=0.7)
plt.plot(np.rad2deg(theta_rad), sine_model(theta_rad, *params_sin), label='Fitted SIN', linestyle='--')
plt.xlabel('Angle (degrees)')
plt.ylabel('SIN_P - SIN_N')
plt.title('SIN Differential Signal and Fit')
plt.legend()

plt.subplot(2, 1, 2)
plt.plot(np.rad2deg(theta_rad), X_COS_DIFF, label='Raw COS', alpha=0.7)
plt.plot(np.rad2deg(theta_rad), cosine_model(theta_rad, *params_cos), label='Fitted COS', linestyle='--')
plt.xlabel('Angle (degrees)')
plt.ylabel('COS_P - COS_N')
plt.title('COS Differential Signal and Fit')
plt.legend()

plt.tight_layout()
plt.show()
