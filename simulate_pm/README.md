# **ECAS 설비 데이터 시뮬레이션 및 PM 모드 변경 알림**

이 프로젝트는 ECAS 설비 데이터를 시뮬레이션하여 MySQL 데이터베이스에 저장하고, 특정 설비의 pm_mode가 변경될 때 이를 감지하여 알림(메일 본문 생성)을 보내는 두 개의 파이썬 스크립트로 구성됩니다.

## **프로젝트 구조**

.  
├── data/  
│ └── equipment_status.json \# mailer가 상태 비교를 위해 사용하는 파일  
├── logs/  
│ ├── data_inserter.log \# 데이터 생성 스크립트 로그  
│ └── mailer.log \# 메일링 스크립트 로그  
├── docker-compose.yml \# Docker 실행 환경 설정  
├── init.sql \# DB 테이블 자동 생성을 위한 스크립트  
├── data_inserter.py \# 5분마다 DB에 데이터를 삽입하는 스크립트  
├── mailer.py \# 2분마다 pm_mode 변경을 감지하는 스크립트  
└── README.md \# 프로젝트 설명서

## **요구사항**

- Docker
- Docker Compose
- Python 3.7+
- mysql-connector-python 라이브러리

## **실행 방법**

### **1\. Python 라이브러리 설치**

스크립트 실행에 필요한 파이썬 라이브러리를 설치합니다.

pip install mysql-connector-python

### **2\. Docker 컨테이너 실행**

프로젝트의 루트 디렉토리에서 아래 명령어를 실행하여 MySQL 데이터베이스 서버를 백그라운드에서 실행합니다.

docker-compose up \-d

- 이 명령은 docker-compose.yml 파일을 읽어 ecas_mysql_db라는 이름의 MySQL 컨테이너를 생성하고 실행합니다.
- 최초 실행 시 init.sql 스크립트가 자동으로 실행되어 ecas_db 데이터베이스와 atlas_ecas_raw 테이블을 생성합니다.
- DB 접속 정보:
  - Host: localhost
  - Port: 3306
  - User: ecas_user
  - Password: ecas_password
  - Database: ecas_db

### **3\. 스크립트 실행**

각각의 파이썬 스크립트를 별도의 터미널에서 실행합니다.

**터미널 1: 데이터 생성 스크립트 실행**

python data_inserter.py

- 이 스크립트는 5분마다 100개 설비의 데이터를 생성하여 DB에 삽입합니다.
- 로그는 logs/data_inserter.log 파일에 기록됩니다.

**터미널 2: 변경 감지 및 메일링 스크립트 실행**

python mailer.py

- 이 스크립트는 2분마다 DB를 확인하여 pm_mode가 변경된 설비가 있는지 확인합니다.
- 변경이 감지되면, 메일 제목과 본문을 터미널에 출력합니다.
- 설비의 최종 상태는 data/equipment_status.json 파일에 저장되어 다음 실행 시 비교 데이터로 사용됩니다.
- 로그는 logs/mailer.log 파일에 기록됩니다.

### **4\. 실행 중지**

스크립트를 중지하려면 각 터미널에서 Ctrl \+ C를 누릅니다.

Docker 컨테이너를 중지하고 관련 리소스(네트워크, 볼륨 등)를 삭제하려면 아래 명령어를 실행하세요.

docker-compose down
