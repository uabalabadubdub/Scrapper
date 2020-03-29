import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd
import re
from headers import headers

url = 'https://covid19.isciii.es/'

pag = requests.get(url, headers[0], timeout=10)

soup = BeautifulSoup(pag.content, features="lxml")
# print(soup.prettify())

print(soup.find_all("script"))


meses = {"enero": 1, "febrero": 2, "marzo": 3,
         "abril": 4, "mayo": 5, "junio": 6,
         "julio": 7, "agosto": 8, "septiembre": 9,
         "octubre": 10, "noviembre": 11, "diciembre": 12}

fecha_act = soup.find("span", id="fecha").string
print(fecha_act)
hora_act = soup.find("span", id="hora").string
print(hora_act)

re_dia = r"[0-9]{2}"
re_mes = r"[a-zA-Z]+"
re_año = r"[0-9]{4}"
fecha_dia = re.findall(re_dia, fecha_act)[0]
fecha_mes = re.findall(re_mes, fecha_act)[1]
fecha_año = re.findall(re_año, fecha_act)[0]
hora = re.findall(re_dia, hora_act)[0]
minuto = re.findall(re_dia, hora_act)[1]

fecha_act = datetime.datetime(int(fecha_año), meses[fecha_mes.lower()],
                              int(fecha_dia), int(hora), int(minuto))

tabla_CCAA = soup.find("table")

a_list = list(enumerate(td.string for td in tabla_CCAA.find_all("td")))

dict_ccaa = dict()

for elemento in a_list:
    if elemento[0] // 2 == elemento[0] / 2:
        clave = elemento[1]
    else:
        valor = elemento[1]
        dict_ccaa[clave] = valor

print(dict_ccaa)

df_act = pd.DataFrame(dict_ccaa, index=[fecha_act])
archivo = "escovid_{}.csv".format(datetime.strftime(fecha_act,
                                                    format="%Y%m%d"))
df_act.to_csv(archivo)
