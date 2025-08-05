-- 데이터베이스가 존재하지 않으면 생성합니다.
CREATE DATABASE IF NOT EXISTS ecas_db;
-- 생성한 데이터베이스를 사용합니다.
USE ecas_db;

-- 기존 테이블이 존재하면 삭제합니다. (개발 편의성)
DROP TABLE IF EXISTS atlas_ecas_raw;

-- atlas_ecas_raw 테이블을 생성합니다.
CREATE TABLE atlas_ecas_raw (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,       -- 자동 증가하는 고유 식별자 (PK)
    eqp_id VARCHAR(255) NOT NULL,               -- 설비 ID
    tm DATETIME NOT NULL,                       -- 기록 시간
    val FLOAT,                                  -- 측정 값
    pm_mode TINYINT,                            -- PM 모드 (0: off, 1: on, NULL: 해제)

    -- eqp_id와 tm의 조합은 유일해야 함
    CONSTRAINT eqp_id_tm_unique UNIQUE (eqp_id, tm)
);

-- 데이터 조회 성능 향상을 위해 인덱스를 추가합니다.
CREATE INDEX idx_eqp_id_tm ON atlas_ecas_raw (eqp_id, tm DESC);
