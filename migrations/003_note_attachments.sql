-- ============================================================
--  003：一条笔记 = 标题 + 正文 + N 个附件
--
--  执行： venv/bin/python migrations/apply.py 003_note_attachments.sql
--  幂等，可重复执行。
-- ============================================================

-- 1) 笔记补上标题与完整正文（原来只有 200 字的 preview，正文碎在 note_embeddings 里）
ALTER TABLE notes ADD COLUMN IF NOT EXISTS title   VARCHAR(200);
ALTER TABLE notes ADD COLUMN IF NOT EXISTS content TEXT;

-- 2) 附件挂到笔记上；note_id 为空 = 独立附件（兼容旧数据）
--    extracted_text 预留给后期的 OCR / 语音转写，现在恒为 NULL
ALTER TABLE media_files ADD COLUMN IF NOT EXISTS note_id        VARCHAR(50) REFERENCES notes(id) ON DELETE CASCADE;
ALTER TABLE media_files ADD COLUMN IF NOT EXISTS position       INTEGER DEFAULT 0;
ALTER TABLE media_files ADD COLUMN IF NOT EXISTS extracted_text TEXT;

CREATE INDEX IF NOT EXISTS idx_media_note ON media_files(note_id);

-- 3) 老数据回填：把分块按 chunk_index 拼回正文
UPDATE notes n
SET content = sub.body
FROM (
    SELECT metadata->>'note_id' AS nid,
           string_agg(content, E'\n\n' ORDER BY COALESCE((metadata->>'chunk_index')::int, 0)) AS body
    FROM note_embeddings
    WHERE metadata ? 'note_id'
    GROUP BY 1
) sub
WHERE n.id = sub.nid
  AND (n.content IS NULL OR btrim(n.content) = '');

-- 4) 老数据回填：标题取正文（或 preview）的第一行
UPDATE notes
SET title = left(btrim(split_part(replace(coalesce(content, preview, ''), E'\r', ''), E'\n', 1)), 80)
WHERE title IS NULL OR btrim(title) = '';

UPDATE notes SET title = '未命名笔记' WHERE title IS NULL OR btrim(title) = '';
