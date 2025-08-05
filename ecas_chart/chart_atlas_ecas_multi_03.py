import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.patches as patches
import json
import numpy as np

# Load the data
file_name = 'mock_data.json'
with open(file_name, 'r') as f:
    data = json.load(f)

# --- Data Preparation ---
# Create a DataFrame for the line chart
df = pd.DataFrame({'timestamp_ms': data['t'], 'value': data['v']})
# Convert to KST
df['datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')

# Alarm data to KST
alarm_datetimes_series = pd.Series(data['a'])
alarm_datetimes = pd.to_datetime(alarm_datetimes_series, unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')

# --- Chart Generation ---
# Create 4x1 subplots. The height is changed from 24 to 16 (2/3 of the original).
fig, axes = plt.subplots(4, 1, figsize=(12, 16))
plt.style.use('seaborn')

# Loop through each subplot to draw the chart
for i, ax in enumerate(axes):
    # Set background color
    ax.set_facecolor('white')

    # --- Data Plotting ---
    ax.plot(df['datetime'], df['value'], color='blue', linewidth=1.5, zorder=2)

    # --- Axis Configuration ---
    min_dt = df['datetime'].min()
    max_dt = df['datetime'].max()
    ax.set_xlim(min_dt, max_dt)
    min_y, max_y = df['value'].min(), df['value'].max()
    ax.set_ylim(min_y, max_y)

    # --- X-Axis Tick Locator ---
    min_num = mdates.date2num(min_dt)
    max_num = mdates.date2num(max_dt)
    x_tick_nums = np.linspace(min_num, max_num, 6)
    ax.xaxis.set_major_locator(ticker.FixedLocator(x_tick_nums))

    # Y-axis ticks
    y_ticks = np.linspace(float(min_y), float(max_y), 7)
    ax.yaxis.set_major_locator(ticker.FixedLocator(y_ticks))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    ax.tick_params(axis='y', colors='black')

    # --- Add Alarm Rectangles ---
    rect_width_days = (max_num - min_num) / 60.0
    rect_height = max_y - min_y
    for alarm_dt in alarm_datetimes:
        if min_dt <= alarm_dt <= max_dt:
            rect = patches.Rectangle(
                (mdates.date2num(alarm_dt), min_y),
                rect_width_days, rect_height,
                facecolor='red', alpha=0.1, edgecolor='none', zorder=1
            )
            ax.add_patch(rect)

    # --- Styling and Labels ---
    ax.grid(True, linestyle='-', alpha=0.7, color='grey')
    ax.set_title(f'current {i+1}', fontsize=16, fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('')

    # Configure x-axis labels for each subplot
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S %Z'))
    plt.setp(ax.get_xticklabels(), rotation=45, ha='center', fontsize=12, fontweight='bold')

# Adjust the overall layout
fig.tight_layout(pad=3.0)
fig.patch.set_facecolor('white')

# Save the final image
image_path = 'line_chart_4x1_resized.png'
plt.savefig(image_path)
plt.close()

print(f"높이가 조절된 4x1 차트가 '{image_path}'로 저장되었습니다.")
