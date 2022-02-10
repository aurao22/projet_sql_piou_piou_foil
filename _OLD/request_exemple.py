import requests

url = "http://my-json-server.typicode.com/rtavenar/fake_api/tasks"

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