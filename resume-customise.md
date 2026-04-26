# Resume Customiser

Local-first. No API cost. Base resume = source of truth. No invented facts, no fabricated metrics.

SCRIPTS = C:\Users\Harsh\.claude\plugins\cache\local\resume-customiser\1.0.0\scripts
REPO    = C:\Users\Harsh\OneDrive\Desktop\Resume\applications

---

## Sub-commands

If user says "show applications", "list applications", "application tracker", or "tracker":
→ Run Step T (Tracker View) directly. Skip resume workflow.

If user says "update status" or "mark as <status>":
→ Run Step U (Update Status) directly.

Otherwise: proceed to Step 0.

---

## Step 0 — Mode Selection

On invoke, greet the user with exactly this message (no extra text):

---
**Resume Customiser**

Choose mode:
1. **Single** — one job, one resume. URL or paste JD.
2. **Batch** — multiple jobs from CSV. URLs or pasted JD text supported.

Reply `1` or `single` to start single mode.
Reply `2` or `batch` to start batch mode.
---

Wait for response. Then:
- `1` / `single` → proceed to Step 1 (Single Mode)
- `2` / `batch` → proceed to Step B (Batch Mode)

---

## Step 1 — Gather Inputs (Single Mode)

Ask the user for ALL of these in one message:

1. **Resume file path** — DOCX or PDF
2. **Job description** — choose ONE:
   - **URL** — paste the job posting URL
   - **Paste text** — paste the full JD directly into the chat
3. **Company name**
4. **Role title**

Note: LinkedIn, Indeed, Glassdoor and similar sites block scraping.
If user gives a LinkedIn/Indeed/Glassdoor URL, tell them immediately: "This site blocks automated access — please paste the JD text directly instead."

Do not proceed until all four are provided.

---

## Step 2 — Parse Resume

```
python "C:\Users\Harsh\.claude\plugins\cache\local\resume-customiser\1.0.0\scripts\parse_resume.py" "<resume_path>"
```

Capture stdout as RESUME_TEXT. If error, report it and stop.

---

## Step 3 — Get JD Text

**If user gave a URL:**
```
python "C:\Users\Harsh\.claude\plugins\cache\local\resume-customiser\1.0.0\scripts\fetch_jd.py" "<url>"
```
- Exit code 0 + stdout → use as JD_TEXT. Continue.
- Exit code 2 (PASTE_REQUIRED) → tell user: "Could not fetch this URL automatically. Please paste the job description text directly into the chat." Wait for paste, then use as JD_TEXT.
- Exit code 1 (other error) → report error message to user and stop.

**If user pasted plain text:** use that directly as JD_TEXT.

---

## Step 4 — Analyse JD (INTERNAL — do not output to user)

Silently extract and hold in context. Do NOT display this analysis. Do NOT summarise it to the user. Use it only to inform Steps 6 and 7.

Extract:
- Role title and seniority level
- Team/function context
- Primary responsibilities
- Required technical skills and tools (named explicitly)
- Required domain or industry experience
- Soft skills and working-style signals
- ATS keywords: exact phrases appearing verbatim in JD (use these in tailored resume where truthfully applicable)

---

## Step 5 — Analyse Resume (INTERNAL — do not output to user)

Silently extract and hold in context. Do NOT display this analysis. Do NOT summarise it to the user. Use it only to inform Steps 6 and 7.

Extract:
- Overall career theme and trajectory
- Seniority level evidenced
- Technical skills with explicit evidence (role/bullet source)
- Tools and technologies mentioned
- Domain and industry exposure evidenced
- Strongest achievements (concrete, quantified where present)
- Weak spots: thin bullets, roles with little detail, skills without evidence

---

## Step 6 — Match / Gap Analysis

Produce a table:

| JD Requirement | Resume Evidence | Match |
|---|---|---|
| <requirement> | <quote or reference from resume> | Strong / Partial / Gap |

- **Strong** — resume directly and clearly evidences this
- **Partial** — related but not exact evidence
- **Gap** — not present or provable from resume

Count: N_STRONG, N_PARTIAL, N_GAPS.

Show this table. Ask user to confirm before tailoring.

---

## Step 7 — Tailor Resume

Rewrite resume to better match JD. Apply these rules strictly:

### MUST:
- Every bullet traces to base resume evidence
- Use JD language and ATS keywords where they accurately describe existing experience
- Preserve experience entries in EXACT original order (chronology is a fact — do not reorder roles)
- Reorder bullets WITHIN each role by JD relevance only
- Reorder non-experience sections (Skills, Education, Certifications) relative to each other where useful
- Tighten weak bullets using context already in resume
- Surface domain/business context already present but underemphasised
- Write or rewrite summary grounded entirely in resume evidence
- Flag gaps at end: list JD requirements not evidenced in resume

### MUST NOT:
- Add skills not in base resume
- Add tools not in base resume
- Invent metrics or numbers
- Change job titles, company names, or dates
- Change order of experience entries — chronology must match base resume exactly
- Remove any role that appears in base resume
- Add responsibilities not evidenced in resume
- Present inferred capability as confirmed experience

### JSON output format for DOCX builder:

```json
{
  "name": "Full Name",
  "contact": {
    "email": "...",
    "phone": "...",
    "linkedin": "...",
    "location": "...",
    "github": "..."
  },
  "summary": "2-3 sentence summary grounded in resume evidence",
  "experience": [
    {
      "title": "Job Title",
      "company": "Company Name",
      "location": "City, Country",
      "dates": "Mon YYYY – Mon YYYY",
      "bullets": [
        "Bullet point one",
        "Bullet point two"
      ]
    }
  ],
  "skills": {
    "Technical": ["skill1", "skill2"],
    "Tools": ["tool1", "tool2"],
    "Domain": ["domain1", "domain2"]
  },
  "education": [
    {
      "degree": "Degree Name",
      "institution": "University Name",
      "dates": "YYYY – YYYY",
      "notes": "optional"
    }
  ],
  "certifications": ["Cert Name, Issuer, Year"],
  "gaps": ["Gap 1", "Gap 2"]
}
```

---

## Step 8 — Save to Repo + Build DOCX

**8a. Create application folder in repo:**

Folder name format: `<Company>_<Role>_<YYYY-MM-DD>` (spaces → underscores, no special chars)

Output DOCX filename: `Harsh_<CompanyName>.docx` (spaces → underscores, no special chars)

```
REPO\<Company>_<Role>_<date>\
├── Harsh_<CompanyName>.docx
└── jd.txt
```

Save JD_TEXT to `jd.txt` in that folder.

**8b. Write JSON to temp file:**

Save the tailored resume JSON to a temp file:
`C:\Users\Harsh\AppData\Local\Temp\resume_temp.json`

**8c. Build DOCX:**

```
python "C:\Users\Harsh\.claude\plugins\cache\local\resume-customiser\1.0.0\scripts\build_docx.py" "<temp_json_path>" "<repo_folder>\Harsh_<CompanyName>.docx"
```

---

## Step 8d — Smoke Test (INTERNAL — do not output to user)

After build_docx.py completes, silently verify the output before proceeding:

```
python -c "
from docx import Document
import os
path = r'<output_docx_path>'
assert os.path.exists(path), 'File not found'
assert os.path.getsize(path) > 1000, 'File too small'
doc = Document(path)
assert len(doc.paragraphs) > 5, 'Too few paragraphs'
print('OK')
"
```

If assertion fails: report error to user and stop. Do NOT proceed to tracker or report.
If output is `OK`: continue silently.

---

## Step 9 — Log to Tracker

After successful DOCX build, log to tracker:

```
python "C:\Users\Harsh\.claude\plugins\cache\local\resume-customiser\1.0.0\scripts\tracker.py" add "<json_entry>"
```

JSON entry format:
```json
{
  "company": "Company Name",
  "role": "Role Title",
  "date": "YYYY-MM-DD",
  "jd_source": "<url or 'pasted text'>",
  "resume_input": "<path to base resume>",
  "resume_output": "<path to tailored_resume.docx>",
  "match_stats": {
    "strong": <N_STRONG>,
    "partial": <N_PARTIAL>,
    "gaps": <N_GAPS>
  },
  "gaps": ["gap1", "gap2"],
  "status": "tailored"
}
```

---

## Step 10 — Report

Tell user:
- Application ID assigned by tracker
- Path to output DOCX
- Match summary: N strong, N partial, N gaps
- List of gaps (so user knows what to address in cover letter)
- Reminder: all content grounded in base resume — no invented facts

Suggest next steps:
- Update status later with: "update application #<id> to applied"
- View all applications with: "show my applications"

---

## Step B — Batch Mode

Process multiple job applications from a CSV file in one run.

### CSV format (required columns):

```
company,role,jd
Google,Senior Analyst,https://careers.google.com/jobs/...
Unilever,Insights Manager,C:\Users\Harsh\Desktop\unilever_jd.txt
McKinsey,Associate,We are looking for an Associate to join...
```

- `company` — company name (used for folder + filename)
- `role` — role title (used for folder name)
- `jd` — one of three forms (auto-detected):
  - **URL**: starts with `http` → fetched via fetch_jd.py
  - **File path**: path to a `.txt` file containing JD text → file is read
  - **Inline text**: anything else → used directly as JD text

For long JDs: save as `.txt` file, put the path in the `jd` column.
For short JDs or URLs: paste directly into the cell.
Excel will automatically quote cells that contain commas or newlines — this is fine.

### B1 — Read CSV

Ask user for:
1. CSV file path
2. Resume file path (DOCX or PDF)

Read and validate CSV:
```
python -c "
import csv, os
with open(r'<csv_path>', newline='', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
for i, r in enumerate(rows, 1):
    company = r.get('company','').strip()
    role = r.get('role','').strip()
    jd = r.get('jd','').strip()
    jd_type = 'URL' if jd.startswith('http') else ('FILE' if os.path.exists(jd) else 'TEXT')
    missing = [k for k in ['company','role','jd'] if not r.get(k,'').strip()]
    status = 'SKIP: missing ' + ','.join(missing) if missing else 'OK'
    print(f'Row {i}: [{status}] {company} | {role} | [{jd_type}] {jd[:60]}')
"
```

Validate: confirm row count. If any row missing `company`, `role`, or `jd` → report and skip that row.

### B2 — Parse Resume (once)

Run parse_resume.py once. Reuse RESUME_TEXT for all jobs in batch.

### B3 — Process each job sequentially

For each row, run the full single-job pipeline silently (Steps 3–9):

**Get JD text per row (auto-detect):**
```
python -c "
import os, sys
jd = r'<jd_cell_value>'
if jd.startswith('http'):
    # URL — will be fetched by fetch_jd.py
    print('URL')
elif os.path.exists(jd):
    with open(jd, encoding='utf-8-sig') as f:
        print(f.read())
else:
    print(jd)
"
```
- If URL → pass to `fetch_jd.py "<url>"`
- If file path → read file content directly as JD_TEXT
- If inline text → use as JD_TEXT directly

Then continue:
- Analyse JD (INTERNAL)
- Match/gap against resume (INTERNAL)
- Tailor resume
- Save to `REPO\<Company>_<Role>_<date>\Harsh_<CompanyName>.docx`
- Save `jd.txt`
- Smoke test
- Log to tracker

Do NOT pause between rows for user input. Process all to completion.

If a row fails (URL unreachable, DOCX build error): log the error, skip that row, continue with next.

### B4 — Batch Summary Report

After all rows processed, show one table:

| # | Company | Role | Strong | Partial | Gaps | Output |
|---|---|---|---|---|---|---|
| 1 | Google | Senior Analyst | 7 | 3 | 2 | Harsh_Google.docx ✓ |
| 2 | Unilever | Insights Manager | 5 | 4 | 4 | FAILED: URL error |

Total processed / total failed.
List any gaps per company only if user asks.

---

## Step T — Tracker View

```
python "C:\Users\Harsh\.claude\plugins\cache\local\resume-customiser\1.0.0\scripts\tracker.py" list
```

Show output. Also offer:
- "show stats" → run `tracker.py stats`
- "view #<id>" → run `tracker.py view <id>`

---

## Step U — Update Status

Ask user for application ID and new status if not already given.

Valid statuses: `tailored | applied | phone_screen | interview | offer | rejected | withdrawn`

```
python "C:\Users\Harsh\.claude\plugins\cache\local\resume-customiser\1.0.0\scripts\tracker.py" update <id> <status>
```

Confirm the update to the user.

---

## Error Recovery

If `python-docx`, `pdfplumber`, `requests`, or `beautifulsoup4` are missing:
```
python "C:\Users\Harsh\.claude\plugins\cache\local\resume-customiser\1.0.0\scripts\setup.py"
```

If JD URL fetch fails, ask user to paste JD text directly instead.
