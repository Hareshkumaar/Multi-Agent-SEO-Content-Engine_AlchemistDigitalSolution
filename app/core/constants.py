"""Every limit, name and label that could change lives here. Nothing is hardcoded elsewhere."""

# SEO limits
TITLE_MAX = 60
DESC_MAX = 155
FIRST_WORDS = 100
MIN_WORDS = 1000
TARGET_WORDS = 1300

# Critic loop
PASS_SCORE = 80
CAP_SCORE = PASS_SCORE - 1      # score ceiling when a hard check fails
MAX_REVISIONS = 1

# LLM calls
LLM_RETRIES = 2                 # extra attempts after invalid JSON
LLM_MAX_TOKENS = 8192
HTTP_RETRIES = 5
MAX_WAIT = 60                   # longest single wait in seconds
REASONING_EFFORT = "low"        # fewer hidden tokens on gpt-oss models
HTTP_BACKOFF = 2                # seconds, doubled each retry
HTTP_TIMEOUT = 120
RETRY_STATUS = (429, 500, 502, 503)

# Reference URLs
MAX_REF_URLS = 3
REF_CHARS = 4000

# Domain values
INTENTS = ("Informational", "Commercial", "News Analysis")
MODES = ("english", "bilingual")
STATUSES = ("draft", "approved", "published")
ALLOWED = {"draft": ["approved"], "approved": ["published", "draft"]}
ACTION_LABELS = {"approved": "Approve", "published": "Publish", "draft": "Back to draft"}
EXPORT_FORMATS = ("md", "html", "json")
EXPORTABLE = ("approved", "published")
RUBRIC = ("keyword_placement", "readability", "factual_consistency", "fluff")

# Pipeline
PIPELINE = ("researcher", "outliner", "writer", "critic")
LABELS = {"researcher": "Researching", "outliner": "Outlining", "writer": "Drafting", "critic": "Reviewing"}

# Database
T_ARTICLES = "articles"
T_RUNS = "agent_runs"
LIST_COLS = "id, topic, search_intent, quality_score, status, created_at"
