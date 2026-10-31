-- ============================================================
--  004：找回密码验证码表
--
--  执行： venv/bin/python migrations/apply.py 004_password_resets.sql
--  幂等，可重复执行。
-- ============================================================

CREATE TABLE IF NOT EXISTS password_resets (
    id          SERIAL PRIMARY KEY,
    user_id     UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    email       VARCHAR(255) NOT NULL,
    code_hash   VARCHAR(64) NOT NULL,          -- 只存验证码的 sha256
    expires_at  DOUBLE PRECISION NOT NULL,     -- epoch 秒
    attempts    INTEGER DEFAULT 0,             -- 输错次数，满 5 次作废
    used_at     DOUBLE PRECISION,              -- 用过的时间，NULL 表示未使用
    created_at  DOUBLE PRECISION DEFAULT EXTRACT(EPOCH FROM NOW())
);

CREATE INDEX IF NOT EXISTS idx_pwreset_email ON password_resets (email, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pwreset_user  ON password_resets (user_id);
