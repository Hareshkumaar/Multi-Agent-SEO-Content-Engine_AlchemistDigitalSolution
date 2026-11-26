-- Run this once in the Supabase SQL editor.
create table if not exists articles (
  id bigint generated always as identity primary key,
  topic text not null,
  target_keyword text,
  search_intent text check (search_intent in ('Informational','Commercial','News Analysis')),
  meta_title text check (char_length(meta_title) <= 60),
  meta_description text check (char_length(meta_description) <= 155),
  outline_json jsonb,
  content_markdown text,
  bilingual_summary text,
  quality_score int check (quality_score between 0 and 100),
  status text not null default 'draft' check (status in ('draft','approved','published')),
  created_at timestamptz not null default now(),
  -- extra columns used by the dashboard
  audience text,
  tone text,
  mode text default 'english',
  research_brief_json jsonb,
  critic_report_json jsonb,
  updated_at timestamptz not null default now()
);

create table if not exists agent_runs (
  id bigint generated always as identity primary key,
  article_id bigint not null references articles(id) on delete cascade,
  agent_name text not null check (agent_name in
    ('researcher','outliner','writer','critic','writer_revision','critic_reaudit')),
  input_tokens int,
  output_tokens int,
  latency_ms int,
  critic_feedback_json jsonb,
  created_at timestamptz not null default now()
);

create index if not exists agent_runs_article_idx on agent_runs (article_id);
create index if not exists articles_status_idx on articles (status, created_at desc);

grant usage on schema public to service_role;
grant all on table public.articles to service_role;
grant all on table public.agent_runs to service_role;
grant usage, select on all sequences in schema public to service_role;
