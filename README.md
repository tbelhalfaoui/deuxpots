# Impôt deux pots

Lorsqu'on est marié ou pacsé, la déclaration d'impôt commune est obligatoire. Lorsque les deux personnes
sont salariées, il est possible d'individualiser le prélèvement à la source. Mais cela ne résout pas le
problème :
- Les personnes non-salariées ne sont pas concernées par le prélèvement à la source.
- Le prélèvement à la source n'est jamais exact : il y a toujours un reliquat à payer ou un trop-perçu 
à récupérer en fin d'année. Comment le partager entre les deux partenaires ?

_Deux pots_ est un outil simple pour offrir le choix à chacun·e qui le souhaite d'indivisualiser son impôt.

Concrètement, il suffit de soumettre le fichier PDF de la déclaration d'impôt commune, et l'outil indique qui 
doit payer (ou récupérer) quel montant.

## Instructions pour le développement

Voir le notebook `build_cerfa_variables.ipynb` pour la construction des fichiers JSON du dossier `resources`.
- Le fichier `cerfa_variables.json`, contenant la liste des cases de la déclaration d'impôt,
est construit à partir du code de [Openfisca-France](https://github.com/openfisca/openfisca-france).
- Le fichier `family_box_coords.json`, contenant les coordonnées des cases à cocher de la page 2 de la
déclaration d'impôt (relatives à la situation familiale), est construit à la main avec l'outil
[Labelme](https://github.com/wkentaro/labelme), en utilisant l'image d'exemple `family_page.png`.
