### APP CONFIG

service: str = "onlyfans"

guild_id: int = 1097584844130750524

discord_token: str = (
    ""
)

avatar_url: str = "https://cdn.discordapp.com/avatars/533329645269942304/09e6c61bc129927ce1cef8603abcf5b8.png"

headers: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"
}

cookie_jar_file: str = "./cookie_jar.json"

### API URLS

base_coomer: str = "https://coomer.party/"

models_url: str = "https://coomer.party/api/creators/"
icon_base_url: str = f"http://coomer.party/icons/{service}/"
banner_base_url: str = f"https://coomer.party/banners/{service}/"

base_onlyfans_url: str = "https://onlyfans.com/"
base_coomer_url: str = f"https://coomer.party/{service}/user/"
