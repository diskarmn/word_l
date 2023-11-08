import requests 

api_key='e74b8091-20e7-49d2-982c-bb8dcbbd7faf'
kata='potato'
url=f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{kata}?key={api_key}'

res=requests.get(url)
definitions=res.json()
print(definitions)
for definition in definitions:
    print(definition)

