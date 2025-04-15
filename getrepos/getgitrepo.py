import requests
import json
import csv
# "https://api.github.com/repos/{owner}/{repo}"
url = "https://api.github.com/repos/"
repos = [
    "pallets/flask",
    "django/django",
    "fake/repo-that-does-not-exist",
    "numpy/numpy",
    "psf/requests"
]


data = []
for i in repos:
    url2 = url + i
    response = requests.get(url2)
    if response.status_code == 200:  # make sure to check this!
        data.append(response.json())
    else:
        print(f"Failed to access {url2} with status code {response.status_code}")
# each item is just one repo
#print(data[0].keys())

# Extracts and prints the following:
# full_name
# stargazers_count
# forks_count
# open_issues_count
data2 = []
for i in data:
    if isinstance(i['stargazers_count'], int):
        j = {
            'full_name': i.get('full_name'),
            'stargazers_count': i.get('stargazers_count'),
            'forks_count': i.get('forks_count'),
            'open_issues_count': i.get('open_issues_count')
        }
        data2.append(j)

# create or overwrite repos.json, f is the opened file object
with open("repos.json", "w") as f:
    json.dump(data2, f, indent=2)

# create or overwrite repos.csv, 
with open("repos.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames = data2[0].keys())
    writer.writeheader()
    writer.writerows(data2)

# reverse = True for descend?
sorted_stars = sorted(data2, key = lambda x : x['stargazers_count'], reverse = True)
for i in sorted_stars:
    slashidx = i['full_name'].index("/") + 1
    name = i['full_name'][slashidx:]
    issues = 'issues' if i['open_issues_count']>1 else 'issue'
    print(f"{name}: ⭐{i['stargazers_count']} | 🍴 {i['forks_count']} | 🐛 {i['open_issues_count']} {issues}")



