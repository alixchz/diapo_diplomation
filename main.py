import os
from datetime import datetime
import pytz

from student_data import read_framaforms_tsv, read_students_list, ajout_personnalisation
from photos import rogner_photo, telecharger_photos
from constantes import FULL_NAMES, PATHS, MENTIONS_OF_DOMINANTES

class Session():
    def __init__(self, location, timeslot_nb, time_start, dominantes):
        self.location = location
        self.timeslot_nb = timeslot_nb
        self.time_start = time_start
        self.dominantes = {}
        for nom_dominante in dominantes:
            self.dominantes[nom_dominante] = MENTIONS_OF_DOMINANTES[nom_dominante]

SESSIONS = [
    Session('Test', 9, '14h00', ['SCOC', 'VSE']),
    Session('Michelin', 1, '14h00', ['MDS', 'PNT']), 
    Session('EDF'     , 1, '14h15', ['IN', 'SCOC']), 
    Session('Michelin', 2, '16h00', ['EN', 'VSE']), 
    Session('EDF',      2, '16h15', ['GSI', 'CVT'])
    ]

# Récupération de la liste de tous les élèves présents
students_all = read_students_list(PATHS['excel_presents'])

# Récupération des données liées à la personnalisation
students_personalized = read_framaforms_tsv(PATHS['csv_personnalisation'])
print(f"\nNombre d'étudiants ayant personnalisé leur slide : {len(students_personalized)}\n")

_ = rogner_photo(PATHS['default_photo'])
telecharger_photos(students_personalized)

# Ajout des données de personnalisation quand elles existent
ajout_personnalisation(students_all, students_personalized)

# Grouper les étudiants par mention
students_by_mention = {}
for student in students_all:
    mention = student.mention
    if mention not in students_by_mention:
        students_by_mention[mention] = []
    students_by_mention[mention].append(student)

# Trier par ordre alphabétique les étudiants au sein de chaque mention
for mention in students_by_mention:
    students_by_mention[mention].sort(key=lambda student: student.nom)


# Comptage du nombre d'étudiants par mention
total = 0
print("\nRépartition des étudiants par mention :")
for mention in students_by_mention:
    print(f"{mention} : {len(students_by_mention[mention])} étudiants")
    total += len(students_by_mention[mention])
print(f"\nTotal : {total} étudiants\n")


# Comptage du nombre d'étudiants par session
for session in SESSIONS:
    total = 0
    for dominante in session.dominantes.keys():
        for mention in session.dominantes[dominante]:
            if mention in students_by_mention:
                total += len(students_by_mention[mention])
    print(f"Session {session.timeslot_nb} - {session.location} - {session.time_start} : {total} étudiants")

def generate_beamer(session):
    # Écrire le contenu des étudiants dans le fichier contenu_beamer.tex
    beamer_content_filename = f"contenu_beamer_session{session.timeslot_nb}_{session.location}.tex"
    timestamp = datetime.now(pytz.timezone("Europe/Paris")).strftime("%Y_%m_%d_%Hh%M_%S")
    if os.path.isfile(beamer_content_filename):
        os.rename(beamer_content_filename, f"archives_contenu_beamer/contenu_beamer_session{session.timeslot_nb}_{session.location}_{timestamp}.tex")

    with open(beamer_content_filename, "w") as f:
        for dominante in session.dominantes.keys():
            f.write("\\begin{section}{Dominante " + dominante + " - " + FULL_NAMES[dominante] + "}\n\n")
            for mention in session.dominantes[dominante]:
                if mention not in students_by_mention:
                    print(f"La mention {mention} n'a pas d'étudiant.")
                    continue
                f.write("\\begin{subsection}{Mention " + mention + " - " + FULL_NAMES[mention] + "}\n\n")
                for student in students_by_mention[mention]:
                    f.write("\\begin{frame}{" + student.prenom + " \\textsc{" + student.nom + "}}{Mention " + student.mention + "}\n")

                    if len(student.photo_path) > 0:
                        f.write("\\begin{figure}\n")
                        f.write("    \\includegraphics[height=0.5\\textheight]{" + student.photo_path + "}\n")
                        f.write("\\end{figure}\n")
                    if len(student.citation) > 0:
                        f.write("\\footnotesize{\\begin{center}\n \\textit{" + student.citation + "}\n\\end{center}}\n")
                    f.write("\\end{frame}\n\n")
                f.write("\\end{subsection}\n")
            f.write("\\end{section}\n")

for session in SESSIONS:
    generate_beamer(session)
print('\nBeamers générés avec succès !')
print('\nPensez à bien vérifier les tables liées aux corrections d`erreurs de remplissage (dossier checks)\n')