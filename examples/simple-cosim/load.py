import pandas as pd
import re
import matplotlib.pyplot as plt

def clean_line(line):
    # Replace 'inf' and 'nan' with empty values
    line = re.sub(r'\binf\b', '0.0', line)
    line = re.sub(r'\bnan\b', '0.0', line)

    # Remove unwanted characters like 'd', 'j', and time zone info like 'PST'
    line = re.sub(r'[djPST]', '', line)

    # Remove any extra spaces
    line = re.sub(r'\s+', ' ', line)

    # Replace multiple commas with a single comma
    line = re.sub(r',+', ',', line)

    # Remove any remaining non-numeric characters except essential signs and delimiters
    line = re.sub(r'[^\d\.\,\-\+\s]', '', line)

    return line.strip()

def extract_real_part(value):
    # Extract the real part of the complex value if it exists
    match = re.match(r'([+-]?\d+(\.\d+)?([eE][+-]?\d+)?)([+-].*)?', value.strip())
    if match:
        return float(match.group(1))
    else:
        return 0.0

def process_csv(file_path):
    cleaned_lines = []
    header_line = ''
    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            if line.startswith('#'):
                # Capture header line to use in cleaned CSV
                if 'timestamp' in line:  # Look for line that contains column names
                    header_line = line[1:].strip()  # Remove '#' and strip
                continue

            # Clean the line
            cleaned_line = clean_line(line.strip())
            cleaned_lines.append(cleaned_line)

    # Write cleaned data to a new CSV file
    cleaned_file_path = 'cleaned_load_data.csv'
    with open(cleaned_file_path, 'w') as cleaned_file:
        # Write header line to cleaned CSV
        if header_line:
            cleaned_file.write(header_line + '\n')
        else:
            print("Error: Header line not found.")
            return

        for cleaned_line in cleaned_lines:
            cleaned_file.write(cleaned_line + '\n')

    # Load cleaned data with pandas
    try:
        # Load the cleaned CSV into a dataframe with proper delimiter handling
        df = pd.read_csv(cleaned_file_path, delimiter=',')
        if df.empty:
            print("No valid data found to plot.")
        else:
            print("Data loaded successfully.")
            print("Columns in DataFrame:", df.columns)

            # Print the first few rows for verification
            print(df.head())

            # Clean up column names and prepare for plotting
            df.columns = [col.strip() for col in df.columns]  # Remove any leading/trailing spaces from column names
            if 'timestamp' not in df.columns:
                print("Error: 'timestamp' column not found in cleaned data.")
                return

            # Convert 'timestamp' to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

            # Dropping rows where timestamp is NaT (due to parsing errors)
            df.dropna(subset=['timestamp'], inplace=True)

            # Extract the real part of the complex values for each column
            for col in df.columns:
                if col != 'timestamp':
                    df[col] = df[col].apply(lambda x: extract_real_part(str(x)))

            # Set timestamp as the index
            df.set_index('timestamp', inplace=True)

            # Copy the initial row's values for 60 timestamps
            initial_values = df.iloc[0]
            timestamps = pd.date_range(start=df.index[0], periods=60, freq='S')
            initial_data = pd.DataFrame([initial_values] * 60, index=timestamps)

            # Plot measured_voltage, measured_current, and measured_power for phases A, B, and C
            plt.figure(figsize=(12, 10))

            # Phase A
            plt.subplot(3, 1, 1)
            plt.plot(initial_data.index, initial_data['measured_voltage_A'], label='Voltage A (V)', color='blue')
            plt.plot(initial_data.index, initial_data['measured_current_A'], label='Current A (A)', color='green')
            plt.plot(initial_data.index, initial_data['measured_power_A'], label='Power A (W)', color='red')
            plt.xlabel('Timestamp')
            plt.ylabel('Measurements (Phase A)')
            plt.title('Initial Load Data Over 60 Seconds (Phase A)')
            plt.legend()
            plt.grid(True)

            # Phase B
            plt.subplot(3, 1, 2)
            plt.plot(initial_data.index, initial_data['measured_voltage_B'], label='Voltage B (V)', color='blue')
            plt.plot(initial_data.index, initial_data['measured_current_B'], label='Current B (A)', color='green')
            plt.plot(initial_data.index, initial_data['measured_power_B'], label='Power B (W)', color='red')
            plt.xlabel('Timestamp')
            plt.ylabel('Measurements (Phase B)')
            plt.title('Initial Load Data Over 60 Seconds (Phase B)')
            plt.legend()
            plt.grid(True)

            # Phase C
            plt.subplot(3, 1, 3)
            plt.plot(initial_data.index, initial_data['measured_voltage_C'], label='Voltage C (V)', color='blue')
            plt.plot(initial_data.index, initial_data['measured_current_C'], label='Current C (A)', color='green')
            plt.plot(initial_data.index, initial_data['measured_power_C'], label='Power C (W)', color='red')
            plt.xlabel('Timestamp')
            plt.ylabel('Measurements (Phase C)')
            plt.title('Initial Load Data Over 60 Seconds (Phase C)')
            plt.legend()
            plt.grid(True)

            plt.tight_layout()
            plt.show()

    except pd.errors.ParserError as e:
        print(f"Error reading CSV file: {e}")

if __name__ == "__main__":
    process_csv('load_data.csv')
