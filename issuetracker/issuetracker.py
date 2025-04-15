import requests
import time

def list_issues(user_id):
    url = 'https://jsonplaceholder.typicode.com/posts'
    params = {'userId': user_id}
    response = requests.get(url, params = params)
    if response.status_code == 200:
        data = response.json()
        for i in data:
            print(f"Issue ID: {i['id']} | Title: {i['title']}")
    else:
        print(f"response failed with status_code {response.status_code}")

def create_issue(user_id, title, body):
    url = "https://jsonplaceholder.typicode.com/posts"
    payload = {
                "userId": user_id,
                "title": title,
                "body": body
            }
    response = requests.post(url, json = payload)
    if response.status_code == 201: # Created
        data = response.json()
        print(f"ID of new issue: {data['user_id']}")
    else: 
        print(f"Failed to create issue. Status code: {response.status_code}")
        print(response.text)
        return None

def update_issue_title(issue_id, new_title):
    url = f'https://jsonplaceholder.typicode.com/posts/{issue_id}'
    payload = {
        'title': new_title
    }
    response = requests.patch(url, payload)
    if response.status_code == 200:
        data = response.json()
        print(f"New Title: {data['title']}")
    else:
        print(f"Failed to patch data with status {response.status_code}")

def delete_issue(issue_id):
    url = f'https://jsonplaceholder.typicode.com/posts/{issue_id}'
    response = requests.delete(url)
    if response.status_code == 200:
        print(f"Deleted issue {issue_id} successfully")

def rate_limit(url):
    response = requests.get(url)
    if response.status_code == 429:
        retry_after = int(response.headers.get("Retry-After", 5))  # default 5 seconds
        print(f"Rate limit hit. Retrying in {retry_after} seconds...")
        time.sleep(retry_after)
        #continue