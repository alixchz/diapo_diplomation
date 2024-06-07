from text import format_name, sanitize_text
import pandas as pd
from mentions import FULL_NAMES

def sanitize_mention(mention_from_excel):
    if len(mention_from_excel) == 0:
        return ""
    matches = []
    for mention in FULL_NAMES.keys():
        if mention in mention_from_excel:
            matches.append(mention)
    if len(matches) == 0:
        print(matches)
        raise Exception(f"Pas de correspondance pour la mention '{mention_from_excel}'.")
    return max(matches, key=len)

class Student:
    def __init__(self, prenom, nom, etunum, mention="", email="", citation="", photo_url=""):
        self.prenom = format_name(prenom)
        self.nom = format_name(nom)
        self.etunum = etunum.replace(' ', '')
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
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.etunum})"

# Fonction pour lire le fichier TSV et récupérer les données des étudiants
def read_framaforms_tsv(nom_fichier):
    students = []
    with open(nom_fichier, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        # Ignorer les deux premières lignes qui ne contiennent pas de données d'étudiant
        for line in lines[3:]:
            data = line.strip().split('\t')
            prenom = data[9].strip('"')
            nom = data[10].strip('"')
            etunum = data[11].strip('"')
            citation = data[13][1:-1]
            photo_url = data[14].strip('"')
            student = Student(prenom, nom, etunum, citation=citation, photo_url=photo_url)
            students.append(student)
    return students

def handle_mention_exceptions(mention_autre):
    exceptions = {
        'SCOM': ['Génie Industriel'],
        'MSc ITM': ['IMT', 'ITM', 'Industry Transformation', 'Industry Transfomation'],
        'CYBER': ['Infosec'],
        'IA': ['AI', 'IA', 'Artificial Intelligence', 'Intelligence Artificielle'],
        'ELEN': ['ELEN'],
        'MACS': ['MACS'],
        'PSY': ['DD'] # ATTTNTION fort risque que ce ne soit pas robuste, fonctionne uniquement car 1 seul élève avait mis "DD" comme mention autre
    }
    for mention, keywords in exceptions.items():
        for keyword in keywords:
            if keyword in mention_autre:
                print(f'Mention "autre" : "{mention_autre}" -> "{mention}"')
                return mention
    raise Exception(f"Exception non gérée : '{mention_autre}'")

def read_students_list(nom_fichier):
    students = []
    df = pd.read_excel(nom_fichier)
    for _, row in df.iterrows():
        etunum = str(row['etunum'])
        nom = row['Last name']
        prenom = row['First name']
        email = row['Email']
        mention = row['mention_choix']
        if mention == 'Autre':
            mention_autre = row['mention_autre']
            mention = handle_mention_exceptions(mention_autre)
        student = Student(prenom, nom, etunum, mention, email)
        students.append(student)
    return students
