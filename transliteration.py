from aiopath import AsyncPath
from re import sub


CYRILLIC_SYMBOLS = (
    "а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с", "т", "у",
    "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я", "є", "і", "ї", "ґ")
LATIN_ALTERNATIVE = (
    "a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
    "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "ya", "je", "i", "ji", "g")

TRANSLITERATION = {}

for cyrillic, latin in zip(CYRILLIC_SYMBOLS, LATIN_ALTERNATIVE):
    """
    Populates the transliteration mapping with "cyrillic": "latin" pairs for uppercase and lowercase letters.
    """
    TRANSLITERATION[ord(cyrillic)] = latin
    TRANSLITERATION[ord(cyrillic.upper())] = latin.capitalize()


def normalize_name(filename: str) -> str:
    """
    Normalizes the filename by replacing cyrillic symbols with latin alternatives, and unrecognized symbols with
    underscores.
    :return: normalized filename with extension
    """
    path = AsyncPath(filename)
    new_name = path.stem
    new_name = new_name.translate(TRANSLITERATION)

    new_name = sub(r"\W", "_", new_name)
    return new_name + path.suffix