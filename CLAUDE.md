# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Git Checkouter is a Python 3.7+ CLI tool that automates finding Git commits by date/time and creates branches pointing to those commits. It processes multiple repositories in batch for rollbacks, audits, or exploring historical code states.

## Commands

```bash
# Run the main script
python git_checkouter.py --path <repos_dir> --date "MM:DD:YYYY HH:MM" [options]

# Run test scenarios (creates test repos, no assertions - manual verification)
./test.sh

# Example with common options
python git_checkouter.py --path "/path/to/repos" --date "09:26:2023 23:00" --timediff 7 --prefix "tst_" --verbose --dry-run
```

## Architecture

Single-file design (`git_checkouter.py`) with no external dependencies - uses only Python standard library.

**Key functions:**
- `run_git_command()` - Git CLI wrapper with error handling for lock files and uncommitted changes
- `nearest_commit()` - Finds closest commit on or before target date within search window (searches default branch only, backward from target date)

**Execution flow:** Iterates immediate subdirectories in `--path`, validates each as a git repo, detects default branch (via `origin/HEAD` or first local branch), finds nearest commit to target date, creates/checks out new branch with prefix+timestamp name.

**Debug mode:** Set `USE_SCRIPT_VARS = True` at top of file to use hardcoded variables instead of CLI args (useful for IDE debugging).

## Important Behavior

- **Commit search**: Searches default branch within bidirectional window (target ± timediff days), but only selects commits on or before target date
- **Checkout behavior**: Without `--date`, still checks out default branch but does not create new branches
- **Dry-run mode**: `--dry-run` prevents all mutations (checkout, branch creation, branch deletion) and shows what would happen
- **Abort conditions**: Script terminates entire run on git index.lock presence or uncommitted local changes
- **Scope**: Processes only immediate subdirectories of `--path` (not recursive), does not fetch from remotes before searching
- **Date format quirk**: Uses colons as separators (MM:DD:YYYY), not slashes

## CLI Options

Run `python git_checkouter.py --help` for full options. Key options:
- `--path` - Directory containing git repositories (required)
- `--date` - Target date in MM:DD:YYYY HH:MM format
- `--timediff` - Search window in days (default: 30)
- `--prefix` - Branch name prefix (default: 'tst_')
- `--delete` - Delete existing prefixed branches before creating new ones (default: False; requires prefix ≥2 chars)
- `--repos` - Comma-separated repo names to include (whitelist; when specified, --ignore-repos is ignored)
- `--ignore-repos` - Comma-separated repo names to skip (no spaces after commas)
- `--verbose` - Enable debug logging
- `--dry-run` - Preview mode, shows what would happen without making changes
- `--create-branch-only` - Create branch without checkout
