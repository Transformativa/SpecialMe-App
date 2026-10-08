# SpecialMe laws data and refresh

US-only laws on disability, special education, IEP, 504 and accommodations. Federal in `data/federal.json`, 50 states + DC in `data/states.json`. `data/sources.json` lists what is watched. Not legal advice.

## Status
- Federal: checked against official or primary pages on 2026-10-08. Items with a `gap` field still need confirming.
- States: `agent_researched_needs_human_review`. Collected from official state sites by research agents. Each record has `gaps`. A human or attorney must review before the app drops the "Pending human review" label.

## Refresh loop (every 6 months, Jan 1 and Jul 1; .github/workflows/laws-refresh.yml)
1. `scripts/check_updates.py` queries the Federal Register API (190-day lookback, topic queries in sources.json) and hashes ~200 official pages (federal pages plus each state's agency, rights, rules and dispute pages).
2. Changes, new Federal Register items and unreachable pages go to `review/REPORT.md` and open a GitHub issue labelled `laws-review`.
3. A person opens each item, edits `data/*.json`, updates `verified_at` / `last_verified`, and closes the issue. The script never edits law text itself.
4. `scripts/build_app_data.py` validates (51 jurisdictions, https links) and writes `data/laws.bundle.json`, which the app embeds or fetches.

First run only saves a baseline. Some state sites block bots (403) or need JavaScript, so they show as "unreachable" and need a manual look.

## Not covered yet
Court decisions beyond the Supreme Court, state legislation tracking (bills), local district policies, Spanish and other translations.
