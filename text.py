from constantes import TEXT_ELEMENTS_TO_REMOVE, PATHS, FULL_NAMES

def format_name(name):
    return '-'.join(word.title() for word in name.split('-'))

def sanitize_text(text):
    sanitized_text = text
    if len(sanitized_text) == 0:
        return sanitized_text
    
    # Replace the first occurrence of "" with \\og{}
    sanitized_text = sanitized_text.replace('""', '\\og{} ', 1)
    # Replace the remaining occurrences of "" with \\fg
    sanitized_text = sanitized_text.replace('""', '\\fg{} ')
    # Guillemets
    sanitized_text = sanitized_text.replace("«", "\\og{} ")
    sanitized_text = sanitized_text.replace("❝", "\\og{} ")
    sanitized_text = sanitized_text.replace("“", "\\og{} ")
    sanitized_text = sanitized_text.replace("»", "\\fg{} ")
    sanitized_text = sanitized_text.replace("”", "\\fg{} ")
    sanitized_text = sanitized_text.replace("❞", "\\fg{} ")
    sanitized_text = sanitized_text.replace('""', "\\fg{} ")

    sanitized_text = sanitized_text.replace("&", "\\&")
    sanitized_text = sanitized_text.replace("%", "\\%")
    sanitized_text = sanitized_text.replace("#", "\\#")
    sanitized_text = sanitized_text.replace("œ", "\\oe ")
    sanitized_text = sanitized_text.replace("_", "\\_")
    sanitized_text = sanitized_text.replace("’", "'")
    #sanitized_text = sanitized_text.replace("  ", " ")
    sanitized_text = sanitized_text.replace("…", "...")
    sanitized_text = sanitized_text.replace(" ", " ")

    if sanitized_text[0]=='"':
        sanitized_text = '\\og{} ' + sanitized_text[1:]
        sanitized_text = sanitized_text.replace('"', '\\fg{} ')

    # Remove unsupported characters
    allowed_characters = set("@ ¡áí{}%#\/<> abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_()+.,:;!'?éèàùâêîôûäëïöüÿçÉÈÀÙÂÊÎÔÛÄËÏÖÜŸÇ~`^&= ")
    sanitized_text = "".join(c for c in sanitized_text if c in allowed_characters)

    # Cas particuliers
    for element_to_remove in TEXT_ELEMENTS_TO_REMOVE:
        sanitized_text = sanitized_text.replace(element_to_remove, '')

    if sanitized_text != text:
        with open(PATHS['citation_cleaning_check_table'], 'a') as file:
            file.write(f'"{text}";"{sanitized_text}"\n')
    return sanitized_text

def sanitize_mention(mention_from_excel):
    if len(mention_from_excel) == 0:
        return ""
    mention_from_excel = mention_from_excel.replace('Msc', 'MSc')
    mention_from_excel = mention_from_excel.replace('MSc IA', 'MSc AI')
    matches = []
    for mention in FULL_NAMES.keys():
        if mention in mention_from_excel:
            matches.append(mention)
    if len(matches) == 0:
        raise Exception(f"Pas de correspondance pour la mention '{mention_from_excel}'.")
    return max(matches, key=len)

