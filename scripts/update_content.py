import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], *, cwd: Path) -> None:
    print(f"$ {' '.join(cmd)}")
    subprocess.run(cmd, check=True, cwd=cwd)


def has_git_changes(*, cwd: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        check=True,
        stdout=subprocess.PIPE,
        text=True,
        cwd=cwd,
    )
    return bool(result.stdout.strip())


def main() -> None:
    parser = argparse.ArgumentParser(description="Update site content pipeline.")
    parser.add_argument(
        "--commit-message",
        default="docs: update content",
        help="Commit message when changes are detected.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    try:
        run(["uv", "run", "scraper.py", "phase1"], cwd=scripts_dir)
        run(["uv", "run", "scraper.py", "images"], cwd=scripts_dir)
        run(["uv", "run", "translator.py"], cwd=scripts_dir)
        run(["uv", "run", "generate_md.py", "--lang", "zh"], cwd=scripts_dir)
    except subprocess.CalledProcessError as exc:
        print(f"Command failed: {exc}", file=sys.stderr)
        sys.exit(exc.returncode)

    if not has_git_changes(cwd=repo_root):
        print("No git changes detected. Skipping commit and push.")
        return

    run(["git", "add", "."], cwd=repo_root)
    run(["git", "commit", "-m", args.commit_message], cwd=repo_root)
    run(["git", "push"], cwd=repo_root)


if __name__ == "__main__":
    main()
