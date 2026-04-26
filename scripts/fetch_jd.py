"""
Fetch job description text from a URL or local file.
Usage: python fetch_jd.py <url_or_file_path>
Outputs JD text to stdout.
Exits with code 2 and message "PASTE_REQUIRED" if site blocks scraping.
"""
import sys
import os
import re
import time

# Sites known to block scraping — require user to paste JD text
BLOCKED_DOMAINS = [
    "linkedin.com",
    "seek.com.au",
    "indeed.com",
    "glassdoor.com",
    "greenhouse.io",
    "lever.co",
    "workday.com",
    "icims.com",
    "taleo.net",
    "smartrecruiters.com",
]

HEADERS_LIST = [
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    },
    {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-GB,en;q=0.9",
        "Connection": "keep-alive",
    },
]

# Ordered selectors to try — from most specific to least
JD_SELECTORS = [
    "[data-testid='job-description']",
    "[class*='jobDescription']",
    "[class*='job-description']",
    "[class*='job_description']",
    "[class*='JobDescription']",
    "[id*='job-description']",
    "[id*='jobDescription']",
    "[class*='description-content']",
    "[class*='posting-description']",
    "[class*='job-details']",
    "[class*='jobDetails']",
    "[class*='vacancy-description']",
    "[itemprop='description']",
    "article",
    "[role='main']",
    "main",
    "#content",
    ".content",
]


def is_blocked_domain(url):
    for domain in BLOCKED_DOMAINS:
        if domain in url.lower():
            return True
    return False


def clean_text(text):
    lines = text.splitlines()
    seen = set()
    cleaned = []
    for line in lines:
        line = line.strip()
        if not line or len(line) < 2:
            continue
        if line in seen:
            continue
        seen.add(line)
        cleaned.append(line)
    # Collapse 3+ blank lines to 1
    result = re.sub(r'\n{3,}', '\n\n', "\n".join(cleaned))
    return result.strip()


def extract_best_text(soup):
    """Try selectors in order, fall back to largest text block."""
    from bs4 import BeautifulSoup

    for selector in JD_SELECTORS:
        try:
            el = soup.select_one(selector)
            if el:
                text = clean_text(el.get_text(separator="\n"))
                if len(text) > 300:
                    return text
        except Exception:
            continue

    # Fallback: find all <div>/<section> blocks, return the one with most text
    candidates = []
    for tag in soup.find_all(["div", "section", "article"]):
        text = clean_text(tag.get_text(separator="\n"))
        if len(text) > 300:
            candidates.append(text)

    if candidates:
        return max(candidates, key=len)

    # Last resort: full body
    body = soup.find("body")
    if body:
        return clean_text(body.get_text(separator="\n"))

    return clean_text(soup.get_text(separator="\n"))


def fetch_url(url):
    import requests
    from bs4 import BeautifulSoup

    if is_blocked_domain(url):
        print(
            f"PASTE_REQUIRED: {url} blocks automated access.\n"
            "Please paste the job description text directly into the chat instead.",
            file=sys.stderr,
        )
        sys.exit(2)

    last_error = None
    for i, headers in enumerate(HEADERS_LIST):
        try:
            session = requests.Session()
            # First hit homepage to get cookies (reduces bot detection)
            from urllib.parse import urlparse
            parsed = urlparse(url)
            base = f"{parsed.scheme}://{parsed.netloc}"
            try:
                session.get(base, headers=headers, timeout=8)
            except Exception:
                pass

            resp = session.get(url, headers=headers, timeout=15, allow_redirects=True)

            if resp.status_code == 403:
                last_error = f"HTTP 403 Forbidden — site is blocking scraper."
                if i < len(HEADERS_LIST) - 1:
                    time.sleep(1)
                    continue
                break

            if resp.status_code == 429:
                last_error = f"HTTP 429 Too Many Requests."
                time.sleep(2)
                continue

            resp.raise_for_status()

            # Parse
            try:
                soup = BeautifulSoup(resp.text, "lxml")
            except Exception:
                soup = BeautifulSoup(resp.text, "html.parser")

            # Remove noise tags
            for tag in soup(["script", "style", "nav", "footer", "header",
                              "aside", "noscript", "svg", "iframe"]):
                tag.decompose()

            text = extract_best_text(soup)

            if len(text.strip()) < 100:
                last_error = "Extracted text too short — page may require JavaScript."
                continue

            return text

        except requests.exceptions.SSLError:
            last_error = "SSL error — try with http:// or paste JD text directly."
            break
        except requests.exceptions.ConnectionError:
            last_error = "Connection failed — check URL or internet connection."
            break
        except requests.exceptions.Timeout:
            last_error = "Request timed out."
            if i < len(HEADERS_LIST) - 1:
                continue
            break
        except Exception as e:
            last_error = str(e)
            break

    # All attempts failed
    print(
        f"PASTE_REQUIRED: Could not fetch URL automatically.\n"
        f"Reason: {last_error}\n"
        "Please paste the job description text directly into the chat instead.",
        file=sys.stderr,
    )
    sys.exit(2)


def fetch_file(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        with open(path, "r", encoding="utf-8-sig") as f:
            return f.read()
    elif ext == ".docx":
        from docx import Document
        doc = Document(path)
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    elif ext == ".pdf":
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            return "\n".join(
                page.extract_text() for page in pdf.pages
                if page.extract_text()
            )
    else:
        with open(path, "r", encoding="utf-8-sig") as f:
            return f.read()


def main():
    if len(sys.argv) < 2:
        print("Usage: fetch_jd.py <url_or_file_path>", file=sys.stderr)
        sys.exit(1)

    source = sys.argv[1]

    if source.startswith("http://") or source.startswith("https://"):
        text = fetch_url(source)
    elif os.path.exists(source):
        text = fetch_file(source)
    else:
        print(f"Error: Not a valid URL or file path: {source}", file=sys.stderr)
        sys.exit(1)

    if not text or len(text.strip()) < 50:
        print("Error: Could not extract meaningful text from source.", file=sys.stderr)
        sys.exit(1)

    print(text)


if __name__ == "__main__":
    main()
