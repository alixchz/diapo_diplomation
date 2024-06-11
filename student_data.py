import pandas as pd
from unidecode import unidecode

from constantes import PATHS, MENTIONS_OTHER_EXCEPTIONS
from text import format_name, sanitize_text, sanitize_mention

def convert_to_int(obj):
    try:
        return int(obj)
    except ValueError:
        #print(obj)
        return 0

class Student:
    def __init__(self, prenom, nom, etunum, mention="", email="", citation="", photo_url=""):
        self.prenom = format_name(prenom)
        self.nom = format_name(nom)
        self.etunum = convert_to_int(etunum) #.replace(' ', '')
        self.email = email
        self.mention = sanitize_mention(mention)
        # Personnalisation de la citation et de la photo
        self.citation = sanitize_text(citation)
        self.photo_url = photo_url
        self.photo_path = ""

    def add_personnalization(self, student_personalized):
        self.citation = student_personalized.citation
        self.photo_url = student_personalized.photo_url
        self.photo_path = student_personalized.photo_path
        self.prenom = student_personalized.prenom
        self.nom = student_personalized.nom
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.etunum})"

def clean_doublons(nom_fichier):
    with open(nom_fichier, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        etunums = []
        noms = []
        prenoms = []
        doublons_idx = []
        for i, line in enumerate(lines[3:]):
            data = line.strip().split('\t')
            prenom = unidecode(data[9].strip('"'))
            nom = unidecode(data[10].strip('"'))
            etunum = unidecode(data[11].strip('"'))
            if etunum in etunums:
                doublons_idx.append(i)
                print(etunum)
            elif nom in noms:
                if prenoms[noms.index(nom)] == prenom :
                    print(nom, prenom)
                    doublons_idx.append(i)
            etunums.append(etunum)
            noms.append(nom)
            prenoms.append(prenom)

# Fonction pour lire le fichier TSV et récupérer les données des étudiants
def read_framaforms_tsv(nom_fichier):
    with open(PATHS['citation_cleaning_check_table'], 'w') as file:
        file.write(f"original_citation;cleaned_citation\n")

    students = []
    etunums = []
    prenoms_noms = []
    students_doubles_to_remove_idx = [] # Liste des index des éléments de la liste "students" à supprimer en cas de doublon (seule la dernière soumission au FramaForms compte)
    with open(nom_fichier, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        # Ignorer les deux premières lignes qui ne contiennent pas de données d'étudiant
        for i, line in enumerate(lines[3:]):
            data = line.strip().split('\t')
            prenom = data[9].strip('"')
            nom = data[10].strip('"')
            etunum = data[11].strip('"')
            citation = data[13][1:-1]
            photo_url = data[14].strip('"')
            prenom_nom = f"{unidecode(prenom).lower()}_{unidecode(nom).lower()}"

            if etunum in etunums:
                print('Doublon :', prenom, nom, etunum)
                students_doubles_to_remove_idx.append(max(loc for loc, val in enumerate(etunums) if val ==etunum))
            elif prenom_nom in prenoms_noms:
                print('Doublon :', prenom, nom, etunum)
                students_doubles_to_remove_idx.append(max(loc for loc, val in enumerate(prenoms_noms) if val == prenom_nom))

            student = Student(prenom, nom, etunum, citation=citation, photo_url=photo_url)
            students.append(student)
            etunums.append(etunum)
            prenoms_noms.append(prenom_nom)
    students = [s for i, s in enumerate(students) if i not in students_doubles_to_remove_idx]
    return students

def handle_mention_exceptions(mention_autre):
    for mention, keywords in MENTIONS_OTHER_EXCEPTIONS.items():
        for keyword in keywords:
            if keyword in mention_autre:
                return mention
    raise Exception(f"Exception non gérée : '{mention_autre}'")

def read_students_list(nom_fichier):
    with open(PATHS['mentions_other_check_table'], 'w') as file:
        file.write(f"etunum;prenom;nom;mention_autre;mention\n")
    students = []
    df = pd.read_excel(nom_fichier)
    for _, row in df.iterrows():
        etunum = convert_to_int(row['etunum'])
        nom = row['Last name']
        prenom = row['First name']
        email = row['Email']
        mention = row['mention_choix']
        if mention == 'Autre':
            mention_autre = row['mention_autre']
            mention = handle_mention_exceptions(mention_autre)
            with open(PATHS['mentions_other_check_table'], 'a') as file:
                file.write(f"{etunum};{prenom};{nom};{mention_autre};{mention}\n")
        student = Student(prenom, nom, etunum, mention, email)
        students.append(student)
    return students

def ajout_personnalisation(students_all, students_personalized):
    for student in students_all:
        student.photo_path = PATHS['default_photo_cropped']
        for i, student_personalized in enumerate(students_personalized):
            if student.etunum == student_personalized.etunum:
                student.add_personnalization(student_personalized)
                students_personalized.pop(i)
                break
    print(f"\n{len(students_personalized)} réponses au framaforms de personnalisation n'ont pas de match par etunum. Tentative par le nom et prénom...")
    to_remove = []
    for i, unmatched_personnalization in enumerate(students_personalized):
        for student in students_all:
            if unidecode(unmatched_personnalization.nom) == unidecode(student.nom):
                if unidecode(unmatched_personnalization.prenom[0:3]) == unidecode(student.prenom[0:3]):
                    student.add_personnalization(unmatched_personnalization)
                    to_remove.append(i)
    students_personalized = [s for i, s in enumerate(students_personalized) if i not in to_remove]
    if len(students_personalized) > 0:
        raise Exception(f"Les étudiants suivants n'ont pas été trouvés : { [[s.nom, s.prenom, s.etunum] for s in students_personalized]}")
    else:
        print("Tous les étudiants ayant répondu au framaforms ont été trouvés.\n")
        return students_all