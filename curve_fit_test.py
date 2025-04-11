import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt

# --- 1. Load the Data ---
df = pd.read_csv('Book2.csv')
df.columns = df.columns.str.strip()

# Create differential signals
df['X_COS_DIFF'] = df['COS_P'] - df['COS_N']
df['Y_SIN_DIFF'] = df['SIN_P'] - df['SIN_N']

# Split into CW and CCW
cw = df.iloc[:65].reset_index(drop=True)
ccw = df.iloc[65:].reset_index(drop=True)

# --- 2. Define Fitting Functions (Frequency free near 360) ---


def fit_sin_variable(x, A, f, phi, O):
    return A * np.sin(np.deg2rad(f * (x + phi))) + O


def fit_cos_variable(x, A, f, phi, O):
    return A * np.cos(np.deg2rad(f * (x + phi))) + O

# --- 3. Fit the Data ---


def fit_signals_variable(x_data, y_data, fit_type='sin'):
    if fit_type == 'sin':
        popt, _ = curve_fit(fit_sin_variable, x_data, y_data,
                            p0=[8000, 1.0, 0, 0], bounds=([0, 0.998, -180, -500], [20000, 1.002, 180, 500]))
    else:
        popt, _ = curve_fit(fit_cos_variable, x_data, y_data,
                            p0=[8000, 1.0, 0, 0], bounds=([0, 0.998, -180, -500], [20000, 1.002, 180, 500]))
    return popt


# Prepare x data
x_cw = np.linspace(0, 360, 65)
x_ccw = np.linspace(0, 360, 65)

# --- 4. Perform Fitting ---
# CW
popt_cw_cos = fit_signals_variable(x_cw, cw['X_COS_DIFF'].values, fit_type='cos')
popt_cw_sin = fit_signals_variable(x_cw, cw['Y_SIN_DIFF'].values, fit_type='sin')

# CCW
popt_ccw_cos = fit_signals_variable(x_ccw, ccw['X_COS_DIFF'].values, fit_type='cos')
popt_ccw_sin = fit_signals_variable(x_ccw, ccw['Y_SIN_DIFF'].values, fit_type='sin')

# --- 5. Compute SSD ---


def compute_ssd(y_true, y_pred):
    return np.sum((y_true - y_pred) ** 2)

# --- 6. Print Fitting Results ---


# Collect parameters
results = {
    'X': [],  # COS signals
    'Y': []   # SIN signals
}

# Refit and Collect


def collect_fit_params(label, popt, x_data, y_data, fit_type='sin'):
    A, f, phi, O = popt
    if fit_type == 'sin':
        y_fit = fit_sin_variable(x_data, A, f, phi, O)
    else:
        y_fit = fit_cos_variable(x_data, A, f, phi, O)

    # After fitting: If COS signal and A > 0, flip amplitude
    if fit_type == 'cos' and A > 0:
        A = -A
        phi = (phi + 180) % 360
        if phi > 180:
            phi -= 360

    ssd = compute_ssd(y_data, y_fit)
    # Store results
    if fit_type == 'cos':
        results['X'].append((A, f * 360, phi, O))
    else:
        results['Y'].append((A, f * 360, phi, O))

    # Also print
    print(f"{label}:")
    print(f"  Amplitude (A) : {A:.6f}")
    print(f"  Frequency (f) : {f * 360:.6f} deg/cycle")
    print(f"  Phase (phi)   : {phi:.6f} deg")
    print(f"  Offset (O)    : {O:.6f}")
    print(f"  SSD           : {ssd:.6f}")
    print()


# Clear old print calls and replace them:
collect_fit_params("CW COS", popt_cw_cos, x_cw, cw['X_COS_DIFF'].values, fit_type='cos')
collect_fit_params("CW SIN", popt_cw_sin, x_cw, cw['Y_SIN_DIFF'].values, fit_type='sin')
collect_fit_params("CCW COS", popt_ccw_cos, x_ccw, ccw['X_COS_DIFF'].values, fit_type='cos')
collect_fit_params("CCW SIN", popt_ccw_sin, x_ccw, ccw['Y_SIN_DIFF'].values, fit_type='sin')

# Calculate mean values
A_X_M, f_X_M, phi_X_M, O_X_M = np.mean(results['X'], axis=0)
A_Y_M, f_Y_M, phi_Y_M, O_Y_M = np.mean(results['Y'], axis=0)

print("\n--- Mean Values ---")
print(f"O_X_M = {O_X_M:.6f}")
print(f"O_Y_M = {O_Y_M:.6f}")
print(f"A_X_M = {A_X_M:.6f}")
print(f"A_Y_M = {A_Y_M:.6f}")
print(f"ϕ_X_M = {phi_X_M:.6f}")
print(f"ϕ_Y_M = {phi_Y_M:.6f}")

# --- 7. Plot the Results ---
x_fit = np.linspace(0, 360, 500)

# CW
y_fit_cw_cos = fit_cos_variable(x_fit, *popt_cw_cos)
y_fit_cw_sin = fit_sin_variable(x_fit, *popt_cw_sin)

# CCW
y_fit_ccw_cos = fit_cos_variable(x_fit, *popt_ccw_cos)
y_fit_ccw_sin = fit_sin_variable(x_fit, *popt_ccw_sin)

# Plotting
plt.figure(figsize=(14, 8))

# CW plots
plt.subplot(2, 2, 1)
plt.title('CW - COS Differential')
plt.plot(x_cw, cw['X_COS_DIFF'].values, 'bo', label='Measured COS CW', markersize=4)
plt.plot(x_fit, y_fit_cw_cos, 'r-', label='Fitted COS CW')
plt.xlabel('Angle [°]')
plt.ylabel('COS_DIFF')
plt.legend()
plt.grid()

plt.subplot(2, 2, 2)
plt.title('CW - SIN Differential')
plt.plot(x_cw, cw['Y_SIN_DIFF'].values, 'go', label='Measured SIN CW', markersize=4)
plt.plot(x_fit, y_fit_cw_sin, 'r-', label='Fitted SIN CW')
plt.xlabel('Angle [°]')
plt.ylabel('SIN_DIFF')
plt.legend()
plt.grid()

# CCW plots
plt.subplot(2, 2, 3)
plt.title('CCW - COS Differential')
plt.plot(x_ccw, ccw['X_COS_DIFF'].values, 'bo', label='Measured COS CCW', markersize=4)
plt.plot(x_fit, y_fit_ccw_cos, 'r-', label='Fitted COS CCW')
plt.xlabel('Angle [°]')
plt.ylabel('COS_DIFF')
plt.legend()
plt.grid()

plt.subplot(2, 2, 4)
plt.title('CCW - SIN Differential')
plt.plot(x_ccw, ccw['Y_SIN_DIFF'].values, 'go', label='Measured SIN CCW', markersize=4)
plt.plot(x_fit, y_fit_ccw_sin, 'r-', label='Fitted SIN CCW')
plt.xlabel('Angle [°]')
plt.ylabel('SIN_DIFF')
plt.legend()
plt.grid()

plt.tight_layout()
plt.show()
