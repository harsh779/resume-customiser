"""
Resume Customiser — Claude Code Skill Installer
Supports Windows, macOS, Linux.

Run once:
    python install.py

What it does:
1. Detects your OS and home directory
2. Copies scripts to ~/.claude/resume-customiser/scripts/
3. Writes ~/.claude/commands/resume-customise.md with your correct paths
4. Creates the applications repo folder
5. Installs Python dependencies
6. Optionally initialises the applications folder as a git repo
"""
import os
import sys
import shutil
import subprocess
import platform

HERE = os.path.dirname(os.path.abspath(__file__))
HOME = os.path.expanduser("~")
IS_WINDOWS = platform.system() == "Windows"
SEP = "\\" if IS_WINDOWS else "/"


def p(*parts):
    """Join path parts with OS separator."""
    return os.path.join(*parts)


def ask(prompt, default=None):
    suffix = f" [{default}]" if default else ""
    val = input(f"{prompt}{suffix}: ").strip()
    return val if val else default


def run(cmd, capture=False):
    r = subprocess.run(cmd, shell=True, capture_output=capture, text=True)
    return r.returncode, r.stdout, r.stderr


def install():
    print("\n=== Resume Customiser — Installer ===\n")

    # --- Paths ---
    scripts_dest = p(HOME, ".claude", "resume-customiser", "scripts")
    commands_dest = p(HOME, ".claude", "commands")
    command_file = p(commands_dest, "resume-customise.md")

    default_repo = p(HOME, "Documents", "resume-applications") if not IS_WINDOWS \
        else p(os.environ.get("USERPROFILE", HOME), "Documents", "resume-applications")

    print(f"Scripts will install to : {scripts_dest}")
    print(f"Command file            : {command_file}")
    repo_dir = ask(f"Applications repo folder", default_repo)
    print()

    # --- Copy scripts ---
    print("Copying scripts...")
    os.makedirs(scripts_dest, exist_ok=True)
    scripts_src = p(HERE, "scripts")
    for fname in os.listdir(scripts_src):
        if fname.endswith(".py"):
            shutil.copy2(p(scripts_src, fname), p(scripts_dest, fname))
            print(f"  Copied: {fname}")

    # --- Install Python deps ---
    print("\nInstalling Python dependencies...")
    code, _, err = run(f'"{sys.executable}" "{p(scripts_dest, "setup.py")}"')
    if code != 0:
        print(f"  WARNING: dependency install failed. Run manually:\n  python {p(scripts_dest, 'setup.py')}")

    # --- Write command file ---
    print("\nWriting Claude Code command file...")
    os.makedirs(commands_dest, exist_ok=True)

    skill_template = p(HERE, "resume-customise.md")
    with open(skill_template, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace placeholder paths with actual paths
    content = content.replace(
        r"C:\Users\Harsh\.claude\plugins\cache\local\resume-customiser\1.0.0\scripts",
        scripts_dest
    )
    content = content.replace(
        r"C:\Users\Harsh\OneDrive\Desktop\Resume\applications",
        repo_dir
    )

    with open(command_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  Written: {command_file}")

    # --- Create applications repo ---
    print(f"\nCreating applications repo at: {repo_dir}")
    os.makedirs(repo_dir, exist_ok=True)

    gitignore = p(repo_dir, ".gitignore")
    if not os.path.exists(gitignore):
        with open(gitignore, "w") as f:
            f.write("*.tmp\n*.log\n")

    # Init git if git is available
    if shutil.which("git"):
        if not os.path.exists(p(repo_dir, ".git")):
            run(f'git -C "{repo_dir}" init')
            run(f'git -C "{repo_dir}" add .gitignore')
            run(f'git -C "{repo_dir}" commit -m "init: resume applications repo"')
            print("  Git repo initialised.")
        else:
            print("  Git repo already exists.")
    else:
        print("  Git not found — skipping git init. Install git for version control.")

    # --- Also update the tracker.py REPO_DIR default ---
    tracker_path = p(scripts_dest, "tracker.py")
    with open(tracker_path, "r", encoding="utf-8") as f:
        tracker = f.read()
    tracker = tracker.replace(
        r'r"C:\Users\Harsh\OneDrive\Desktop\Resume\applications"',
        f'r"{repo_dir}"'
    )
    with open(tracker_path, "w", encoding="utf-8") as f:
        f.write(tracker)
    print("  tracker.py updated with your repo path.")

    # --- Done ---
    print("\n=== Installation complete ===\n")
    print("Next steps:")
    print("1. Restart Claude Code (close and reopen)")
    print("2. Type /resume-customise to start")
    print(f"3. Your resumes will be saved to: {repo_dir}")
    print()
    print("Blocked sites (LinkedIn, Indeed, Glassdoor) require pasting JD text directly.")
    print("Other company career pages can be scraped via URL.\n")


if __name__ == "__main__":
    install()
