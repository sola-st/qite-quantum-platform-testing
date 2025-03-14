import os
import requests
import pandas as pd
from bs4 import BeautifulSoup
import click
import hashlib


@click.command()
@click.option(
    '--bug_csv', '-i', required=True, type=click.Path(exists=True),
    help='Path to the input CSV file.')
@click.option('--output_folder', '-o', required=True, type=click.Path(),
              help='Path to the output directory.')
@click.option('--full', is_flag=True,
              help='Download all comments, not just the first one.')
@click.option('--github_token_path', default='github_token.txt',
              help='Path to file containing GitHub token.')
@click.option('--to_anonymize', help='Word to be replaced with <<ANONYMOUS>>')
def download_issues(
        bug_csv, output_folder, full, github_token_path, to_anonymize):
    # Read GitHub token
    try:
        with open(github_token_path, 'r') as f:
            github_token = f.read().strip()
    except FileNotFoundError:
        raise click.ClickException(
            f"GitHub token file not found: {github_token_path}")
    # Set up headers for authenticated requests
    headers = {
        'Authorization': f'bearer {github_token}',
        'Content-Type': 'application/json',
    }

    # GraphQL endpoint
    url = 'https://api.github.com/graphql'

    # Ensure output directory exists
    os.makedirs(output_folder, exist_ok=True)

    # Read the CSV file
    df = pd.read_csv(bug_csv)

    for index, row in df.iterrows():
        github_link = row['github_link']
        # Extract owner, repo, and issue number from the URL
        parts = github_link.split('/')
        owner = parts[3]
        repo = parts[4]
        issue_number = int(parts[6])

        # GraphQL query with author information
        query = """
        query($owner: String!, $repo: String!, $number: Int!) {
            repository(owner: $owner, name: $repo) {
            issue(number: $number) {
                title
                body
                author {
                    login
                }
                comments(first: 100) {
                nodes {
                    body
                    author {
                        login
                    }
                }
                }
            }
            }
        }
        """

        variables = {
            'owner': owner,
            'repo': repo,
            'number': issue_number
        }

        try:
            response = requests.post(
                url, json={'query': query, 'variables': variables},
                headers=headers)
            response.raise_for_status()
            data = response.json()

            issue_data = data['data']['repository']['issue']
            issue_content = f"Title: {issue_data['title']}\nAuthor: {issue_data['author']['login']}\n\n{issue_data['body']}"

            if full:
                print(f"Downloading full content for {github_link}")
                comments = [
                    f"Author: {comment['author']['login']}\n{comment['body']}"
                    for comment in issue_data['comments']['nodes']]
                issue_content += '\n\nComments:\n' + '\n---\n'.join(comments)

            if to_anonymize:
                issue_content = issue_content.replace(
                    to_anonymize, '<<ANONYMOUS>>')

            filename = f"{owner}_{repo}_{issue_number}.txt"
            if to_anonymize:
                # hash the filename
                filename = hashlib.md5(
                    github_link.encode()).hexdigest()[
                    : 6] + '.txt'
            with open(os.path.join(output_folder, filename), 'w') as f:
                f.write(issue_content)

        except Exception as e:
            print(f"Error processing {github_link}: {str(e)}")
            with open(os.path.join(output_folder, f"{owner}_{repo}_{issue_number}.txt"), 'w') as f:
                f.write(f"Error: {str(e)}")

    if any(df['github_link'].str.contains("https://github.com")):
        anonymized_csv = bug_csv.replace('.csv', '_anonymized.csv')
        df_bugs = pd.read_csv(bug_csv)
        df_bugs['github_link'] = df_bugs['github_link'].apply(
            lambda x: hashlib.md5(x.encode()).hexdigest()[:6])
        df_bugs.to_csv(anonymized_csv, index=False)
        print(f"Anonymized CSV saved to {anonymized_csv}")

# Example usage:
# python -m reports.download_issues -i reports/bugs_v001.csv -o reports/github_issues_full --full --to_anonymize "John Doe"


if __name__ == '__main__':
    download_issues()
