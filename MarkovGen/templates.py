from PIL import Image, ImageDraw, ImageFont
import aiohttp
import demapi

# Function to add a newline every n characters in a text
def add_newline_every_n_characters(input_text, n):
    lines = []
    current_line = []
    current_line_length = 0

    for word in input_text.split():
        if current_line_length + len(word) <= n:
            current_line.append(word)
            current_line_length += len(word) + 1
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
            current_line_length = len(word)

    if current_line:
        lines.append(' '.join(current_line))
    return '\n'.join(lines)

# Function to generate a demotivation meme
async def gen_demot(templates_path, url, *sentences):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                image_data = await response.read()
                with open(f"{templates_path}demot.jpg", 'wb') as file:
                    file.write(image_data)

    conf = demapi.Configure(
        base_photo=f"{templates_path}demot.jpg",
        title=sentences[0],
        explanation=sentences[1]
    )
    image = await conf.coroutine_download()
    image.save(f"{templates_path}demot_meme.png")

# Function to generate a "Paulo Coelho" meme
async def gen_paulo(templates_path, sentence):
    image_path = f"{templates_path}paulo.png"
    image = Image.open(image_path)
    image = image.convert('RGB')
    draw = ImageDraw.Draw(image)
    text = add_newline_every_n_characters(sentence, 30)
    font_size = 25
    font_color = (255, 255, 255)
    font_path = f"{templates_path}Roboto.ttf"
    font = ImageFont.truetype(font_path, font_size)
    draw.text((230, 80), text, font=font, fill=font_color)
    output_path = f"{templates_path}paulo_meme.jpg"
    image.save(output_path)
    image.close()

# Function to generate a "Gru" meme
async def gen_gru(templates_path, sentence):
    image_path = f"{templates_path}gru.jpg"
    image = Image.open(image_path)
    image = image.convert('RGB')
    draw = ImageDraw.Draw(image)
    font_size = 20
    font_color = (0, 0, 0)
    font_path = f"{templates_path}Aller_Bd.ttf"
    text = add_newline_every_n_characters(sentence, 11)
    font = ImageFont.truetype(font_path, font_size)
    draw.text((200, 50), text, font=font, fill=font_color)
    draw.text((200, 270), text, font=font, fill=font_color)
    output_path = f"{templates_path}gru_meme.jpg"
    image.save(output_path)
    image.close()

# Function to generate a comic-style meme
async def gen_komix(templates_path, *sentences):
    image_path = f"{templates_path}komix.png"
    image = Image.open(image_path)
    image = image.convert('RGB')
    draw = ImageDraw.Draw(image)
    font_size = 18
    font_color = (0, 0, 0)
    font_path = f"{templates_path}Aller_Bd.ttf"
    font = ImageFont.truetype(font_path, font_size)
    draw.text((10, 0), str(sentences[0]), font=font, fill=font_color)
    draw.text((260, 0), str(sentences[1]), font=font, fill=font_color)
    draw.text((10, 190), str(sentences[2]), font=font, fill=font_color)
    draw.text((260, 190), str(sentences[3]), font=font, fill=font_color)
    output_path = f"{templates_path}komix_meme.jpg"
    image.save(output_path)
    image.close()