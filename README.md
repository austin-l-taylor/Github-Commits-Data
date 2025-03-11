# GitHub Repository and Commit Tracker

This Python script is designed to fetch, process, and store GitHub repository and commit data for an organization. It uses the GitHub API to gather information about repositories, branches, and commits, and then pushes this data to a SQL database for further analysis or reporting.

## Features

- Fetch repositories, branches, and commit history for a specified GitHub organization.
- Retrieve detailed commit statistics, including additions, deletions, and total changes.
- Update a SQL database with the latest repository and commit data.
- Execute a stored procedure to fetch and process existing data from the database.
- Identify and process missing repositories or commits to ensure data consistency.

## Prerequisites

### Python Packages
- `requests`: For making HTTP requests to the GitHub API.
- `pandas`: For data manipulation and handling.
- `pyodbc`: For connecting to and interacting with a SQL database.
- `keeper`: For secret management and authentication.

### SQL Database
- Requires a database table named `GitHub.CommitHistory` with the following schema:
  - `Organization` (VARCHAR)
  - `Project` (VARCHAR)
  - `commitSHA` (VARCHAR)
  - `commitDate` (DATETIME)
  - `commitName` (VARCHAR)
  - `commitEmail` (VARCHAR)
  - `commitMessage` (VARCHAR)
  - `commitURL` (VARCHAR)
  - `numAdditions` (INT)
  - `numDeletions` (INT)
  - `totalChanges` (INT)
  - `branch` (VARCHAR)

- A stored procedure named `MWA.GitHub.GetProjectAndMostRecentCommit` is also required.

## Setup

1. Clone the repository.
2. Create or activate your virtual environment.
```bash
python -m venv "environment name"
```
3. Activate Environment.
```bash
./"environment name"/Scripts/activate
```
4. Install packages.
```bash
pip install -r requirements.txt
```

## Usage

1. Update the `ORG_NAME` variable with the GitHub organization name.
2. Run the script:
   ```bash
   python script_name.py
   ```

### Workflow

1. **Fetch Repositories**: Retrieves the list of repositories from the organization.
2. **Fetch Branches**: Identifies all branches within each repository.
3. **Fetch Commits**: Retrieves commit history and statistics for each branch.
4. **Database Update**: Pushes new or updated commit data to the SQL database.

## Functions

### `fetch_repos(org_name)`
Fetches the list of repositories for the specified organization.

### `fetch_branches(org_name, repo_name)`
Retrieves all branches for a given repository.

### `fetch_commits(org_name, repo_name, branch, since_date)`
Fetches commit history for a branch, optionally filtering by date.

### `fetch_commit_stats(org_name, repo_name, commits)`
Retrieves detailed statistics (additions, deletions, and totals) for each commit.

### `sql_data_match(organization, rp_name, data)`
Formats commit data for insertion into the SQL database.

### `sql_push(df)`
Inserts a Pandas DataFrame into the SQL database.

### `sql_stored_procedure()`
Executes a stored procedure and retrieves existing commit data from the database.

### `main()`
Coordinates the fetching, processing, and updating of commit data.

## Example Output

- Prints information about missing repositories and branches.
- Displays fetched commit data.
- Logs SQL insertion and connection statuses.

## Notes

- Ensure your Keeper secrets are properly configured and authorized.
- Use a GitHub personal access token with sufficient permissions for the organization.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
```