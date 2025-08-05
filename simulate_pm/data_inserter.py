import mysql.connector
import time
import random
import datetime
import logging
from logging.handlers import TimedRotatingFileHandler
import os

# --- 로깅 설정 ---
def cleanup_old_logs(log_dir, days_to_keep):
    """지정된 기간보다 오래된 로그 파일을 삭제하는 함수"""
    if not os.path.exists(log_dir):
        return
    
    cutoff = time.time() - (days_to_keep * 24 * 60 * 60)
    
    try:
        for filename in os.listdir(log_dir):
            file_path = os.path.join(log_dir, filename)
            if os.path.isfile(file_path):
                if os.path.getmtime(file_path) < cutoff:
                    os.remove(file_path)
                    print(f"Deleted old log file: {file_path}") # 로거 설정 전이므로 print 사용
    except Exception as e:
        print(f"Error cleaning up old log files: {e}")

def setup_logger(name, log_file, level=logging.INFO):
    """일일 롤링 로그를 설정하고, 7일 지난 로그를 정리합니다."""
    log_dir = os.path.dirname(log_file)
    # 스크립트 시작 시 7일 지난 로그 파일 정리
    cleanup_old_logs(log_dir, 7)
    # 로그 파일이 저장될 디렉토리 생성
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=30)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)
    return logger

logger = setup_logger('DataInserter', 'logs/data_inserter.log')

# --- DB 연결 정보 ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'ecas_user',
    'password': 'ecas_password',
    'database': 'ecas_db',
    'port': 3306
}

# --- 시뮬레이션 설정 ---
NUM_EQUIPMENTS = 100
INSERT_INTERVAL_SECONDS = 300  # 5분
EQUIPMENT_IDS = [f'EQP-{i:03d}' for i in range(1, NUM_EQUIPMENTS + 1)]

# 각 설비의 PM 모드 상태를 저장 (메모리)
# 초기 상태는 모두 OFF (0)으로 설정 후, DB와 동기화
equipment_pm_states = {eqp_id: 0 for eqp_id in EQUIPMENT_IDS}

def connect_to_db():
    """데이터베이스에 연결을 시도하고 커넥션 객체를 반환"""
    while True:
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            logger.info("Successfully connected to the database.")
            return conn
        except mysql.connector.Error as err:
            logger.error(f"Database connection failed: {err}")
            logger.info("Retrying in 10 seconds...")
            time.sleep(10)

def sync_initial_pm_states(conn):
    """DB에서 최신 PM 모드 상태를 가져와 메모리와 동기화"""
    logger.info("Syncing initial PM mode states from database...")
    query = """
    WITH RankedLogs AS (
        SELECT
            eqp_id,
            pm_mode,
            ROW_NUMBER() OVER (PARTITION BY eqp_id ORDER BY tm DESC) as rn
        FROM
            atlas_ecas_raw
        WHERE
            pm_mode IS NOT NULL
    )
    SELECT
        eqp_id,
        pm_mode
    FROM
        RankedLogs
    WHERE
        rn = 1;
    """
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        updated_count = 0
        for row in cursor.fetchall():
            eqp_id = row['eqp_id']
            pm_mode = row['pm_mode']
            if eqp_id in equipment_pm_states:
                equipment_pm_states[eqp_id] = pm_mode
                updated_count += 1
        logger.info(f"Successfully synced PM modes for {updated_count} equipments.")
    except mysql.connector.Error as err:
        logger.error(f"Failed to sync initial PM states: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()

def insert_simulation_data(conn):
    """100개 설비의 시뮬레이션 데이터를 DB에 삽입"""
    cursor = conn.cursor()
    insert_query = """
    INSERT INTO atlas_ecas_raw (eqp_id, tm, val, pm_mode)
    VALUES (%s, %s, %s, %s)
    """
    
    records_to_insert = []
    current_time = datetime.datetime.now()

    for eqp_id in EQUIPMENT_IDS:
        changed = False
        # 1/10 확률로 pm_mode 상태 변경
        if random.randint(1, 10) == 1:
            current_state = equipment_pm_states.get(eqp_id)
            # 현재 ON(1)이면 NULL(해제)로, 아니면 ON(1)으로 변경
            new_state = 0 if current_state == 1 else 1
            equipment_pm_states[eqp_id] = new_state
            logger.info(f"PM mode for {eqp_id} changed from {current_state} to {new_state}")
            changed = True

        # 데이터 생성
        tm = current_time
        val = round(random.uniform(100.0, 500.0), 2) if not changed else None
        pm_mode = equipment_pm_states.get(eqp_id) if changed else None

        records_to_insert.append((eqp_id, tm, val, pm_mode))

    try:
        cursor.executemany(insert_query, records_to_insert)
        conn.commit()
        logger.info(f"Successfully inserted {cursor.rowcount} records.")
    except mysql.connector.Error as err:
        logger.error(f"Failed to insert data: {err}")
        conn.rollback()
    finally:
        cursor.close()

def main():
    """메인 실행 함수"""
    logger.info("Data inserter process started.")
    db_connection = connect_to_db()

    # 스크립트 시작 시, DB의 최신 상태와 동기화
    sync_initial_pm_states(db_connection)
    
    while True:
        try:
            # DB 연결이 끊어졌는지 확인하고 재연결
            if not db_connection.is_connected():
                logger.warning("Database connection lost. Reconnecting...")
                db_connection = connect_to_db()
            
            insert_simulation_data(db_connection)
            
            logger.info(f"Waiting for {INSERT_INTERVAL_SECONDS} seconds for the next cycle.")
            time.sleep(INSERT_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            logger.info("Process stopped by user.")
            break
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            # 예기치 않은 오류 발생 시 잠시 대기 후 재시도
            time.sleep(60)

    if db_connection and db_connection.is_connected():
        db_connection.close()
        logger.info("Database connection closed.")

if __name__ == "__main__":
    main()
