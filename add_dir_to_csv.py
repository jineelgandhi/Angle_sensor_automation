import pandas as pd


def add_dir_col_to_data(file_path):
    df = pd.read_csv(file_path)
    directions = []
    reset_counter = 0
    for idx, row in df.iterrows():
        if row['step'] == 0 and idx != 0:
            reset_counter += 1
        if reset_counter % 2 == 0:
            directions.append('CW')
        else:
            directions.append('CCW')
    df['direction'] = directions
    df.to_csv(file_path, index=False)


if __name__ == "__main__":
    add_dir_col_to_data("measurement_log_20250408_084234.csv")
