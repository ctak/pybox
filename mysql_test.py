import mysql.connector
from mysql.connector import Error
from datetime import datetime

def main():
    """
    MySQL 데이터베이스에 연결하여 데이터를 삽입하고 조회하는 메인 함수
    """
    # ----------------------------------------------------
    # 1. 데이터베이스 연결 정보 설정
    # ----------------------------------------------------
    db_config = {
        'host': '127.0.0.1',
        'port': 3306,
        'user': 'root',
        'password': '1234', # 여기에 설정한 비밀번호를 입력하세요.
        'database': 'mydatabase'
    }

    connection = None
    try:
        # ----------------------------------------------------
        # 2. 데이터베이스에 연결
        # ----------------------------------------------------
        connection = mysql.connector.connect(**db_config)

        if connection.is_connected():
            print("MySQL 데이터베이스에 성공적으로 연결되었습니다.")
            cursor = connection.cursor()

            # ----------------------------------------------------
            # 3. 데이터 삽입 (INSERT) 💾
            # ----------------------------------------------------

            # --- `atlas_ecas` 테이블에 데이터 삽입 ---
            sql_insert_ecas = """
            INSERT INTO atlas_ecas (type, tm, val)
            VALUES (%s, %s, %s)
            """
            data_ecas = [
                ('temperature', datetime.now(), 25.5),
                ('humidity', datetime.now(), 60.2),
                ('pressure', datetime.now(), 1012.5)
            ]
            cursor.executemany(sql_insert_ecas, data_ecas)
            print(f"{cursor.rowcount}개의 데이터가 `atlas_ecas` 테이블에 삽입되었습니다.")

            # --- `atlas_ecas_alarms` 테이블에 데이터 삽입 ---
            sql_insert_alarms = """
            INSERT INTO atlas_ecas_alarms (type, tm, grade)
            VALUES (%s, %s, %s)
            """
            data_alarms = [
                ('high_temperature', datetime.now(), 1),
                ('low_pressure', datetime.now(), 2)
            ]
            cursor.executemany(sql_insert_alarms, data_alarms)
            print(f"{cursor.rowcount}개의 데이터가 `atlas_ecas_alarms` 테이블에 삽입되었습니다.")

            # 변경사항을 데이터베이스에 최종 반영 (커밋)
            connection.commit()

            print("\n" + "="*40 + "\n")

            # ----------------------------------------------------
            # 4. 데이터 조회 (SELECT) 🔍
            # ----------------------------------------------------

            # --- `atlas_ecas` 테이블 조회 ---
            print("--- [atlas_ecas] 테이블 데이터 조회 결과 ---")
            cursor.execute("SELECT id, type, tm, val FROM atlas_ecas;")
            records = cursor.fetchall()
            for row in records:
                print(f"ID: {row[0]}, Type: {row[1]}, Time: {row[2]}, Value: {row[3]}")

            print("\n")

            # --- `atlas_ecas_alarms` 테이블 조회 ---
            print("--- [atlas_ecas_alarms] 테이블 데이터 조회 결과 ---")
            cursor.execute("SELECT id, type, tm, grade FROM atlas_ecas_alarms;")
            records = cursor.fetchall()
            for row in records:
                print(f"ID: {row[0]}, Type: {row[1]}, Time: {row[2]}, Grade: {row[3]}")



            # ----------------------------------------------------
            # 5. 데이터 조회 (SELECT) - WHERE, ORDER BY 추가 🔍
            # ----------------------------------------------------

            print("\n")

            # --- `atlas_ecas` 테이블 조회 ---
            print("--- [atlas_ecas] 테이블 데이터 조회 (조건: type='temperature', 정렬: tm DESC) ---")

            # 조회할 조건을 변수로 설정
            search_type = 'temperature'

            # SQL 쿼리: WHERE 조건에는 %s 플레이스홀더를 사용하고, ORDER BY를 추가
            sql_select_query = """
            SELECT id, type, tm, val
            FROM atlas_ecas
            WHERE type = %s
            ORDER BY tm DESC
            """

            # execute 메서드의 두 번째 인자로 파라미터를 튜플 형태로 전달
            cursor.execute(sql_select_query, (search_type,))

            records = cursor.fetchall()

            if not records:
                print(f"'{search_type}' 타입의 데이터를 찾을 수 없습니다.")
            else:
                for row in records:
                    print(f"ID: {row[0]}, Type: {row[1]}, Time: {row[2]}, Value: {row[3]}")


    except Error as e:
        print(f"데이터베이스 연결 또는 작업 중 오류 발생: {e}")

    finally:
        # ----------------------------------------------------
        # 5. 연결 종료
        # ----------------------------------------------------
        if connection and connection.is_connected():
            cursor.close()
            connection.close()
            print("\nMySQL 연결이 종료되었습니다.")


if __name__ == '__main__':
    main()