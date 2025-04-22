import serial
import time
import re
import csv
from datetime import datetime
import pandas as pd
from cycle_calibration import Calibration

# Configuration
SERIAL_PORT = '/dev/ttyACM0'  # COM port of Arduino
BAUDRATE = 115200  # Communication rate
CYCLE_DURATION_MIN = 1  # Approx duration of one cycle in minutes
ENCODER_PPR = 40000  # Total pulse per rotation of encoder in the system

# ---------------------SET SYSTEM RUN TIME-------------------------------------------------------------------------
RUN_SYSTEM_MIN = 7250
# -----------------------------------------------------------------------------------------------------------------

# Regex pattern to parse data (DO NOT CHANGE!)
SENSOR_DATA_REGEX = r"\s*(\d+)\s+(-?\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)"
CYCLE_ENDED_INDICATOR = "Measurements ended for the cycle"
CYCLE_START_OK = "You have selected option 2 the main program"
ENCODER_0_360_COUNT_REGEX = r"0°-360° cw\s+(-?\d+)"
ENCODER_360_0_COUNT_REGEX = r"360°-0° ccw\s+(-?\d+)"
CW_ENCODER_ERROR_REGEX = r"Correction cw:\s*(-?\d+)"
CCW_ENCODER_ERROR_REGEX = r"Correction ccw:\s*(-?\d+)"

# Derived values (DO NOT CHANGE!)
NUM_CYCLES = max(1, int(RUN_SYSTEM_MIN / CYCLE_DURATION_MIN))
TIMESTAMP = datetime.now().strftime('%Y%m%d_%H%M%S')
DATA_FILENAME = f"measurement_log_{TIMESTAMP}.csv"
LOG_FILENAME = f"cycle_log_{TIMESTAMP}.txt"
ENCODER_FILENAME = f"encoder_errors_{TIMESTAMP}.csv"

# Time and Date format of the system (DO NOT CHANGE!)
DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"


class Automation:
    def __init__(self):
        self.system_start = time.time()  # The variable is used to note down the system start time, it is not noted here
        self.cycle_count = 0  # To store the current cycle number
        self.notedown_system_start_time = True
        self.csv_writer = None
        self.csvfile = None
        self.log_file = None
        self.encoder_file = None
        self.csv_encoder_error_writer = None
        self.encoder_error_after_CCW_prev = 0.0
        self.cw_encoder_error_diff = 0
        self.ccw_encoder_error_diff = 0

    def parse_sensor_data(self, line):
        def fetch_sensor_data():
            match = re.match(SENSOR_DATA_REGEX, line)
            if match:
                return {
                    "step": int(match.group(1)),
                    "encoder": int(match.group(2)),
                    "SIN_P": int(match.group(3)),
                    "COS_P": int(match.group(4)),
                    "SIN_N": int(match.group(5)),
                    "COS_N": int(match.group(6)),
                    "cycle": self.cycle_count
                }
            return None

        parsed_data = fetch_sensor_data()
        if parsed_data:
            timestamp = datetime.now().strftime(DATE_TIME_FORMAT)
            print(f"Step {parsed_data['step']:>2} | Time {timestamp} | "
                  f"Enc={parsed_data['encoder']:>5} | SIN_P={parsed_data['SIN_P']} | "
                  f"COS_P={parsed_data['COS_P']} | SIN_N={parsed_data['SIN_N']} | "
                  f"COS_N={parsed_data['COS_N']} | cycle={self.cycle_count}")

            self.csv_writer.writerow([
                parsed_data['step'], timestamp, parsed_data['encoder'],
                parsed_data['SIN_P'], parsed_data['COS_P'],
                parsed_data['SIN_N'], parsed_data['COS_N'],
                self.cycle_count
            ])
            self.csvfile.flush()

    def wait_for_ack(self, ser, expected_str):
        """ Wait for Arduino to confirm cycle start """
        while True:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if expected_str in line:
                if self.notedown_system_start_time:  # only note down the start time once in the begining.
                    self.system_start = time.time()
                    self.notedown_system_start_time = False
                return
            elif line:
                print(f"Waiting for Arduino to start cycle: {self.cycle_count}...")

    def log_event(self, message, write_timestamp: bool = False):
        if write_timestamp:
            timestamp = datetime.now().strftime(DATE_TIME_FORMAT)
            self.log_file.write(f"[{timestamp}] {message}\n")
        else:
            self.log_file.write(f"{message}\n")

    def add_dir_col_to_data(self, file_path):
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

    def system_init_procedure(self):
        # Initiate data csv file
        self.csv_writer = csv.writer(self.csvfile)
        self.csv_writer.writerow(["step", "timestamp", "encoder", "SIN_P", "COS_P", "SIN_N", "COS_N", "cycle"])

        # Initiate encoder csv file
        self.csv_encoder_error_writer = csv.writer(self.encoder_file)
        self.csv_encoder_error_writer.writerow(
            ["cycle", "encoder_error_cw", "encoder_error_ccw"])

        print(f"Starting system...\nLogging to: {DATA_FILENAME}")
        print(f"Cycle log: {LOG_FILENAME}")
        print(f"System runtime: {RUN_SYSTEM_MIN} min → Estimated cycles: {NUM_CYCLES}")

        self.log_event(f"System started. Runtime goal: {RUN_SYSTEM_MIN} min", write_timestamp=True)

    def parse_encoder_errors(self, ser):
        '''
        Calculation of Encoder error:
        CSV file columns -> [Step0_of_CW, Step0_of_CCW]
        if, Cycle=1 → [0, CW - PPR]
        else → [ PE, (PE + CW) - PPR]
        where, PE = Previous Error, PPR = Pulse Per Relovution

        For, example:
        Cycle1 -> [0, (CW1 - PPR) ]
        Cycle2 -> [ PE, (PE + CW2) - PPR] (PE = CW1 + CCW1)
        Cycle3 -> [ PE, (PE + CW3) - PPR] (PE = CW1 + CCW1 + CW2 + CCW2)
        ..................
        '''
        encoder_error_stored_CW = False
        encoder_error_stored_CCW = False
        # Run in a loop until encoder values are not received
        while not encoder_error_stored_CW or not encoder_error_stored_CCW:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if match := re.search(ENCODER_0_360_COUNT_REGEX, line):
                current_encoder_error_CW = int(match.group(1))
                encoder_error_stored_CW = True
            elif match := re.search(ENCODER_360_0_COUNT_REGEX, line):
                current_encoder_error_CCW = int(match.group(1))
                encoder_error_stored_CCW = True

        # Calculating total error after cw rotation and adding previous error, this will be used in next loop
        encoder_error_after_CCW = self.encoder_error_after_CCW_prev + current_encoder_error_CW + current_encoder_error_CCW

        # Save the encoder error in a csv file
        if (self.cycle_count == 1):
            self.csv_encoder_error_writer.writerow(
                [self.cycle_count, 0, current_encoder_error_CW - ENCODER_PPR])  # [0, CW - PPR]
        else:
            encoder_error_after_CW = (self.encoder_error_after_CCW_prev + current_encoder_error_CW) - ENCODER_PPR
            self.csv_encoder_error_writer.writerow([self.cycle_count, self.encoder_error_after_CCW_prev,
                                                    encoder_error_after_CW])  # [ PREVIOUS_ERR, (PREVIOUS_ERR + CW) - PPR]
        self.encoder_file.flush()
        self.encoder_error_after_CCW_prev = encoder_error_after_CCW  # Storing the value of previous error
        return [current_encoder_error_CW, current_encoder_error_CCW]

    def fit_encoder_error_to_measurements(self):
        # Load both CSVs
        encoder_error = pd.read_csv(ENCODER_FILENAME)
        measurements = pd.read_csv(DATA_FILENAME)
        # Iterate through each cycle
        for idx, row in encoder_error.iterrows():
            cycle_num = row['cycle']
            error_cw = row['encoder_error_cw']
            error_ccw = row['encoder_error_ccw']
            # Find all step 0 entries for this cycle
            step0_rows = measurements[(measurements['cycle'] == cycle_num) & (measurements['step'] == 0)]
            # Get the indexes
            first_step0_idx = step0_rows.index[0]
            second_step0_idx = step0_rows.index[1]
            # Update the encoder values
            measurements.at[first_step0_idx, 'encoder'] = error_cw
            measurements.at[second_step0_idx, 'encoder'] = error_ccw
        # Overwrite the existing file
        measurements.to_csv(DATA_FILENAME, index=False)

    def main_loop(self):
        try:
            with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as ser, \
                    open(DATA_FILENAME, mode='w', newline='', buffering=1) as self.csvfile, \
                    open(LOG_FILENAME, mode='w') as self.log_file, \
                    open(ENCODER_FILENAME, mode='w', newline='', buffering=1) as self.encoder_file:

                self.system_init_procedure()

                time.sleep(2)
                ser.reset_input_buffer()
                ser.reset_output_buffer()

                full_system_start = datetime.now()

                while (time.time() - self.system_start) <= RUN_SYSTEM_MIN * 60:
                    # Trigger a new cycle
                    ser.write(b'2\n')
                    self.cycle_count += 1
                    self.wait_for_ack(ser, CYCLE_START_OK)

                    self.log_event(f"Cycle {self.cycle_count} started", write_timestamp=True)

                    print(f"\n{'*'*50}\nStarting cycle {self.cycle_count}\n{'*'*50}")

                    while True:
                        line = ser.readline().decode('utf-8', errors='ignore').strip()
                        if not line:
                            continue

                        self.parse_sensor_data(line)

                        match_cw = re.search(CW_ENCODER_ERROR_REGEX, line)
                        if match_cw:
                            self.cw_encoder_error_diff = match_cw.group(1)
                        match_ccw = re.search(CCW_ENCODER_ERROR_REGEX, line)
                        if match_ccw:
                            ccw_encoder_error_diff = match_ccw.group(1)

                        if CYCLE_ENDED_INDICATOR in line:
                            encoder_errors = self.parse_encoder_errors(ser)
                            self.log_event(
                                f"Cycle {self.cycle_count} ended -> {encoder_errors} -> [{self.cw_encoder_error_diff},{ccw_encoder_error_diff}]")
                            print(f"\n{'*'*50}\nFinished cycle {self.cycle_count}\n{'*'*50}")
                            break

                full_system_end = datetime.now()
                total_runtime_min = round((full_system_end - full_system_start).total_seconds() / 60, 2)

                print("====================================================")
                print(f"System completed. Total cycles: {self.cycle_count}")
                print(f"Data logged to: {DATA_FILENAME}")
                print(f"Logs are saved in: {LOG_FILENAME}")
                print(f"Encoder error file saved as   : {ENCODER_FILENAME}")
                print("====================================================")

                print("Preparing the CSV file, it might take some time...")

                # Final summary to be logged
                self.log_event("\n================ SYSTEM SUMMARY ===============")
                self.log_event(f"Total cycles completed: {self.cycle_count}")
                self.log_event(f"System started at     : {full_system_start.strftime(DATE_TIME_FORMAT)}")
                self.log_event(f"System ended at       : {full_system_end.strftime(DATE_TIME_FORMAT)}")
                self.log_event(f"Total time elapsed    : {total_runtime_min} minutes")

                # Adding ecoder errors to the data
                print("Fitting encoder counts...")
                self.log_event(f"Start fitting Encoder counts", write_timestamp=True)
                self.fit_encoder_error_to_measurements()
                self.log_event(f"Finished fitting Encoder counts", write_timestamp=True)
                self.log_event(f"Encoder error file saved as   : {ENCODER_FILENAME}")

                # Add direction column (CW/CCW) to the data
                print("Adding direction column...")
                self.log_event(f"Adding direction column to CSV", write_timestamp=True)
                self.add_dir_col_to_data(DATA_FILENAME)
                self.log_event(f"Finished adding direction", write_timestamp=True)

                # Calibrating, Calculating and storing angle error
                print("Calibrating, Calculating and storing Angle Error...")
                self.log_event(f"Started calculating Angle Error", write_timestamp=True)
                calibration = Calibration(csv_path=DATA_FILENAME)
                calibration.all_cycles()
                self.log_event(f"Angle errors calculated and csv updated", write_timestamp=True)

                self.log_event(f"Logs are saved in     : {LOG_FILENAME}")
                self.log_event(f"Final CSV saved to  : {DATA_FILENAME}")
                self.log_event("====================================================")
                print("All tasks completed!")

        except KeyboardInterrupt:
            print(f"\nInterrupted by user. Data saved to {DATA_FILENAME}")
        except serial.SerialException as e:
            print(f"Serial connection error: {e}")


if __name__ == "__main__":
    automation = Automation()
    automation.main_loop()
