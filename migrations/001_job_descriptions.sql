CREATE TABLE IF NOT EXISTS job_descriptions (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    profile_id   UUID REFERENCES profiles(id) ON DELETE CASCADE,
    company      TEXT NOT NULL,
    role         TEXT NOT NULL,
    description  TEXT NOT NULL,
    requirements JSONB DEFAULT '[]',
    created_at   TIMESTAMPTZ DEFAULT now(),
    updated_at   TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_jobs_profile_id ON job_descriptions(profile_id);
