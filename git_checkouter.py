import os
import sys
import subprocess
import argparse
from datetime import datetime, timedelta

# This is useful for debugging the script
USE_SCRIPT_VARS = False

# Script variables - these will be used if USE_SCRIPT_VARS is set to True
# I used it for debugging purposes - like working inside IDE instead from command line
specified_path_script = ""
target_str_script = "09:26:2023 23:00"
min_time_diff_script = timedelta(weeks=4)
prefix_script = "tst_"
delete_existing_script = True # deletes prefixed branch if exists
ignore_repos_existing_script = [] # String array of repository names to ignore
verbose_logging_script = False
dry_run_script = False
create_branch_only_script = True

# Global variables
verbose_logging = False
master_branch_name = "main" # it will be deduced later on in get_default_remote_branch

def run_git_command(path, command):
    full_command = ['git', '-C', path] + command

    global verbose_logging
    if verbose_logging:
        print(f"Running git command `{' '.join(full_command)}` in {path}")
    try:
        output = subprocess.check_output(full_command, text=True, stderr=subprocess.PIPE).strip()
        return output
    except subprocess.CalledProcessError as e:
        error_message = e.stderr.strip() if e.stderr else ""
        print(f"Error running git command {' '.join(full_command)} in {path}. Continuing to the next directory.")

        # There are cases when git command was interruped leaving index.lock file, but there are more
        # different lock fieles
        if "Unable to create" in error_message and "index.lock" in error_message:
            print("Git index.lock file exists, aborting script.")
            raise Exception("Git index.lock file exists, aborting.")

        # Check if the error is due to local changes that would be overwritten
        if "Your local changes to the following files would be overwritten" in error_message:
            print("Local changes detected that would be overwritten by checkout. Aborting script.")
            raise Exception("Local changes detected. Aborting.")

        return None
def nearest_commit(path, target_date, min_time_diff):
    global master_branch_name

    since_date = (target_date - min_time_diff).strftime("%Y-%m-%d")
    until_date = (target_date + min_time_diff).strftime("%Y-%m-%d")

    date_range_args = ['--since', since_date, '--until', until_date]
    commit_hashes = run_git_command(path, ['rev-list', master_branch_name] + date_range_args)

    global verbose_logging
    if commit_hashes is None:
        if verbose_logging:
            print(f"Couldn't get the commit hashes for {path}. Skipping this repository.")
        return None

    nearest_commit_hash = None
    nearest_time_diff = min_time_diff
    commits = commit_hashes.split('\n')

    for commit_hash in commits:
        if not commit_hash:
            if verbose_logging:
                print(f"Skipping empty commit hash in {path}.")
            continue

        commit_time_str = run_git_command(path, ['show', '-s', '--format=%ct', commit_hash])
        if commit_time_str is None:
            continue

        commit_time = int(commit_time_str)
        commit_date = datetime.fromtimestamp(commit_time)
        time_diff = target_date - commit_date

        if verbose_logging:
            print(f"Evaluating commit {commit_hash}, time difference: {time_diff}, new candidate? {'Yes' if timedelta(0) <= time_diff < nearest_time_diff else 'No'}")

        if timedelta(0) <= time_diff < nearest_time_diff:
            nearest_time_diff = time_diff
            nearest_commit_hash = commit_hash

    return nearest_commit_hash

def branch_exists(path, branch_name):
    existing_branches_output = run_git_command(path, ['branch', '--list'])
    if existing_branches_output is None:
        return False

    existing_branches = existing_branches_output.split('\n')
    return branch_name in existing_branches or f"* {branch_name}" in existing_branches

def delete_branches(path, prefix):
    existing_branches = run_git_command(path, ['branch', '--list'])
    if existing_branches != None:
        for branch in existing_branches.split('\n'):
            if branch.strip().startswith(prefix):
                run_git_command(path, ['branch', '-D', branch.strip()])

def get_default_remote_branch(dir_path):
    # First, check if a remote is set
    remote_check_command = ['git', 'remote']
    full_remote_check_command = ["bash", "-c", f'cd {dir_path} && {" ".join(remote_check_command)}']
    remote_output = subprocess.check_output(full_remote_check_command, text=True).strip()

    if not remote_output:
        # No remote, get the first local branch
        local_branch_command = ['git', 'branch']
        full_local_branch_command = ["bash", "-c", f'cd {dir_path} && {" ".join(local_branch_command)}']
        local_branch_output = subprocess.check_output(full_local_branch_command, text=True).strip()
        first_local_branch = local_branch_output.split('\n')[0].replace('*', '').strip()

        if first_local_branch:
            print(f"No remote set for this repository. Using first local branch: {first_local_branch}")
            return first_local_branch
        else:
            print("No local branches found.")
            return None

    # If remote is set, proceed to get the default branch name
    command = ['git', 'symbolic-ref', 'refs/remotes/origin/HEAD']
    full_command = ["bash", "-c", f'cd {dir_path} && {" ".join(command)}']

    try:
        output = subprocess.check_output(full_command, text=True).strip()
        return output.split('/')[-1]
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def is_git_repo(dir_path, verbose_logging=False):
    try:
        output = subprocess.check_output(['git', 'rev-parse', '--is-inside-work-tree'], cwd=dir_path, text=True).strip()
        if output == 'true':
            return True
    except subprocess.CalledProcessError:
        # The command will fail if it's not a Git repository
        if verbose_logging:
            print(f"Skipping {dir_path}, not a git repository.")
        return False
def main():
    global master_branch_name

    # Handle command-line arguments
    parser = argparse.ArgumentParser(
        description="Checkout to a git branch based on a date."
    )

    parser.add_argument("--path", type=str, help="Specifies the folder where all your Git repositories are located.")
    parser.add_argument("--date", type=str, help="The target date and time in MM:DD:YYYY HH:MM format.")
    parser.add_argument("--timediff", type=int, default=30, help="The minimum time difference, in days, for the closest commit.")
    parser.add_argument("--prefix", type=str, default="tst_",
                        help="The prefix for the new branch name. Default is 'tst_'.")
    parser.add_argument("--delete", type=bool, default=True,
                        help="Delete existing branches with the specified prefix. Default is True.")
    parser.add_argument("--ignore-repos", type=str, help="Comma-separated list of repository names to ignore.",
                        default="")
    parser.add_argument("--verbose", action='store_true', default=False, help="Enable verbose logging.")
    parser.add_argument("--dry-run", action='store_true', default=False, help="Run the script without making any changes.")
    parser.add_argument("--create-branch-only", action="store_true", default=False,
                        help="Only create the new branches without checking them out.")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)

    global verbose_logging
    if USE_SCRIPT_VARS:
        specified_path = specified_path_script
        target_str = target_str_script
        min_time_diff = min_time_diff_script
        prefix = prefix_script
        delete_existing = delete_existing_script
        ignore_repos = ignore_repos_existing_script
        verbose_logging = verbose_logging_script
        dry_run = dry_run_script
        create_branch_only = create_branch_only_script
    else:
        specified_path = args.path
        target_str = args.date
        min_time_diff = timedelta(days=args.timediff)
        prefix = args.prefix
        delete_existing = args.delete
        ignore_repos = args.ignore_repos.split(",") if args.ignore_repos else []
        verbose_logging = args.verbose
        dry_run = args.dry_run
        create_branch_only = args.create_branch_only

    if dry_run:
        print("Dry-run mode enabled. No changes will be made.")

    target_date = None
    new_branch_name = None
    if target_str != None:
        try:
            target_date = datetime.strptime(target_str, "%m:%d:%Y %H:%M")
        except TypeError:
            print("Error: The target date-time is not specified correctly: '" + str(target_str) + "'")
            print("Example of a correct date-time format: 09:25:2021 12:45")
            sys.exit(1)

        new_branch_name = prefix + target_date.strftime("%m_%d_%Y_%H_%M")

    for dir_name in os.listdir(specified_path):
        dir_path = os.path.join(specified_path, dir_name)

        if dir_name in ignore_repos:
            if verbose_logging:
                print(f"Skipping {dir_name} as it's in the ignore list.")
            continue

        if not os.path.isdir(dir_path):
            if verbose_logging:
                print(f"Skipping {dir_name}, not a directory.")
            continue

        if not is_git_repo(dir_path, verbose_logging):
            if verbose_logging:
                print(f"Skipping {dir_name}, not git repository.")
            continue

        master_branch_name = get_default_remote_branch(dir_path)

        print(f"\n+----+----+----+----+----+----+----+----+\nProcessing {dir_name}")

        try:
            run_git_command(dir_path, ['status'])
        except subprocess.CalledProcessError:
            print(f"Skipping {dir_name}, not a Git repository.")
            continue

        # Checkout to [master|main|...] branch before performing other operations
        try:
            if not dry_run and not create_branch_only:
                run_git_command(dir_path, ['checkout', master_branch_name])
                print(f"Checed out to master branch in {dir_name}")
            else:
                print(f"Would have checked out to master branch in {dir_name}")
        except subprocess.CalledProcessError:
            print(f"Couldn't checkut to master in {dir_name}. Continuing with the next repository.")
            continue

        if delete_existing and not create_branch_only:
            delete_branches(dir_path, prefix)

        if target_date == None:
            continue

        if branch_exists(dir_path, new_branch_name):
            print(f"Branch {new_branch_name} already exists in {dir_name}. Skipping.")
            continue

        commit_hash = nearest_commit(dir_path, target_date, min_time_diff)

        if commit_hash:
            if create_branch_only:
                run_git_command(dir_path, ['branch', new_branch_name, commit_hash])
                print(f"New branch {new_branch_name} created in {dir_name} without checkout.")
            else:
                run_git_command(dir_path, ['checkout', '-b', new_branch_name, commit_hash])
                print(f"Chcked out to new branch {new_branch_name} in {dir_name}")
        else:
            print(f"No sutable commit found in {dir_name} within the time range. Staying on the master branch.")


if __name__ == "__main__":
    main()
