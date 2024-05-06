import argparse
import requests
from bs4 import BeautifulSoup
from PIL import Image
import os
import json
from concurrent.futures import ThreadPoolExecutor
import PyPDF2

# Constants for file paths
IMAGE_DIR = 'images/'
if not os.path.exists(IMAGE_DIR):
    os.makedirs(IMAGE_DIR)

# Obtener URLs de productos
def lister(base_url):
    product_urls = []
    page_number = 1
    while True:
        url = f"{base_url}?page={page_number}"
        response = requests.get(url)
        if response.status_code != 200:
            break
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.select('table.loop-product-table a.woocommerce-LoopProduct-link')
        if not links:
            break
        product_urls.extend(link['href'] for link in links)
        page_number += 1
    return product_urls

# Obtener datos de un producto desde el enlace
def crawler(product_url):
    try:
        response = requests.get(product_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        product = {
            "id": soup.find('span', class_='sku').text.strip(),
            "name": soup.find('h1', class_='product-title').text.strip(),
            "CAS": soup.find('div', class_='product-prop', text=lambda x: 'CAS number:' in x).text.split(': ')[1].strip(),
            "structure": soup.find('span', class_='prop-label', text='Molecular formula:').find_next_sibling('span').text.strip(),
            "smiles": soup.find('span', class_='prop-label', text='Smiles:').find_next_sibling('span').text.strip(),
            "description": soup.find('div', class_='product-description').text.strip(),
            "molecular_weight": soup.find('span', class_='prop-label', text='Molecular weight:').find_next_sibling('span').text.strip(),
            "url": product_url,
            "image_path": download_and_convert_image(soup.find('img')['src']),
            "img": soup.find('img')['src']
        }

        # Opcional: Parse PDF
        pdf_link = soup.find('a', text='MSDS')
        if pdf_link:
            product["pdf_msds"] = pdf_link['href']
            product["un_number"] = extract_un_number(pdf_link['href'])

        return product
    except Exception as e:
        return {"error": str(e), "url": product_url}

# Descargar imagen
def download_and_convert_image(image_url):
    response = requests.get(image_url, stream=True)
    file_name = f"{IMAGE_DIR}{image_url.split('/')[-1].split('.')[0]}.png"
    if response.status_code == 200:
        with open(file_name, 'wb') as out_file:
            out_file.write(response.content)
        img = Image.open(file_name)
        img.thumbnail((128, 128))
        img.save(file_name, "PNG")
    return file_name

# Extraer el PDF
def extract_un_number(pdf_url):
    response = requests.get(pdf_url, stream=True)
    with open('temp.pdf', 'wb') as f:
        f.write(response.content)
    with open('temp.pdf', 'rb') as f:
        reader = PyPDF2.PdfFileReader(f)
        for page in range(reader.numPages):
            content = reader.getPage(page).extractText()
            if 'UN Number' in content:
                return content.split('UN Number: ')[1].split()[0]
    return "Not available"

# Funcion Main
def main(base_url, num_crawlers):
    urls = lister(base_url)
    with ThreadPoolExecutor(max_workers=num_crawlers) as executor:
        results = list(executor.map(crawler, urls))
    with open('product_data.json', 'w') as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Web crawler for product data.")
    parser.add_argument("base_url", help="Base URL for the product pages.")
    parser.add_argument("-c", "--crawlers", type=int, default=1, help="Number of concurrent crawlers.")
    args = parser.parse_args()
    main(args.base_url, args.crawlers)
