# 패킹과 언패킹
# 파이썬에서 *와 **는 함수의 인자를 처리하는 데 사용되는 특별한 문법입니다.
# *args는 위치 인자를 튜플로 패킹하고, **kwargs는 키워드 인자를 딕셔너리로 패킹합니다.
def add_all(*args):
  print(f"전달받은 인자들 (튜플): {args}")
  print(f"타입: {type(args)}")

  total = 0
  for num in args:
    total += num
  return total

# 다양한 개수의 인자로 함수 호출
print(f"결과: {add_all(1, 2, 3)}")
print("-" * 20)
print(f"결과: {add_all(10, 20, 30, 40, 50)}")

print("-" * 20)

def print_user_info(**kwargs):
  print(f"전달받은 키워드 인자들 (딕셔너리): {kwargs}")
  print(f"타입: {type(kwargs)}")

  for key, value in kwargs.items():
    print(f"{key}: {value}")

# 다양한 키워드 인자로 함수 호출
print_user_info(name="Alice", age=30, city="Seoul")
print("-" * 20)
print_user_info(name="Bob", age=25, job="Engineer", country="Korea")

print("-" * 20)
print("-" * 20)

# *args 와 **kwargs 함께 사용하기
# 일반 인수, *args, **kwargs 는 함께 사용될 수 있으며, 반드시 정해진 순서를 지켜야 합니다.
#
# 순서: 일반 위치 인수 -> *args -> 일반 키워드 인수 -> **kwargs
def process_data(user_id, *items, status="pending", **details):
    print(f"User ID: {user_id}")
    print(f"Items (tuple): {items}")
    print(f"Status: {status}")
    print(f"Details (dict): {details}")
# 함수 호출 예시
process_data(1, "item1", "item2", status="completed", location="Seoul", priority="high")
print("-" * 20)
process_data(2, 'apple', 'banana', 'cherry', notes="Urgent", tags=["fruit", "fresh"])
print("-" * 20)

#
# 언패킹
#
def calulate(a, b, c):
  return a + b + c

numbers = [2, 3, 4]
# 언패킹 사용
result = calulate(*numbers)
print(f"결과: {result}")
print("-" * 20)
# 딕셔너리 언패킹: 딕셔너리의 키는 반드시 함수의 파라미터 이름과 일치해야 합니다.
def greet(name, greeting):
  print(f"{greeting}, {name}!")

user_data = {"name": "Charlie", "greeting": "Hello"}
greet(**user_data)
print("-" * 20)
