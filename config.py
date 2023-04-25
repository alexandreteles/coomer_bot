### APP CONFIG

bot_name: str = "Coomer"

service: str = "onlyfans"

guild_id: int = 1097584844130750524

avatar_url: str = "https://cdn.discordapp.com/avatars/533329645269942304/09e6c61bc129927ce1cef8603abcf5b8.png"

headers: dict[str, str] = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.48"
}

cookie_jar_file: str = "./cookie_jar.json"

### AI GENERATION CONFIG

model: str = "dreamlike-diffusion-2.0.safetensors [fdcf65e7]"

prompt_prefix: str = "masterpiece, best quality, good anatomy, high quality, highres, high resolution, global illumination, real hair movement, realistic light, realistic shadow, "

negative_prompt: str = "worst quality, low quality, normal quality, lowres, low resolution, cropped, out of frame, sketch, poorly drawn, bad anatomy, wrong anatomy, extra limb, extra limbs, multiple arms, extra arms, missing limb, floating limbs, mutated hands and fingers, disconnected limbs, mutation, mutated, ugly, disgusting, blurry, amputation, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry, poorly drawn hands, poorly drawn limbs, bad anatomy, deformed, amateur drawing, odd"

cfg_scale: int = 8

steps: int = 32

upscale: bool = True

aspect_ratio: str = "portrait"

sampler: str = "Heun"

### SERVICE RELATED CONFIG

coomer_home_title: str = "Coomer"

### API URLS

base_coomer: str = "https://coomer.party"
models_url: str = f"{base_coomer}/api/creators"
icon_base_url: str = f"{base_coomer}/icons/{service}"
banner_base_url: str = f"{base_coomer}/banners/{service}"
user_base_url: str = f"{base_coomer}/{service}/user"

prodia_url: str = "https://api.prodia.com/v1/job"
