import requests
from piou_piou_raoul_aurelie_dao import *
from piou_piou_raoul_aurelie_objets import *
from datetime import datetime
import time


# ---------------------------------------------------------------------------------------------
#                               CONSTANTES
# ---------------------------------------------------------------------------------------------
stations_proche_nantes = {
    "Groix": 298,
    "Brétignolles sur mer": 113,
    "L'île-d'Olonne":308,
    "La Rochelle":565
}

stations_22 = {
    "Pordic": 194,
    "Plérin": 116,
    "Champeaux":334
}

BDD_NAME = 'my_piou_piou_raoul_aurelie.db'
PP_URL_API_LIVE = "http://api.pioupiou.fr/v1/live/"
TIMEOUT = 5 # nombre de seconde à attendre
SLEEP_TIME =  30 # in secondes

MAX_MESURE_MOD_STATION = 'station'
MAX_MESURE_MOD_ALL = 'all'

max_mesure=10
max_mesure_mod = MAX_MESURE_MOD_STATION

curent_path = getcwd()+ "\\projet_sql_piou_piou_foil\\"

# verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.
verbose = 1



# ---------------------------------------------------------------------------------------------
#                               FONCTIONS
# ---------------------------------------------------------------------------------------------

def api_station_information(url, id_station, verbose=False):
    """Appelle l'API pour récupérer la mesure de la station reçue

    Args:
        url (str): url de l'API (sans l'id de la station)
        id_station (int): identifiant de la station
        verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.

    Raises:
        Exception: En cas d'incohérence entre les donnes reçues et la station
        http_error : En cas d'erreur d'accès à l'API

    Returns:
        Station: la station ou None
    """
    nouvelle_station = None
    if id_station is not None and isinstance(id_station, int):       
        # Récupération des données de l'API avec l'ID de la station
        resp = requests.get(url=url+str(id_station))
        data = resp.json()
        # Vérification du code réponse
        if resp.status_code == 200 :
            if verbose>1:
                print(f"API > Statut {resp.status_code}")
            # Traitement de la réponse JSON
            data = data['data']
            # Information sur la station
            id = data['id']
            name = data['meta']['name']
            longitude = data['location']['longitude']
            latitude = data['location']['latitude']
            
            nouvelle_station = Station(id, name, latitude, longitude)
            if verbose:
                    print(f"{nouvelle_station}")
        else:
            print(f'{resp.status_code} => {data["error_code"]} : {data["error_message"]}')
            resp.raise_for_status()
    return nouvelle_station


def api_mesure_courante_pour_la_station(url, station, verbose=False):
    """Appelle l'API pour récupérer la mesure de la station reçue

    Args:
        url (str): url de l'API (sans l'id de la station)
        station (Station): Station à mettre à jour
        verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.

    Raises:
        Exception: En cas d'incohérence entre les donnes reçues et la station
        http_error : En cas d'erreur d'accès à l'API

    Returns:
        Mesure: la mesure ou None
    """
    mesure = None
    if station is not None and isinstance(station, Station):       
        # Récupération des données de l'API avec l'ID de la station
        resp = requests.get(url=url+str(station.id))
        data = resp.json()
        # Vérification du code réponse
        if resp.status_code == 200 :
            if verbose>1:
                print(f"API > Statut {resp.status_code}")
            # Traitement de la réponse JSON
            data = data['data']
            # Information sur la station
            id = data['id']
            name = data['meta']['name']
            # Vérification de la cohérence entre la station de la mesure et la station courante
            if id == station.id:
                # Information sur la mesure
                data = data['measurements']
                measures_date_str1 = data['date']
                # convertion en date
                measures_date_str = datetime.fromisoformat(measures_date_str1[:-1])
                # "2022-01-17T09:45:47.000Z"  ==> YYYY-MM-DDTHH:MM:SS.mmmmmm
                measures_date = measures_date_str.strftime('%Y-%m-%d %H:%M:%S')
                wind_heading = data['wind_heading']
                wind_speed_avg = data['wind_speed_avg']
                wind_speed_min = data['wind_speed_min']
                wind_speed_max = data['wind_speed_max']
                if verbose:
                    print(f"{id} : {measures_date} - {wind_heading}, {wind_speed_avg}, {wind_speed_min} => {name}")
                mesure = station.ajouter_mesure(date=measures_date, wind_heading=wind_heading, wind_speed_avg=wind_speed_avg, wind_speed_max=wind_speed_max, wind_speed_min=wind_speed_min)
            else:
                raise Exception(f"La mesure reçue pour la station {id}-{name} ne concerne pas la station {station.id}-{station.name}")
        else:
            print(f'{resp.status_code} => {data["error_code"]} : {data["error_message"]} \n {url+str(station.id)}')
            resp.raise_for_status()
    return mesure
   
def api_recuperer_mesures(url, gestionnaire, verbose=False):
    """[summary]

    Args:
        url ([type]): [description]
        gestionnaire ([type]): [description]
        verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.

    Returns:
        List[Mesures]: Liste des mesures récupérées
    """

    mesures = []
    stations = gestionnaire.stations
    # Récupéreration des mesures pour chaque station
    for station in stations.values():
        mesure = api_mesure_courante_pour_la_station(url, station, verbose)
        if mesure is not None:
            mesures.append(mesure)
            
    return mesures

def dao_ajouter_mesures_bdd(mesures, ma_dao, verbose=False):
    """Vérifie et au besoin ajoute en BDD les mesures en mémoire qui ne sont pas encore en BDD

    Args:
        mesures (List[Mesure]): mesures à ajouter
        ma_dao (PiouPiouDao): dao
        verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.
    """
    # Vérifier si les mesures en BDD sont différentes ou non
    for mesure in mesures:
        # id_station=None, mesure_date=None, wind_heading=None, wind_speed_avg=None, wind_speed_min=None,wind_speed_max=None
        dao_mesure_list = ma_dao.select_mesures(station=mesure.station, mesure_date=mesure.date, wind_heading=mesure.wind_heading, wind_speed_avg=mesure.wind_speed_avg, wind_speed_min=mesure.wind_speed_min,wind_speed_max=mesure.wind_speed_max, verbose=verbose)
        if dao_mesure_list is not None and len(dao_mesure_list)>0:
            pass
        else:
            # Sauvegarder en BDD
            ma_dao.ajouter_mesure(mesure, verbose)


def dao_synchroniser_bdd(gestionnaire, ma_dao, verbose=False):
    """Rafraîchit les mesures de chaque station par rapport à ce qui est en BDD

    Args:
        gestionnaire (GestionnaireDeStations): gestionnaire des stations
        ma_dao (PiouPiouDao): dao
        verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.
    """
    stations = gestionnaire.stations
    # Récupéreration des mesures pour chaque station
    for station in stations.values():
        # pour être sûre d'avoir les mêmes données qu'en BDD, on remplace les données en mémoire par les données de la BDD        
        station.mesures = ma_dao.select_mesures(station=station, verbose=verbose)

# ---------------------------------------------------------------------------------------------
#                               MAIN
# ---------------------------------------------------------------------------------------------

gestionnaire = GestionnaireDeStations()
ma_dao = PiouPiouDao(curent_path+BDD_NAME)

if ma_dao.initialiser_bdd(verbose=verbose):

    nb_stations = ma_dao.nombre_stations(verbose=verbose)
    if nb_stations == 0:
        # Création des stations en BDD
        for id in stations_proche_nantes.values():  
            # Récupérer les informations de la station via l'API
            station = api_station_information(PP_URL_API_LIVE, id, verbose)
            if station is not None:
                res = ma_dao.ajouter_station(station)
                if res != id:
                    print(f"SQLite > La station {id} soit {station} n'a pas pu être insérée en BDD.")
            else:
                print(f"API > Aucune information récupérée sur la station {id}.")
    
    # Normalement ici il y a des stations en BDD
    nb_stations = ma_dao.nombre_stations(verbose=verbose)
    if nb_stations == 0:
        raise Exception("Aucune station.")
        
    station_list = ma_dao.stations()
    if station_list is not None:
        # Ajout de la nouvelle station dans le gestionnaire
        gestionnaire.stations = station_list
  
    # Initialisation des mesures
    dao_synchroniser_bdd(gestionnaire, ma_dao, verbose)
    
    # Boucler pour mise à jour régulière
    sortie = False    
    while not sortie:
         # Récupéreration des mesures pour chaque station
        mesures_ajoutees = api_recuperer_mesures(PP_URL_API_LIVE, gestionnaire, verbose)
        dao_ajouter_mesures_bdd(mesures_ajoutees, ma_dao, verbose)
        dao_synchroniser_bdd(gestionnaire, ma_dao, verbose)
        time.sleep(SLEEP_TIME)

    print(f"---------------------- END ----------------------")
    

