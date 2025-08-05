import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.patches as patches
import json
from datetime import datetime
import numpy as np

# Load the data
file_name = 'mock_data.json'
with open(file_name, 'r') as f:
    data = json.load(f)

# Create a DataFrame for the line chart
df = pd.DataFrame({'timestamp_ms': data['t'], 'value': data['v']})

# Convert to datetime objects first (this creates timezone-naive datetimes)
df['datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms')

# Now, use the .dt accessor to localize to UTC and then convert to the desired timezone
df['datetime'] = df['datetime'].dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')


# Do the same for the alarm data
alarm_datetimes_series = pd.Series(data['a'])
# Convert to datetime, then localize and convert timezone
alarm_datetimes = pd.to_datetime(alarm_datetimes_series, unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')


# Set Matplotlib backend for non-interactive use
plt.switch_backend('Agg')

# Apply a style for a modern look
plt.style.use('seaborn')

# Create the plot
fig, ax = plt.subplots(figsize=(12, 6))

# Set chart background to white
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

# Plot the line chart
ax.plot(df['datetime'], df['value'], color='blue', linewidth=1.5, zorder=2)

# --- X-axis configuration ---
min_dt = df['datetime'].min()
max_dt = df['datetime'].max()
ax.set_xlim(min_dt, max_dt)

min_num = mdates.date2num(min_dt)
max_num = mdates.date2num(max_dt)
x_tick_nums = np.linspace(min_num, max_num, 6)

ax.xaxis.set_major_locator(ticker.FixedLocator(x_tick_nums))
# Add %Z to the formatter to display the timezone abbreviation (e.g., KST)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S %Z'))
ax.tick_params(axis='x', colors='black')

# --- Y-axis configuration ---
min_y, max_y = df['value'].min(), df['value'].max()
ax.set_ylim(min_y, max_y)

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
            rect_width_days,
            rect_height,
            facecolor='red',
            alpha=0.1,
            edgecolor='none',
            zorder=1
        )
        ax.add_patch(rect)

# Add grid lines
ax.grid(True, linestyle='-', alpha=0.7, color='grey')

# Remove Title and Axis Labels
ax.set_title('Current I', fontsize=16, fontweight='bold', color='black')
ax.set_xlabel('')
ax.set_ylabel('')

# Rotate x-axis labels, center them, and make them larger and bold
plt.xticks(rotation=45, ha='center', fontsize=12, fontweight='bold')

# Adjust layout
plt.tight_layout()

# Save the chart as an image
image_path = 'line_chart_kst.png'
plt.savefig(image_path)
plt.close()

print(f"시간 축이 한국 표준시(KST)로 수정된 차트가 '{image_path}'로 저장되었습니다.")
