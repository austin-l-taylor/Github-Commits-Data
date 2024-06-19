import requests
from pprint import pprint
import json

ACCESS_TOKEN = 'access token here'
ORG_NAME = 'McKenney-s-Inc-RPA'
REPO_NAME = 'CylanceReport'

# TODO: Add grab HTML URL for each commit
# TODO: Add Message for each commit
# TODO: Filter based off last changed date for commits

def main():
    # List to store commit details
    commit_details_list = []
    commit_sha_data = []
    
    # GitHub API URL to list commits
    url = f'https://api.github.com/repos/{ORG_NAME}/{REPO_NAME}/commits'

    # Headers for the request
    headers = { 
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Accept': 'application/vnd.github.v3+json',
    }

    # API request
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses
        commits = response.json()
        
        # View JSON data in a before format
        with open('commit_data.json', 'w') as f:
            json.dump(commits, f, indent=4)
            
        for commit in commits:
            # Extract the commit SHA and API URL (SHA Secure Hash Algorithm)
            commit_sha = commit['sha']
            commit_details = commit['commit']['committer']
            
            # Dictionary to store commit details
            commit_details_dict = {
                'commit_sha': commit_sha,
                'commit_date': commit_details['date'],
                'commit_name': commit_details['name'],
                'commit_email': commit_details['email']
            }
            
            commit_details_list.append(commit_details_dict)

        # Fetch commit stats
        for commit in commit_details_list:
            commit_sha = commit['commit_sha']
            url = f'https://api.github.com/repos/{ORG_NAME}/{REPO_NAME}/commits/{commit_sha}' 
            response = requests.get(url, headers=headers)
            commits = response.json() 
            commit_sha_data.append(commits)
            commit_stats = commits['stats'] 
            commit['commit_stats'] = commit_stats

        # All SHA data
        with open('commit_sha_data.json', 'w') as f:
            json.dump(commit_sha_data, f, indent=4)
        
        # Filtered JSON data  
        with open('commit_filtered_data.json', 'w') as f:
            json.dump(commit_details_list, f, indent=4) 
            
    except requests.exceptions.RequestException as e:
         print(f"Failed to fetch commits: {e}")

if __name__ == '__main__':
    main()