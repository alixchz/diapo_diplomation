import os
from datetime import datetime
import pytz

from get_data_from_csv import read_framaforms_tsv, read_students_list
from photos import rogner_photo, telecharger_photos
from mentions import MENTIONS_OF_DOMINANTES, FULL_NAMES

IMAGE_SIZE = 250 # temporaire pour avoir pdf plus léger

# Chemins vers les données
csv_framaforms_path = 'data/personnalisation_de_ton_passage_sur_scene.tsv'
excel_presents = 'data/guests_and_checkins_rdd_cs_2024_31.xlsx'

root_path = os.path.dirname(os.path.abspath(__file__))
# Dossiers locaux de stockage des photos (à créer si besoin)
photos_folder = os.path.join(root_path, 'data/photos')
photos_folder_cropped = os.path.join(root_path, 'data/photos_cropped')
if not os.path.isdir('checks'):
    os.mkdir('checks')

class Session():
    def __init__(self, location, timeslot_nb, time_start, dominantes):
        self.location = location
        self.timeslot_nb = timeslot_nb
        self.time_start = time_start
        self.dominantes = {}
        for nom_dominante in dominantes:
            self.dominantes[nom_dominante] = MENTIONS_OF_DOMINANTES[nom_dominante]

# Répartition dans les sessions
sessions = [
    Session('Michelin', 1, '14h00', ['MDS', 'PNT']), 
    Session('EDF'     , 1, '14h15', ['IN', 'SCOC']), 
    Session('Michelin', 2, '16h00', ['EN', 'VSE']), 
    Session('EDF',      2, '16h15', ['GSI', 'CVT'])
    ]

# Récupération de la liste de tous les élèves présents
students_all = read_students_list(excel_presents)

# Récupération des données liées à la personnalisation
students_personalized = read_framaforms_tsv(csv_framaforms_path)
print(f"\nNombre d'étudiants ayant personnalisé leur slide : {len(students_personalized)}\n")
default_photo_path = rogner_photo('data/photos/default.jpg', photos_folder_cropped=os.path.join(os.path.dirname(photos_folder), "photos_cropped"), desired_size=IMAGE_SIZE)
telecharger_photos(students_personalized, default_photo_path, photos_folder, desired_size=IMAGE_SIZE, )

for student in students_all:
    student.photo_path = default_photo_path
    for i, student_personalized in enumerate(students_personalized):
        if student.etunum == student_personalized.etunum:
            student.add_personnalization(student_personalized)
            students_personalized.pop(i)
            break
print(f"\n{len(students_personalized)} réponses du framaforms n'ont pas de match par etunum. Tentative par le nom et prénom...")
to_remove = []
for i, unmatched_personnalization in enumerate(students_personalized):
    for student in students_all:
        if unmatched_personnalization.nom == student.nom:
            if unmatched_personnalization.prenom[0:3] == student.prenom[0:3]:
                student.add_personnalization(unmatched_personnalization)
                to_remove.append(i)
students_personalized = [s for i, s in enumerate(students_personalized) if i not in to_remove]
if len(students_personalized) > 0:
    raise Exception(f"Les étudiants suivants n'ont pas été trouvés : { [[s.nom, s.prenom, s.etunum] for s in students_personalized]}")
else:
    print("Tous les étudiants ayant répondu au framaforms ont été trouvés.\n")

students_by_mention = {}
for student in students_all:
    mention = student.mention
    if mention not in students_by_mention:
        students_by_mention[mention] = []
    students_by_mention[mention].append(student)

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
for session in sessions:
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
            f.write("\\begin{section}{Dominante " + dominante + " - " + FULL_NAMES[dominante] + "}")
            for mention in session.dominantes[dominante]:
                f.write("\\begin{subsection}{Mention " + mention + " - " + FULL_NAMES[mention] + "}")
                if mention not in students_by_mention:
                    print(f"La mention {mention} n'a pas d'étudiant.")
                    continue
                for student in students_by_mention[mention]:
                    f.write("\\begin{frame}{" + student.prenom + " \\textsc{" + student.nom + "}}{Mention " + student.mention + "}\n")

                    if len(student.photo_path) > 0:
                        f.write("\\begin{figure}\n")
                        f.write("    \\includegraphics[height=0.4\\textheight]{" + student.photo_path + "}\n")
                        f.write("\\end{figure}\n")
                    if len(student.citation) > 0:
                        f.write("\\begin{center}\n \\textit{" + student.citation + "}\n\\end{center}\n")
                    f.write("\\end{frame}\n\n")
                f.write("\\end{subsection}\n")
            f.write("\\end{section}\n")

for session in sessions:
    generate_beamer(session)
print('\nBeamers générés avec succès !\n')