# Cal PR Agent

A simple CLI tool to automate Pull Request creation for Cal.com with standardized templates and conventions.

## Features

- Automatically generates PR titles from branch names following Cal.com conventions
- Uses standardized PR template with mandatory tasks
- Supports draft PRs
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
GITHUB_REPO=calcom/cal.com // write the name of your fork repo if you are using a fork
```

## Usage

Basic usage:
```bash
python pr.py feat/new-feature
```

Full options:
```bash
python pr.py <branch> [options]

Arguments:
  branch                Branch name (must start with feat/fix/chore/perf)

Options:
  -t, --title TEXT      Custom PR title (optional, generated from branch name if not provided)
  --ticket TEXT         Linear CAL ticket number (optional)
  --test TEXT           Link to provide for testing (optional)
  --base TEXT           Base branch (default: main)
  -d, --draft           Create as draft PR
```

Examples:
```bash
# Simple usage
python pr.py feat/new-onboarding

# With ticket number and testing steps
python pr.py perf/speed-update --ticket 123 --test "Check homepage load time"

# Create draft PR
python pr.py fix/bug-fix -d

# Custom title
python pr.py feat/new-feature -t "feat: implement amazing new feature"
```

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT