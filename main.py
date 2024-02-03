import sys
from datetime import datetime, timedelta
import json
import aiohttp
import asyncio
import platform


class HttpError(Exception):
    pass


async def request(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result
                else:
                    raise HttpError(f"Error status: {resp.status} for {url}")
        except aiohttp.ClientConnectorError as err:
            raise HttpError(f'Connection error: {url}', str(err))


async def main(index_days):
    responses = []
    for index_day in range(0, int(index_days)):
        d = datetime.now() - timedelta(days=index_day)
        shift = d.strftime("%d.%m.%Y")
        try:
            response = await request(f'https://api.privatbank.ua/p24api/exchange_rates?date={shift}')
            currencies = {}
            for rate in response['exchangeRate']:
                if rate['currency'] in ['EUR', 'USD']:
                    currencies[rate['currency']] = {
                        'sale': rate['saleRateNB'],
                        'purchase': rate['purchaseRateNB']
                    }
            responses.append({shift: currencies})
        except HttpError as err:
            print(err)
            responses.append({shift: None})
    return json.dumps(responses, indent=2)


if __name__ == '__main__':
    if platform.system() == 'Windows':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main(sys.argv[1]))
    print(r)

    

