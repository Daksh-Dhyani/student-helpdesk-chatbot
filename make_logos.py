from PIL import Image

src = Image.open("assets/logo_original.png").convert("RGB")

# Full poster, smaller file
full = src.resize((1000, round(1000 * src.height / src.width)), Image.LANCZOS)
full.save("assets/logo_full.png", optimize=True)

# Star icon for the browser tab
star = src.crop((514, 131, 1024, 641)).resize((256, 256), Image.LANCZOS)
star.save("assets/icon.png", optimize=True)

# Wordmark for the sidebar
word = src.crop((300, 635, 1240, 765))
word = word.resize((600, round(600 * word.height / word.width)), Image.LANCZOS)
word.save("assets/logo.png", optimize=True)

print("done")