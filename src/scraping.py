from bs4 import BeautifulSoup
import requests
import scholar as sch
import urllib.request
from crossref_commons.retrieval import get_entity
from crossref_commons.types import EntityType, OutputType
from clases import Paper,Author,Author_Affiliation,Institution,Finantial_Institution
from datosConexion import conectarBd
from mongoengine import Q
from crossref_commons.iteration import iterate_publications_as_json
import re

def get_papers():
    conectarBd()
    papers = Paper.objects(Q(inclusion1=True) & Q(inclusion2=True) & Q(citationsWanted__exists=False))
    return papers

def get_scholarlink(phrase):
    link = sch.scholar(phrase[:-1])
    print(link)
    return link

def get_beautifulsoup(url):
    """ Me devuelve un objeto beautiful soup del url que obtiene como parámetro."""

    parser = 'html.parser'  # or 'lxml' (preferred) or 'html5lib', if installed
    resp = requests.get(
            url,
            headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
        })
    soup = BeautifulSoup(resp.text, parser)

    return soup

def set_inclusion():
    conectarBd()
    papers = Paper.objects()[21:50]
    print(len(papers))
    for paper in papers:
        paper.inclusion1 = True
        paper.inclusion2 = True
        paper.citationsWanted = False
        # print(paper.doi)
        paper.save()

def get_pages(url):
    """Obtiene los links de todas las páginas de citaciones dado el link de la primer página."""
    
    #Hace una búsqueda en anchura para encontrar todas las páginas de citas
    print(url)
    seen = set([url])
    active = set([url])
    while active:
        next_active = set()
        for url in active:
            try: page = get_beautifulsoup(url)
            except: continue
            tags = page.find_all('a', class_ = 'gs_nma')
            for tag in tags:
                tag = 'https://scholar.google.com'+tag['href']
                if tag not in seen:
                    seen.add(tag)
                    next_active.add(tag)
        active = next_active

    #Crea un objeto beautifulsoup para cada página
    pages=[]
    print(len(seen),"páginas encontradas")
    textfile = open("urls", "w")
    for url in seen:
        textfile.write(url + "\n")
        try: 
            page = get_beautifulsoup(url)
            pages.append(page)
        except: continue
    textfile.close()
    return pages

def get_links(bs):
    """Navegamos el árbol hasta conseguir todos los links"""
    array = bs.find_all('h3', class_ = 'gs_rt') # gs_or_ggsm
    links = []
    for row in array:
        for a in row.children:
            try:
                links.append(a['href'])
            except:
                pass
    return links


def save_bs(bs):
    """Guardamos la informacion del objeto BeautifulSoup"""
    with open('../output/bs.html', 'w') as f:
        f.write(str(bs))

def get_doi(url):
    result = requests.get(
        url,
        headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.163 Safari/537.36'
    })
    doi = re.findall("10\.\d{3,9}\/[a-zA-Z0-9-._;():/]+", result.text)
    doi_clean = list(set(doi))
    if len(doi_clean):
        print(doi_clean[0])
        return doi_clean[0]
    else:
        print('error')
        return None

def get_citations(paper):
    # phrase = "Early detection of grapevine leafroll disease in a red-berried wine grape cultivar using hyperspectral imaging"
    #set_inclusion()
    pages = get_pages("https://scholar.google.com.ar/scholar?cites=4991506072918913408&as_sdt=2005&sciodt=0,5&hl=es")
    return pages
    # all_dois = set()
    # url = get_scholarlink(paper.title)
    # if not url:
    #     continue 
    # paper.citationsSearched = True
    # pages = get_pages(url)
    # print(pages)
    # for page in pages:
    #     links = get_links(page)
    #     for link in links:
    #         dois = get_doi(link)
    #         paper.citedBy = dois
    #         all_dois.add(dois)
    # return all_dois
