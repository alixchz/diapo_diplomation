import os
import requests
from tqdm import tqdm
import yaml
from PIL import Image, ImageDraw
from datetime import datetime
import pytz

IMAGE_SIZE = 200 # temporaire pour avoir pdf plus léger
csv_filename = 'personnalisation_de_ton_passage_sur_scene.tsv'
photos_folder = 'photos'
photos_folder_cropped = 'photos_cropped'

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
    allowed_characters = set("¡áí{}\<> abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_()+.,:;!'?éèàùâêîôûäëïöüÿçÉÈÀÙÂÊÎÔÛÄËÏÖÜŸÇ~`^&= ")
    sanitized_text = "".join(c for c in sanitized_text if c in allowed_characters)
    if sanitized_text != text:
        print(f"Texte nettoyé : {text} -> {sanitized_text}")
    return sanitized_text

class Student:
    def __init__(self, prenom, nom, etunum, mention, citation, photo_url, photo_path = ""):
        self.prenom = format_name(prenom)
        self.nom = format_name(nom)
        self.etunum = etunum
        self.mention = sanitize_text(mention)
        self.citation = sanitize_text(citation)
        self.photo_url = photo_url
        self.photo_path = photo_path


# Fonction pour lire le fichier TSV et récupérer les données des étudiants
def lire_fichier_tsv(nom_fichier):
    students = []
    with open(nom_fichier, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        # Ignorer les deux premières lignes qui ne contiennent pas de données d'étudiant
        for line in lines[3:]:
            data = line.strip().split('\t')
            prenom = data[9].strip('"')
            nom = data[10].strip('"')
            etunum = data[11].strip('"')
            mention = data[12].strip('"')
            citation = data[13][1:-1]
            photo_url = data[14].strip('"')
            student = Student(prenom, nom, etunum, mention, citation, photo_url)
            students.append(student)
    return students

# Lecture du fichier TSV et récupération des données des étudiants
students = lire_fichier_tsv(csv_filename)

print(f"Nombre d'étudiants : {len(students)}\n")

credentials = yaml.safe_load(open('credentials.yml'))
data = {
    'name': credentials["username"],
    'pass': credentials["password"],
    'form_build_id': 'form-URbK4Py_-m4VfzceQLTp9L8vqQwrDg1F8ia_V54DZe0',
    'form_id': 'user_login',
    'op': 'Se connecter'
}

def rogner_photo(photo_path):
    desired_size = IMAGE_SIZE
    img = Image.open(photo_path)
    img=img.convert('RGBA')
    # On veut faire une image carrée de hauteur 1000px -> on
    # prend la plus petit dimension de l'image et on la ramène à 1000px
    # 1er cas : la largeur est plus grande que la hauteur : on ramène la hauteur à
    # la hauteur désirée et on ajuste la largeur
    if img.size[0] >= img.size[1]:
        ratio_old_to_new = desired_size / img.size[1]
        img = img.resize((int(ratio_old_to_new * img.size[0]), desired_size))
        # Coordonnées de l'ellipse
        # Point en haut à gauche
        x_0, y_0 = int(img.size[0] / 2 - desired_size / 2), 0
        # Point en bas à droite de l'ellipse
        x_1, y_1 = int(desired_size / 2 + img.size[0] / 2), desired_size

    # Sinon on ramène la largeur à 1000 et on ajuste la hauteur
    else:
        ratio_old_to_new = desired_size / img.size[0]
        img = img.resize((desired_size, int(ratio_old_to_new * img.size[1])))
        # Coordonnées de l'ellipse
        # Point en haut à gauche
        x_0, y_0 = 0, int(img.size[1] / 2 - desired_size / 2)
        # Point en bas à droite de l'ellipse
        x_1, y_1 = desired_size, int(desired_size / 2 + img.size[1] / 2)

    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((x_0, y_0, x_1, y_1), fill=255)

    # Apply the mask to the image
    img.putalpha(mask)

    # Suppress the image outside the mask
    img = img.crop(img.getbbox())
    new_width=img.size[0]
    new_width=new_width*3700
    new_height=img.size[1]
    new_height=new_height*3700

    photo_name = os.path.basename(photo_path).replace('jpg', 'png')
    cropped_photo_path = os.path.join(photos_folder_cropped, photo_name)
    img.save(cropped_photo_path)
    return cropped_photo_path

def telecharger_photos(students):
    if not os.path.exists(photos_folder):
        os.makedirs(photos_folder)
    session = requests.session()
    # Envoyer la requête POST pour se connecter
    response = session.post('https://framaforms.org/user', data=data)
    if response.status_code == 200:
        print("Connexion à Framaforms réussie !\nTéléchargement des photos...")
        for student in tqdm(students):
            photo_name = f"{student.prenom}_{student.nom}.jpg"
            photo_path = os.path.join(photos_folder, photo_name)
            if not os.path.isfile(photo_path):
                photo_url = student.photo_url
                if len(photo_url) == 0:
                    continue
                response = session.get(photo_url, stream=True)
                if response.status_code == 200:
                    with open(photo_path, 'wb') as photo_file:
                        photo_file.write(response.content)
                else:
                    print(f"Impossible de télécharger la photo de {student.prenom} {student.nom}.")
            cropped_photo_path = rogner_photo(photo_path)
            student.photo_path = cropped_photo_path
    else:
        print("Échec de la connexion.")

telecharger_photos(students)


# Fonction pour écrire le contenu des étudiants dans le fichier contenu_beamer.tex
def ecrire_contenu_beamer(students):
    timestamp = datetime.now(pytz.timezone("Europe/Paris")).strftime("%Y_%m_%d_%Hh%M_%S")
    with open(f"contenu_beamer_{timestamp}.tex", "w") as f:
        for student in students:
            f.write("\\begin{frame}{" + student.prenom + " \\textsc{" + student.nom + "}}{Mention " + student.mention + "}\n")

            if len(student.photo_path) > 0:
                f.write("\\begin{figure}\n")
                f.write("    \\includegraphics[height=0.4\\textheight]{../" + student.photo_path + "}\n")
                f.write("\\end{figure}\n")
            if len(student.citation) > 0:
                f.write("\\begin{center}\n \\textit{" + student.citation + "}\n\\end{center}\n")
            f.write("\\end{frame}\n\n")

# Appeler la fonction pour écrire le contenu dans le fichier
ecrire_contenu_beamer(students)

print('\nBeamer généré avec succès !\n')
