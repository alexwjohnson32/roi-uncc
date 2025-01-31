import pandas as pd
import re
import matplotlib.pyplot as plt

def clean_line(line):
    # Replace 'inf' and 'nan' with empty values
    line = re.sub(r'\binf\b', '0.0', line)
    line = re.sub(r'\bnan\b', '0.0', line)

    # Remove unwanted characters like 'd', 'j', and time zone info like 'PST'
    line = re.sub(r'[djPST]', '', line)

    # Replace multiple spaces with a single space
    line = re.sub(r'\s+', ' ', line)

    # Replace multiple commas with a single comma
    line = re.sub(r',+', ',', line)

    return line.strip()

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

            # Check if 'timestamp' is in columns after cleaning
            df.columns = [col.strip() for col in df.columns]  # Remove any leading/trailing spaces from column names
            if 'timestamp' not in df.columns:
                print("Error: 'timestamp' column not found in cleaned data.")
                return

            # Convert 'timestamp' to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

            # Dropping rows where timestamp is NaT (due to parsing errors)
            df.dropna(subset=['timestamp'], inplace=True)

            # Set timestamp as the index
            df.set_index('timestamp', inplace=True)

            # Plot some example columns, assuming the column names exist
            plt.figure(figsize=(10, 6))
            if 'measured_voltage_A' in df.columns and 'measured_power_A' in df.columns:
                plt.plot(df.index, df['measured_voltage_A'], label='Voltage A', color='blue')
                plt.plot(df.index, df['measured_power_A'], label='Power A', color='red')
            else:
                print("Error: Required columns ('measured_voltage_A' and 'measured_power_A') not found in data.")
                return

            plt.xlabel('Timestamp')
            plt.ylabel('Measurements')
            plt.title('Load Data Over Time')
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

    except pd.errors.ParserError as e:
        print(f"Error reading CSV file: {e}")

if __name__ == "__main__":
    process_csv('load_data.csv')


