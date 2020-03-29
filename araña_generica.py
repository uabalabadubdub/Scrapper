'''Scrapper para PRA1 de TyCv Datos - 27/03/2020
Fotocasa'''
from requests_html import HTMLSession
from pprint import pprint
from requests import status_codes
import datetime as dt
import re
import pandas as pd
import os
from time import sleep


class Scrapper(HTMLSession):
    '''Una araña genérica para rascar información de una web usando
    requests-html'''

    def __init__(self, url):
        self.sesion = HTMLSession()
        self.url = url
        self.respuesta = self.sesion.get(self.url)
        if self.respuesta.status_code != 200:
            print('La llamada ha fallado')
            print(status_codes._codes[self.respuesta.status_code])
        else:
            print(self.respuesta)

    def contenido(self):
        '''Devuelve el contenido en html del cuerpo de la respuesta'''
        return self.respuesta.html.html

    def parse(self, parser):
        '''Aplica una función parser a la respuesta y devuelve el resultado'''
        return parser(self.respuesta)

    def cerrar(self):
        '''método para cerrar la conexion y la sesión'''
        self.respuesta.close()
        self.sesion.close()

    def render(self, **options):
        '''Si la página es dinámica (contiene scripts de js), llamar a render
        tras la primera carga sirve para ejecutar los scripts'''
        self.respuesta.html.render()


# Debug Scrapper ############################################################
url = ('http://www.salute.gov.it/portale/nuovocoronavirus/' +
       'dettaglioContenutiNuovoCoronavirus.jsp?' +
       'lingua=english&id=5367&absarea=nuovoCoronavirus&' +
       'menu=vuoto')
url2 = 'https://covid19.isciii.es/'
aranya_test = Scrapper(url)
aranya_test.render(sleep=8, keep_page=True)
pprint(aranya_test.contenido())
# fin debug Scrapper ########################################################


def Aranya_covid19():
    '''
    Función que incluye urls, parsers para cada url, una función para obtener
    fecha y hora en python de etiquetas de texto, una función para formatear
    los resultados a csv y un bucle para realizar llamadas de forma secuencial
    '''
    # Urls
    urls = {'url_mses': 'https://covid19.isciii.es/',
            'url_msit': ('http://www.salute.gov.it/portale/nuovocoronavirus/' +
                         'dettaglioContenutiNuovoCoronavirus.jsp?' +
                         'lingua=english&id=5367&absarea=nuovoCoronavirus&' +
                         'menu=vuoto')}

    def fecha_y_hora_parser(fecha, hora, lg='es'):
        '''
        Dada dos cadenas de texto fecha, hora y un indicador de idioma,
        devuelve la fecha y hora en un objeto datetime de python.
        - fecha: cadena de texto que incluya la fecha con día numérico de dos
                 cifras, mes cómo nombre en texto completo y año cómo número
        - hora:  cadena de texto con hora cómo dos numeros y minuto cómo dos
                 numeros separados por dos puntos
        - lg:    cadena de texto que sigue formato iso de idiomas indicadora
                 del idioma en que esta escrito el mes (sólo se acepta es y en)
        '''
        # Diccionarios de meses (es y en)
        meses_es = {"enero": 1, "febrero": 2, "marzo": 3,
                    "abril": 4, "mayo": 5, "junio": 6,
                    "julio": 7, "agosto": 8, "septiembre": 9,
                    "octubre": 10, "noviembre": 11, "diciembre": 12}
        meses_en = {"january": 1, "february": 2, "march": 3,
                    "april": 4, "may": 5, "june": 6,
                    "july": 7, "august": 8, "september": 9,
                    "october": 10, "november": 11, "december": 12}
        # Validación de idioma
        if lg == 'es':
            meses = meses_es
        elif lg == 'en':
            meses = meses_en
        else:
            return print('Lengua no sorportada')
        # Usamos re para trocear las etiquetas en los valores que nos interesan
        re_dia = r"[0-9]{2}"
        re_mes = r"[0-9]{2} ([a-zA-Z]+) [0-9]{4}"
        re_año = r"[0-9]{4}"
        fecha_dia = re.findall(re_dia, fecha)[0]
        fecha_mes = re.findall(re_mes, fecha)[0]
        fecha_año = re.findall(re_año, fecha)[0]
        hh = re.findall(re_dia, hora)[0]
        minuto = re.findall(re_dia, hora)[1]
        # Generamos una variable con la fecha en un formato de python
        fecha_act = dt.datetime(int(fecha_año), meses[fecha_mes.lower()],
                                int(fecha_dia), int(hh), int(minuto))
        return fecha_act

    # Parsers
    def msit_parser(respuesta):
        # Obtenemos fecha y hora de actualización
        css_fechayh = 'h4.blu-italia-base-color'
        fechayh = respuesta.html.find(css_fechayh, first=True).text
        fecha_act = fecha_y_hora_parser(fechayh[:-5], fechayh[-5:], lg='en')
        # Obtenemos cifras
        css_cas_tot = 'div.col-lg-4:nth-child(7) > div:nth-child(2)'
        casos_totales = respuesta.html.find(css_cas_tot, first=True).text
        css_fall = 'div.col-lg-4:nth-child(7) > div:nth-child(2)'
        defunciones = respuesta.html.find(css_fall, first=True).text
        css_cur = 'div.col-lg-4:nth-child(7) > div:nth-child(2)'
        recuperados = respuesta.html.find(css_cur, first=True).text
        return {'Italia': [casos_totales, None, None, recuperados,
                           defunciones, fecha_act]}

    def mses_parser(respuesta):
        # Sacamos la fecha y hora de actualización de los datos
        fecha = respuesta.html.find('#fecha', first=True).text
        hora = respuesta.html.find('#hora', first=True).text
        fecha_act = fecha_y_hora_parser(fecha, hora, lg='es')
        # Obtenemos los valores totales para España
        casos_totales = respuesta.html.find('#casos', first=True).text
        casos_24h = respuesta.html.find('#casos24h', first=True).text
        recuperados = respuesta.html.find('#recuperados', first=True).text
        defunciones = respuesta.html.find('#defunciones', first=True).text
        # Recogemos los datos de la tabla de CCAA
        a_list = [td.text for td in respuesta.html.find("td")]
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
                dict_ccaa[clave] = [valor1, valor2, valor3, None, None,
                                    fecha_act]
                contador = 0
        # Añadimos los totales para España
        dict_ccaa['España'] = [casos_totales, casos_24h, None, recuperados,
                               defunciones, fecha_act]
        return dict_ccaa

    def formatear(diccionario, fecha):
        # Cargamos todos los datos en un dataframe de pandas
        df_act = pd.DataFrame(diccionario.values(), index=diccionario.keys(),
                              columns=['Casos', 'Ult.24h', 'Inc.14d',
                                       'Recup', 'Fallec', 'Fecha_act']
                              )
        archivo = "covid19_{}.csv".format(dt.datetime.strftime(fecha,
                                                               format="%Y%m%d")
                                          )
        # Debug
        print(df_act)
        # Creamos un csv con los datos
        print('El archivo se guardará en la siguiente dirección:', os.getcwd())
        df_act.to_csv(archivo)

    dicc = {}
    for clave, url in urls.items():
        aranya = Scrapper(url)
        # Debug
        print(aranya.contenido())
        sleep(2)
        aranya.render()
        if clave == 'url_mses':
            dicc_t = aranya.parse(mses_parser)
        elif clave == 'url_msit':
            dicc_t = aranya.parse(msit_parser)
        dicc = {**dicc, **dicc_t}
        aranya.cerrar()
    formatear(dicc, dt.datetime.today())


Aranya_covid19()
