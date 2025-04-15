import requests

url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    # print(data[0])
    sort_coins = []
    for i in data: 
        # can't be none, has to exist
        if i['price_change_percentage_24h'] and i['price_change_percentage_24h'] != None:
            j = {
                'id': i.get('id'),
                'symbol': i.get('symbol'),
                'name': i.get('name'),
                'current_price': i.get('current_price'),
                'price_change_percentage_24h': i.get('price_change_percentage_24h')
            }
            sort_coins.append(j)
    sort_gains = sorted(sort_coins, key= lambda x: x['price_change_percentage_24h'], reverse = True)
    for i in range(5):
        item = sort_gains[i]
        posneg = '+' if item['price_change_percentage_24h'] > 0 else '-'
        print(f"{i+1}. {item['id']} ({item['symbol']}): ${item['current_price']}({posneg}{item['price_change_percentage_24h']}%)")

    

else:
    print("Response failed with status ", response.status_code)