import csv
import sys
import requests
from time import sleep
from bs4 import BeautifulSoup
from urllib.parse import urljoin

tempo = 0.5
urlBase = "https://www.pai.pt"

miDoc = requests.get(urlBase)
docFinal = BeautifulSoup(miDoc.text, "html.parser")


def getLink(html):
    for tipo in html.select(".grid-container .categories-list .category-item"):
        link = urljoin(urlBase, tipo.select_one("a").attrs["href"])
        yield link


def getLink2(enlace1):

    sleep(tempo)
    enlace = requests.get(enlace1)

    docFinalEnlace = BeautifulSoup(enlace.text, "html.parser")

    for tipo in docFinalEnlace.select(".card-section .card-title"):
        try:
            enlace2 = urljoin(urlBase, tipo.select_one("a").attrs["href"])

            yield enlace2

        except AttributeError:
            siguiente_pag = docFinalEnlace.find("ul", class_="pagination")

            a_siguiente = siguiente_pag.find("a").attrs["href"]

            nuevo_enlace = urljoin(urlBase, a_siguiente)

            yield from getLink2(nuevo_enlace)
        

def getNombre(enlace2):
    sleep(tempo)
    enlace = requests.get(enlace2)
    docFinalEnlace = BeautifulSoup(enlace.text, "html.parser")
    try:

        div = docFinalEnlace.find("div", class_="listing-business")
        nombre = div.find("h1")
        return nombre.get_text()
    
    except AttributeError:
        return ""


def getEmail(enlace2):
    sleep(tempo)
    enlace = requests.get(enlace2)
    docFinalEnlace = BeautifulSoup(enlace.text, "html.parser")
    try:

        lista_li = docFinalEnlace.find_all("li", class_="listing-item")
        mail = lista_li[2].find("a")
        return mail.text
    
    except IndexError:
        return ""


mails = {}
enlaces1 = getLink(docFinal)

MAX_MAILS = 9999
MAX_FAMILIA = 20
contador_mails = 0


# contador_mails = 0
for i in enlaces1:
    contador_familia = 0
    #cuenta el número total de mails que guardará el script
    if contador_mails >= MAX_MAILS:
        break

    print("familia: ", i, "i")
    print()

    enlaces2 = getLink2(i)

    for j in enlaces2:
        sleep(2)
        if contador_mails >= MAX_MAILS or contador_familia >= MAX_FAMILIA:
            break

        print("     enlace: ", j, "j")
        nombre = getNombre(j)
        email = getEmail(j)

        mails[nombre] = email

        print("     nombre: ", nombre, "email: ", email)
        print("     mails: ", contador_mails+1)
        print()
        contador_familia += 1
        contador_mails += 1

print(mails)

archivo_csv = "mails.csv"

# Abrir el archivo CSV en modo escritura
with open(archivo_csv, "w", newline="", encoding="utf-8") as archivo:
    # Crear el escritor CSV
    writer = csv.writer(archivo, delimiter=";")

    # Escribir los pares clave-valor en el archivo CSV
    for clave, valor in mails.items():
        writer.writerow([clave, valor])

print("Los datos se han almacenado en el archivo '{archivo_csv}'")
