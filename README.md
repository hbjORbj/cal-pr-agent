# Cal PR Agent

A simple CLI tool to automate Pull Request creation and management for Cal.com with standardized templates and conventions.

## Features

- Automatically generates PR titles from branch names following Cal.com conventions
- Uses standardized PR template with mandatory tasks
- Supports draft PRs
- Updates multiple PRs with main branch in bulk
- Detects and reports merge conflicts
- Configurable via environment variables
- Branch name validation (feat/fix/chore/perf)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/cal-pr-agent.git
cd cal-pr-agent
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_token_here
GITHUB_REPO=calcom/cal.com # write the name of your fork repo if you are using a fork
```

## Usage

### Creating PRs

Basic usage:

```bash
python pr.py create feat/new-feature
```

Full options for PR creation:

```bash
python pr.py create <branch> [options]

Arguments:
  branch                Branch name (must start with feat/fix/chore/perf)

Options:
  -t, --title TEXT      Custom PR title (optional, generated from branch name if not provided)
  --ticket TEXT         Linear CAL ticket number (optional)
  --test TEXT          Link to provide for testing (optional)
  --base TEXT          Base branch (default: main)
  -d, --draft          Create as draft PR
```

Examples of PR creation:

```bash
# Simple usage
python pr.py create feat/new-onboarding

# With ticket number and testing steps
python pr.py create perf/speed-update --ticket 123 --test "Check homepage load time"

# Create draft PR
python pr.py create fix/bug-fix -d

# Custom title
python pr.py create feat/new-feature -t "feat: implement amazing new feature"
```

### Managing PRs

You can update all your open PRs with the main branch using the refresh command:

```bash
# Show what changes would be made without actually making them
python pr.py refresh --dry-run

# Actually update the PRs
python pr.py refresh
```

The refresh command will:

1. List all your open PRs
2. Check each PR for merge conflicts with main
3. Show which PRs can be updated and which have conflicts
4. Update conflict-free PRs with main (after confirmation)
5. Display URLs of PRs that need manual conflict resolution

## Branch Name Convention

Branch names must follow the pattern: `{type}/{description}`

Valid types:

- `feat`: New feature
- `fix`: Bug fix
- `chore`: Maintenance tasks
- `perf`: Performance improvements

Examples:

- `feat/new-onboarding`
- `fix/login-issue`
- `chore/cleanup-deps`
- `perf/reduce-bundle-size`

## PR Title Convention

PR titles are automatically generated from branch names in the format:
`type: description`

Examples:

- `feat: new onboarding`
- `fix: login issue`
- `chore: cleanup deps`
- `perf: reduce bundle size`

## License

MIT
