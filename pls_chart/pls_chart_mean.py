import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase

def get_diverging_color(value, min_val, mean_val, max_val):
    """
    평균값을 기준으로 파랑-흰색-빨강으로 변하는 색상을 반환합니다.
    색상은 0.0 ~ 1.0 범위의 (R, G, B) 튜플로 반환됩니다.
    """
    # 입력 값이 범위를 벗어나는 경우 처리
    value = np.clip(value, min_val, max_val)
    
    # 평균값을 기준으로 색상 계산
    if value < mean_val:
        # 최소값(파랑) -> 평균값(흰색)
        ratio = (value - min_val) / (mean_val - min_val) if mean_val != min_val else 1.0
        # 파란색 (0,0,1)에서 흰색 (1,1,1)으로 보간
        r = ratio
        g = ratio
        b = 1.0
    elif value > mean_val:
        # 평균값(흰색) -> 최대값(빨강)
        ratio = (value - mean_val) / (max_val - mean_val) if max_val != mean_val else 1.0
        # 흰색 (1,1,1)에서 빨간색 (1,0,0)으로 보간
        r = 1.0
        g = 1.0 - ratio
        b = 1.0 - ratio
    else: # value == mean_val
        r, g, b = 1.0, 1.0, 1.0 # 흰색
        
    return (r, g, b)

# --- 시뮬레이션 데이터 생성 ---
# 일부러 평균이 중앙이 아니도록 비대칭(skewed) 데이터를 생성
np.random.seed(0)
x_data = np.random.rand(100) * 10
y_data = np.random.rand(100) * 10
# 품질(Y) 데이터: 대부분 낮은 값에 몰려있고, 일부 높은 값이 있음
quality_data = np.concatenate([np.random.normal(20, 5, 80), np.random.normal(60, 10, 20)])

# 핵심 통계량 계산
min_q = np.min(quality_data)
max_q = np.max(quality_data)
mean_q = np.mean(quality_data)

print(f"최소값: {min_q:.2f}")
print(f"최대값: {max_q:.2f}")
print(f"평균값: {mean_q:.2f}")
print(f"산술적 중앙값: {(min_q + max_q) / 2:.2f} (평균값과 다름!)")

# --- 시각화 ---
fig, ax = plt.subplots(figsize=(10, 8))

# 각 데이터 포인트에 대해 색상 계산하여 Scatter 차트 그리기
colors = [get_diverging_color(q, min_q, mean_q, max_q) for q in quality_data]
ax.scatter(x_data, y_data, c=colors, s=60, edgecolor='black', alpha=0.8)
ax.set_title('Scatter Plot with Custom Diverging Colormap (Mean as Center)')
ax.set_xlabel('Latent Variable 1 (t1)')
ax.set_ylabel('Latent Variable 2 (t2)')

# --- 커스텀 색상 막대 그리기 ---
# 색상 막대 위치 설정
cax = fig.add_axes([0.92, 0.15, 0.02, 0.7]) # [left, bottom, width, height]

# 색상 막대를 위한 그라데이션 생성
gradient = np.linspace(0, 1, 256)
vals = np.linspace(min_q, max_q, 256)
color_map_for_bar = np.array([get_diverging_color(v, min_q, mean_q, max_q) for v in vals])

# 색상 막대 그리기 - reshape 부분을 (256, 1, 3)으로 수정
cax.imshow(color_map_for_bar.reshape(256, 1, 3), aspect='auto', origin='lower')
cax.set_yticks([0, np.interp(mean_q, vals, range(256)), 255])
cax.set_yticklabels([f'{min_q:.1f} (Min)', f'{mean_q:.1f} (Mean)', f'{max_q:.1f} (Max)'])
cax.yaxis.tick_right()

plt.show()
