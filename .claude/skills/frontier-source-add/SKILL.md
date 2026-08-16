# /frontier-source-add

**When to invoke:** Every time a new data source is added to the pipeline. One invocation per source.

---

## What This Skill Does

Guides the end-to-end addition of a single new data source — from feasibility check through implementation, testing, and integration into the digest pipeline.

---

## Steps

### 1. Identify the Source
Ask the user:
```
1. Which source are we adding? (name and URL)
2. What type is it?
   a) RSS / Atom feed
   b) Public REST API (e.g., Reddit API, YouTube Data API)
   c) Web scraping (last resort — fragile)
   d) Newsletter / email ingestion
3. Which topic domains from ideas_v2.md does this source cover?
   (e.g., "Agentic AI", "New Models", "Research Papers")
4. How often does this source publish? (helps calibrate expected item volume)
```

### 2. Feasibility Check
Before writing code:
- Check if the source has a public API or RSS feed (preferred over scraping)
- Check API rate limits and authentication requirements
- Check if the source is already in `ideas_v2.md` source list
- Check if a fetcher for this source type already exists in `backend/app/services/fetchers/`
  - If yes, a new source using the same type can reuse the base class

Report findings to the user. If scraping is the only option, ask for explicit approval.

### 3. Plan the Fetcher
Before writing code, outline:
- File name: `backend/app/services/fetchers/<source_name>.py`
- Class name: `<SourceName>Fetcher`
- Must extend `BaseFetcher` (defined in `fetchers/base.py`)
- Fields the fetcher must return for each item:
  - `title: str`
  - `summary: str` (raw text, before LLM synthesis)
  - `source_name: str` (e.g., "arXiv", "Yannic Kilcher")
  - `source_url: str` (direct URL to the specific item — not the homepage)
  - `domain_tags: list[str]` (from the topic list in ideas_v2.md)
  - `published_at: datetime`
  - `content_type: str` (e.g., "video", "paper", "post", "newsletter")

### 4. Implement the Fetcher
- Create `backend/app/services/fetchers/<source_name>.py`
- Handle: authentication, rate limits, timeouts (default: 10s), empty responses, source downtime
- Fetcher failure must raise a typed exception — never swallow errors silently
- Add the source to the source registry (ask where this lives if not yet created)

### 5. Write Tests
Create `backend/tests/fetchers/test_<source_name>.py`:
- Test successful fetch with mocked response
- Test empty response handling
- Test timeout handling
- Test rate limit handling (if applicable)
- Test that all required fields are populated on the returned items

### 6. Run Reviews
- ECC `ecc:python-reviewer` on the new fetcher file
- ECC `ecc:silent-failure-hunter` to confirm errors are not swallowed

### 7. Sample Output Check
Run the fetcher against the live source (or a recorded fixture) and show the user a sample of 3–5 fetched items. Ask:
```
"Here are 3 sample items from [source name]:
[show sample]

Does this look right? Are these the kind of items you want surfaced?"
```

Wait for confirmation before considering the source complete.

### 8. Integration
- Add the new source to the scheduler's source list
- Confirm it appears correctly in a test digest run
- Run `/frontier-digest-review` after integration

---

## Related ECC Skills
- `ecc:python-reviewer` — Review the fetcher implementation
- `ecc:silent-failure-hunter` — Verify error handling is correct
- `ecc:database-reviewer` — If the fetcher adds new DB fields
- `/frontier-digest-review` — Verify the new source's items appear correctly in the digest
