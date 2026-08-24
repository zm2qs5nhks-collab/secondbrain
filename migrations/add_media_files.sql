-- 迁移脚本：添加 media_files 表
-- 在服务器上执行: psql -U secondbrain -d secondbrain -f migrations/add_media_files.sql

CREATE TABLE IF NOT EXISTS media_files (
    file_id VARCHAR(20) PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    original_name VARCHAR(500) NOT NULL,
    saved_name VARCHAR(200) NOT NULL,
    file_path TEXT NOT NULL,
    media_type VARCHAR(20) NOT NULL,
    file_size BIGINT DEFAULT 0,
    tags JSONB DEFAULT '[]',
    importance VARCHAR(20) DEFAULT 'normal',
    description TEXT DEFAULT '',
    created_at DOUBLE PRECISION DEFAULT EXTRACT(EPOCH FROM NOW())
);

CREATE INDEX IF NOT EXISTS idx_media_user ON media_files(user_id);
CREATE INDEX IF NOT EXISTS idx_media_type ON media_files(media_type);
