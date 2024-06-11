# Générateur de diapo de diplômation

## Récupération des données
1. Télécharger les données du FramaForms sous forme d'un tableur `tsv` (laisser les réglages par défaut). Le placer dans un dossier `data` au même niveau d'arborescence que ce README.
2. Créer si besoin le fichier `credentials.yml` qui contient 2 clés : `username` et `password`, permettant de se connecter au compte FramaForms de l'organisation de la RDD. 
3. Récupérer le fichier Excel contenant la liste de tous les diplômés présents le jour J, et le placer dans le dossier `data` également.
4. Remplir les paramètres dans `constantes.py` notamment :
- taille finale d'image désirée (utiliser une valeur plus petite pour rendre le code plus rapide mais penser à remettre une bonne qualité pour l'export final). 
- nom du fichier correspondant à l'image par défaut (à placer dans `data/photos`, dossier créé automatiquement s'il n'existe pas déjà la première fois que le script est lancé).
- dans le dictionnaire `PATH` : bien remplir les noms de fichier des 2 tableurs récupérés aux étapes précédentes, contenant respectivement les réponses au FramaForm de personnalisation et la liste de tous les diplômés présents.\
Les variables en majuscule sont à modifier, éviter de toucher au reste.
5. Remplir la composition des sessions de diplômation par acronyme de dominante dans `main.py`.

## Lancer le code
Dans le terminal, lancer la commande
```
python main.py
```
Le contenu des diapositives beamer sera généré dans le dossier parent.

## Vérifier le résultat

- Compiler les 4 beamers pour vérifier que tout est OK visuellement.
- Vérifier les tableurs dans le dossier `check` qui montrent les corrections des cas particuliers (mentions "autre", nettoyage du texte des citations).\

En cas de problème concernant les mentions "autre", éditer les exceptions dans le fichier `constantes.py` en vérifiant à nouveau le résultat ensuite. Les mots-clés à chercher dans les réponses des étudiants sont à ajouter dans la liste correspondant à la mention concernée.