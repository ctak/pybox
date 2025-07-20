import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import matplotlib.patches as patches
import json
import numpy as np

# 한글 폰트 설정 (맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

# Load the data
file_name = 'mock_data.json'
with open(file_name, 'r') as f:
    data = json.load(f)

# --- 데이터 준비 ---
# Create a DataFrame for the line chart
df = pd.DataFrame({'timestamp_ms': data['t'], 'value': data['v']})
# Convert to KST
df['datetime'] = pd.to_datetime(df['timestamp_ms'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')

# Alarm data to KST
alarm_datetimes_series = pd.Series(data['a'])
alarm_datetimes = pd.to_datetime(alarm_datetimes_series, unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Seoul')

# --- 차트 생성 ---
# 4행 1열의 서브플롯을 생성하고, x축을 공유합니다.
fig, axes = plt.subplots(4, 1, figsize=(12, 24), sharex=True)
# plt.style.use('seaborn-v0_8') # Seaborn 스타일 적용
plt.style.use('seaborn') # Seaborn 스타일 적용

# 각 서브플롯에 차트를 그리기 위한 루프
for i, ax in enumerate(axes):
    # 배경색 설정
    ax.set_facecolor('white')

    # --- 데이터 플로팅 ---
    ax.plot(df['datetime'], df['value'], color='blue', linewidth=1.5, zorder=2)

    # --- 축 설정 ---
    min_dt = df['datetime'].min()
    max_dt = df['datetime'].max()
    ax.set_xlim(min_dt, max_dt)
    min_y, max_y = df['value'].min(), df['value'].max()
    ax.set_ylim(min_y, max_y)

    # Y축 틱 설정
    y_ticks = np.linspace(float(min_y), float(max_y), 7)
    ax.yaxis.set_major_locator(ticker.FixedLocator(y_ticks))
    ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.2f'))
    ax.tick_params(axis='y', colors='black')

    # --- 알람 영역 추가 ---
    min_num = mdates.date2num(min_dt)
    max_num = mdates.date2num(max_dt)
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

    # --- 스타일링 ---
    ax.grid(True, linestyle='-', alpha=0.7, color='grey')
    ax.set_title(f'알람을 포함한 시계열 데이터 (차트 {i+1})', fontsize=16, fontweight='bold')
    ax.set_xlabel('')
    ax.set_ylabel('')

# 마지막 차트의 X축 라벨만 보이도록 설정 (sharex=True 이므로 자동이지만, 명시적으로 스타일 적용)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M:%S %Z'))
plt.setp(ax.get_xticklabels(), rotation=45, ha='center', fontsize=12, fontweight='bold')

# 전체 레이아웃 조정
fig.tight_layout(pad=3.0)
fig.patch.set_facecolor('white')

# 이미지로 저장
plt.savefig('line_chart_4x1.png')
plt.close()

print("4x1 차트가 'line_chart_4x1.png'로 저장되었습니다.")
