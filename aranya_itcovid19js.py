from requests_html import HTMLSession
import re
import datetime as dt

sesion = HTMLSession()

url = ('http://www.salute.gov.it/portale/nuovocoronavirus/' +
       'homeNuovoCoronavirus.jsp?lingua=english')
r = sesion.get(url)
r.html.render(sleep=1, keep_page=True)
# print(r.html.html)


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


# Obtenemos fecha y hora de actualización
css_fechayh = '#datiItalia > div.col-lg-8.col-md-8.col-sm-12 > h3'
fechayh = r.html.find(css_fechayh, first=True).text
fecha_act = fecha_y_hora_parser(fechayh[:-5], fechayh[-5:], lg='en')
# Obtenemos cifras
css_cas_tot = '#datiItalia > div:nth-child(4) > div:nth-child(2)'
casos_totales = r.html.find(css_cas_tot, first=True).text
css_fall = '#datiItalia > div:nth-child(5) > div:nth-child(2)'
defunciones = r.html.find(css_fall, first=True).text
css_cur = '#datiItalia > div:nth-child(6) > div:nth-child(2)'
recuperados = r.html.find(css_cur, first=True).text
dicc = {'Italia': [casos_totales, None, None, recuperados,
                   defunciones, fecha_act]}

print(dicc)
r.close()
