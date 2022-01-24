# Y'a-t-il du vent pour mon foil? Récupération de données en temps réel

par Aurélie RAOUL

# 1. Description du programme

## 1.1. Structure du projet

* ```piou_piou_raoul_aurelie_controller.py``` : Programme principal qui coordonne l'ensemble et contient les fonctions d'appelle de l'API
* ```piou_piou_raoul_aurelie_objets.py``` : contient les classes représentant les objets nécessaires au programme
* ```piou_piou_raoul_aurelie_dao.py``` : Traite des accès à la base de données (exécution des requêtes)
* ---
* ```my_piou_piou_raoul_aurelie.db``` : base de données du programme, en cas d'absence de ce fichier, le programme créera automatiquement le fichier et la base de données
* ```my_piou_piou_raoul_aurelie.backup.db``` : Back-up de la base de données, en cas d'absence de ce fichier, le programme le créera automatiquement
* ```my_piou_piou_bdd_script.sql``` : Le script SQL de création de la BDD, non nécessaire car intégré dans le programme


## 1.2. Lancement

Le programme doit être lancé via le script : ```piou_piou_raoul_aurelie_controller.py```    
Une fois lancé, il faut utiliser ```CTRL + Z``` pour l'arrêter   

Si la BDD n'existe pas, le programme créera la BDD dans le répertoire d'exécution, il possible de modifier l'emplacement dans le controller

# 2. Contexte du projet

## 2.1. Description

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


## 2.2. Contenu de la réponse de l'API
```json
{
  "doc": "http://developers.pioupiou.fr/api/live/",
  "license": "http://developers.pioupiou.fr/data-licensing",
  "attribution": "(c) contributors of the Pioupiou wind network <http://pioupiou.fr>",
  "data": [
    {
      "id": 1,
      "meta": {
        "name": "Pioupiou 1",
        "description": null,
        "picture": null,
        "date": null,
        "rating": {
          "upvotes": 0,
          "downvotes": 0
        }
      },
      "location": {
        "latitude": 0,
        "longitude": 0,
        "date": null,
        "success": false
      },
      "measurements": {
        "date": "2015-08-18T08:19:46.000Z",
        "pressure": null,
        "wind_heading": 157.5,
        "wind_speed_avg": 2,
        "wind_speed_max": 4,
        "wind_speed_min": 0
      },
      "status": {
        "date": "2015-08-18T08:19:46.000Z",
        "snr": 23.24,
        "state": "on"
      }
    },
    {
      "id": 27,
      "meta": {
        "name": "Pioupiou 27",
        "description": null,
        "picture": null,
        "date": null,
        "rating": {
          "upvotes": 0,
          "downvotes": 0
        }
      },
      "location": {
        "latitude": 44.907284,
        "longitude": 5.677965,
        "date": "2015-08-15T13:48:38.000Z",
        "success": true
      },
      "measurements": {
        "date": "2015-08-18T08:18:26.000Z",
        "pressure": null,
        "wind_heading": 45,
        "wind_speed_avg": 15,
        "wind_speed_max": 17.5,
        "wind_speed_min": 10.5
      },
      "status": {
        "date": "2015-08-18T08:18:26.000Z",
        "snr": 12.01,
        "state": "on"
      }
    },
    {...more stations...},
    {...more stations...}
  ]
}
```

## 2.3. Description des données

|Name                         |live |live-with-meta|Description                                                                                                                     |Unit         |
|-----------------------------|-----|--------------|--------------------------------------------------------------------------------------------------------------------------------|-------------|
|id                           |x    |x             |Numeric ID of the station                                                                                                       |             |
|meta.name                    |x    |x             |Name of the station                                                                                                             |             |
|meta.description             |     |x             |Description of the station, or null                                                                                             |             |
|meta.picture                 |     |x             |URL of station's picture, or null                                                                                               |             |
|meta.date                    |     |x             |Date of last metadata update, or null                                                                                           |ISO 8601, UTC|
|meta.rating.upvotes          |     |x             |Station rating : Positive votes count                                                                                           |             |
|meta.rating.downvotes        |     |x             |Station rating : Negative votes count                                                                                           |             |
|location.latitude            |x    |x             |Last known Latitude of the station, or null                                                                                     |WGS84        |
|location.longitude           |x    |x             |Last known Longitude of the station, or null                                                                                    |WGS84        |
|location.date                |x    |x             |Date of last location update (succeed or failed), or null                                                                       |ISO 8601, UTC|
|location.success             |x    |x             |Is the last known position still valid ? true or false                                                                          |             |
|measurements.date            |x    |x             |Date of last measurements, or null                                                                                              |ISO 8601, UTC|
|measurements.pressure        |x    |x             |null (deprecated)                                                                                                               |             |   
|measurements.wind_heading    |x    |x             |Wind heading, or null (0° means the wind is blowing from North to Sud)                                                          |degrees      |   
|measurements.wind_speed_avg  |x    |x             |Wind speed average, or null (over the last 4 minutes before measurements.date, divide by 1.852 for converting to knots)         |km/h         | 
|measurements.wind_speed_min  |x    |x             |Minimum wind speed, or null (over the last 4 minutes before measurements.date, divide by 1.852 for converting to knots)         |km/h         | 
|measurements.wind_speed_max  |x    |x             |Maximum wind speed, or null (over the last 4 minutes before measurements.date, divide by 1.852 for converting to knots)         |km/h         | 
|status.date                  |x    |x             |Date of the last contact with the station, or null                                                                              |ISO 8601, UTC|
|status.snr                   |x    |x             |Signal-to-Noise ratio = radio link quality, or null (<10 : bad, >20: very good)                                                 |dB           | 
|status.state                 |x    |x             |"Station power state, ""on"", ""off"" or null. ""off"" means that the station have been shutdown by pressing it's power switch."|             |

## 2.4. Codes d'erreur

An ```HTTP/1.1 200 OK``` header is sent on successful request. HTTP status code other than ```200``` means that an error has occured.

In most cases the application will return a JSON object, including details about the error.

```
$ curl -i "http://api.pioupiou.fr/v1/live/999999"
```

```json
HTTP/1.1 404 Not Found

{
  "error_code": "station_not_found",
  "error_message": "unable to find station with this {station_id}"
}
```

|error_code       |HTTP code |Description                                 |
|-----------------|----------|--------------------------------------------|
|station_not_found| 	404 	 |The requested station is not in the database|
|missing_argument | 	400 	 |The station ID is missing or invalid        |

# 3. Représentation des données

## 3.1. Réprésentation générale

![Réprésentation générale](https://github.com/aurao22/projet_sql_piou_piou_foil/blob/master/schema_pioupiou_full.png)

## 3.2. Sélection des données nécessaires pour le programme

![Données sélectionnées](https://github.com/aurao22/projet_sql_piou_piou_foil/blob/master/schema_pioupiou_selected.png)
