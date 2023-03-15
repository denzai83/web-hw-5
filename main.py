import aiohttp
import asyncio
import json
import sys
from datetime import datetime, timedelta

API_URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&date='


async def get_data(date):
    url = API_URL + date.strftime('%d.%m.%Y')
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                return await resp.json()
        except aiohttp.ClientError as err:
            print(f"Error getting data for date {date.strftime('%d.%m.%Y')}: {err}")
            return None



async def get_data_for_period(days):
    result = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        data = await get_data(date)
        if data is not None:
            result.append(data)
    return result


async def main(days, currencies):
    data = await get_data_for_period(days)
    result = []
    for d in data:
        item = {}
        for rate in d['exchangeRate']:
            item['date'] = d['date']
            if rate['currency'] in currencies:
                if 'saleRate' in rate and 'purchaseRate' in rate:
                    item[rate['currency']] = {'sale': rate['saleRate'], 'purchase': rate['purchaseRate']}
                else:
                    continue
        result_item = {item['date']: {}}
        for currency in currencies:
            if currency in item:
                result_item[item['date']][currency] = {'sale': item[currency]['sale'], 'purchase': item[currency]['purchase']}
        result.append(result_item)
    print(json.dumps(result, indent=2))



if __name__ == '__main__':
    try:
        days = int(sys.argv[1])
    except ValueError:
        print('Please enter the required period between 1 and 10 days')
        sys.exit(1)
    except IndexError:
        print('Please enter the required period and currencies')
        sys.exit(1)
    currencies = ['USD', 'EUR']
    if len(sys.argv) > 2:
        extra_currencies = [c.upper() for c in sys.argv[2:]]
        currencies.extend(extra_currencies)
    if days > 10:
        print('You can get exchange rates for no more than 10 days')
        sys.exit(1)
    asyncio.run(main(days, currencies))
   