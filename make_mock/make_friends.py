# iyagibox 에서 python 을 이용하여 mock.json 을 만들기.
from faker import Faker
import pandas as pd

# Faker 초기화
fake = Faker("ko_KR")

# 데이터 생성 함수
def generate_fake_data(num_records):
  data = []
  for idx in range(num_records):
    person = {
      "_id": idx + 1,
      "avatar_nm": fake.name(),
      "age": fake.random_int(min=18, max=99),
      "address": fake.address(),
      "email": fake.email(),
      "phone_number": fake.phone_number(),
      "job": fake.job(),
      "company": fake.company(),
      "birthdate": fake.date_of_birth(minimum_age=18, maximum_age=99).isoformat(),
      "gender": fake.random_element(elements=["M", "F"]),
      "status": fake.random_element(elements=["on", "off"]),
      "region": fake.random_element(elements=["02", "051", "032", "042", "053", "062", "052", "031", "033", "041", "061", "055", "064"]),
      # "last_activity_time": fake.date_time_between(start_date="-1y", end_date="now").isoformat()
      "last_activity_time": fake.date_time_between(start_date="-1y", end_date="-1d").isoformat()
    }
    data.append(person)
  return data

# 메인 스크립트
def main():
  # num_people = 10_000 # 생성할 사람의 수
  num_people = 100_000 # 생성할 사람의 수
  print(f"{num_people}명의 데이터를 생성 중...")

  # 가짜 데이터 생성
  fake_data = generate_fake_data(num_people)

  # Pandas DataFrame 생성
  df = pd.DataFrame(fake_data)

  # JSON 파일로 저장
  # output_file = "fake_people_data.json"
  output_file = "fake_people_data_10.json"
  df.to_json(output_file, orient="records", indent=4, force_ascii=False)

  print(f"데이터가 JSON 파일로 저장되었습니다: {output_file}")

if __name__ == "__main__":
  main()
