import pandas as pd
import re

# Please enter the file paths to prepare a final CSV file.
raw_data_file_path = "measurement_log_20250414_084146.csv"
temp_chamber_file_path = "14 April Temp chamber.csv"


class PrepareData:
    def __init__(self, raw_data_file_path: str = None, temp_chamber_file_path: str = None):
        self.raw_data_file_path = raw_data_file_path
        self.temp_chamber_file_path = temp_chamber_file_path
        if self.raw_data_file_path is not None and self.temp_chamber_file_path is not None:
            self.df_raw_data = pd.read_csv(raw_data_file_path)
            self.df_tmp_chmber = pd.read_csv(temp_chamber_file_path)
        else:
            print(f'No file path present while preparing data.')

    def make_final_csv(self):
        try:
            # Convert timestamps to datetime
            self.df_raw_data['timestamp'] = pd.to_datetime(self.df_raw_data['timestamp'])
            self.df_tmp_chmber['Date/Time'] = pd.to_datetime(self.df_tmp_chmber['Date/Time'],
                                                             format='%Y.%m.%d %H:%M:%S')

            # Select and rename relevant columns
            self.df_tmp_chmber = self.df_tmp_chmber.set_index('Date/Time')[['Ideal', 'Actual']]

            # Reset temp chamber for merging
            df_tmp_chmber_reset = self.df_tmp_chmber.reset_index().rename(columns={"Date/Time": "timestamp"})

            # Combine raw timestamps and temp chamber timestamps
            combined_df = pd.concat([self.df_raw_data[['timestamp']], df_tmp_chmber_reset], axis=0, ignore_index=True)
            combined_df = combined_df.sort_values('timestamp')

            # Fill temperature values
            combined_df = combined_df.set_index('timestamp')
            combined_df['Ideal'] = combined_df['Ideal'].interpolate(method='time')
            combined_df['Actual'] = combined_df['Actual'].interpolate(method='time')

            # Special handling: Fill leading NaN (timestamps before first temp chamber reading)
            combined_df['Ideal'] = combined_df['Ideal'].fillna(method='bfill')
            combined_df['Actual'] = combined_df['Actual'].fillna(method='bfill')

            combined_df = combined_df.reset_index()

            # Filter to only Arduino timestamps
            final_temp_values = combined_df[combined_df['timestamp'].isin(
                self.df_raw_data['timestamp'])].reset_index(drop=True)

            # Merge with Arduino data
            final_df = self.df_raw_data.copy()
            final_df['ideal_tmp'] = final_temp_values['Ideal']
            final_df['actual_tmp'] = final_temp_values['Actual']

            # Extract timestamp from data file name and save the CSV
            match = re.search(r"(\d{8})_(\d{6})", self.raw_data_file_path)
            if match:
                date_part = match.group(1)
                time_part = match.group(2)
                final_file_name = f'Final_{date_part+"_"+time_part}.csv'
            else:
                final_file_name = "Final_output.csv"
                print("No timestamp found in filename. Saving as Final_output.csv.")

            # Save to new CSV
            final_df.to_csv(final_file_name, index=False)
            print(f"✅ Final CSV generated and saved as: {final_file_name}")

        except BaseException as e:
            print(f"❌ ERROR while preparing final csv file: {e}")


if __name__ == "__main__":
    prepare_data = PrepareData(raw_data_file_path=raw_data_file_path, temp_chamber_file_path=temp_chamber_file_path)
    prepare_data.make_final_csv()
