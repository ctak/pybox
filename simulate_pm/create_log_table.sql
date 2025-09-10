-- ECAS 시스템의 모든 로그를 저장하기 위한 테이블
CREATE TABLE IF NOT EXISTS ecas_logs (
    -- 고유 식별자 (PK), 로그가 많아질 것을 대비해 BIGINT 사용
    log_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- 로그가 기록된 시간 (기본값으로 현재 시간이 자동 입력됨)
    log_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- 로그 레벨 (INFO, WARNING, ERROR 등)
    log_level VARCHAR(10) NOT NULL,
    
    -- 로그를 발생시킨 스크립트 이름 (예: 'mailer.py')
    source_script VARCHAR(50),
    
    -- 로그와 관련된 설비 ID (관련이 없는 로그는 NULL이 될 수 있음)
    eqp_id VARCHAR(255),
    
    -- 실제 로그 메시지 (오류 스택 트레이스 등 긴 메시지를 위해 TEXT 타입 사용)
    message TEXT,
    
    -- 빠른 조회를 위한 인덱스 설정
    INDEX idx_log_time (log_time),
    INDEX idx_log_level (log_level),
    INDEX idx_eqp_id (eqp_id)
);
