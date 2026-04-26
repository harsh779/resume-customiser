# Resume Customiser — Claude Code Skill

**A local-first career operating system for evidence-based, ATS-safe job applications.**

Tailors your resume to any job description — without inventing facts, skills, tools, or metrics you don't actually have.

[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue)](https://www.python.org/)
[![Claude Code](https://img.shields.io/badge/powered%20by-Claude%20Code-orange)](https://claude.ai/code)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)

---

## Why This Exists

Sending the same resume to every job is ineffective. Manually rewriting it for each application is slow. Generic AI resume tools hallucinate credentials and produce undefendable claims.

This tool solves all three:

- Your base resume is the **single source of truth** — nothing is added that isn't already there
- JD analysis is contextual, not keyword matching — it understands what the role actually needs
- Outputs a clean, ATS-safe DOCX — ready to send

---

## Core Features

| Feature | Description |
|---|---|
| JD ingestion | URL, pasted text, or local `.txt` file |
| Fit analysis | Contextual match/gap table per role |
| Resume tailoring | Reframes and reprioritises existing content only |
| DOCX output | ATS-safe, single-column Word document |
| Application tracking | Full pipeline tracker with status flow |
| Batch processing | Process multiple jobs from a CSV |
| Anti-fabrication rules | Hard constraints — no invented claims, ever |

---

## How It Works

```
Your Base Resume (DOCX or PDF)
         │
         ▼
  Claude Code reads resume context
         │
         ▼
  Job Description (URL / paste / .txt file)
         │
         ▼
  JD Analysis — role, skills, domain, seniority
         │
         ▼
  Match/Gap Table — STRONG / PARTIAL / GAP per requirement
         │
         ▼
  Resume Tailoring — reframe, reorder, tighten existing content
         │
         ├── Anti-fabrication rules enforced throughout
         │
         ▼
  ATS-Safe DOCX output + application logged to tracker
```

No API key needed. Runs entirely through [Claude Code](https://claude.ai/code) with a Pro subscription.

---

## Installation

**Requirements:** Python 3.9+, [Claude Code](https://claude.ai/code) (Pro subscription)

```bash
git clone https://github.com/your-username/resume-customiser.git
cd resume-customiser
python install.py
```

The installer will ask for:
- Where to save your applications (default: `~/Documents/resume-applications`)
- Your first name (used in output filenames)

Then restart Claude Code.

---

## Usage

### Single Job

Open Claude Code in any directory and run:

```
/resume-customise
```

Choose **Single** mode. Provide when prompted:
- Resume file path (DOCX or PDF)
- Job description — URL, paste, or file path
- Company name + role title

> **Note:** LinkedIn, Indeed, Glassdoor, and most ATS platforms block scraping.
> The tool detects these and asks you to paste the JD text instead.

### Batch Mode

Fill in `batch_jobs_template.csv` (copy it to your working directory):

```csv
company,role,jd
Google,Senior Analyst,https://careers.google.com/jobs/...
Unilever,Insights Manager,We are looking for an Insights Manager who...
McKinsey,Associate,C:\Users\Harsh\Desktop\mckinsey_jd.txt
```

The `jd` column accepts:
- **URL** — fetched automatically (company career pages)
- **Inline text** — paste JD directly in the cell
- **File path** — path to a `.txt` file with the JD

Run `/resume-customise` and choose **Batch** mode.

### Tracker Commands

Say these in Claude Code chat:

```
show my applications          → full application table
show stats                    → pipeline summary
view application #3           → full detail for one application
update application #3 to applied
update application #3 to interview
```

Status flow: `tailored → applied → phone_screen → interview → offer → rejected / withdrawn`

---

## Output

Each run creates:

```
<applications-repo>/
└── Google_SeniorAnalyst_2026-04-26/
    ├── YourName_Google.docx   ← tailored resume
    └── jd.txt                 ← JD saved for reference
```

Plus an entry in `applications.json` with match stats, gaps, and status.

---

## Anti-Fabrication Rules

Enforced on every output. No exceptions.

- Every bullet traces to your base resume
- No tools or technologies not in the base resume
- No metrics not in the base resume
- No changes to employment dates, employer names, or job titles
- No achievements not evidenced in the base resume
- **If the JD requires something missing → it appears in the gap analysis, not the resume**
- Reframe existing experience; never invent new experience

---

## ATS Compliance

- Single-column layout
- No tables, images, graphics, or icons
- No multi-column sections
- Standard fonts (Calibri)
- Clear heading hierarchy
- Contact info in body text (not header/footer)

---

## Project Structure

```
resume-customiser/
  install.py                 ← one-time setup (run this first)
  resume-customise.md        ← Claude Code command (workflow + rules)
  batch_jobs_template.csv    ← template for batch mode
  requirements.txt           ← Python dependencies

  scripts/
    parse_resume.py          ← extract text from DOCX/PDF
    fetch_jd.py              ← load JD from URL, file, or text
    build_docx.py            ← generate ATS-safe DOCX from JSON
    tracker.py               ← application tracker CLI
    setup.py                 ← Python dependency installer

  assets/                    ← screenshots (see assets/README.md)
  samples/                   ← anonymised sample outputs
```

---

## Suggested GitHub Repo Metadata

**Description:**
> Local-first Claude Code skill that tailors resumes to job descriptions, creates ATS-safe DOCX files, and tracks applications without inventing facts.

**Topics:**
`resume` `claude-code` `job-search` `ats` `python` `career-tools` `automation`

---

## Roadmap

- [ ] HTML match/gap report output
- [ ] Cover letter generator (same anti-fabrication rules)
- [ ] Status dashboard view
- [ ] PDF output option

---

## Limitations

- Requires Claude Code with Pro subscription (no standalone Python mode)
- URL fetching fails on LinkedIn, Indeed, Glassdoor, and most ATS portals — paste JD text for these
- Batch mode still processes jobs sequentially (one Claude session per job)
- No email or calendar integration

---

## License

MIT
