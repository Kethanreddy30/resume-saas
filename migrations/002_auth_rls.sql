-- Run after Supabase Auth is enabled. Backfill user_id for existing rows before enforcing RLS.

ALTER TABLE profiles ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
ALTER TABLE job_descriptions ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);
ALTER TABLE uploads ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES auth.users(id);

CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_uploads_user_id ON uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_user_id ON job_descriptions(user_id);

-- Drop permissive policies before applying isolation (adjust policy names to match your project).
-- DROP POLICY IF EXISTS "Allow all" ON profiles;
-- DROP POLICY IF EXISTS "Allow all" ON uploads;
-- DROP POLICY IF EXISTS "Allow all" ON job_descriptions;

ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE job_descriptions ENABLE ROW LEVEL SECURITY;

CREATE POLICY profiles_isolation ON profiles
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY uploads_isolation ON uploads
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());

CREATE POLICY jobs_isolation ON job_descriptions
    FOR ALL
    USING (user_id = auth.uid())
    WITH CHECK (user_id = auth.uid());
