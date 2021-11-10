# -*- coding: utf-8 -*-
import os.path #Este modulo nos permite gestionar diferentes opciones relativas al sistema de ficheros como pueden ser ficheros, directorios, etc.
import pickle
import json
import random
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import opciones as op
import streamlit as st
from datetime import date
from shutil import copyfile
from datosConexion import conectarBd
from exceptions import InputError
from clases import Paper
from mongoengine import Q

def mostrarPantallaSeleccionEstudios(user): #FALTAN CONDICIONES DE REFERENCIAS Y LOADBEFORE
    if user != "Seleccionar..." and user is not None:
        conectarBd()
        if st.checkbox("Ver avance"):
            mostrarAvance(True)
        if os.path.exists("inclusion"):
            try:
                with open('inclusion', 'r') as fp:
                    paper_dict = json.loads(json.load(fp))
                    paper = Paper.objects.get(doi=paper_dict["_id"])
                    if paper.inclusion1 is None: number = 1
                    else:
                        if paper.user_inclusion1 == user or paper.inclusion2 is not None:
                            os.remove("inclusion")
                            paper, number = elegirPaper(user)
                        with open('inclusion', 'w') as fp:
                            json.dump(paper.to_json(), fp)
                        number=2
            except: #el archivo inclusion está corrupto y se debe eliminar 
                os.remove("inclusion")
                paper = None
        else:
            paper, number = elegirPaper(user)
            if paper is not None:
                with open('inclusion', 'w') as fp:
                    json.dump(paper.to_json(), fp)
        if paper is None:
            st.error("No existen más papers en la base de datos que usted pueda verificar sin introducir un sesgo en el review.")
        else:
            show_warning = False
            if paper.on_revision is not None: st.success("Este paper fue recuperado de una sesión incompleta anterior.") #muestra mensaje de exito
            else:
                show_warning = True
                paper.on_revision = user
                paper.save()
            st.write("Lea el título y abstract del siguiente artículo y marque si cumple alguna de las siguientes condiciones.")
            if paper.title is not None: 
                st.markdown("#### Título") 
                st.write(paper.title)
            if paper.abstract is not None: 
                st.markdown("#### Abstract") 
                st.write(paper.abstract)
            if paper.doi is not None: 
                st.markdown("#### Doi")
                st.markdown("["+paper.doi+"](https://doi.org/"+paper.doi+")")
            if st.button("Cambiar paper"):
                del paper.on_revision
                paper.save()
                os.remove("inclusion")
            st.markdown("#### Criterios")
            col1, col2 = st.beta_columns(2) 
            with col1: 
                st.markdown("##### Inclusión")
                ci1 = st.checkbox("1. El estudio NO utiliza algún proceso de extracción de información automatizado sobre imágenes de cualquier región del espectro electromagnético en alguna de sus etapas.")
                ci2 = st.checkbox("2. El estudio NO se enfoca en la medición de variables visuales de interés vitícola. Entendemos por esto a toda información necesaria para la toma de decisiones agronómica que se manifiesta de forma visual en alguna parte de la planta de vid.")
            with col2: 
                st.markdown("##### Exclusión")
                ce1 = st.checkbox("1.  El estudio utiliza como entrada imágenes satelitales.")
                ce2 = st.checkbox("2.  El algoritmo opera sobre información electromagnética que NO viene en forma de imagen (entiéndase representación visual bidimensional a partir de una matriz numérica).")
                ce3 = st.checkbox("3.  El paper está orientado a automatismo de la gestión, NO a medición de variables.")
                ce4 = st.checkbox("4.  El estudio NO está escrito en Inglés.")
                ce5 = st.checkbox("5.  La publicación del estudio NO se sometió a un proceso de revisión por pares.")
            st.markdown("#### Comentarios") 
            comments = st.text_area("En el caso de que tenga alguna duda con la decisión qué tomó, vuelquela en el siguiente apartado para que sea tenida en cuenta en la próxima reunión. (Si no hay texto se asume que se ha tomado la decision con plena confidencia)") #text area para colocar el comentario
            guardar = st.button("Guardar") 
            if show_warning: 
                st.warning("El paper a revisar ha cambiado. \n"+  "Desplácese hacia arriba para analizar su contenido. \n"+ 
                           "Asegúrese de no presionar el botón 'Guardar' hasta modificar los checkboxes de acuerdo a su revisión.") 
            if guardar: 
                del paper.on_revision
                if ci1 or ci2 or ce1 or ce2 or ce3 or ce4 or ce5:
                    criteria =[]
                    if ci1 : criteria.append("CI1")
                    if ci2 : criteria.append("CI2")
                    if ce1 : criteria.append("CE1")
                    if ce2 : criteria.append("CE2")
                    if ce3 : criteria.append("CE3")
                    if ce4 : criteria.append("CE4")
                    if ce5 : criteria.append("CE5")
                    if number == 1:
                        paper.inclusion1 = False
                        paper.user_inclusion1 = user
                        paper.criteria_inclusion1 = criteria
                        if comments is not None: paper.comments1 = comments
                    if number == 2:
                        paper.inclusion2 = False
                        paper.user_inclusion2 = user
                        paper.criteria_inclusion2 = criteria
                        if comments is not None: paper.comments2 = comments
                    mess = "Se ha guardado su decisión de excluir el artículo "+ paper.title+" ya que hay conflictos con los siguientes criterios: "
                    for cr in criteria:
                        mess = mess + "\n " + cr
                    st.success(mess)
                else: 
                    if number == 1:
                        paper.inclusion1 = True
                        paper.user_inclusion1 = user
                        if comments is not None: paper.comments1 = comments
                    if number == 2:
                        paper.inclusion2 = True
                        paper.user_inclusion2 = user
                        if comments is not None: paper.comments2 = comments
                    st.success("Se ha guardado su decisión de incluir el artículo "+ paper.title)
                paper.save()
                if st.button("Revisar otro paper"):
                    del paper.on_revision
                    paper.save()
                    os.remove("inclusion")
                st.json(paper.to_json())
#@st.cache(allow_output_mutation=True)
def elegirPaper(user):
    papers = list(Paper.objects(on_revision=user))
    if papers:
        paper = random.choice(papers) #permite elegir un elementos de una lista (en este caso la lista de papers)
        if paper.inclusion1 is None: number = 1
        else: number=2
        #print("opcion1")
        return paper,number
    papers = list(Paper.objects(Q(inclusion2__exists=False) & Q(user_inclusion1__ne=user) & Q(on_revision__exists=False) & (Q(isOnlyReference=False)| Q(isOnlyReference__exists=False))))
    if papers:
        paper = random.choice(papers)
        if paper.inclusion1 is None: number = 1
        else: number=2
        #print("opcion2")
        return paper,number
    else:
        return None,None
        
def mostrarAvance(users_distribution):
    opciones = op.opciones.copy()
    users = list(opciones["users"])
    revisions = {}
    for user in users:
        revisions[user] = 0
    cantidadRevisiones = 0
    cantidadRevisados = 0
    cantidadSinRevisar = 0
    incluidos = 0
    conflictos = 0
    soloUnaSeleccion = 0
    excluidos = 0
    for paper in Paper.objects(Q(isOnlyReference=False) | Q(isOnlyReference__exists=False)):
        isOnlyReference = False #por las dudas que quede algun paper cargado desde antes de que exista este atributo
        cantidadRevisiones += 2
        if paper.inclusion1 is not None:
            revisions[paper.user_inclusion1] += 1
            cantidadRevisados += 1
            if paper.inclusion2 is not None:
                if paper.user_inclusion2==paper.user_inclusion1:
                    del paper.inclusion2
                    del paper.user_inclusion2
                    del paper.criteria_inclusion2
                    del paper.comments2
                    soloUnaSeleccion += 1
                    paper.save()
                else:
                    revisions[paper.user_inclusion2] += 1
                    cantidadRevisados += 1
                    if paper.inclusion1 and paper.inclusion2: incluidos += 1
                    if not paper.inclusion1 and not paper.inclusion2: excluidos += 1
                    if paper.inclusion1 != paper.inclusion2: conflictos += 1
            else: soloUnaSeleccion += 1
        else: cantidadSinRevisar += 1

    progress = cantidadRevisados/cantidadRevisiones
    finish = st.progress(progress)
    st.write("Progreso: "+str(cantidadRevisados)+"/"+str(cantidadRevisiones)+"="+str(round(progress*100,2))+"%")
    st.write("Sin Revisar: "+str(cantidadSinRevisar))
    if users_distribution:
        st.set_option('deprecation.showPyplotGlobalUse', False)
        y = np.arange(len(users))
        plt.barh(y,width=list(revisions.values()))
        plt.yticks(y,list(revisions.keys()))
        plt.xticks(list(revisions.values()))
        st.pyplot(plt.show())

    if st.checkbox("Ver Resultados Preliminares"):
        st.set_option('deprecation.showPyplotGlobalUse', False)
        eje_x = ['Incluidos', 'Excluidos', 'Conflictos' , 'En Revisión']
        eje_y = [incluidos, excluidos, conflictos, soloUnaSeleccion]
        plt.bar(eje_x, eje_y)
        plt.yticks(eje_y)
        st.pyplot(plt.show())
        if st.button("Ver conflictos"):
            dataConflictos = []
            for paper in Paper.objects(Q(inclusion1=True) & Q(inclusion2=False)):
                    dataConflictos.append([paper.doi, paper.user_inclusion1, paper.inclusion1, paper.user_inclusion2, paper.inclusion2])
            for paper in Paper.objects(Q(inclusion1=False) & Q(inclusion2=True)):
                    dataConflictos.append([paper.doi, paper.user_inclusion1, paper.inclusion1, paper.user_inclusion2, paper.inclusion2])
            conflictosDF = pd.DataFrame(data=dataConflictos,
                columns=("doi", "Revisor 1", "Veredicto 1","Revisor 2", "Veredicto 2"))
            st.dataframe(conflictosDF)
        if st.button("Ver incluidos"):
            dataIncluidos = []
            for paper in Paper.objects(Q(inclusion1=True) & Q(inclusion2=True)):
                    dataIncluidos.append([paper.doi, paper.title, paper.user_inclusion1, paper.user_inclusion2])
            incluidosDF = pd.DataFrame(data=dataIncluidos,
                columns=("doi", "Título", "Revisor 1","Revisor 2"))
            st.dataframe(incluidosDF)

    




