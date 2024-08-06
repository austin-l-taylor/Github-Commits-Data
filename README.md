# GitHub Repository and Commit Data Processor

This Python script fetches repository and commit data from a GitHub organization and pushes it to a SQL database. It leverages the Keeper security service to securely retrieve sensitive information such as access tokens and database credentials.

## Prerequisites

- Python 3.x
- `requests` library
- `datetime` library
- `pandas` library
- `pyodbc` library
- `json` library
- `keeper` library (for accessing Keeper secrets)

## Setup

1. Install required libraries:
   ```bash
   pip install requests pandas pyodbc json keeper
   ```
2. Ensure you have the Keeper library set up for handling secrets.
3. Configure the `SECRET_ID` in the script with your Keeper secret ID.
4. Update the `ORG_NAME` variable with the name of the GitHub organization you want to fetch data from.

## Functions

- `fetch_repos(org_name)`: Fetches repositories from the specified organization.
- `fetch_commits(org_name, repo_name, since_date)`: Fetches commits from a repository since a specific date.
- `fetch_commit_stats(org_name, repo_name, commits)`: Fetches commit stats for each commit.
- `merge_commit_data(commits, commit_details)`: Merges commit details with their stats.
- `sql_data_match(organization, rp_name, data)`: Prepares data for SQL insertion.
- `sql_push(df)`: Pushes data to the SQL database.
- `sql_stored_procedure()`: Executes a stored procedure in SQL.
- `main()`: Main function to orchestrate fetching and processing commits.

## Security

This script uses the Keeper library for secure access to secrets, ensuring that sensitive information like API tokens and database credentials are not hard-coded into the script.