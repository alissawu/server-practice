import requests
import time


# unifinised bc this bitch thing wants me to parse thro like 343379.04 pages of data 

def top50lang(LANGUAGE):
    url = f"https://api.github.com/search/repositories?q=language:{LANGUAGE}&sort=stars&order=desc&per_page=50"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        # print(data.keys()) 
        # dict_keys(['total_count', 'incomplete_results', 'items'])
        repodata = data['items']
        repos = []
        total_stars = 0
        total_forks = 0
        total_repos = data['total_count']
        num_over_100_issues = 0
        for i in repodata:
            j = {
                'full_name': i.get('full_name'),
                'stargazers_count': i.get('stargazers_count'),
                'forks_count': i.get('forks_count'),
                'open_issues_count': i.get('open_issues_count'),
                'created_at': i.get('created_at'),
                'owner.login': i.get('owner.login')
            }
            total_forks += i.get('forks_count')
            total_stars += i.get('stargazers_count')
            num_over_100_issues += 1 if i.get('open_issues_count')>100 else 0
            time.sleep(0.07)
            print("Item added to repos")
            print(j)
            repos.append(j)
        print(len(repos))
        print(total_repos)
        avg_stars = total_stars / total_repos
        percent_over_100_issues = num_over_100_issues / total_repos


    elif response.status_code == 403:
        print(f"Access denied ({response.status_code})")
    elif response.status_code == 404:
        print(f"Not found ({response.status_code})")
    else: 
        print(f"Error: Access code ({response.status_code})")

    
    
top50lang('python')