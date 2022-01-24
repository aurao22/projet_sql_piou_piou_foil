import atexit
import sqlite3
from os import getcwd, remove, path
from piou_piou_raoul_aurelie_objets import *


class PiouPiouDao:

    def __init__(self, nom_bdd, backup_path=None, frequence_backup=5, max_mesure=10):
        """[summary]

        Args:
            nom_bdd (str): Chemin complet de la bdd
            frequence_backup (int, optional): Fréquence de backup de la BDD. Defaults to 5.
        """
        self.nom_bdd = nom_bdd
        self.frequence_backup = frequence_backup
        self._nb_enregistrement = 0
        if backup_path is None:
            backup_path = self.nom_bdd.replace(".db", ".backup.db")
        self.backup_path = backup_path
        self.max_mesure = max_mesure


    def connecter(self, verbose=False):
        conn = None
        try:
            conn = sqlite3.connect(self.nom_bdd)
        except sqlite3.Error as error:
            print("SQLite > Erreur de connexion à la BDD", error)
            try:
                if verbose > 1:
                    print("SQLite > La connexion est fermée")
                conn.close()
            except Exception:
                pass       
            raise error
        return conn


    def test_connexion(self, verbose=False):
        try:
            sql = "SELECT sqlite_version();"       
            res = self._executer_sql(sql, verbose)
            print("La version de SQLite est: ", res)
            return True
        except sqlite3.Error as error:
            print("Erreur lors de la connexion à SQLite", error)
            return False

    def liste_tables(self, verbose=False):
        """
        Args:
            verbose (bool, optional): [description]. Defaults to False.

        Returns:
            List: Retourne la liste des tables créées dans la BDD
        """
        tables = self._executer_sql("SELECT name FROM sqlite_master WHERE type='table';", verbose=verbose)
        tables_name = []
        for it in tables:
            tables_name.append(it[0])
        return tables_name

    def nombre_stations(self, verbose=False):
        res = self._executer_sql("SELECT count(*) FROM station;", verbose=verbose)
        if verbose:
            print(res[0][0])
        # on retourne la 1ère valeur de la 1ère ligne
        return res[0][0]

    def nombre_mesures(self, verbose=False):
        res = self._executer_sql("SELECT count(*) FROM mesure;", verbose=verbose)
        if verbose:
            print(res[0][0])
        # on retourne la 1ère valeur de la 1ère ligne
        return res[0][0]

    def ajouter_station(self, station, verbose=False):
        res = None
        if station is not None:
            if isinstance(station, Station):
                res = self._executer_sql(f"INSERT INTO station (id, station_name, latitude, longitude) VALUES ({station.id},'{station.name}',{station.latitude}, {station.longitude});", verbose=verbose)
            elif isinstance(station, list):
                res = []
                try:
                    for st in station:
                        res.append(self.ajouter_station(st, verbose))
                # on ajoute toutes les stations qui n'existent pas déjà
                except sqlite3.IntegrityError:
                    print(f"La station {st} existe déjà en BDD.")
            elif isinstance(station, dict):
                res = []
                try:
                    for st in station.values():
                        res.append(self.ajouter_station(st, verbose))
                # on ajoute toutes les stations qui n'existent pas déjà
                except sqlite3.IntegrityError:
                    print(f"La station {st} existe déjà en BDD.")
            else:
                raise TypeError(f"type Station attendu et non {station}")
        else:
            raise ValueError("La station ne peut pas être vide ou Null")
        return res

    def ajouter_mesure(self, mesure, verbose=False):
        res = None
        if mesure is not None:
            if isinstance(mesure, Mesure):
                nb_mesure = self.nombre_mesures(verbose)
                if nb_mesure == self.max_mesure:
                    # on supprime la mesure la plus ancienne pour garder uniquement les 10 dernières mesures
                    self._executer_sql(f"DELETE FROM mesure WHERE id = (SELECT MIN(id) FROM mesure);", verbose=verbose)
                res = self._executer_sql(f"INSERT INTO mesure (id, mesure_date, wind_heading, wind_speed_avg, wind_speed_max, wind_speed_min, station) VALUES (NULL,'{mesure.date}',{mesure.wind_heading}, {mesure.wind_speed_avg}, {mesure.wind_speed_max}, {mesure.wind_speed_min},  {mesure.station.id});", verbose=verbose)
                
            elif isinstance(mesure, list):
                res = []
                try:
                    for st in mesure:
                        res.append(self.ajouter_mesure(st, verbose))
                # on ajoute toutes les stations qui n'existent pas déjà
                except sqlite3.IntegrityError:
                    print(f"La mesure {st} existe déjà en BDD.")
            elif isinstance(mesure, dict):
                res = []
                try:
                    for st in mesure.values():
                        res.append(self.ajouter_mesure(st, verbose))
                # on ajoute toutes les stations qui n'existent pas déjà
                except sqlite3.IntegrityError:
                    print(f"La mesure {st} existe déjà en BDD.")
            else:
                raise TypeError(f"type Station attendu et non {mesure}")
        else:
            raise ValueError("La mesure ne peut pas être vide ou Null")
        return res

    def stations(self, verbose=False):
        res = self._executer_sql(f"SELECT id, station_name, latitude, longitude FROM station ORDER BY id;", verbose=verbose)
        stations_list = []
        for row in res:
            station = Station(id=row[0], name=row[1], latitude=row[2], longitude=row[3])
            stations_list.append(station)
        return stations_list

    def mesures(self, id_station=None, verbose=False):

        sql = ""
        if id_station is not None and isinstance(id_station, int):
            sql = f"SELECT id, mesure_date, wind_heading, wind_speed_avg, wind_speed_min, wind_speed_max, station FROM mesure WHERE station = {id_station} ORDER BY id;"
        else:
            sql = f"SELECT id, mesure_date, wind_heading, wind_speed_avg, wind_speed_min, wind_speed_max, station FROM mesure ORDER BY station, id;"

        res = self._executer_sql(sql, verbose=verbose)
        mesures_list = []
        for row in res:
            # date, wind_heading, wind_speed_avg, wind_speed_max, wind_speed_min, station
            mesure = Mesure(date=row[1],wind_heading=row[2], wind_speed_avg=row[3], wind_speed_max=row[5], wind_speed_min=row[4])
            mesures_list.append(mesure)

        return mesures_list


    def select_mesures(self, station=None, mesure_date=None, wind_heading=None, wind_speed_avg=None, wind_speed_min=None,wind_speed_max=None, id_mesure=None, verbose=False):

        nb_param = 0

        sql = f"SELECT id, mesure_date, wind_heading, wind_speed_avg, wind_speed_min, wind_speed_max, station FROM mesure "
        sql_where = ""
        sql_key = "WHERE"
        sql_end = " ORDER BY station, id;"

        if station is not None and isinstance(station, Station):
            sql_where += f"{sql_key} station = {station.id} "
            nb_param += 1
            sql_key = "AND"
        
        if id_mesure  is not None and isinstance(id_mesure, int):
            sql_where += f"{sql_key} id = {id_mesure} "
            nb_param += 1
            sql_key = "AND"

        if mesure_date  is not None and isinstance(mesure_date, str):
            sql_where += f"{sql_key} mesure_date = '{mesure_date}' "
            nb_param += 1
            sql_key = "AND"

        if wind_heading  is not None and isinstance(wind_heading, float):
            sql_where += f"{sql_key} wind_heading = {wind_heading} "
            nb_param += 1
            sql_key = "AND"

        if wind_speed_avg  is not None:
            sql_where += f"{sql_key} wind_speed_avg = {wind_speed_avg} "
            nb_param += 1
            sql_key = "AND"

        if wind_speed_min  is not None:
            sql_where += f"{sql_key} wind_speed_min = {wind_speed_min} "
            nb_param += 1
            sql_key = "AND"

        if wind_speed_max  is not None:
            sql_where += f"{sql_key} wind_speed_max = {wind_speed_max} "
            nb_param += 1
            sql_key = "AND"

        requete = sql+sql_where+sql_end
        res = self._executer_sql(requete, verbose=verbose)
        mesures_list = []
        for row in res:
            # date, wind_heading, wind_speed_avg, wind_speed_max, wind_speed_min, station
            mesure = Mesure(date=row[1],wind_heading=row[2], wind_speed_avg=row[3], wind_speed_max=row[5], wind_speed_min=row[4], station=station)
            mesures_list.append(mesure)

        return mesures_list


    def initialiser_bdd(self, drop_if_exist = False, verbose=False):
        """Créé les tables manquantes

        Args:
            drop_if_exist (bool, optional): Pour supprimer les tables si elles existent déjà /!\ Suppression des données. Defaults to False.
            verbose (bool, optional): [description]. Defaults to False.

        Returns:
            bool: Si les tables existent dans la BDD ou non
        """
        if drop_if_exist:
            self._supprimer_table_mesure(verbose)
            self._supprimer_table_station(verbose)
        # Vérifier si la BDD existe déjà
        tables = self.liste_tables(verbose)
        if "station" not in tables:
            self._creer_table_station(verbose)
        if "mesure" not in tables:
            self._creer_table_mesure(verbose)
        # vérifier que les tables sont bien créées
        tables = self.liste_tables(verbose)
        return "station" in tables and "mesure" in tables

    def creer_sauvegarde(self, file_path, verbose=False):
        """Créer un fichier de sauvegarde de la BDD courante

        Args:
            file_path (str): Chemin complet avec nom du fichier de la sauvegarde
            verbose (bool, optional): [description]. Defaults to False.

        Returns:
            boolean: True si fichier de sauvegarde créé, False sinon
        """
        success = False
        try:
            conn = self.connecter()
            BDD_Destination = sqlite3.connect (file_path)
            conn.backup (BDD_Destination)
            if verbose:
                print("SQLite DAO > Sauvegarde effectuée :",file_path)
        # Fermeture des connexions
        finally:
            try:
                BDD_Destination.close()
                if verbose > 1:
                    print("SQLite DAO > connexion sauvegarde fermée")
            except Exception:
                pass
            try:
                conn.close()
                if verbose > 1:
                    print("SQLite DAO > La connexion est fermée")
            except Exception:
                pass
        # Vérification que le fichier existe bien
        try:
            with open(file_path): success=True
        except IOError:
            pass   
        return success

    def _supprimer_table_station(self, verbose=False):
        res = self._executer_sql("DROP TABLE IF EXISTS station;", verbose=verbose)
        return res

    def _supprimer_table_mesure(self, verbose=False):
        res = self._executer_sql("DROP TABLE IF EXISTS mesure;", verbose=verbose)
        return res

    def _creer_table_station(self, verbose=False):
        res = self._executer_sql("CREATE TABLE station (id INTEGER PRIMARY KEY, station_name TEXT NOT NULL, latitude REAL, longitude REAL);", verbose=verbose)
        return res

    def _creer_table_mesure(self, verbose=False):
        res = self._executer_sql("CREATE TABLE mesure (id INTEGER PRIMARY KEY AUTOINCREMENT, mesure_date TEXT NOT NULL, wind_heading REAL, wind_speed_avg REAL, wind_speed_max REAL, wind_speed_min REAL, station INTEGER, FOREIGN KEY(station) references station(id));", verbose=verbose)
        return res

    def _executer_sql(self, sql, verbose=False):
        conn = None
        cur = None
        # Séparation des try / except pour différencier les erreurs
        try:
            conn = self.connecter()
            cur = conn.cursor()
            if verbose > 1:
                print("SQLite DAO > Base de données crée et correctement connectée à SQLite")
            try:
                if verbose:
                    print("SQLite DAO >", sql, end="")
                cur.execute(sql)
                conn.commit()
                if "INSERT" in sql:
                    res = cur.lastrowid
                    self._nb_enregistrement += 1
                    if self.frequence_backup > 0 and self._nb_enregistrement >= self.frequence_backup :
                        if self.backup_path is not None:
                            if self.creer_sauvegarde(self.backup_path, verbose):
                                self._nb_enregistrement = 0
                        else:
                            print("Impossible de sauvegarder, backup_path vide")
                else:
                    res = cur.fetchall()
                if verbose:
                    print(" =>",res)
            except sqlite3.Error as error:
                print("SQLite > Erreur exécution SQL", error)
                raise error
        except sqlite3.Error as error:
            print("SQLite > Erreur de connexion à la BDD", error)
            raise error
        finally:
            try:
                if verbose > 1:
                    print("SQLite > Le curseur est fermé")
                cur.close()
            except Exception:
                pass
            try:
                if verbose > 1:
                    print("SQLite > La connexion est fermée")
                conn.close()
            except Exception:
                pass       
        return res
        

if __name__ == "__main__":

    verbose = 1
    # Récupère le répertoire du programme
    curent_path = getcwd()+ "\\simplon\\projets\\projet_sql\\"
    print(curent_path)

    ma_dao = PiouPiouDao(curent_path+'my_piou_piou_raoul_aurelie.db')
    assert ma_dao.test_connexion(verbose=verbose)
    # Création avec une BDD vide
    assert ma_dao.initialiser_bdd(verbose=verbose)
    res = ma_dao.liste_tables(verbose=verbose)
    print("liste des tables:",res)
    assert res is not None
    res = ma_dao.stations(verbose=verbose)
    print(res)
    assert res is not None
    res = ma_dao.mesures(verbose=verbose)
    print(res)
    assert res is not None

    assert ma_dao.creer_sauvegarde(curent_path+"my_piou_sauvegarde.db", verbose=verbose)

    # suppression du fichier s'il existe déjà (sinon les tests seront failed)
    bdd_test_path = curent_path+'bdd_test_to_remove.db'
    try:
        if path.exists(bdd_test_path):
            remove(bdd_test_path)
    except OSError as e:
        print(e)
    
    ma_dao2 = PiouPiouDao(bdd_test_path)
    assert ma_dao2.test_connexion(verbose=verbose)
    res = ma_dao2.liste_tables(verbose=verbose)
    print("liste des tables:",res)
    assert res is None or len(res) ==0
    
    # Création avec une BDD vide
    assert ma_dao2.initialiser_bdd(verbose=verbose)
    res = ma_dao2.liste_tables(verbose=verbose)
    print("liste des tables:",res)
    assert res is not None and len(res)>1

    # Création alors que les tables existent déjà
    assert ma_dao2.initialiser_bdd(verbose=verbose)
    res = ma_dao2.liste_tables(verbose=verbose)
    print("liste des tables:",res)
    assert res is not None and len(res)>1

    # Création avec suppression en premier
    assert ma_dao2.initialiser_bdd(verbose=verbose)
    res = ma_dao2.liste_tables(verbose=verbose)
    print("liste des tables:",res)
    assert res is not None and len(res)>1

    res = ma_dao2.nombre_stations(verbose=verbose)
    print("Nombre de stations :",res)
    assert res == 0

    list_stations = test_station_mesure_constructeur(verbose=verbose)

    res = ma_dao2.ajouter_station(list_stations[334], verbose=verbose)
    print("Id de la station ajoutée :",res)
    assert res == 334

    res = ma_dao2.ajouter_station(list(list_stations.values()), verbose=verbose)
    print("Max station added :",max(res))
    assert max(res) == 194
    assert len(res) == 2

    stations = ma_dao2.stations(verbose=verbose)
    print("Stations:",res)
    assert len(stations) == 3

    mesures = ma_dao2.mesures(verbose=verbose)
    print("Mesures:",res)
    assert len(mesures) == 0

    mesures_list = []
    # Tester l'ajout de mesure
    for s in list(list_stations.values()) :
        res = ma_dao2.ajouter_mesure(s.mesures, verbose=verbose)
        mesures_list.extend(s.mesures)
    
    nb_mesures = ma_dao2.nombre_mesures(verbose=verbose)
    # Tester la suppression des mesures les plus anciennes
    i = 0.5
    while nb_mesures < 10:
        for m in mesures_list:
            m2 = Mesure(m.date, m.wind_heading+i, m.wind_speed_avg+i, m.wind_speed_max+i, m.wind_speed_min+i, m.station)
            res = ma_dao2.ajouter_mesure(m2, verbose=verbose)
        i += .5
        nb_mesures = ma_dao2.nombre_mesures(verbose=verbose)
    


  
