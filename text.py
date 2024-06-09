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

    sanitized_text = sanitized_text.replace("&", "\\&")
    sanitized_text = sanitized_text.replace("%", "\\%")
    sanitized_text = sanitized_text.replace("#", "\\#")
    sanitized_text = sanitized_text.replace("œ", "\\oe ")
    sanitized_text = sanitized_text.replace("_", "\\_")
    sanitized_text = sanitized_text.replace("«", "\\og{} ")
    sanitized_text = sanitized_text.replace("“", "\\og{} ")
    sanitized_text = sanitized_text.replace("»", "\\fg{} ")
    sanitized_text = sanitized_text.replace("”", "\\fg{} ")
    sanitized_text = sanitized_text.replace('""', "\\fg{} ")
    sanitized_text = sanitized_text.replace("’", "'")
    sanitized_text = sanitized_text.replace("  ", " ")
    if sanitized_text[0]=='"':
        sanitized_text = '\\og{} ' + sanitized_text[1:]
        sanitized_text = sanitized_text.replace('"', '\\fg{} ')
    # Remove strange characters
    allowed_characters = set("@¡áí{}\<> abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_()+.,:;!'?éèàùâêîôûäëïöüÿçÉÈÀÙÂÊÎÔÛÄËÏÖÜŸÇ~`^&= ")
    sanitized_text = "".join(c for c in sanitized_text if c in allowed_characters)

    # Cas particuliers
    sanitized_text = sanitized_text.replace('(  .  )', '')

    if sanitized_text != text:
        with open('checks/check_citation_cleaning.csv', 'a') as file:
            file.write(f'"{text}";"{sanitized_text}"\n')
        #print(f"Texte nettoyé : {text} -> {sanitized_text}")
    return sanitized_text