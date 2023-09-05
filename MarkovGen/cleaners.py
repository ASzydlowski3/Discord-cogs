import re

# Function to remove links from a text file
async def links_remover(path):
    try:
        with open(path, 'r', encoding='utf-8') as input_file:
            text = input_file.read()
        
        pattern = r'\bhttps?://\S+\b'
        
        text_without_links = re.sub(pattern, '', text)
        
        with open(path, 'w', encoding='utf-8') as output_file:
            output_file.write(text_without_links)
    except:
        return

# Function to replace Polish characters with their English equivalents
async def polish_remover(path):
    polish_to_english = {
        'ą': 'a',
        'ć': 'c',
        'ę': 'e',
        'ł': 'l',
        'ń': 'n',
        'ó': 'o',
        'ś': 's',
        'ź': 'z',
        'ż': 'z',
        'Ą': 'A',
        'Ć': 'C',
        'Ę': 'E',
        'Ł': 'L',
        'Ń': 'N',
        'Ó': 'O',
        'Ś': 'S',
        'Ź': 'Z',
        'Ż': 'Z'
    }

    def replace_polish_with_english(text):
        for polish_letter, english_substitute in polish_to_english.items():
            text = text.replace(polish_letter, english_substitute)
        return text

    try:
        with open(path, 'r', encoding='utf-8') as input_file:
            input_text = input_file.read()
        
        modified_text = replace_polish_with_english(input_text)
        
        with open(path, 'w', encoding='utf-8') as output_file:
            output_file.write(modified_text)
    except:
        return

# Function to remove emojis from a text file
async def emoji_remover(path):
    try:
        with open(path, 'r', encoding='utf-8') as input_file:
            text = input_file.read()
        
        pattern = r'<[^>]+>'
        
        text_without_emojis = re.sub(pattern, '', text)
        
        with open(path, 'w', encoding='utf-8') as output_file:
            output_file.write(text_without_emojis)
    except:
        return
