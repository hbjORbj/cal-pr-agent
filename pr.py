from github import Github
import os
from dotenv import load_dotenv
import argparse
import re
from github.GithubException import GithubException
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init()

# Load environment variables from .env file
load_dotenv()

PR_TEMPLATE = """## What does this PR do?

- Fixes CAL-{ticket}

## Mandatory Tasks (DO NOT REMOVE)

- [x] I have self-reviewed the code (A decent size PR without self-review might be rejected).
- [x] N/A - I have updated the developer docs in /docs if this PR makes changes that would require a [documentation change](https://cal.com/docs). If N/A, write N/A here and check the checkbox.
- [x] I confirm automated tests are in place that prove my fix is effective or that my feature works.

## How should this be tested?

- Please use the latest Vercel preview and test please 🙏."""

VALID_PREFIXES = {"feat", "fix", "chore", "perf"}


class PRCreator:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.default_repo = os.getenv("GITHUB_REPO", "owner/repo")
        self.github = Github(self.token)
        self.repo = self.github.get_repo(self.default_repo)

    def generate_title_from_branch(self, branch):
        """Generate standardized PR title from branch name"""
        # Extract prefix and description from branch name
        match = re.match(r"^(feat|fix|chore|perf)/(.+)$", branch)
        if not match:
            raise ValueError(
                f"Branch name must start with one of {VALID_PREFIXES} followed by '/' and description. "
                f"Example: feat/new-feature"
            )

        prefix, description = match.groups()
        # Convert hyphens to spaces and create title case description
        description = description.replace("-", " ").lower()

        # Format: "prefix: description"
        return f"{prefix}: {description}"

    def create_pr(
        self,
        branch,
        ticket_number="[FILL IN]",
        title=None,
        base="main",
        draft=False,
    ):
        """Create a single PR with the standard template"""
        try:
            # Generate title from branch if not provided
            if title is None:
                title = self.generate_title_from_branch(branch)

            # Generate description using the template
            description = PR_TEMPLATE.format(
                ticket=ticket_number,
            )

            pr = self.repo.create_pull(
                title=title, body=description, head=branch, base=base, draft=draft
            )
            return pr
        except ValueError as e:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
            return None
        except Exception as e:
            print(f"{Fore.RED}Error creating PR: {e}{Style.RESET_ALL}")
            return None

    def get_user_prs(self):
        """Get all open PRs created by the authenticated user"""
        user = self.github.get_user()
        all_prs = self.repo.get_pulls(state="open")
        return [pr for pr in all_prs if pr.user.login == user.login]

    def check_merge_conflicts(self, pr):
        """Check if a PR has merge conflicts with main"""
        try:
            # Force GitHub to update mergeable state
            pr.update()
            # Note: mergeable can be None if GitHub hasn't computed it yet
            if pr.mergeable is None:
                print(
                    f"{Fore.YELLOW}⏳ GitHub is still checking PR #{pr.number} for conflicts...{Style.RESET_ALL}"
                )
                return True  # Assume conflict until we know for sure
            return not pr.mergeable
        except GithubException as e:
            print(
                f"{Fore.RED}Error checking merge status for PR #{pr.number}: {str(e)}{Style.RESET_ALL}"
            )
            return True

    def update_pr_with_main(self, pr):
        """Merge main into the PR branch"""
        try:
            # Get the main branch
            main_branch = self.repo.get_branch("main")

            # Create merge commit
            merge_msg = f"Merge 'main' into {pr.head.ref}"
            self.repo.merge(pr.head.ref, "main", merge_msg)
            return True
        except GithubException as e:
            print(
                f"{Fore.RED}Error updating PR #{pr.number}: {str(e)}{Style.RESET_ALL}"
            )
            return False

    def refresh_prs(self, dry_run=False):
        """Update all PRs without merge conflicts with main"""
        prs = self.get_user_prs()
        conflict_urls = []
        updated_prs = []

        print(f"\n{Fore.CYAN}Analyzing your open PRs...{Style.RESET_ALL}")

        # First analyze all PRs
        pr_status = []
        for pr in prs:
            print(
                f"\n{Fore.BLUE}Checking PR #{pr.number}: {Style.BRIGHT}{pr.title}{Style.RESET_ALL}"
            )
            has_conflicts = self.check_merge_conflicts(pr)
            pr_status.append((pr, has_conflicts))

        # Summarize what will be done
        conflicting_prs = [pr for pr, has_conflicts in pr_status if has_conflicts]
        updateable_prs = [pr for pr, has_conflicts in pr_status if not has_conflicts]

        print(f"\n{Fore.CYAN}Found {len(prs)} open PRs:{Style.RESET_ALL}")
        print(
            f"{Fore.GREEN}- {len(updateable_prs)} PRs can be updated with main{Style.RESET_ALL}"
        )
        print(f"{Fore.RED}- {len(conflicting_prs)} PRs have conflicts{Style.RESET_ALL}")

        # First show what would be updated
        for pr, has_conflicts in pr_status:
            if has_conflicts:
                conflict_urls.append(pr.html_url)
                print(
                    f"{Fore.RED}❌ PR #{pr.number} has merge conflicts{Style.RESET_ALL}"
                )
            else:
                print(f"{Fore.CYAN}✓ PR #{pr.number} would be updated{Style.RESET_ALL}")

        if conflict_urls:
            print(f"\n{Fore.RED}PRs with merge conflicts:{Style.RESET_ALL}")
            for url in conflict_urls:
                print(url)

        if not updateable_prs:
            return

        if dry_run:
            response = input(
                f"\n{Fore.YELLOW}Would you like to proceed with the actual updates? (y/N): {Style.RESET_ALL}"
            ).lower()
            if response != "y":
                print(f"{Fore.YELLOW}Operation cancelled.{Style.RESET_ALL}")
                return
            print(f"\n{Fore.CYAN}Proceeding with updates...{Style.RESET_ALL}")

        # Actually perform the updates
        updated_prs = []
        for pr, has_conflicts in pr_status:
            if not has_conflicts:
                if self.update_pr_with_main(pr):
                    updated_prs.append(pr.number)
                    print(
                        f"{Fore.GREEN}✅ Successfully updated PR #{pr.number} with main{Style.RESET_ALL}"
                    )
                else:
                    print(
                        f"{Fore.YELLOW}⚠️ Failed to update PR #{pr.number}{Style.RESET_ALL}"
                    )

        if updated_prs:
            print(
                f"\n{Fore.GREEN}Successfully updated {len(updated_prs)} PRs with main{Style.RESET_ALL}"
            )
            print(
                f"PR numbers: {Fore.CYAN}{', '.join(map(str, updated_prs))}{Style.RESET_ALL}"
            )


def main():
    parser = argparse.ArgumentParser(
        description=f"{Fore.CYAN}GitHub PR creator and manager{Style.RESET_ALL}"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Create PR command
    create_parser = subparsers.add_parser("create", help="Create a new PR")
    create_parser.add_argument(
        "branch", help=f"Branch name (must start with {VALID_PREFIXES} followed by /)"
    )
    create_parser.add_argument(
        "-t", "--title", help="PR title (optional, will be generated from branch name)"
    )
    create_parser.add_argument("--ticket", help="CAL ticket number (e.g., 123)")
    create_parser.add_argument(
        "--base", default="main", help="Base branch (default: main)"
    )
    create_parser.add_argument(
        "-d", "--draft", action="store_true", help="Create as draft PR"
    )

    # Refresh PRs command
    refresh_parser = subparsers.add_parser(
        "refresh", help="Update PRs with main branch"
    )
    refresh_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )

    args = parser.parse_args()
    creator = PRCreator()

    if args.command == "create":
        pr = creator.create_pr(
            branch=args.branch,
            ticket_number=args.ticket if args.ticket else "[FILL IN]",
            title=args.title,
            base=args.base,
            draft=args.draft,
        )

        if pr:
            print(f"\n{Fore.GREEN}PR created successfully!{Style.RESET_ALL}")
            print(f"{Fore.CYAN}URL: {pr.html_url}{Style.RESET_ALL}")

    elif args.command == "refresh":
        creator.refresh_prs(dry_run=args.dry_run)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
