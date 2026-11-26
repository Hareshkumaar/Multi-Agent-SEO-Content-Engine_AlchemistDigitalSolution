"""Hard-check rules and the score cap. Each rule: (passes?, issue text, fix text)."""
from statistics import mean

from app.core.constants import CAP_SCORE, DESC_MAX, MIN_WORDS, RUBRIC, TARGET_WORDS, TITLE_MAX
from app.schemas.critic import CriticReport

RULES = (
    (lambda c: c["word_count"] >= MIN_WORDS,
     "Article has {word_count} words, minimum is %d." % MIN_WORDS,
     "Expand the sections using facts from the brief to about %d words." % TARGET_WORDS),
    (lambda c: c["kw_in_h1"],
     "Primary keyword is missing from the H1.", "Put the exact primary keyword in the H1."),
    (lambda c: c["kw_in_first_100"],
     "Primary keyword is missing from the first 100 words.", "Use the exact primary keyword in the opening paragraph."),
    (lambda c: c["meta_title_len"] <= TITLE_MAX,
     "Meta title is {meta_title_len} characters.", "Shorten the meta title to %d characters." % TITLE_MAX),
    (lambda c: c["meta_description_len"] <= DESC_MAX,
     "Meta description is {meta_description_len} characters.", "Shorten the meta description to %d characters." % DESC_MAX),
)


def hard_failures(checks: dict) -> list[dict]:
    """Feedback items (same shape as the Critic's) for every failed hard check."""
    return [{"issue": issue.format(**checks), "fix": fix, "severity": "high"}
            for ok, issue, fix in RULES if not ok(checks)]


def final_score(report: CriticReport, failures: list) -> int:
    score = round(mean(getattr(report, k) for k in RUBRIC))
    return min(score, CAP_SCORE) if failures else score
