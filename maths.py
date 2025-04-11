from math import pi, sin, cos, degrees, atan2
import pandas as pd

ENCODER_PPR = 40000  # Total pulse per rotation of encoder in the system


class Formula:
    def __init__(self, o_x_m: float, o_y_m: float, a_x_m: float, a_y_m: float, phi_x_m: float, phi_y_m: float):
        self.O_X_M = o_x_m
        self.O_Y_M = o_y_m
        self.A_X_M = a_x_m
        self.A_Y_M = a_y_m
        self.PHI_X_M = phi_x_m
        self.PHI_Y_M = phi_y_m
        self.PHI_M = self.PHI_X_M - self.PHI_Y_M
        self.prev_encoder_degree = 0.0

    def y_sin_diff(self, sin_p, sin_n):
        y_sin_diff = sin_p - sin_n
        return y_sin_diff

    def x_cos_diff(self, cos_p, cos_n):
        x_cos_diff = cos_p - cos_n
        return x_cos_diff

    def encoder_theta_degree(self, theta_bits, prev_theta_bits):
        theta_degree = ((360/ENCODER_PPR)*theta_bits)+prev_theta_bits
        self.prev_encoder_degree = theta_degree
        return theta_degree

    def y1_sin(self, y_sin_diff):
        y1_sin = y_sin_diff - self.O_Y_M
        return y1_sin

    def x1_cos(self, x_cos_diff):
        x1_cos = x_cos_diff - self.O_X_M
        return x1_cos

    def y2_sin(self, y1_sin):
        y2_sin = y1_sin/self.A_Y_M
        return y2_sin

    def x2_cos(self, x1_cos):
        x2_cos = x1_cos/self.A_X_M
        return x2_cos

    def y3_sin(self, x2_cos, y2_sin):
        angle = -(self.PHI_M * pi)/180
        y3_sin = (y2_sin - x2_cos * sin(angle)) / cos(angle)
        return y3_sin

    def alpha(self, step, dir, x2_cos, y3_sin):
        angle = degrees(atan2(y3_sin, x2_cos)) - (self.PHI_X_M)
        angle = (angle + 360) % 360
        if step == 0:  # For step 0 of CW and CCW
            if dir == 'CW':
                if angle > 5:
                    return angle - 360
                else:
                    return angle
            else:
                if angle < 355:
                    return angle + 360
                else:
                    return angle
        elif step == 64:  # For step 64 of CW and CCW
            if dir == 'CW':
                if angle < 355:
                    return angle + 360
                else:
                    return angle
            else:
                if angle > 5:
                    return angle - 360
                else:
                    return angle
        else:  # For step 1-63 of CW and CCW
            return angle

    def calculate_and_update_angle_errors(self, file_path):
        """
        Calculates angle errors from a CSV file, adds an 'angle_error' column, and overwrites the CSV.
        Args:
            file_path (str): Path to the CSV file.
        """
        try:
            df = pd.read_csv(file_path)

            angle_errors = []
            alpha_angle = []
            encoder_angle = []

            for idx in range(0, len(df)):
                step = df.at[idx, 'step']
                dir = df.at[idx, 'direction']
                sin_p = df.at[idx, 'SIN_P']
                cos_p = df.at[idx, 'COS_P']
                sin_n = df.at[idx, 'SIN_N']
                cos_n = df.at[idx, 'COS_N']
                theta_bits = df.at[idx, 'encoder']
                prev_theta_bits = self.prev_encoder_degree  # previous encoder degree value

                # Apply formula chain
                y_sin_diff = self.y_sin_diff(sin_p, sin_n)
                x_cos_diff = self.x_cos_diff(cos_p, cos_n)
                encoder_theta_degree = self.encoder_theta_degree(theta_bits, prev_theta_bits)
                y1_sin = self.y1_sin(y_sin_diff)
                x1_cos = self.x1_cos(x_cos_diff)
                y2_sin = self.y2_sin(y1_sin)
                x2_cos = self.x2_cos(x1_cos)
                y3_sin = self.y3_sin(x2_cos, y2_sin)
                alpha_degree = self.alpha(step, dir, x2_cos, y3_sin)
                angle_error = alpha_degree - encoder_theta_degree

                angle_errors.append(angle_error)
                alpha_angle.append(alpha_degree)
                encoder_angle.append(encoder_theta_degree)

            # Add the new column to the dataframe
            df['angle_error'] = angle_errors
            df['alpha'] = alpha_angle
            df['theta'] = encoder_angle

            # Overwrite the file
            df.to_csv(file_path, index=False)
            return True

        except Exception as e:
            print(f"Error occurred: {e}")
            return False


if __name__ == "__main__":
    formula = Formula(
        o_x_m=3.7854016025888395,
        o_y_m=-68.1212087931653,
        a_x_m=-8329.256046248338,
        a_y_m=8410.02408859496,
        phi_x_m=-35.059167998465355,
        phi_y_m=-34.193377820597
    )
    formula.calculate_and_update_angle_errors("measurement_log_20250410_114038.csv")
