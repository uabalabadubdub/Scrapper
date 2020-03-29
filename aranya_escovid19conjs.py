
# para poder ejecutar js usaremos requests-html: pip install requests-html
# se ha de usar una sesión para que se ejecute correctamente el js
from requests_html import HTMLSession
# tanto bs4 cómo requests están incorporados ya en requests_html
# from bs4 import BeautifulSoup
# import requests
import datetime
import pandas as pd
import re
from pprint import pprint
import os

# Página que vamos a rascar
url = 'https://covid19.isciii.es/'

# Abrimos una sesión, de este modo simulamos que somos un navegador:
sesion = HTMLSession()

# Hacemos la llamada
r = sesion.get(url)
# Código de respuesta
print(r)
# Con el método render ejecutamos los scripts de js que tenga la página
r.html.render()

# Sacamos la fecha y hora de actualización de los datos
fecha = r.html.find('#fecha', first=True).text
hora = r.html.find('#hora', first=True).text

# Debug
# print(fecha)
# print(hora)

# Para posar a formato reconocido en python necesitaremos un diccionario
# de meses a valor numérico
meses = {"enero": 1, "febrero": 2, "marzo": 3,
         "abril": 4, "mayo": 5, "junio": 6,
         "julio": 7, "agosto": 8, "septiembre": 9,
         "octubre": 10, "noviembre": 11, "diciembre": 12}

# Usamos re para trocear las etiquetas en los valores que nos interesan
re_dia = r"[0-9]{2}"
re_mes = r"[a-zA-Z]+"
re_año = r"[0-9]{4}"
fecha_dia = re.findall(re_dia, fecha)[0]
fecha_mes = re.findall(re_mes, fecha)[1]
fecha_año = re.findall(re_año, fecha)[0]
hh = re.findall(re_dia, hora)[0]
minuto = re.findall(re_dia, hora)[1]

# Generamos una variable con la fecha en un formato de python
fecha_act = datetime.datetime(int(fecha_año), meses[fecha_mes.lower()],
                              int(fecha_dia), int(hh), int(minuto))
# Debug
print(fecha_act)

# Obtenemos los valores totales para España
casos_totales = r.html.find('#casos', first=True).text
casos_24h = r.html.find('#casos24h', first=True).text
recuperados = r.html.find('#recuperados', first=True).text
defunciones = r.html.find('#defunciones', first=True).text

# Recogemos los datos de la tabla de CCAA
a_list = [td.text for td in r.html.find("td")]

# Debug
# pprint(a_list)

# Los cargamos en un diccionario con clave CCAA
dict_ccaa = dict()
contador = 0
for elemento in a_list:
    if contador == 0:
        clave = elemento
        contador += 1
    elif contador == 1:
        valor1 = elemento
        contador += 1
    elif contador == 2:
        valor2 = elemento
        contador += 1
    elif contador == 3:
        valor3 = elemento
        dict_ccaa[clave] = [valor1, valor2, valor3, None, None, fecha_act]
        contador = 0
# Añadimos los totales para España
dict_ccaa['España'] = [casos_totales, casos_24h, None, recuperados,
                       defunciones, fecha_act]

# Debug
# print(dict_ccaa)

# Cargamos todos los datos en un dataframe de pandas
df_act = pd.DataFrame(dict_ccaa.values(), index=dict_ccaa.keys(), columns=[
                      'Casos', 'Ult.24h', 'Inc.14d',
                      'Recup', 'Fallec', 'Fecha_act'])
archivo = "escovid_{}.csv".format(datetime.datetime.strftime(fecha_act,
                                                             format="%Y%m%d"))
# Debug
print(df_act)

# Creamos un csv con los datos
print(os.getcwd())
df_act.to_csv(archivo)

# Cerramos las conexiones
r.close()
sesion.close()
