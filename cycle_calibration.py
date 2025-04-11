import pandas as pd
from fit import CurveFit
from maths import Formula
import os

# Constants
CYCLE_SIZE = 130  # 65 CW + 65 CCW steps


class Calibration:
    def __init__(self, csv_path: str = ""):
        self.csv_path = csv_path

    def all_cycles(self):
        # Load the full CSV
        df_full = pd.read_csv(self.csv_path)
        # Buffers for final data
        updated_dfs = []

        # Process cycle by cycle
        for cycle_start in range(0, len(df_full), CYCLE_SIZE):
            cycle_end = cycle_start + CYCLE_SIZE
            df_cycle = df_full.iloc[cycle_start:cycle_end].copy()
            # Skip incomplete last cycle if any
            if len(df_cycle) < CYCLE_SIZE:
                break
            # Save temporary CSV
            temp_csv = "temp_cycle.csv"
            df_cycle.to_csv(temp_csv, index=False)

            # Step 1: Calibrate using CurveFit
            curve_fitter = CurveFit(csv_path=temp_csv)
            curve_fitter.calculate_curve_fit(plot_graph=False)

            # Step 2: Create Formula object with fresh calibration
            formula = Formula(
                o_x_m=curve_fitter.o_x_m,
                o_y_m=curve_fitter.o_y_m,
                a_x_m=curve_fitter.a_x_m,
                a_y_m=curve_fitter.a_y_m,
                phi_x_m=curve_fitter.phi_x_m,
                phi_y_m=curve_fitter.phi_y_m
            )

            # Step 3: Calculate angle errors
            angle_errors = []
            alpha_angles = []
            theta_angles = []
            for _, row in df_cycle.iterrows():
                step = row['step']
                dir = row['direction']
                sin_p = row['SIN_P']
                cos_p = row['COS_P']
                sin_n = row['SIN_N']
                cos_n = row['COS_N']
                theta_bits = row['encoder']
                prev_theta = formula.prev_encoder_degree
                # Apply full formula chain
                y_sin_diff = formula.y_sin_diff(sin_p, sin_n)
                x_cos_diff = formula.x_cos_diff(cos_p, cos_n)
                encoder_theta_degree = formula.encoder_theta_degree(theta_bits, prev_theta)
                y1_sin = formula.y1_sin(y_sin_diff)
                x1_cos = formula.x1_cos(x_cos_diff)
                y2_sin = formula.y2_sin(y1_sin)
                x2_cos = formula.x2_cos(x1_cos)
                y3_sin = formula.y3_sin(x2_cos, y2_sin)
                alpha_degree = formula.alpha(step, dir, x2_cos, y3_sin)
                angle_error = alpha_degree - encoder_theta_degree

                angle_errors.append(angle_error)
                alpha_angles.append(alpha_degree)
                theta_angles.append(encoder_theta_degree)

            # Update this cycle's dataframe
            df_cycle['theta'] = theta_angles
            df_cycle['alpha'] = alpha_angles
            df_cycle['angle_error'] = angle_errors
            # Collect updated cycle
            updated_dfs.append(df_cycle)

        # Clean up temporary file
        if os.path.exists("temp_cycle.csv"):
            os.remove("temp_cycle.csv")
        # Merge all updated cycles
        final_df = pd.concat(updated_dfs, ignore_index=True)
        # Save back to the original CSV
        final_df.to_csv(self.csv_path, index=False)


if __name__ == "__main__":
    CSV_PATH = ""
    calibration = Calibration(csv_path=CSV_PATH)
    calibration.all_cycles()
