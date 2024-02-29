import os
import requests
from tqdm import tqdm
import yaml

csv_filename = 'test.tsv'

class Student:
    def __init__(self, prenom, nom, mention, citation, photo_url, photo_path = ""):
        self.prenom = prenom
        self.nom = nom
        self.mention = mention
        self.citation = citation
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
            mention = data[11].strip('"')
            citation = data[-1].strip('"')
            photo_url = data[-3].strip('"')
            student = Student(prenom, nom, mention, citation, photo_url)
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

def telecharger_photos(students):
    if not os.path.exists("photos"):
        os.makedirs("photos")
    session = requests.session()
    # Envoyer la requête POST pour se connecter
    response = session.post('https://framaforms.org/user', data=data)
    if response.status_code == 200:
        print("Connexion à Framaforms réussie !\nTéléchargement des photos...")
        for student in tqdm(students):
            photo_name = f"{student.prenom}_{student.nom}.jpg"
            photo_path = os.path.join("photos", photo_name)
            student.photo_path = photo_path
            if os.path.isfile(photo_path):
                continue
            else:
                photo_url = student.photo_url
                response = session.get(photo_url, stream=True)
                if response.status_code == 200:
                    with open(photo_path, 'wb') as photo_file:
                        photo_file.write(response.content)
                else:
                    print(f"Impossible de télécharger la photo de {student.prenom} {student.nom}.")

    else:
        print("Échec de la connexion.")

telecharger_photos(students)

# Fonction pour écrire le contenu des étudiants dans le fichier contenu_beamer.tex
def ecrire_contenu_beamer(students):
    with open("contenu_beamer.tex", "w") as f:
        for student in students:
            f.write("\\begin{frame}{" + student.prenom + " \\textsc{" + student.nom + "}}\n")
            f.write("\\begin{figure}\n")
            f.write("    \\includegraphics[height=0.4\\textheight]{../" + student.photo_path + "}\n")
            f.write("\\end{figure}\n")
            f.write("\\textit{\\og{}" + student.citation + "\\fg}\n")
            f.write("\\end{frame}\n\n")

# Appeler la fonction pour écrire le contenu dans le fichier
ecrire_contenu_beamer(students)

print('\nBeamer généré avec succès !\n')