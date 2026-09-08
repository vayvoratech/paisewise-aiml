CREATE TABLE IF NOT EXISTS audit_log (
    id              BIGSERIAL       PRIMARY KEY,
    user_id         UUID,
    action          VARCHAR(60)     NOT NULL,
    entity_type     VARCHAR(30)     NOT NULL,
    entity_id       UUID,
    old_values      JSONB,
    new_values      JSONB,
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    device_id       VARCHAR(200),
    session_id      VARCHAR(100),
    request_id      VARCHAR(100),
    result          VARCHAR(10)     NOT NULL DEFAULT 'SUCCESS' CHECK (result IN ('SUCCESS', 'FAILURE')),
    failure_reason  TEXT,
    created_at      TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);


CREATE INDEX IF NOT EXISTS idx_audit_log_user_id
    ON audit_log(user_id, created_at DESC)
    WHERE user_id IS NOT NULL;

-- Security monitoring: all failed logins
CREATE INDEX IF NOT EXISTS idx_audit_log_failures
    ON audit_log(action, result, created_at DESC)
    WHERE result = 'FAILURE';

-- all actions on a specific order or entity
CREATE INDEX IF NOT EXISTS idx_audit_log_entity
    ON audit_log(entity_type, entity_id, created_at)
    WHERE entity_id IS NOT NULL;

-- Time-based queries
CREATE INDEX IF NOT EXISTS idx_audit_log_created_at
    ON audit_log(created_at DESC);
