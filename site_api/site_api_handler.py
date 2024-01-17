import aiohttp

from config_data.config import RAPID_API_KEY


async def user_request(params: dict) -> dict:
    """
    Function to send request to airbnb
    :param params: Dictionary of user parameters to send to airbnb
    :return: Dictionary of response from airbnb
    """
    url = "https://airbnb13.p.rapidapi.com/search-location"
    querystring = {
        "location": params['city'],
        "checkin": params['enter_date'],
        "checkout": params['exit_date'],
        "adults": params['adults'],
        "children": params.get('children', '0'),
        "infants": params.get('infants', '0'),
        "pets": params.get('pets', '0'),
        "page": "1-8",
        "currency": params.get('currency', 'USD')
    }
    headers = {
        "X-RapidAPI-Key": RAPID_API_KEY,
    }

    async with aiohttp.ClientSession() as session:
        response = await session.get(url, params=querystring, headers=headers)
        data = await response.json()
        return data
