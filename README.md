# Y'a-t-il du vent pour mon foil? Récupération de données en temps réel

par Aurélie RAOUL

## Structure du projet

* ```piou_piou_raoul_aurelie_controller.py``` : Programme principal qui coordonne l'ensemble et contient les fonctions d'appelle de l'API
* ```piou_piou_raoul_aurelie_objets.py``` : contient les classes représentant les objets nécessaires au programme
* ```piou_piou_raoul_aurelie_dao.py``` : Traite des accès à la base de données (exécution des requêtes)
* ---
* ```my_piou_piou_raoul_aurelie.db``` : base de données du programme, en cas d'absence de ce fichier, le programme créera automatiquement le fichier et la base de données
* ```my_piou_piou_raoul_aurelie.backup.db``` : Back-up de la base de données, en cas d'absence de ce fichier, le programme le créera automatiquement
* ```my_piou_piou_bdd_script.sql``` : Le script SQL de création de la BDD, non nécessaire car intégré dans le programme


## Lancement

Le programme doit être lancé via le script : ```piou_piou_raoul_aurelie_controller.py```    
Une fois lancé, il faut utiliser ```CTRL + Z``` pour l'arrêter   

Si la BDD n'existe pas, le programme créera la BDD dans le répertoire d'exécution, il possible de modifier l'emplacement dans le controller

## Contexte du projet

Après avoir vu les images de l’America’s cup dans la baie d’Auckland, Cléante de Nantes a décidé de se mettre au catamaran avec foil.

Avant d’investir dans son engin high tech, elle a décidé de faire une petite application pour sa montre connectée qui donne en temps réel les dernières mesures sur 3 stations locales disposant d’un anémomètre. Elle souhaite savoir où se diriger pour trouver le vent nécessaire à ses futures activités.

Malheureusement sa montre dispose d’un stockage particulièrement réduit, donc la base de données locale devra être mise à jour régulièrement tout en s’assurant de ne pas dépasser un volume de stockage correspondant aux 10 derniers enregistrements. Enfin, un tantinet paranoïaque, elle souhaite absolument avoir la dernière sauvegarde qui devra être mise à jour régulièrement (une fois tous les 5 enregistrements).

Pourrez-vous aider Cléante à réaliser son projet en moins de 48h chrono?

Contrainte: usage de SQLite sur la montre

Les données pourront être récupérées auprès d’anémomètres connectés: les “pioupiou”s https://www.openwindmap.org/PP308

Ceux-ci disposent d’une API qui peut être interrogée: http://developers.pioupiou.fr/api/live/

Modalités pédagogiques : Groupes de 1 ou 2 apprenants
Critères de performance : Efficience du code
Livrables : La base de données, le code d'actualisation de la base en continu et sa méthode de sauvegarde.
