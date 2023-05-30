# Impôt deux pots

## Un outil simple pour individualiser l'impôt au sein du couple.

https://deuxpots.fr

En 2023, en France, les couples mariés ou pacés doivent faire une déclaration de revenus commune. L'administration fiscale réclame ou reverse ensuite une somme globale au couple, sans distinguer la part de chacun·e. Le prélèvement à la source individualisé est un début de réponse, mais qui ne s'applique pas à toutes les situations (travailleur·euse·s indépendant·e·s, forte variation de revenus d'une année sur l'autre, etc.).

Ce fonctionnement peut léser les personnes qui ont choisi de conserver une indépendance financière au sein du couple, en particulier si les différences de revenus sont importantes.

À partir de votre dernière déclaration commune, _Deux pots_ calcule le montant que chacun·e doit payer ou récupérer.

## Instructions pour le développement

### Construction des fichiers de données

Voir le notebook `build_cerfa_variables.ipynb` pour la construction des fichiers JSON du dossier `resources`.
- Le fichier `cerfa_variables.json`, contenant la liste des cases de la déclaration d'impôt,
est construit à partir du code HTML du simulateur des impôts.
- Le fichier `family_box_coords.json`, contenant les coordonnées des cases à cocher de la page 2 de la
déclaration d'impôt (relatives à la situation familiale), est construit à la main avec l'outil
[Labelme](https://github.com/wkentaro/labelme), en utilisant l'image d'exemple `family_page.png`.


### Lancement de l'application

#### Backend
Depuis le dossier `backend` (et de préférence dans un environnement virtuel) :

Installer les dépendances :
```bash
pip install -r requirements.txt
pip install -r requirements_dev.txt
```

Pour lancer l'API Python (en mode développement) :
```bash
flask --app deuxpots/app.py run --debug --port 8080
```

#### Frontend
Depuis le dossier `frontend`:

Installer les dépendances :
```bash
npm install
```

Lancer le frontend (en mode développement):
```bash
npm run start
```
