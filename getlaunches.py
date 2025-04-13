import requests

url = "https://api.spacexdata.com/v4/launches"
response = requests.get(url)

def print_keys(d, indent = 0):
    if isinstance(d, dict):
        for key, value in d.items():
            print("  " * indent + str(key))
            print_keys(value, indent + 1)
    elif isinstance(d, list) and len(d)>0:
        print_keys(d[0]) # check to see if inside the list are more keys?

if response.status_code == 200:
    data = response.json() # fetches all
    # see the shape of the data
    # print(data[0])
    # see the categories
    # print(data[0].keys())
    # print_keys(data)
    failed_data = []
    # 'success': False -- means failed
    
    for i in data:
        if i['success'] is False:
            j = {
                    'name': i.get('name'),
                    'date': i.get('date_utc'),
                    'reason': i.get('details'),
                    'article': i.get('article')
                }
            failed_data.append(j)
            print(j)
    print("Number of failed launches: ", len(failed_data))
            
else:
    print("Data retrieval failed with error code: ", response.status_code)




