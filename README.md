# Resume Customiser — Claude Code Skill

Local-first resume tailoring powered by Claude Code (Pro subscription). No API cost.  
Tailors your resume to a specific job description without inventing facts.

## What it does

1. Reads your base resume (DOCX or PDF)
2. Reads the job description (URL or paste)
3. Analyses both in context — role requirements vs your evidence
4. Produces a match/gap table
5. Rewrites your resume using only existing evidence (no fabrication)
6. Saves an ATS-safe DOCX + tracks the application

## Requirements

- [Claude Code](https://claude.ai/code) with Pro subscription
- Python 3.9+
- Git (optional, for versioning your applications)

## Install

```bash
git clone https://github.com/harsh779/resume-customiser
cd resume-customiser
python install.py
```

Restart Claude Code. Done.

## Usage

Open Claude Code in any directory and type:

```
/resume-customise
```

Choose **Single** (one job) or **Batch** (multiple jobs from CSV).

### Single mode
Provide when prompted:
- Resume file path (DOCX or PDF)
- JD — URL or paste text directly
- Company name + role title

### Batch mode
Fill `batch_jobs_template.csv`:

```csv
company,role,jd
Google,Senior Analyst,https://careers.google.com/jobs/...
Unilever,Insights Manager,We are looking for an Insights Manager who...
McKinsey,Associate,C:\path\to\mckinsey_jd.txt
```

The `jd` column accepts:
- **URL** — scraped automatically (most company career pages work)
- **Inline text** — paste JD text directly in the cell
- **File path** — path to a `.txt` file with the JD

> **Note:** LinkedIn, Indeed, Glassdoor, and ATS platforms block scraping. Paste JD text for these.

### Tracker commands

Say these in Claude Code chat:

```
show my applications          → full application table
show stats                    → pipeline summary
view application #3           → full detail
update application #3 to applied
update application #3 to interview
```

Status flow: `tailored → applied → phone_screen → interview → offer → rejected / withdrawn`

## Output

Each run creates:
```
<applications_repo>/
└── Google_SeniorAnalyst_2026-04-26/
    ├── Harsh_Google.docx      ← your tailored resume
    └── jd.txt                 ← JD saved for reference
```

Plus an entry in `applications.json` tracker.

## Key rules (enforced by the skill)

- Every bullet point must trace to your base resume
- Experience chronology is never changed
- No skills, tools, or metrics are invented
- Gaps are flagged explicitly, not fabricated

## Files

| File | Purpose |
|---|---|
| `install.py` | One-time installer — sets paths, installs deps, creates repo |
| `resume-customise.md` | Claude Code command (workflow instructions) |
| `scripts/parse_resume.py` | Extracts text from DOCX/PDF |
| `scripts/fetch_jd.py` | Fetches JD from URL or file |
| `scripts/build_docx.py` | Builds ATS-safe single-column DOCX |
| `scripts/tracker.py` | Application tracker (add/list/update/view/stats) |
| `scripts/setup.py` | Python dependency installer |
| `batch_jobs_template.csv` | Batch mode template |

## License

MIT
