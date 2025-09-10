import mysql.connector
import time
import json
from logging.handlers import TimedRotatingFileHandler
import os
import datetime

# --- DB 연결 정보 ---
DB_CONFIG = {
    'host': 'localhost',
    'user': 'ecas_user',
    'password': 'ecas_password',
    'database': 'ecas_db',
    'port': 3306
}

# --- 설정 ---
SCRIPT_NAME = os.path.basename(__file__)
CHECK_INTERVAL_SECONDS = 120  # 2분
STATUS_FILE_PATH = 'data/equipment_status.json'

def log_to_db(conn, level, message, eqp_id=None):
    """로그를 데이터베이스의 ecas_logs 테이블에 기록합니다."""
    insert_query = """
    INSERT INTO ecas_logs (log_level, source_script, eqp_id, message)
    VALUES (%s, %s, %s, %s)
    """
    try:
        cursor = conn.cursor()
        cursor.execute(insert_query, (level, SCRIPT_NAME, eqp_id, message))
        # autocommit=True 이므로 conn.commit()이 필요 없습니다.
        cursor.close()
    except mysql.connector.Error as err:
        # DB 로깅 실패 시, 최후의 수단으로 표준 출력에 에러를 표시합니다.
        print(f"!!! CRITICAL: FAILED TO LOG TO DATABASE: {err} !!!")
        print(f"!!! ORIGINAL LOG: [{level}] {message} !!!")

def connect_to_db():
    """데이터베이스에 연결을 시도하고 커넥션 객체를 반환"""
    while True:
        try:
            # autocommit=True를 추가하여 각 쿼리가 독립적인 트랜잭션으로 실행되도록 함. get_latest_statuses 함수의 "트랜잭션 스냅샵" 문제 해결.
            conn = mysql.connector.connect(**DB_CONFIG, autocommit=True)
            log_to_db(conn, 'INFO', "Successfully connected to the database.")
            return conn
        except mysql.connector.Error as err:
            print(f"Database connection failed: {err}")
            print("Retrying in 10 seconds...")
            time.sleep(10)

def get_latest_statuses(conn):
    """각 설비의 가장 최근 상태(pm_mode와 tm)를 조회"""
    statuses = {}
    query = """
    WITH RankedLogs AS (
        SELECT
            eqp_id,
            pm_mode,
            tm,
            ROW_NUMBER() OVER (PARTITION BY eqp_id ORDER BY tm DESC) as rn
        FROM
            atlas_ecas_raw
        WHERE
            pm_mode IS NOT NULL
    )
    SELECT
        eqp_id,
        pm_mode,
        tm
    FROM
        RankedLogs
    WHERE
        rn = 1;
    """
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query)
        for row in cursor.fetchall():
            # pm_mode와 tm을 함께 딕셔너리로 저장
            statuses[row['eqp_id']] = {
                'pm_mode': row['pm_mode'],
                'tm': row['tm']
            }
            # log_to_db(f"Fetched status for eqp_id {row['eqp_id']}: pm_mode={row['pm_mode']}, tm={row['tm']}")
        log_to_db(conn, 'INFO', f"Fetched latest statuses for {len(statuses)} equipments.")
    except mysql.connector.Error as err:
        log_to_db(conn, 'ERROR', f"Failed to fetch latest statuses: {err}")
    finally:
        if 'cursor' in locals() and cursor:
            cursor.close()
    return statuses

def load_previous_statuses(conn):
    """파일에서 이전 설비 상태를 로드"""
    try:
        status_dir = os.path.dirname(STATUS_FILE_PATH)
        if not os.path.exists(status_dir):
            os.makedirs(status_dir)
            
        with open(STATUS_FILE_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log_to_db(conn, 'WARNING', "Status file not found. Starting with an empty state.")
        return {}
    except json.JSONDecodeError:
        log_to_db(conn, 'ERROR', "Failed to decode status file. Starting with an empty state.")
        return {}

def save_current_statuses(statuses, conn):
    """현재 설비 상태를 파일에 저장"""
    try:
        with open(STATUS_FILE_PATH, 'w') as f:
            # datetime 객체를 JSON으로 저장하기 위해 default=str 사용
            json.dump(statuses, f, indent=4, default=str)
        log_to_db(conn, 'INFO', f"Successfully saved current statuses to {STATUS_FILE_PATH}")
    except IOError as e:
        log_to_db(conn, 'ERROR', f"Failed to save statuses to file: {e}")

def format_pm_mode(mode):
    """pm_mode 값을 사람이 읽기 쉬운 형태로 변환"""
    if mode == 1:
        return "ON"
    if mode == 0:
        return "OFF"
    if mode is None:
        return "RELEASED (NULL)"
    return str(mode)

def main():
    """메인 실행 함수"""
    db_connection = connect_to_db()
    log_to_db(db_connection, 'INFO', f"Mailer process '{SCRIPT_NAME}' started.")

    while True:
        try:
            if not db_connection.is_connected():
                log_to_db(db_connection, 'WARNING', "Database connection lost. Reconnecting...")
                db_connection = connect_to_db()

            log_to_db(db_connection, 'INFO', "Checking for pm_mode changes...")

            previous_statuses = load_previous_statuses(db_connection)
            current_statuses = get_latest_statuses(db_connection)

            if not current_statuses:
                log_to_db(db_connection, 'WARNING', "Could not fetch current statuses. Skipping this cycle.")
                time.sleep(CHECK_INTERVAL_SECONDS)
                continue

            # 변경된 설비 감지 및 메일 본문 생성
            for eqp_id, current_status in current_statuses.items():
                previous_status = previous_statuses.get(eqp_id, {})
                
                current_pm = current_status.get('pm_mode')
                previous_pm = previous_status.get('pm_mode', 'Not Available')
                # log_to_db(f"Equipment {eqp_id}: Previous PM: {previous_pm}, Current PM: {current_pm}")
                
                if previous_pm != current_pm:
                    change_time_str = current_status.get('tm', datetime.datetime.now().isoformat())
                    if isinstance(change_time_str, datetime.datetime):
                         change_time_str = change_time_str.strftime('%Y-%m-%d %H:%M:%S')

                    log_to_db(db_connection, 'WARNING', f"Change detected for {eqp_id}: from '{previous_pm}' to '{current_pm}'")

                    # --- 메일 본문 생성 ---
                    mail_subject = f"[ECAS PM 알림] 설비 {eqp_id}의 PM 모드 변경"
                    mail_body = f"""
                    안녕하세요.
                    
                    설비 {eqp_id}의 PM 모드가 변경되어 알림 메일을 보냅니다.
                    
                    - 변경 시간: {change_time_str}
                    - 설비 ID: {eqp_id}
                    - 이전 상태: {format_pm_mode(previous_pm)}
                    - 현재 상태: {format_pm_mode(current_pm)}
                    
                    감사합니다.
                    ECAS 모니터링 시스템
                    """

                    log_to_db(db_connection, 'INFO', "--- SENDING EMAIL (SIMULATION) ---")
                    log_to_db(db_connection, 'INFO', f"Subject: {mail_subject}")
                    log_to_db(db_connection, 'INFO', f"Body: {mail_body}")

            # 최신 상태를 파일에 저장
            save_current_statuses(current_statuses, db_connection)

            log_to_db(db_connection, 'INFO', f"Check complete. Waiting for {CHECK_INTERVAL_SECONDS} seconds.")
            time.sleep(CHECK_INTERVAL_SECONDS)

        except KeyboardInterrupt:
            log_to_db(db_connection, 'WARNING', "Process stopped by user.")
            break
        except Exception as e:
            log_to_db(db_connection, 'ERROR', f"An unexpected error occurred: {e}", exc_info=True)
            time.sleep(60)

    if db_connection and db_connection.is_connected():
        log_to_db(db_connection, 'INFO', "Database connection closed.")
        db_connection.close()

if __name__ == "__main__":
    main()
