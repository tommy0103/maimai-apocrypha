import argparse
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], *, cwd: Path, label: str | None = None) -> None:
    if label:
        print(f"==> {label}")
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
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument("--retry-backoff", type=float, default=0.8)
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parents[1]
    scripts_dir = repo_root / "scripts"
    try:
        retry_args = [
            "--timeout",
            str(args.timeout),
            "--max-retries",
            str(args.max_retries),
            "--retry-backoff",
            str(args.retry_backoff),
        ]
        run(
            ["uv", "run", "scraper.py", "phase1", *retry_args],
            cwd=scripts_dir,
            label="Scrape phase1",
        )
        run(
            ["uv", "run", "scraper.py", "images", *retry_args],
            cwd=scripts_dir,
            label="Download images",
        )
        run(
            ["uv", "run", "translator.py"],
            cwd=scripts_dir,
            label="Translate data",
        )
        run(
            ["uv", "run", "generate_md.py", "--lang", "zh"],
            cwd=scripts_dir,
            label="Generate markdown",
        )
    except subprocess.CalledProcessError as exc:
        print(f"Command failed: {exc}", file=sys.stderr)
        sys.exit(exc.returncode)

    if not has_git_changes(cwd=repo_root):
        print("No git changes detected. Skipping commit and push.")
        return

    run(["git", "add", "."], cwd=repo_root, label="Stage changes")
    run(
        ["git", "commit", "-m", args.commit_message],
        cwd=repo_root,
        label="Commit changes",
    )
    run(["git", "push"], cwd=repo_root, label="Push changes")


if __name__ == "__main__":
    main()
