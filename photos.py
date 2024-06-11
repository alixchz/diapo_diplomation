import os
import yaml
import requests
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageOps

from constantes import PATHS, IMAGE_SIZE

credentials = yaml.safe_load(open(PATHS['framaforms_credentials']))
data = {
    'name': credentials["username"],
    'pass': credentials["password"],
    'form_build_id': 'form-URbK4Py_-m4VfzceQLTp9L8vqQwrDg1F8ia_V54DZe0',
    'form_id': 'user_login',
    'op': 'Se connecter'
}

def rogner_photo(photo_path):
    desired_size = IMAGE_SIZE
    photo_name = os.path.basename(photo_path).replace('jpg', 'png')
    cropped_photo_path = os.path.join(PATHS['photos_folder_cropped'], photo_name)

    # Ne pas recrop si la photo croppée existe déjà et est de la bonne taille
    if os.path.isfile(cropped_photo_path):
        img = Image.open(cropped_photo_path)
        if img.size[0] == desired_size:
            return cropped_photo_path
        
    img = Image.open(photo_path)
    img = ImageOps.exif_transpose(img)
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

    img.save(cropped_photo_path)
    return cropped_photo_path


def telecharger_photos(students):
    session = requests.session()
    # Envoyer la requête POST pour se connecter
    response = session.post('https://framaforms.org/user', data=data)
    if response.status_code == 200:
        print("Connexion à Framaforms réussie !\nRécupération et rognage des photos...")
        for student in tqdm(students):
            photo_name = f"{student.prenom}_{student.nom}.jpg"
            photo_path = os.path.join(PATHS['photos_folder'], photo_name)
            if not os.path.isfile(photo_path):
                photo_url = student.photo_url
                if len(photo_url) == 0:
                    student.photo_path = PATHS['default_photo_cropped']
                    continue
                response = session.get(photo_url, stream=True)
                if response.status_code == 200:
                    with open(photo_path, 'wb') as photo_file:
                        photo_file.write(response.content)
                else:
                    print(f"Impossible de télécharger la photo de {student.prenom} {student.nom}.")
            student.photo_path = rogner_photo(photo_path)
    else:
        print("Échec de la connexion.")