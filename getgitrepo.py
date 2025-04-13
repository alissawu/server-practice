import requests
import pprint 
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
    data.append(response.json())
# each thing is just one repo
print(data[0].keys())

# Extracts and prints the following:
# full_name
# stargazers_count
# forks_count
# open_issues_count
