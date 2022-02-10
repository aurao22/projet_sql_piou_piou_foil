import requests

stations_id = []

url = "http://api.pioupiou.fr/v1/live/all"

reponse = requests.get(url)
print(reponse)
print("----------------------------------------------------------------------------")
contenu_txt = reponse.text
print(type(contenu_txt))
print("----------------------------------------------------------------------------")

contenu = reponse.json()
print(type(contenu))
print("----------------------------------------------------------------------------")
print(contenu)