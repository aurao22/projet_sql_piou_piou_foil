class Station:
    """Représente une station PiouPiou
    """
    # verbose (bool/int, optional): Niveau de détail pour les traces. Defaults to False.
    verbose = False

    def __init__(self, id, name, latitude=None, longitude=None, max_mesure = -1):
        """
        Args:
            id (int): Numeric ID of the station
            name (str): Name of the station
            latitude (float, optional): Last known Latitude of the station, or null. Defaults to None.
            longitude (float, optional): Last known Longitude of the station, or null. Defaults to None.
            max_mesure (int, optional): nombre de mesure à sauvegarder au maximum, si -1 pas de limite. Defaults to -1.
        """
        self.id = id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self._mesures = []
        self._max_mesure = max_mesure

    def ajouter_mesure(self, nouvelle_mesure=None, date=None, wind_heading=None, wind_speed_avg=None, wind_speed_max=None, wind_speed_min=None):
        """Créé et ajoute la mesure (si différente de la dernière mesure enregistrée)

        Args:
            nouvelle_mesure (Mesure) : Mesure à ajouter
            date (str): Date of last measurements, or null
            wind_heading (float): Wind heading, or null (0° means the wind is blowing from North to Sud)
            wind_speed_avg (float): Wind speed average, or null (over the last 4 minutes before measurements.date, divide by 1.852 for converting to knots)
            wind_speed_max (float): Maximum wind speed, or null (over the last 4 minutes before measurements.date, divide by 1.852 for converting to knots)
            wind_speed_min (float): Minimum wind speed, or null (over the last 4 minutes before measurements.date, divide by 1.852 for converting to knots)

        Returns:
            Mesure: la mesure a bien été ajoutée, False si la dernière mesure était équivalente, donc cette mesure n'a pas été ajoutée
        """
        if nouvelle_mesure is None:
            nouvelle_mesure = Mesure(date, wind_heading, wind_speed_avg, wind_speed_max, wind_speed_min, self)
        # Ajout de la mesure via l'accesseur
        self.mesures = nouvelle_mesure

        # Récupération de la dernière mesure ajoutée, qui correspond soit à la mesure actuelle, soit l'équivalent précédémment ajoutée
        if len(self._mesures) > 0:
            nouvelle_mesure = self._mesures[-1]
        else:
            nouvelle_mesure = None
        return nouvelle_mesure

    def nb_mesures(self):
        return len(self._mesures)

    @property
    def mesures(self):
        return self._mesures.copy()

    @mesures.setter
    def mesures(self, mesures):
        if isinstance(mesures, list):
            self._mesures = []
            for mesure in mesures:
                self.mesures =  mesure 
        elif isinstance(mesures, Mesure):
            # Pour limiter le nombre d'enregistrements
            # Vérification que la dernière mesure identique (même si l'heure est différente)
            if len(self._mesures) > 0 and self._mesures[-1] != mesures:
                if self._max_mesure > 0 and len(self._mesures) == self._max_mesure:
                        del self._mesures[0]
                self._mesures.append(mesures)
            elif len(self._mesures) == 0:
                self._mesures.append(mesures)
            else:
                if Station.verbose:
                    print("Cette mesure est égale au dernier enregistrement")
        else:
            raise TypeError(f"Un objet de type Mesure est attendu et non {type(mesures)}")
 
    def __repr__(self):
        return str(self)
    
    def __str__(self):
        return f"{self.name} ({self.id}), avec {len(self._mesures)} mesures"

    def __eq__(self, other):
        if type(other) != type(self):
            return False        
        equa = self.id == other.id and self.name == other.name and self.latitude == other.latitude and self.longitude == other.longitude
        return equa
    

class Mesure:
    def __init__(self, date, wind_heading, wind_speed_avg, wind_speed_max, wind_speed_min, station, id=None):
        """
        Args:
            date (str): Date of last measurements, or null
            wind_heading (float): Wind heading, or null (0° means the wind is blowing from North to Sud)
            wind_speed_avg (float): Wind speed average, or null (over the last 4 minutes before measurements.date, divide by 1.852 for converting to knots)
            wind_speed_max (float): Maximum wind speed, or null (over the last 4 minutes before measurements.date, divide by 1.852 for converting to knots)
            wind_speed_min (float): Minimum wind speed, or null (over the last 4 minutes before measurements.date, divide by 1.852 for converting to knots)
            station (Station): Station de la mesure
        """
        self.date = date
        self.wind_heading = wind_heading
        self.wind_speed_avg = wind_speed_avg
        self.wind_speed_max = wind_speed_max
        self.wind_speed_min = wind_speed_min
        self._station = None
        if station is not None:
            self.station = station
        self.id = id

    @property
    def station(self):
        return self._station

    @station.setter
    def station(self, station):
        if isinstance(station, Station):
            self._station = station
        else:
            raise TypeError(f"Un objet de type Station est attendu et non {type(station)}")

    def __repr__(self):
        return str(self)
    
    def __str__(self):
        st_name = "None"
        if self.station is not None:
            st_name = self.station.name
        return f"{st_name} le {self.date}, WIND heading : {self.wind_heading}°, mean : {self.wind_speed_avg} km/h, max : {self.wind_speed_max} km/h"
    
    def __eq__(self, other):
        
        if type(other) != type(self):
            return False
        
        # On vérifie l'égalité dans les deux sens
        equa = self.wind_heading == other.wind_heading and self.wind_speed_max == other.wind_speed_max and self.wind_speed_avg == other.wind_speed_avg and self.wind_speed_min == other.wind_speed_min and self._station == other._station
        return equa
    
    # Less Than
    def __lt__(self, other):
        if isinstance(other, type(self)):
            if self != other:
                if self.wind_speed_avg == other.wind_speed_avg:
                    if self.wind_speed_max == other.wind_speed_max:
                        return self.wind_speed_min < other.wind_speed_min
                    else:
                        return self.wind_speed_max < other.wind_speed_max
                return self.wind_speed_avg < other.wind_speed_avg
            else:
                return False
        return NotImplemented

    # Less Than or equals
    def __le__(self, other):
        if isinstance(other, type(self)):
            if self != other:
                if self.wind_speed_avg == other.wind_speed_avg:
                    if self.wind_speed_max == other.wind_speed_max:
                        return self.wind_speed_min <= other.wind_speed_min
                    else:
                        return self.wind_speed_max <= other.wind_speed_max
                return self.wind_speed_avg <= other.wind_speed_avg
            else:
                return True
        return NotImplemented
    
    # Greater Than
    def __gt__(self, other):
        if isinstance(other, type(self)):
            if self != other:
                if self.wind_speed_avg == other.wind_speed_avg:
                    if self.wind_speed_max == other.wind_speed_max:
                        return self.wind_speed_min > other.wind_speed_min
                    else:
                        return self.wind_speed_max > other.wind_speed_max
                return self.wind_speed_avg > other.wind_speed_avg
            else:
                return False
        return NotImplemented

    # Greater Than or equals
    def __ge__(self, other):
        if isinstance(other, type(self)):
            if self != other:
                if self.wind_speed_avg == other.wind_speed_avg:
                    if self.wind_speed_max == other.wind_speed_max:
                        return self.wind_speed_min >= other.wind_speed_min
                    else:
                        return self.wind_speed_max >= other.wind_speed_max
                return self.wind_speed_avg >= other.wind_speed_avg
            else:
                return True
        return NotImplemented

    # Comparaison
    def __cmp__(self, other):
        if isinstance(other, type(self)):
            if self == other:
                return 0
            elif self < other:
                return -1
            elif self > other:
                return 1
        return NotImplemented


class GestionnaireDeStations:
    """Contient la liste des stations à surveiller
    """

    def __init__(self, stations=None):
        self._stations = {}
        if stations is not None:
            self.stations = stations

    @property
    def stations(self):
        return self._stations.copy()

    @stations.setter
    def stations(self, stations):
        if self._stations is None:
            self._stations = {}
        if isinstance(stations, Station):
            self._stations[stations.id] = stations
        elif isinstance(stations, list):
            for st in stations:
                self.stations = st
        elif isinstance(stations, dict):
            for st in stations.values():
                self.stations = st
        else:
            raise TypeError(f"Un objet de type Station est attendu et non {type(stations)}")

    def station(self, station=None):
        # Recherche par ID
        if station is not None and isinstance(station, int):
            return self._stations.get(station, None)
        # Recherche par le nom, on parcours la liste des stations
        elif station is not None and isinstance(station, str):
            for st in self._stations.values():
                if station in st.name:
                    return st
            return None
        # Sans critère on retourne la liste des stations
        else:
            return self._stations.copy()

    def ajouter_mesure(self, station, nouvelle_mesure):
         
        if station is not None and nouvelle_mesure is not None:
            if isinstance(station, int):
                station = self.station(station)
            
            if station is None or not isinstance(station, Station):
                raise TypeError(f"Un objet de type Station est attendu et non {type(station)}")
            
            if isinstance(nouvelle_mesure, Mesure):                       
                nouvelle_mesure = station.ajouter_mesure(nouvelle_mesure)
            else:
                raise TypeError(f"Un objet de type Mesure est attendu et non {type(nouvelle_mesure)}")
        else:
            if station is None:
                raise ValueError(f"Un objet de type Station est attendus (None reçu)")
            else:
                raise ValueError(f"Un objet de type Mesuse est attendus (None reçu)")
        return nouvelle_mesure
            
                
    

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#                                              TESTS
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Station
stations_22 = {
    "Pordic": (194,48.582274,-2.780045,  "Balise des Goélands d'Armor de la pointe de Pordic"),
    "Plérin": (116,48.555885,-2.722313, "Balise des Goélands d'Armor de Martin Plage"),
    "Champeaux": (334, 48.732567 , -1.539339, "Pioupiou 334")
}

def test_station_mesure_constructeur(verbose=False):
    print("Station > constucteur et repr")
    stations = {}
    for ville, valeurs in stations_22.items():
        stations[valeurs[0]] = Station(valeurs[0], ville, valeurs[1], valeurs[2])

    assert len(stations) == len(stations_22)
    print("Station > str")
    assert str(stations[334]) == "Champeaux (334), avec 0 mesures"
    assert str(stations[116]) == "Plérin (116), avec 0 mesures"
    assert str(stations[194]) == "Pordic (194), avec 0 mesures"
    # ajout des mesures
    # nouvelle_mesure=None, id=None, date=None, wind_heading=None, wind_speed_avg=None, wind_speed_max=None, wind_speed_min=None
    print("Mesure > constucteur et Station > ajouter_mesure")
    mesure_334_0 = Mesure("2022-01-17T15:23:40.000Z", 202.5, 3, 5.25, 1, stations[334])
    mesure_334_0_b = stations[334].ajouter_mesure(nouvelle_mesure=mesure_334_0)
    assert mesure_334_0 == mesure_334_0_b
    mesure_334_1 = stations[334].ajouter_mesure(date="2022-01-17T15:23:40.000Z", wind_heading=202.5, wind_speed_avg=3, wind_speed_max=5.25, wind_speed_min=1)
    assert mesure_334_1  == mesure_334_0_b
    
    mesure_334_2 = Mesure("2022-01-17T15:35:44.000Z", 202.5, 3, 4.5, 0.25, stations[334])
    assert stations[334].ajouter_mesure(mesure_334_2) == mesure_334_2

    mesure_116_1 = Mesure("2022-01-17T15:32:29.000Z", 202.5, 3, 5.25, 1, stations[116])
    assert stations[116].ajouter_mesure(mesure_116_1) == mesure_116_1
    mesure_116_2 = Mesure("2022-01-18T08:26:10.000Z", 112.5, 3.75, 9.75, 0, stations[334])
    assert stations[116].ajouter_mesure(mesure_116_2) == mesure_116_2

    # test que l'ajout de la mesure n'est pas faite si la dernière mesure est équivalente
    assert stations[116].ajouter_mesure(mesure_116_2) == mesure_116_2
    assert len(stations[116].mesures) == 2
    assert stations[116].ajouter_mesure(Mesure("2022-01-18T08:26:10.000Z", 112.5, 3.75, 9.75, 0, stations[334])) == mesure_116_2
    assert len(stations[116].mesures) == 2

    return stations


def test_station_mesure_error(station, verbose=False):
    print("Station / Mesure > Error")
    
    # ajout des mesures
    # nouvelle_mesure=None, id=None, date=None, wind_heading=None, wind_speed_avg=None, wind_speed_max=None, wind_speed_min=None
    mesure_334_0 = Mesure("2022-01-17T15:23:40.000Z", 202.5, 3, 5.25, 1, station)
    try:
        mesure_334_0 < 5
    except TypeError:
        assert True

    try:
        mesure_334_0 > 5
    except TypeError:
        assert True

    try:
        mesure_334_0 >= 5
    except TypeError:
        assert True

    try:
        mesure_334_0 <= 5
    except TypeError:
        assert True

    try:
        mesure_334_0.station = 14
    except TypeError:
        assert True
    
    try:
        station.mesures = "toto"
    except TypeError:
        assert True


# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# GestionnaireDeStations

def test_GestionnaireDeStations(stations):
    print("GestionnaireDeStations > constructeur")
    gestionnaire = GestionnaireDeStations()
    assert len(gestionnaire.stations) == 0
    gestionnaire = GestionnaireDeStations(stations)
    assert len(gestionnaire.stations) == 3
    assert gestionnaire.station(334) == stations[334]
    station_res = gestionnaire.station(stations[334].name)
    assert station_res == stations[334]


if __name__ == "__main__":
    Station.verbose = False
    stations = test_station_mesure_constructeur()
    test_station_mesure_error(stations[334])
    test_GestionnaireDeStations(stations)
