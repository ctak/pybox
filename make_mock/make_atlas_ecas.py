import datetime
import time
import random
import json

def create_mock_data():
  """
  - v, t: 2일 전부터 현재까지 5분 간격의 값과 시간
  - a: 약 1/3 확률로 발생하는 알람 시간
  """
  # --- 1. 시간 설정 ---
  # 현재 시간
  end_time = datetime.datetime.now()

  # 시작 시간: 2일 전 00시 04분 59초
  start_time = end_time - datetime.timedelta(days=2)
  start_time = start_time.replace(hour=0, minute=4, second=59, microsecond=0)

  # 5분 간격 설정
  time_interval = datetime.timedelta(minutes=5)

  # --- 2. 데이터 구조 초기화 ---
  mock_data = {
    "a": [], # 알람 시간 (ms)
    "v": [], # 값 (6.5-7.6 사이의 랜덤 값)
    "t": []  # 시간 (ms)
  }

  # --- 3. 데이터 생성 루프 ---
  current_time = start_time
  while current_time <= end_time:
    # 밀리초 단위 timestamp 생성
    js_timestamp = int(current_time.timestamp() * 1000)

    # 'v'와 't' 데이터 추가 (매 5분마다 항상 생성)
    # value = random.uniform(6.5, 7.6)
    value = round(random.uniform(6.5, 7.6), 6)
    mock_data["v"].append(value)
    mock_data["t"].append(js_timestamp)

    # 'a' 데이터 추가 (약 1/3 확률로 생성)
    if random.randint(1, 3) == 1:
      mock_data["a"].append(js_timestamp)

    # 다음 시간으로 5분 증가
    current_time += time_interval

  return mock_data

# --- 4. JSON으로 변환하여 출력 ---
if __name__ == "__main__":
  # MockData 생성
  chart_data = create_mock_data()

  # JSON 문자열로 변환 (보기 좋게 indent 적용)
  json_data = json.dumps(chart_data, indent=2)

  # 결과 출력
  print(json_data)

  # 파일로 저장
  with open("mock_data.json", "w") as f:
    f.write(json_data)

  print("Mock data has been created and saved to 'mock_data.json'.")

  # 생성된 데이터 개수 확인 (참고용)
  print("\n--- Data Counts ---")
  print(f"Value/Time points (v, t): {len(chart_data['v'])}")
  print(f"Alarm points (a): {len(chart_data['a'])}")
