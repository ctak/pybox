import time
import random

# ANSI 이스케이프 코드 정의
CURSOR_UP_ONE = '\x1b[1A'
ERASE_LINE = '\x1b[2K'

services = {
    "database": "Pulling fs layer",
    "backend": "Waiting",
    "frontend": "Waiting"
}

# 처음 3줄을 출력하기 위해 빈 줄을 만듭니다.
print("\n" * len(services))

try:
    while True:
        # 상태를 랜덤하게 업데이트 (실제로는 Docker의 상태겠죠)
        if services["database"] == "Running" and random.random() < 0.5:
            services["backend"] = "Building"
        if services["backend"] == "Building" and random.random() < 0.7:
            services["backend"] = "Running"
        if services["backend"] == "Running" and random.random() < 0.5:
            services["frontend"] = "Running"

        # --- 핵심 부분 ---
        # 1. 서비스 개수만큼 커서를 위로 올립니다.
        print(CURSOR_UP_ONE * len(services), end="")

        # 2. 각 줄을 지우고 새로운 내용으로 덮어씁니다.
        for name, status in services.items():
            print(f"{ERASE_LINE}Service '{name}': {status}")
        # ----------------

        if services["frontend"] == "Running":
            print("All services are running!")
            break

        time.sleep(0.5)

        # 상태 업데이트 (예시)
        if "Pulling" in services["database"]:
            services["database"] = "Running"

except KeyboardInterrupt:
    print("\nProcess interrupted by user.")
