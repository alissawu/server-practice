import requests
import time
url = 'https://jsonplaceholder.typicode.com/users'
response = requests.get(url)
if response.status_code == 200:
    data = response.json()
    for u in data:
        url2 = f'https://jsonplaceholder.typicode.com/posts?userId={u['id']}'
        response2 = requests.get(url2)
        if response2.status_code == 200:
            data2 = response2.json()
            print(f'{u['name']} has {len(data2)} posts.')