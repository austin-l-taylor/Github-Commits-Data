import requests
import datetime
import pandas as pd
import pyodbc
import configparser

# Configuration
# Initialize the ConfigParser
config = configparser.ConfigParser()
config.read("config.key")
access_token = config.get("DEFAULT", "access_token")

ORG_NAME = "McKenneys-App-Dev"
HEADERS = {
    "Authorization": f"Bearer {access_token}",
    "Accept": "application/vnd.github.v3+json",
}


def fetch_repos(org_name):
    """
    Fetch repositories from an organization.

    Args:
        org_name (str): The name of the organization.

    Returns:
        list: A list of repository names.
    """
    url = f"https://api.github.com/orgs/{org_name}/repos"
    repo_list = []

    # Fetch all repositories from the organization
    while url:
        try:
            response = requests.get(url, headers=HEADERS)
            response.raise_for_status()
            repos = response.json()
            for repo in repos:
                repo_list.append(repo["name"])
            # Get the URL for the next page of results, if any
            url = response.links.get("next", {}).get("url")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch repositories: {e}")
            return None
    return repo_list


def fetch_branches(org_name, repo_name):
    """
    Fetch branches from a repository.

    Args:
        org_name (str): The name of the organization.
        repo_name (str): The name of the repository.

    Returns:
        list: A list of branches.
    """

    url = f"https://api.github.com/repos/{org_name}/{repo_name}/branches"
    branch_names = []

    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        branches = response.json()

        for branch in branches:
            branch_name = branch["name"]
            branch_names.append(branch_name)
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print(f"Repository {repo_name} not found.")
        else:
            print(f"Failed to fetch branches for {repo_name}: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Request exception occurred: {e}")

    return branch_names


def fetch_commits(org_name, repo_name, branch, since_date):
    """
    Fetch commits from a repository since a specific date.

    Args:
        org_name (str): The name of the organization.
        repo_name (str): The name of the repository.
        since_date (str): The ISO 8601 date string to filter commits.

    Returns:
        list: A list of commits.
    """

    url = f"https://api.github.com/repos/{org_name}/{repo_name}/commits"
    params = {"sha": branch}
    if since_date:
        params["since"] = since_date  # include since date if provided
    commits = []

    print(f"fetching commits for Repo: {repo_name} Branch: {branch}")

    while url:
        try:
            # Fetch commits from the repository
            response = requests.get(url, headers=HEADERS, params=params)
            response.raise_for_status()
            # Append the fetched commits to the list
            commits += response.json()
            # Get the URL for the next page of results, if any
            url = response.links.get("next", {}).get("url")
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch commits for {repo_name}: {e}")
            break  # Stop fetching commits if an error occurs

    return commits


def fetch_commit_stats(org_name, repo_name, commits):
    """
    Fetch commit stats for each commit.

    Args:
        org_name (str): The name of the organization.
        repo_name (str): The name of the repository.
        commit_details_list (list): A list of commit details.

    """
    commit_sha_data = {}

    for commit in commits:
        commit_sha = commit["sha"]
        url = (
            f"https://api.github.com/repos/{org_name}/{repo_name}/commits/{commit_sha}"
        )
        response = requests.get(url, headers=HEADERS)
        commits = response.json()

        commit_sha_data[commit_sha] = {
            "additions": commits["stats"]["additions"],
            "deletions": commits["stats"]["deletions"],
            "total": commits["stats"]["total"],
        }

    return commit_sha_data


def merge_commit_data(commits, commit_details, branch):
    """
    Extract and Merge commit details from commits with their stats.

    Args:
        commits (list): A list of commits.
        commit_details (dict): A dictionary with commit SHA as keys and stats data as values.

    Returns:
        list: A list of merged commit details dictionaries.
    """
    commit_details_list = []

    for commit in commits:
        commit_sha = commit["sha"]
        # Initialize commit_details_dict with common commit details
        commit_details_dict = {
            "commit_sha": commit["sha"],
            "commit_date": commit["commit"]["committer"]["date"],
            "commit_name": commit["commit"]["committer"]["name"],
            "commit_email": commit["commit"]["committer"]["email"],
            "commit_message": commit["commit"]["message"],
            "commit_url": commit["html_url"],
            "commit_branch": branch,
        }

        # Check if commit SHA is in commit_details and update the commit_details_dict with stats
        if commit_sha in commit_details:
            commit_details_dict.update(
                {
                    "additions": commit_details[commit_sha]["additions"],
                    "deletions": commit_details[commit_sha]["deletions"],
                    "total": commit_details[commit_sha]["total"],
                }
            )

        # Append the updated commit_details_dict to commit_details_list
        commit_details_list.append(commit_details_dict)

    return commit_details_list


def sql_data_match(organization, rp_name, data):
    """
    Write data to a CSV file with specified organization and project name.

    Args:
        organization (str): The name of the organization.
        rp_name (str): The name of the project/repository.
        data (list): A list of dictionaries with data to be included in the CSV.
    """

    key_mapping = {
        "commit_sha": "commitSHA",
        "commit_date": "commitDate",
        "commit_name": "commitName",
        "commit_email": "commitEmail",
        "commit_message": "commitMessage",
        "commit_url": "commitURL",
        "additions": "numAdditions",
        "deletions": "numDeletions",
        "total": "totalChanges",
        "commit_branch": "branch",
    }

    # Initialize an empty list to hold the data for the DataFrame
    df_data = []

    # Iterate over the data to populate the df_data list with dictionaries
    # Each dictionary represents a row in the DataFrame
    for item in data:
        row = {"Organization": organization, "Project": rp_name}
        for key, value in item.items():
            # Update row with additional data, applying key mapping if necessary
            new_key = key_mapping.get(key, key)
            row[new_key] = value

        df_data.append(row)

    # Create a DataFrame from the df_data list
    df = pd.DataFrame(df_data)

    return df


def sql_push(df):
    """
    Push DataFrame to SQL database.
    """
    username = config.get("DEFAULT", "username")
    password = config.get("DEFAULT", "password")
    server = config.get("DEFAULT", "server")
    database = config.get("DEFAULT", "database")

    try:
        # Create the connection string
        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=" + server + ";"
            "DATABASE=" + database + ";"
            "UID=" + username + ";"
            "PWD=" + password
        )
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # Test the connection (optional)
        print("Connection successful!")

        # Handle empty values and cast to appropriate types
        df["Organization"] = df["Organization"].fillna("").astype(str)
        df["Project"] = df["Project"].fillna("").astype(str)
        df["commitSHA"] = df["commitSHA"].fillna("").astype(str)
        df["commitDate"] = pd.to_datetime(df["commitDate"], errors="coerce").fillna(
            pd.Timestamp("1900-01-01")
        )
        df["commitName"] = df["commitName"].fillna("").astype(str)
        df["commitEmail"] = df["commitEmail"].fillna("").astype(str)
        df["commitMessage"] = df["commitMessage"].fillna("").astype(str)
        df["commitURL"] = df["commitURL"].fillna("").astype(str)
        df["numAdditions"] = df["numAdditions"].fillna(0).astype(int)
        df["numDeletions"] = df["numDeletions"].fillna(0).astype(int)
        df["totalChanges"] = df["totalChanges"].fillna(0).astype(int)

        # Insert DataFrame into SQL table
        for _, row in df.iterrows():
            cursor.execute(
                """
                INSERT INTO Table Name (Organization, Project, commitSHA, commitDate, commitName, commitEmail, commitMessage, commitURL, numAdditions, numDeletions, totalChanges, branch) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                row["Organization"],
                row["Project"],
                row["commitSHA"],
                row["commitDate"],
                row["commitName"],
                row["commitEmail"],
                row["commitMessage"],
                row["commitURL"],
                row["numAdditions"],
                row["numDeletions"],
                row["totalChanges"],
                row["branch"],
            )

        connection.commit()
        print("Data pushed to SQL successfully!")

    except Exception as e:
        print(f"Error connecting to database: {e}")

    finally:
        connection.close()


def sql_stored_procedure():
    """
    Execute a stored procedure in SQL and return the results.
    """
    username = config.get("DEFAULT", "username")
    password = config.get("DEFAULT", "password")
    server = config.get("DEFAULT", "server")
    database = config.get("DEFAULT", "database")

    connection = None

    try:
        # Create the connection string
        connection_string = (
            "DRIVER={ODBC Driver 17 for SQL Server};"
            "SERVER=" + server + ";"
            "DATABASE=" + database + ";"
            "UID=" + username + ";"
            "PWD=" + password
        )
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # Test the connection (optional)
        print("Connection successful!")

        # Execute the stored procedure
        cursor.execute("EXEC Stored Procedure Name")
        result = cursor.fetchall()
        connection.commit()
        print("Stored procedure executed successfully!")

        return result

    except pyodbc.Error as e:
        print(f"Error executing stored procedure: {e}")
        if connection:
            connection.rollback()
        return None

    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

    finally:
        if connection:
            connection.close()


def main():
    """
    Main function to fetch and process commits for repositories in an organization.
    """

    # Fetch the list of repositories for the organization
    repo_list = fetch_repos(ORG_NAME)

    # Retrive commit data
    repo_data = sql_stored_procedure()

    # Extracts Repo Names from Stored Proc
    project_names = [repo[1] for repo in repo_data]

    # Convertes Tuples to Sets
    repo_list_set = set(repo_list)
    project_name_set = set(project_names)

    # Gets list of missing repos from the stored procedure and the fetched repos
    missing_repos = repo_list_set - project_name_set
    print(f"\nmissing repos: {missing_repos}")

    # Dictionary to store branches for each repo
    branch_dict = {}

    # Adds branches for missing repos
    for repo in missing_repos:
        branch_dict[repo] = fetch_branches(ORG_NAME, repo)

    # Adds new repos and commits not in database
    for repo, branches in branch_dict.items():
        for branch in branches:
            new_commits = fetch_commits(
                ORG_NAME, repo, branch, since_date=None
            )  # Fetches all commits for the new repo
            new_commit_stats = fetch_commit_stats(
                ORG_NAME, repo, new_commits
            )  # Fetches commit stats for the new repo
            new_commit_details = merge_commit_data(
                new_commits, new_commit_stats, branch
            )  # Merges commit data for the new repo

            # Data match and SQL push
            if new_commit_details:
                new_sql_data = sql_data_match(ORG_NAME, repo, new_commit_details)

                # Fix branch names
                branch_name_replace = branch.replace("/", "-")
                df = pd.DataFrame(new_sql_data)
                df.to_csv(
                    f"./Commit Data/{repo}_{branch_name_replace}.csv", index=False
                )  # Write to CSV
                sql_push(new_sql_data)

    # Grabs latest commits from existing repos in database
    for row in repo_data:
        project = row[1]  # Repo Name Index
        previous_date = row[2]  # Date Index

        # changing to ISO format
        current_date = previous_date + datetime.timedelta(seconds=1)
        current_date = current_date.isoformat()

        branches = fetch_branches(ORG_NAME, project)

        for branch in branches:
            commits = fetch_commits(
                ORG_NAME, project, branch, current_date
            )  # Fetches all commits for the repo
            commit_stats = fetch_commit_stats(
                ORG_NAME, project, commits
            )  # Fetch commit stats for the commits
            commit_details = merge_commit_data(
                commits, commit_stats, branch
            )  # Extract commit details from the commits

            # Data match and SQL push
            if commit_details:
                sql_data = sql_data_match(ORG_NAME, project, commit_details)
                print(f"Commit Data:\n{sql_data}")
                sql_push(sql_data)

            else:
                print(f"No New Commits for Repo: {project} Branch: {branch}")


if __name__ == "__main__":
    main()
