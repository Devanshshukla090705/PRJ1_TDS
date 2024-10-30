# -*- coding: utf-8 -*-
"""scrapper.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1kScZ0icOhQOCRJ313NkTmIfV1M7DZfGh
"""

import requests
import pandas as pd
import csv

# GitHub API Setup
TOKEN = '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'
HEADERS = {'Authorization': f'token {TOKEN}'}

# API URL for searching users in Chicago with > 100 followers
USER_SEARCH_URL = "https://api.github.com/search/users"
REPO_URL_TEMPLATE = "https://api.github.com/users/{}/repos"

def get_users():
    users = []
    params = {'q': 'location:Chicago followers:>100', 'per_page': 100}
    response = requests.get(USER_SEARCH_URL, headers=HEADERS, params=params)
    data = response.json()

    for user in data.get('items', []):
        login = user['login']
        user_details = get_user_details(login)
        if user_details:
            users.append(user_details)

    return users

def get_user_details(login):
    """Fetch and clean user details."""
    url = f"https://api.github.com/users/{login}"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        user = response.json()
        return {
            'login': user['login'],
            'name': user.get('name', ''),
            'company': clean_company(user.get('company', '')),
            'location': user.get('location', ''),
            'email': user.get('email', ''),
            'hireable': str(user.get('hireable', '')),
            'bio': user.get('bio', ''),
            'public_repos': user.get('public_repos', 0),
            'followers': user.get('followers', 0),
            'following': user.get('following', 0),
            'created_at': user.get('created_at', '')
        }
    return None

def clean_company(company):
    """Clean company name as required."""
    company = company.strip().lstrip('@').upper() if company else ''
    return company

def get_repositories(login):
    """Fetch repositories of a given user."""
    url = REPO_URL_TEMPLATE.format(login)
    params = {'per_page': 500}
    response = requests.get(url, headers=HEADERS, params=params)
    if response.status_code == 200:
        repos = response.json()
        return [
            {
                'login': repo['owner']['login'],
                'full_name': repo['full_name'],
                'created_at': repo['created_at'],
                'stargazers_count': repo['stargazers_count'],
                'watchers_count': repo['watchers_count'],
                'language': repo.get('language', ''),
                'has_projects': str(repo.get('has_projects', '')),
                'has_wiki': str(repo.get('has_wiki', '')),
                'license_name': repo['license']['key'] if repo.get('license') else ''
            }
            for repo in repos
        ]
    return []

def save_to_csv(users, repositories):
    """Save users and repositories data to CSV."""
    users_df = pd.DataFrame(users)
    repos_df = pd.DataFrame(repositories)

    users_df.to_csv('users.csv', index=False)
    repos_df.to_csv('repositories.csv', index=False)

def main():
    users = get_users()
    repositories = []
    for user in users:
        repos = get_repositories(user['login'])
        repositories.extend(repos)

    save_to_csv(users, repositories)
    print("Data saved to users.csv and repositories.csv")

if __name__ == "__main__":
    main()

import pandas as pd

# Load the data
users_df = pd.read_csv('users.csv')
repos_df = pd.read_csv('repositories.csv')

# 1. Top 5 users with the highest number of followers
top_5_followers = users_df.nlargest(5, 'followers')['login'].tolist()
print("Top 5 users by followers:", ', '.join(top_5_followers))

# 2. 5 earliest registered GitHub users in ascending order of created_at
earliest_users = users_df.sort_values('created_at').head(5)['login'].tolist()
print("5 earliest registered users:", ', '.join(earliest_users))

# 3. 3 most popular licenses (ignoring missing licenses)
popular_licenses = repos_df['license_name'].dropna().value_counts().head(3).index.tolist()
print("3 most popular licenses:", ', '.join(popular_licenses))

# 4. Company with the majority of developers
major_company = users_df['company'].mode()[0]
print("Company with the majority of developers:", major_company)

# 5. Most popular programming language
popular_language = repos_df['language'].mode()[0]
print("Most popular programming language:", popular_language)

# 6. Second most popular language among users who joined after 2020
users_2020 = users_df[pd.to_datetime(users_df['created_at']) >= '2020-01-01']
second_popular_language = repos_df[repos_df['login'].isin(users_2020['login'])]['language'].value_counts().index[1]
print("Second most popular language (after 2020):", second_popular_language)

# 7. Language with the highest average number of stars per repository
avg_stars_per_language = repos_df.groupby('language')['stargazers_count'].mean().idxmax()
print("Language with highest average stars per repo:", avg_stars_per_language)

# 8. Top 5 users by leader_strength (followers / (1 + following))
users_df['leader_strength'] = users_df['followers'] / (1 + users_df['following'])
top_5_leader_strength = users_df.nlargest(5, 'leader_strength')['login'].tolist()
print("Top 5 users by leader_strength:", ', '.join(top_5_leader_strength))

# 9. Correlation between the number of followers and public repositories
correlation_followers_repos = users_df['followers'].corr(users_df['public_repos'])
print(f"Correlation between followers and public repos: {correlation_followers_repos:.3f}")

# 10. Regression slope: followers vs. public repositories
slope_followers_repos = users_df['followers'].cov(users_df['public_repos']) / users_df['public_repos'].var()
print(f"Regression slope of followers on repos: {slope_followers_repos:.3f}")

# 11. Correlation between having projects and wikis enabled
projects_wiki_corr = repos_df['has_projects'].astype(bool).corr(repos_df['has_wiki'].astype(bool))
print(f"Correlation between projects and wiki enabled: {projects_wiki_corr:.3f}")

# 12. Difference in average following for hireable vs. non-hireable users
hireable_avg_following = users_df[users_df['hireable'] == 'True']['following'].mean()
non_hireable_avg_following = users_df[users_df['hireable'] != 'True']['following'].mean()
following_difference = hireable_avg_following - non_hireable_avg_following
print(f"Difference in average following (hireable vs. non-hireable): {following_difference:.3f}")

# 13. Regression slope: followers vs. bio word count (ignore empty bios)
users_df['bio_word_count'] = users_df['bio'].fillna('').str.split().apply(len)
slope_followers_bio = users_df['followers'].cov(users_df['bio_word_count']) / users_df['bio_word_count'].var()
print(f"Regression slope of followers on bio word count: {slope_followers_bio:.3f}")

# 14. Top 5 users by the number of repositories created on weekends
repos_df['created_at'] = pd.to_datetime(repos_df['created_at'])
repos_df['is_weekend'] = repos_df['created_at'].dt.dayofweek >= 5
weekend_repos_count = repos_df[repos_df['is_weekend']].groupby('login').size()
top_5_weekend_users = weekend_repos_count.nlargest(5).index.tolist()
print("Top 5 users by repos created on weekends:", ', '.join(top_5_weekend_users))

# 15. Do hireable users share emails more often?
hireable_with_email = users_df[users_df['hireable'] == 'True']['email'].notna().mean()
non_hireable_with_email = users_df[users_df['hireable'] != 'True']['email'].notna().mean()
email_fraction_difference = hireable_with_email - non_hireable_with_email
print(f"Difference in email sharing (hireable vs. non-hireable): {email_fraction_difference:.3f}")

# 16. Most common surname (last word in the name, ignore missing names)
users_df['surname'] = users_df['name'].fillna('').str.split().str[-1]
most_common_surnames = users_df['surname'].value_counts()
max_count = most_common_surnames.max()
common_surnames = most_common_surnames[most_common_surnames == max_count].index.tolist()
print("Most common surname(s):", ', '.join(sorted(common_surnames)))

# Ensure 'hireable' column is boolean (treat empty values as False)
users_df['hireable'] = users_df['hireable'].fillna('').astype(str).str.lower().map({'true': True, 'false': False}).fillna(False)

# Calculate the average 'following' for hireable and non-hireable users
hireable_avg_following = users_df[users_df['hireable'] == True]['following'].mean()
non_hireable_avg_following = users_df[users_df['hireable'] == False]['following'].mean()

# Calculate the difference
following_difference = hireable_avg_following - non_hireable_avg_following
print(f"Difference in average following (hireable vs. non-hireable): {following_difference:.3f}")

# Ensure 'hireable' column is boolean
users_df['hireable'] = users_df['hireable'].fillna('').astype(str).str.lower().map({'true': True, 'false': False}).fillna(False)

# Count the fraction of users with email addresses for hireable and non-hireable users
hireable_with_email = users_df[users_df['hireable'] == True]['email'].notna().mean()
non_hireable_with_email = users_df[users_df['hireable'] == False]['email'].notna().mean()

# Calculate the difference
email_fraction_difference = hireable_with_email - non_hireable_with_email
print(f"Difference in email sharing (hireable vs. non-hireable): {email_fraction_difference:.3f}")

# Ensure 'name' column is clean (ignore missing names)
users_df['surname'] = users_df['name'].fillna('').str.split().str[-1]

# Get the most common surname(s) and their counts
most_common_surnames = users_df['surname'].value_counts()
max_count = most_common_surnames.max()
common_surnames = most_common_surnames[most_common_surnames == max_count]

# Extract the surnames and their count
surnames_list = common_surnames.index.tolist()
surname_count = common_surnames.iloc[0]  # All will have the same count due to the tie

# Print the result
print(f"Most common surname(s): {', '.join(sorted(surnames_list))}")
print(f"Number of users with the most common surname: {surname_count}")