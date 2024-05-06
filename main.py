import argparse
import json
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import os


# Obtener URLs de productos
def get_product_urls(base_url):
    product_urls = []
    page_number = 1
    while True:
        url = f"{base_url}?page={page_number}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', class_='loop-product-table')
        if not table:
            break
        rows = table.find_all('tr')
        for row in rows:
            link = row.find('a', class_='woocommerce-LoopProduct-link')
            if link:
                product_urls.append(link['href'])
        page_number += 1
    return product_urls


# Obtener datos de un producto
def get_product_data(product_url):
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Encontrar el div que contiene la información del producto
    product_div = soup.find('div', class_='product')

    # Extraer los datos del producto
    product_title = product_div.find('h1', class_='product-title').text.strip()
    product_id = product_div.find('span', class_='sku').text.strip()
    cas_number = product_div.find('div', class_='product-prop').text.strip().split(': ')[1]
    molecular_formula = product_div.find('span', class_='prop-label', text='Molecular formula:').find_next_sibling('span').text.strip()
    molecular_weight = product_div.find('span', class_='prop-label', text='Molecular weight:').find_next_sibling('span').text.strip()
    smiles = product_div.find('span', class_='prop-label', text='Smiles:').find_next_sibling('span').text.strip()

    # Obtener la URL de la imagen
    structure_div = product_div.find('div', class_='prod-structure')
    image_url = structure_div.find('img')['src']

    # Crear un diccionario con los datos del producto
    product_data = {
        "title": product_title,
        "id": product_id,
        "cas_number": cas_number,
        "molecular_formula": molecular_formula,
        "molecular_weight": molecular_weight,
        "smiles": smiles,
        "image_url": image_url
    }

    return product_data


# Función para procesar un producto y guardar la imagen
def process_product(product_url):
    product_data = get_product_data(product_url)
    # Aquí puedes agregar el código para procesar la imagen y guardarla
    return product_data


# Función para manejar múltiples crawlers de forma paralela
def run_crawlers(product_urls, num_crawlers):
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_crawlers) as executor:
        results = list(executor.map(process_product, product_urls))
    return results

def main(base_url, num_crawlers):
    # Obtener URLs de productos
    product_urls = get_product_urls(base_url)
    
    # Lanzar crawlers
    product_data = run_crawlers(product_urls, num_crawlers)
    
    # Escribir resultado en un archivo JSON
    with open('product_data.json', 'w') as outfile:
        json.dump(product_data, outfile, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("base_url", help="URL base de la página de productos")
    parser.add_argument("-c", "--crawlers", type=int, default=1, help="Número de crawlers a ejecutar simultáneamente")
    args = parser.parse_args()

    main(args.base_url, args.crawlers)
