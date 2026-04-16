from PIL import Image
import os
import base64
from io import BytesIO

img_path = 'static/img/map2002.jpg'
webp_path = 'static/img/map2002.webp'
placeholder_path = 'static/img/map2002_tiny.jpg'

if os.path.exists(img_path):
    with Image.open(img_path) as img:
        # 1. Create high-quality WebP (usually 50-70% smaller than JPG)
        img.save(webp_path, 'WEBP', quality=75, method=6)
        print(f"Created WebP: {os.path.getsize(webp_path) / 1024 / 1024:.2f} MB")
        
        # 2. Create a truly tiny placeholder for Base64 inlining
        placeholder = img.copy()
        placeholder.thumbnail((100, 100))
        buffered = BytesIO()
        placeholder.save(buffered, format="JPEG", quality=20)
        img_str = base64.b64encode(buffered.getvalue()).decode()
        print(f"BASE64_START:{img_str}:BASE64_END")

