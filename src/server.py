# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 13:03:16 2020

@author: pablo
"""

import streamlit as st
import pandas as pd
import numpy as np
import os.path
from PIL import Image
from seleccionEstudios import mostrarPantallaSeleccionEstudios
from curacionBibliografica import automatizarCarga, mostrarPantallaCuracionBibliografica
from extraccionDeDatos import mostrarSeccionExtracción
from cargaInicial import mostrarSeccionCarga
from obtenerCitaciones import obtenerCitaciones
from users import verificarUsuario
#preprocesamiento
# if os.path.exists("affiliations"): os.remove("affiliations")
# if os.path.exists("features"): os.remove("features")
# if os.path.exists("publication"): os.remove("publication")
# if os.path.exists("financement"): os.remove("financement") 

#iu

st.title('Computer Vision in Precission Viticulture: a Scoping Review')
# with col2:
user = verificarUsuario()
        
pantalla = st.sidebar.selectbox(label="Tipo de extracción", options=["Seleccionar...","Selección de Estudios",'Datos Bibliográficos',"Contenido del Paper","Carga de Búsqueda Primaria", "Obtener Citaciones"])


        
if pantalla == "Seleccionar...":
    col1, col2 = st.beta_columns(2)
    with col1:
        image = Image.open('img/example.png')
        st.image(image)
    with col2: 
        image = Image.open('img/dharma.jpg')
        st.image(image)
            
if pantalla == 'Datos Bibliográficos':
    mostrarPantallaCuracionBibliografica()
if pantalla == "Selección de Estudios":
    mostrarPantallaSeleccionEstudios(user)
if pantalla == "Contenido del Paper":
    mostrarSeccionExtracción(user)
if pantalla == "Carga de Búsqueda Primaria":
    mostrarSeccionCarga()
if pantalla == "Obtener Citaciones":
    obtenerCitaciones()











# paper1 = Paper(
#     title = "paper1",
#     doi = "https://www.doi.org",
#     publication_year = 2015).save()

# paper2 = Paper(
#     title = "paper2",
#     doi = "https://www.google.com",
#     publication_year = 2010).save()

# for paper in Author.objects:
#     print(paper.name)
#     print(paper.scopusID)

# =============================================================================
# Paper.drop_collection()
#Author.drop_collection()
# Institution.drop_collection()
# Finantial_Institution.drop_collection()
# =============================================================================
