import asyncio
import aiohttp
from config import API_WEATHER_URL, API_WEATHER_TOKEN


async def get_temperature_async(city) -> float | int | None:
    url = API_WEATHER_URL
    params = {"q": city, "appid": API_WEATHER_TOKEN, "units": "metric"}
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(API_WEATHER_URL, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('main', None).get('temp', None)
                else:
                    print(f"Ошибка API: {response.status}, {await response.text()}", flush=True)
        except aiohttp.ClientError as e:
            print(f"Ошибка клиента API: {e}", flush=True)
        except asyncio.TimeoutError:
            print("Ошибка: Таймаут при запросе к API", flush=True)
    return None

async def get_food_info_async(product_name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?action=process&search_terms={product_name}&json=true"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    products = data.get('products', [])
                    if products:  # Проверяем, есть ли найденные продукты
                        first_product = products[0]
                        return {
                            'name': first_product.get('product_name', 'Неизвестно'),
                            'calories': first_product.get('nutriments', {}).get('energy-kcal_100g', 0)
                        }
                    return None
                else:
                    print(f"Ошибка API: {response.status}, {await response.text()}", flush=True)
        except aiohttp.ClientError as e:
            print(f"Ошибка клиента API: {e}", flush=True)
        except asyncio.TimeoutError:
            print("Ошибка: Таймаут при запросе к API", flush=True)
    return None
