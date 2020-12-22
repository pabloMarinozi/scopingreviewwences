# -*- coding: utf-8 -*-
import os.path
import pickle
import json
import random
import matplotlib.pyplot as plt
import numpy as np
import opciones as op
import streamlit as st
from datetime import date
from shutil import copyfile
from mongoengine import disconnect,connect,Q
from exceptions import InputError
from clases import Paper

def mostrarPantallaSeleccionEstudios(user):
    if user != "Seleccionar..." and user is not None:
        disconnect()
        
        connect('scopingReview',host="mongodb+srv://admin:LccNwXd87QkFzvu@cluster0.w9zqf.mongodb.net/scopingReview?retryWrites=true&w=majority", alias='default')
        st.title('Selección de Estudios')
        if st.checkbox("Ver avance"):
            mostrarAvance(True)
        if os.path.exists("inclusion"):
            with open('inclusion', 'r') as fp:
                paper_dict = json.loads(json.load(fp))
                paper = Paper.objects.get(doi=paper_dict["_id"])
                if paper.inclusion1 is None: number = 1
                else:
                    if paper.user_inclusion1 == user:
                        os.remove("inclusion")
                        paper, number = elegirPaper(user)
                    with open('inclusion', 'w') as fp:
                        json.dump(paper.to_json(), fp)
                    number=2
        else:
            paper, number = elegirPaper(user)
            with open('inclusion', 'w') as fp:
                json.dump(paper.to_json(), fp)
        if paper is not None:
            if paper.on_revision is not None: st.success("Este paper fue recuperado de una sesión incompleta anterior.")   
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
                ci2 = st.checkbox("2. El estudio NO se enfoca en la medición de variables de interés vitícola indistintamente de la ubicación geográfica y el sistema de conducción de los viñedos y del varietal y propósito de comercialización de las uvas.")
            with col2: 
                st.markdown("##### Exclusión")
                ce1 = st.checkbox("1.  El estudio utiliza como entrada imágenes en las que la resolución de un pixel es mayor a un metro.")
                ce2 = st.checkbox("2.  El algoritmo opera sobre información electromagnética que NO viene en forma de imagen (entiéndase representación visual bidimensional a partir de una matriz numérica).")
                ce3 = st.checkbox("3.  El paper está orientado a automatismo de la gestión, NO a medición de variables.")
                ce4 = st.checkbox("4.  El estudio NO está escrito en Inglés.")
                ce5 = st.checkbox("5.  La publicación del estudio NO se sometió a un proceso de revisión por pares.")
            guardar = st.button("Guardar")
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
                    if number == 2:
                        paper.inclusion2 = False
                        paper.user_inclusion2 = user
                        paper.criteria_inclusion2 = criteria
                    mess = "Se ha guardado su decisión de excluir el artículo "+ paper.title+" ya que hay conflictos con los siguientes criterios: "
                    for cr in criteria:
                        mess = mess + "\n " + cr
                    st.success(mess)
                else:    
                    if number == 1:
                        paper.inclusion1 = True
                        paper.user_inclusion1 = user
                    if number == 2:
                        paper.inclusion2 = True
                        paper.user_inclusion2 = user
                    st.success("Se ha guardado su decisión de incluir el artículo "+ paper.title)
                paper.save()
                st.json(paper.to_json())
                if st.button("Revisar otro paper"):
                        os.remove("inclusion")
        else: 
            st.error("No existen más papers en la base de datos que usted pueda verificar sin introducir un sesgo en el review.")
       

#@st.cache(allow_output_mutation=True)                    
def elegirPaper(user):
    papers = list(Paper.objects(on_revision=user))
    if papers:
        paper = random.choice(papers)
        paper = random.choice(papers)
        if paper.inclusion1 is None: number = 1
        else: number=2
        return paper,number
    papers = list(Paper.objects(Q(inclusion2__exists=False) & Q(user_inclusion1__ne=user) & Q(on_revision__exists=False)))
    if papers:
        paper = random.choice(papers)
        if paper.inclusion1 is None: number = 1
        else: number=2
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
    for paper in Paper.objects():
        cantidadRevisiones += 2
        if paper.inclusion1 is not None:
            revisions[paper.user_inclusion1] += 1
            cantidadRevisados += 1
        if paper.inclusion2 is not None:
            revisions[paper.user_inclusion2] += 1
            cantidadRevisados += 1
    progress = cantidadRevisados/cantidadRevisiones
    finish = st.progress(progress)
    st.write("Progreso: "+str(cantidadRevisados)+"/"+str(cantidadRevisiones)+"="+str(round(progress,2))+"%")
    if users_distribution:
        st.set_option('deprecation.showPyplotGlobalUse', False)
        y = np.arange(len(users))
        plt.barh(y,width=list(revisions.values()))
        plt.yticks(y,list(revisions.keys()))
        plt.xticks(range(max(list(revisions.values()))+1))
        st.pyplot(plt.show())
    
    
    
    
            
            
        
    
    
    


    
