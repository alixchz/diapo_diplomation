import os
import random
# Seules les constantes (variables en majuscule) doivent être modifiées (sauf exception)

IMAGE_SIZE = 251 # temporaire pour avoir pdf plus léger
DEFAULT_PHOTO_FILENAME = 'default.jpg'

# ==============================================================================
# Gestion des cas particuliers liés au mauvais remplissage des forms
# ==============================================================================

MENTIONS_OTHER_EXCEPTIONS = {
        'SCOM': ['Génie Industriel'],
        'MSc ITM': ['IMT', 'ITM', 'Industry Transformation', 'Industry Transfomation'],
        'MSc AI': ['MSc AI'],
        'CYBER': ['Infosec'],
        'IA': ['AI', 'IA', 'Artificial Intelligence', 'Intelligence Artificielle'],
        'ELEN': ['ELEN'],
        'MACS': ['MACS'],
        'PSY': ['DD'] # ATTENTION fort risque que ce ne soit pas robuste, fonctionne uniquement car 1 seul élève avait mis "DD" comme mention autre
    }

TEXT_ELEMENTS_TO_REMOVE = [
    '(  .  )', # partially cleaned emoji with special characters
    ]

# ==============================================================================
# CHEMINS des dossiers et fichiers
# ==============================================================================

root_path = os.path.dirname(os.path.abspath(__file__))

folders = ['data', 'checks', 'data/photos', 'data/photos_cropped', 'data/photos_exceptions']
for folder in folders:
    if not os.path.isdir(folder):
        os.mkdir(folder)

PATHS = {
    # IMPORTANT à remplir : chemins vers les tableurs contenant les données des élèves
    'csv_personnalisation': 'data/personnalisation_de_ton_passage_sur_scene.tsv',
    'excel_presents': 'data/Liste diplômés présents RDD 19.06.2024.xlsx',

    # Autres chemins (normalement inutile de les modifier)
    'framaforms_credentials': 'credentials.yml', 
    'citation_cleaning_check_table': 'checks/check_citation_cleaning.csv',
    'mentions_other_check_table': 'checks/mentions_autres_affectation.csv',
    'etunums_mismatchs_check_table': 'checks/etunums_mismatchs.csv',
    'photos_folder': 'data/photos',
    'photos_folder_cropped': 'data/photos_cropped',
    'photos_exception_folder': 'data/photos_exceptions',
    'default_photo_cropped': 'data/photos_cropped/default.png',
}

# Transformer en chemins absolus pour éviter les soucis dans LaTeX ensuite
for path in ['photos_folder', 'photos_folder_cropped']:
    PATHS[path] = os.path.join(root_path, PATHS[path])
    if not os.path.isdir(PATHS[path]):
        os.mkdir(PATHS[path])

PATHS['default_photo'] = os.path.join(PATHS['photos_folder'], DEFAULT_PHOTO_FILENAME)
PATHS['default_photo_cropped'] = os.path.join(PATHS['photos_folder_cropped'], DEFAULT_PHOTO_FILENAME.replace('jpg', 'png'))

# ==============================================================================
# Noms complets des mentions & dominantes, associations dominantes - mentions
# ==============================================================================

FULL_NAMES = {
    'MMF': 'Modélisation mathématique et Mathématiques Financières',
    'SDI (PS)': "Sciences des Données et de l'Information (Paris-Saclay)",
    'SDI (M)': "Sciences des Données et de l'Information (Metz)",
    'MSc DSBA': 'Master in Data Sciences \\& Business Analytics',
    'QTE': 'Quantum Engineering',
    'PSY': 'Photonic and nanosystem engineering',
    'IA': 'Intelligence Artificielle',
    'SL': 'Sciences du Logiciel',
    'ASI': 'Architecture des Systèmes Informatiques',
    'CYBER': 'Cybersécurité',
    'MSc AI': 'Master in Artificial Intelligence',
    'SRI': 'Systèmes et Réseaux Intelligents',
    'MACS': 'Systèmes communicants mobiles et autonomes',
    'OCENE': 'Objets communicants et électronique numérique embarquée',
    'NUMVI': 'Numérique et Vivant',
    'ELEN': 'Electronic Engineering',
    'ICE': 'Information and Communication Engineering',
    'RE': 'Ressources Énergétiques',
    'E2': 'Efficacité Énergétique',
    'PEG': 'Power Energy Grids',
    'SES': 'Sustainable Energy Systems',
    'HSB': 'Healthcare et Services en Biomédical',
    'ESP': 'Environnement et Production Durable',
    'CE': 'Control Engineering',
    'DS': 'Design and System Sciences',
    'SCOM': 'Supply Chain \\& Operations Management',
    'MSc ITM': 'Master in Industry Transformation Management',
    'AET': 'Aéronautique, Espace et Transports',
    'SIC': 'Sciences et Ingénieries de la Construction',
    'MDS': 'Mathématiques et Data Sciences',
    'PNT': 'Photonique et Nanotechnologies',
    'IN': 'Informatique et Numérique',
    'EN': 'Énergie',
    'VSE': 'Vivant, Santé, Environnement',
    'GSI': 'Grands Systèmes en Interaction',
    'CVT': 'Construction, Ville, Transports',
    'SCOC': 'Systèmes Communicants et Objets Connectés',
}

MENTIONS_OF_DOMINANTES = {
    'MDS': ['MMF', 'SDI (PS)', 'SDI (M)', 'MSc DSBA'],
    'PNT': ['QTE', 'PSY'],
    'IN': ['IA','SL', 'ASI', 'CYBER', 'MSc AI'],
    'SCOC': ['SRI', 'MACS', 'OCENE', 'NUMVI', 'ELEN', 'ICE'],
    'EN': ['RE', 'E2', 'PEG', 'SES'], 
    'VSE': ['HSB', 'ESP'],
    'GSI': ['CE', 'DS', 'SCOM'], 
    'CVT': ['MSc ITM', 'AET', 'SIC']
}

RESPONSABLES_MENTIONS = {
    'MMF': 'Modélisation mathématique et Mathématiques Financières',
    'SDI (PS)': "Sciences des Données et de l'Information (Paris-Saclay)",
    'SDI (M)': "Sciences des Données et de l'Information (Metz)",
    'MSc DSBA': 'Master in Data Sciences \\& Business Analytics',
    'QTE': 'Quantum Engineering',
    'PSY': 'Photonic and nanosystem engineering',
    'IA': 'Intelligence Artificielle',
    'SL': 'Sciences du Logiciel',
    'ASI': 'Architecture des Systèmes Informatiques',
    'CYBER': 'Cybersécurité',
    'MSc AI': 'Master in Artificial Intelligence',
    'SRI': 'Systèmes et Réseaux Intelligents',
    'MACS': 'Systèmes communicants mobiles et autonomes',
    'OCENE': 'Objets communicants et électronique numérique embarquée',
    'NUMVI': 'Numérique et Vivant',
    'ELEN': 'Electronic Engineering',
    'ICE': 'Information and Communication Engineering',
    'RE': 'Ressources Énergétiques',
    'E2': 'Efficacité Énergétique',
    'PEG': 'Power Energy Grids',
    'SES': 'Sustainable Energy Systems',
    'HSB': 'Healthcare et Services en Biomédical',
    'ESP': 'Environnement et Production Durable',
    'CE': 'Control Engineering',
    'DS': 'Design and System Sciences',
    'SCOM': 'Supply Chain \\& Operations Management',
    'MSc ITM': 'Master in Industry Transformation Management',
}