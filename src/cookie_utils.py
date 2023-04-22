import os

import aiofiles
import ujson as json
from loguru import logger as log


async def save_cookies(cookies, cookie_jar):
    """Save cookies to file

    Args:
        cookies (Cookies): Cookies to save
        cookie_jar (str): Path to cookie jar
    """
    async with aiofiles.open(cookie_jar, "w") as file:
        log.debug(f"Saving cookies to {cookie_jar}")
        await file.write(json.dumps(dict(cookies)))


def load_cookies(cookie_jar) -> dict[str, str]:
    """Load cookies from file

    Args:
        cookie_jar (str): Path to cookie jar

    Returns:
        dict[str, str]: Cookies
    """
    if not os.path.exists(cookie_jar):
        log.info(f"Cookie jar {cookie_jar} does not exist. Returning empty dict.")
        return {}
    with open(cookie_jar, "r") as file:
        log.debug(f"Loading cookies from {cookie_jar}")
        return json.loads(file.read())
