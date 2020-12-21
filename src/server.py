# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 13:03:16 2020

@author: pablo
"""

import streamlit as st
import pandas as pd
import numpy as np
import os.path
import clases,curacionBibliografica,extraccionDeDatos,opciones,exceptions
from PIL import Image
import opciones as op
from seleccionEstudios import mostrarPantallaSeleccionEstudios
from curacionBibliografica import mostrarPantallaCuracionBibliografica
from extraccionDeDatos import mostrarSeccionExtracción
from cargaInicial import mostrarSeccionCarga

#preprocesamiento
# if os.path.exists("affiliations"): os.remove("affiliations")
# if os.path.exists("features"): os.remove("features")
# if os.path.exists("publication"): os.remove("publication")
# if os.path.exists("financement"): os.remove("financement") 

#iu

st.title('Computer Vision in Precission Viticulture: a Scoping Review')
# with col2:
if os.path.exists("user_selected"):
    user = f = open("user_selected", "r").read()
    st.sidebar.write("Usuario: "+user)
    if st.sidebar.button("Cambiar Usuario"):
        os.remove("user_selected")
else:
    st.markdown("#### Usuario")
    opciones = op.opciones.copy()
    options = list(opciones["users"])
    options.append("Otro")
    options = ["Seleccionar..."] + options
    user = st.selectbox(label="Seleccione su nombre de entre la lista de usuarios. Si usted no se encuentra en la lista elija 'Otro' y carguelo manualmente por única vez.",options=options)
    if user == "Otro":
        user = st.text_input(label="Ingrese un usuario para agregar a la base de datos.")
    if st.button("Guardar Usuario"):
        f = open("user_selected", "w")
        f.write(user)
        f.close()
        
pantalla = st.sidebar.selectbox(label="Tipo de extracción", options=["Seleccionar...","Selección de Estudios",'Datos Bibliográficos',"Contenido del Paper","Carga de búsqueda primaria"])


        
if pantalla == "Seleccionar...":
    col1, col2 = st.beta_columns(2)
    with col1:
        image = Image.open('img/example.png')
        st.image(image)
    with col2: 
        image = Image.open('img/dharma.jpg')
        st.image(image)
            
if pantalla == 'Datos Bibliográficos':
    mostrarPantallaCuracionBibliografica(user)
if pantalla == "Selección de Estudios":
    mostrarPantallaSeleccionEstudios(user)
if pantalla == "Contenido del Paper":
    mostrarSeccionExtracción(user)
if pantalla == "Carga de búsqueda primaria":
    mostrarSeccionCarga()










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
