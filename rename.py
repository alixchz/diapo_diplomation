import os
import time

# Nom du fichier original
original_filename = "beamer/test/beamer_test.pdf"

# Vérifier si le fichier existe
if not os.path.exists(original_filename):
    print(f"Le fichier {original_filename} n'existe pas.")
else:
    # Obtenir le temps actuel
    current_time = time.strftime("%dmai_%Hh%M")

    # Créer le nouveau nom de fichier
    new_filename = f"beamer/test/beamer_test_{current_time}.pdf"

    i = 1
    while os.path.exists(new_filename):
        i += 1
        new_filename = f"beamer/test/beamer_test_{current_time}_{i}.pdf"
    # Renommer le fichier
    os.rename(original_filename, new_filename)
    print(f"Le fichier a été renommé en {new_filename}.")
