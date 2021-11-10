from scraping import get_citations
import streamlit as st
import pandas as pd
import os.path
import pickle
import json
from mongoengine import Q
from datetime import date
from shutil import copyfile
from datosConexion import conectarBd
from exceptions import InputError
from clases import Paper,Author,Author_Affiliation,Institution,Finantial_Institution
import crossref_commons.retrieval
from crossref_commons.retrieval import get_entity
from crossref_commons.types import EntityType, OutputType
from crossref_commons.iteration import iterate_publications_as_json

def obtenerCitaciones():
    conectarBd()
    papers = Paper.objects(Q(inclusion1=True) & Q(inclusion2=True) & Q(citationsSearched__exists=False))
    count_papers = len(papers)
    if count_papers > 0:
        st.success("Se encontraron disponibles " + str(count_papers) + " papers de los cuales obtener citaciones.")
        st.markdown("## ¿Desea buscar las citaciones ahora?")
        buscar = st.button("Buscar")
        if buscar:
            st.error("Este módulo aún se encuentra en desarrollo.")
            # all_dois = set()
            # cont = len(papers)
            # #for paper in papers:
            # dois = get_citations(papers)
            # st.success("Se encontraron "+str(len(dois))+" páginas de citaciones")
            # #st.markdown(all_dois)
            # #Dar posibilidad de descargar la lista en un archivo.
    else:
        st.error("No hay papers disponibles para buscar citaciones.")