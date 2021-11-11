# -*- coding: utf-8 -*-
"""
Created on Mon Nov  11 11:05:16 2021

@author: pablo
"""
import os.path
import pickle
import streamlit as st
import opciones as op
from clases import Paper
from datosConexion import conectarBd

def verificarUsuario():
    if os.path.exists("user_selected"):
        user = f = open("user_selected", "r").read()
        st.sidebar.write("Usuario: "+user)
        if st.sidebar.button("Cambiar Usuario"):
            os.remove("user_selected")
        return user
    else:
        if os.path.exists("user_session"):
            with open('user_session', 'rb') as fp:
                opciones = pickle.load(fp)
        else:
            opciones = op.opciones.copy()
            conectarBd()
            with st.spinner("Conectando con la Base de Datos..."):
                for paper in Paper.objects():
                    if paper.user_inclusion1 is not None: 
                        opciones["users"].add(paper.user_inclusion1)
                        if paper.user_inclusion2 is not None: 
                            opciones["users"].add(paper.user_inclusion2)
                with open('user_session', 'wb') as fp:
                    pickle.dump(opciones,fp, protocol=pickle.HIGHEST_PROTOCOL)
        options = list(opciones["users"])
        options.append("Otro")
        options = ["Seleccionar..."] + options
        st.markdown("#### Usuario")
        user = st.selectbox(label="Seleccione su nombre de entre la lista de usuarios. Si usted no se encuentra en la lista elija 'Otro' y carguelo manualmente por única vez.",options=options)
        if user == "Otro":
            user = st.text_input(label="Ingrese un usuario para agregar a la base de datos.")
        if st.button("Guardar Usuario"):
            f = open("user_selected", "w")
            f.write(user)
            f.close()
            os.remove("user_session")
            return user
    