import requests
import time
# 1. Fetch CRM users
def fetch_crm_users():
    url = 'https://jsonplaceholder.typicode.com/users'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data

# 2. Fetch Billing Users
def fetch_billing_users():
    url = 'https://api.mockbilling.com/customers'
    all_customers = []
    headers = {"Authorization": "Bearer faketoken123"}
    while url: # use this to loop to next, if no more then this is None
        response = requests.get(url, headers = headers)
        if response.status_code != 200:
            if response.status_code == 404:
                print(f"Resource not found")
            elif response.status_code == 500:
                print(f"Internal server error")
            else:
                print(f"Request failed")
            break
        data = response.json()
        all_customers.extend(data.get('customers', []))
        # parse Link header to find next page
        url = data.get("meta", {}).get("next")
    return all_customers

# 3. Sync users
def sync_users(crm_data, billing_users):
    new_bill, update_email, delete_ghost = 0,0,0
    for crm_user in crm_data:
        url = f'https://api.mockbilling.com/customers'
        # in billing, crm_id is used for the crm_user's id
        params = {'crm_id': crm_user['id']}
        response = requests.get(url, params = params)
        if response.status_code == 404:
            payload = {
                'crm_id': crm_user['id'],
                'full_name': crm_user['name'], 
                'email_address': crm_user['email']
            }
            postresp = requests.post(url, json=payload)
            new_bill += 1
        elif response.status_code == 200:
            data = response.json()
            if data['email_address'] != crm_user['email']:
                payload = {
                    'email_address': crm_user['email']
                }
                response.patch(url, json = payload)
                update_email += 1
    # if user not in CRM, delete
    for bill_user in billing_users:
        url = 'https://jsonplaceholder.typicode.com/users'
        response = requests.get(url)
        crm_ids = {u['id'] for u in crm_data}
        for bill_user in billing_users:
            if bill_user['crm_id'] not in crm_ids:
                bill_url = f'https://api.mockbilling.com/customers'
                params = {'crm_id': bill_user['crm_id']}
                response = requests.delete(bill_url, params = params)
                delete_ghost += 1
    print(f'Created {new_bill} new billing users \n Updated {update_email} emails \n "Deleted {delete_ghost} ghost billing users')



if __name__ == "__main__":
    fetch_crm_users()
    fetch_billing_users()
