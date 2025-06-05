import re
import aiohttp


async def get_client_id() -> str:
    """
    Asynchronously retrieves the SoundCloud client ID by parsing the SoundCloud homepage
    and its associated JavaScript files.
    Args:
        session (aiohttp.ClientSession): An active aiohttp session used to perform HTTP requests.
    Returns:
        str: The extracted SoundCloud client ID.
    Raises:
        RuntimeError: If the client ID cannot be found in the JavaScript files.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get("https://soundcloud.com") as resp:
            html = await resp.text()

        js_urls = re.findall(
            r'src="(https://a-v2\.sndcdn\.com/assets/\w+-\w+\.js)"', html
        )
        for js_url in js_urls:
            async with session.get(js_url) as js_resp:
                js = await js_resp.text()
                match = re.search(r'client_id\s*:\s*"(?P<client_id>\w+)"', js)
                if match:
                    return match.group("client_id")
    raise RuntimeError("client_id not found")
