import streamlit as st
import json
from io import StringIO  
from pybtex.database import parse_string 
from mongoengine import disconnect,connect
from clases import Paper

def mostrarSeccionCarga():
    disconnect()
    connect('scopingReview',host="mongodb+srv://admin:LccNwXd87QkFzvu@cluster0.w9zqf.mongodb.net/scopingReview?retryWrites=true&w=majority", alias='default')
    uploaded_file = st.file_uploader("Archivo Bibtex con la información de los papers")
    before = len(Paper.objects)
    if uploaded_file is not None:
        # To read file as bytes:
        bytes_data = uploaded_file.read()
        data = bytes_data.decode("utf-8")
        bib_data = parse_string(data, 'bibtex')
        notdoi = []
        papers = []
        with st.spinner("Preprocesando el archivo para la carga..."):
            total = sum(1 for entry in bib_data.entries.values())
        st.success("Se iniciará la carga de "+str(total)+" papers a la base de datos.")
        my_bar = st.progress(.0)
        loaded = 0
        for entry in bib_data.entries.values():
            fields = entry.fields
            title = fields["title"].replace('{', '').replace('}', '')
            doi = fields.get("doi")
            loaded+=1
            my_bar.progress(loaded/total)
            if doi is None: 
                notdoi.append(title)
                continue
            abstract = fields.get("abstract","")
            paper = Paper(title = title, doi = doi , abstract = abstract).save()
            papers.append(paper)
            
        after = len(Paper.objects)
        st.success("Se ingresaron "+ str(after-before) + " papers a la base de datos")
        st.write([x.title for x in papers])
        if len(notdoi):
            st.error ("No se pudo ingresar " + str(len(notdoi)) + " debido a que no se conocía su doi")
            st.write(notdoi)