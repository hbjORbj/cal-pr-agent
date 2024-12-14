from github import Github
import os
from dotenv import load_dotenv
import argparse
import re

# Load environment variables from .env file
load_dotenv()

PR_TEMPLATE = """## What does this PR do?

- Fixes CAL-{ticket}

## Mandatory Tasks (DO NOT REMOVE)

- [x] I have self-reviewed the code (A decent size PR without self-review might be rejected).
- [x] N/A - I have updated the developer docs in /docs if this PR makes changes that would require a [documentation change](https://cal.com/docs). If N/A, write N/A here and check the checkbox.
- [x] I confirm automated tests are in place that prove my fix is effective or that my feature works.

## How should this be tested?

- Go to {testing_steps}."""

VALID_PREFIXES = {"feat", "fix", "chore", "perf"}


class PRCreator:
    def __init__(self):
        self.token = os.getenv("GITHUB_TOKEN")
        self.default_repo = os.getenv("GITHUB_REPO", "owner/repo")
        self.github = Github(self.token)

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
        testing_steps="[FILL IN]",
        title=None,
        base="main",
        draft=False,
    ):
        """Create a single PR with the standard template"""
        try:
            repo = self.github.get_repo(self.default_repo)

            # Generate title from branch if not provided
            if title is None:
                title = self.generate_title_from_branch(branch)

            # Generate description using the template
            description = PR_TEMPLATE.format(
                ticket=ticket_number, testing_steps=testing_steps
            )

            pr = repo.create_pull(
                title=title, body=description, head=branch, base=base, draft=draft
            )
            return pr
        except ValueError as e:
            print(f"Error: {e}")
            return None
        except Exception as e:
            print(f"Error creating PR: {e}")
            return None


def main():
    parser = argparse.ArgumentParser(description="Quick GitHub PR creator")
    parser.add_argument(
        "branch", help=f"Branch name (must start with {VALID_PREFIXES} followed by /)"
    )
    parser.add_argument(
        "-t", "--title", help="PR title (optional, will be generated from branch name)"
    )
    parser.add_argument("--ticket", help="CAL ticket number (e.g., 123)")
    parser.add_argument("--test", help="Testing steps (optional)")
    parser.add_argument("--base", default="main", help="Base branch (default: main)")
    parser.add_argument("-d", "--draft", action="store_true", help="Create as draft PR")
    args = parser.parse_args()

    creator = PRCreator()
    pr = creator.create_pr(
        branch=args.branch,
        ticket_number=args.ticket if args.ticket else "[FILL IN]",
        testing_steps=args.test if args.test else "[FILL IN]",
        title=args.title,
        base=args.base,
        draft=args.draft,
    )

    if pr:
        print(f"\nPR created successfully!")
        print(f"URL: {pr.html_url}")


if __name__ == "__main__":
    main()
