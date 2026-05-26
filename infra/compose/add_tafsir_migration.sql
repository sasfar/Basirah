-- Add 'tafsir' to source_type check constraint

-- Drop the old constraint
ALTER TABLE corpus DROP CONSTRAINT IF EXISTS corpus_source_type_check;

-- Add new constraint with tafsir included
ALTER TABLE corpus ADD CONSTRAINT corpus_source_type_check
    CHECK (source_type IN ('quran', 'bukhari', 'muslim', 'tafsir'));

-- Verify
SELECT conname, pg_get_constraintdef(oid)
FROM pg_constraint
WHERE conrelid = 'corpus'::regclass AND conname = 'corpus_source_type_check';
