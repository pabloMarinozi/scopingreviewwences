import streamlit as st
import pandas as pd
import os.path
import pickle
import json
from datetime import date
from shutil import copyfile
from mongoengine import disconnect,connect
from exceptions import InputError
from clases import Paper,Author,Author_Affiliation,Institution,Finantial_Institution

def mostrarPantallaCuracionBibliografica(user):
    #Buscar respuestas anteriores 
    disconnect()
    connect('scopingReview',host="mongodb+srv://admin:LccNwXd87QkFzvu@cluster0.w9zqf.mongodb.net/scopingReview?retryWrites=true&w=majority", alias='default')
    
    authors_list = []
    intitutions_list = []
    finantial_institutions_list = []
    
    for author in Author.objects:
        authors_list.append(author.name)
    for inst in Institution.objects:
        intitutions_list.append(inst.name)
    for f_inst in Finantial_Institution.objects:
        finantial_institutions_list.append(f_inst.name)
    
    authors_list.append("Otro")
    intitutions_list.append("Otro")
    finantial_institutions_list.append("Otras")
        
    st.markdown('# Curación de datos bibliográficos')
    if not os.path.exists("paper"):
        st.sidebar.write("Complete los datos en las siguientes secciones. Cuando esté satisfecho con los datos ingresados presione enviar.")
        seccion = st.sidebar.radio(label="Secciones", options=["Publicación", "Financiamiento", "Autores"])
        
        if seccion == "Publicación":
            if os.path.exists("publication"):
                st.markdown("#### Ya se han cargado los datos de esta sección")
                with open('publication', 'r') as fp:
                    data = json.load(fp)
                st.json(data)
                if st.button("Eliminar datos cargados"):
                    os.remove("publication")
            else:
                st.markdown("## Publicación")
                st.markdown("#### Título")
                title = st.text_area(label="Título del artículo...")
                st.markdown("#### DOI")
                doi = st.text_input(label="Ingrese el doi del artículo en su formato url. Por ejemplo:https://doi.org/10.1109/CVPR.2016.609")
                st.markdown("#### Keywords")
                keywords = st.text_input(label="Ingrese las keywords separadas por comas")
                st.markdown("#### Fecha de Publicación")
                publication_date = st.date_input(label="Ingrese el mes y el año correspondiente. Se ignorará el día del mes ingresado.", min_value=date(1950, 1, 1),max_value=date.today())
                if st.button("Guardar"):
                    cargarPublicacion(title,doi,keywords,publication_date)
        
        if seccion == "Financiamiento":
            if os.path.exists("financement"):
                st.markdown("#### Ya se han cargado los datos de esta sección")
                finan = pd.read_csv('financement')
                st.dataframe(finan)
                if st.button("Eliminar datos cargados"):
                    os.remove("financement")
            else:
                st.markdown("## Financiamiento")
                finantial_institutions = st.multiselect(label="Seleccione todas las instituciones que financiaron la investigación."+
                                                        "En caso de que alguna no aparezca en las opciones, seleccione 'Otras' e ingreselo manualmente", options = finantial_institutions_list)
                if "Otras" in finantial_institutions:
                    finantial_institutions2 = st.text_area(label="Ingresar una institución por linea con su pais separado por comas."+
                                                           "Por ejemplo: National Council of Scientific and Technical Research (CONICET), Argentina")
                guardar = st.button("Guardar")
                if guardar and not "Otras" in finantial_institutions:  
                   cargarFinanciamiento(finantial_institutions)
                if guardar and "Otras" in finantial_institutions:  
                   cargarFinanciamiento(finantial_institutions,finantial_institutions2)
                    
        if seccion == "Autores":
            if os.path.exists("affiliations_def"):
                st.markdown("#### Ya se han cargado los datos de esta sección")
                aff = pd.read_csv('affiliations_def')
                st.dataframe(aff)
                if st.button("Cargar más datos"):
                    os.remove("affiliations_def")
                if st.button("Eliminar datos cargados"):
                    os.remove("affiliations")
                    os.remove("affiliations_def")
            else:
                st.markdown("## Autores")  
                st.write("En esta sección se ingresarán los autores del paper y las instituciones a las que se encontraban afiliados al momento de escribirlo.")
                st.write("Deberá ingresar una institución, cargar todos los autores afiliados a esa institución y presionar el botón 'Cargar Afiliaciones'")
                st.write("Repita este proceso para cada una de las instituciones que participaron en el paper.")
                st.write("Cuando haya finalizado con todas las instituciones presione 'Guardar'")
                st.markdown("#### Instituciones")
                institution = st.selectbox(label="Seleccione una institución a la que estén afiliados algunos/todos los autores",options=intitutions_list)
                if institution == "Otro":
                    institution = st.text_input(label="Institución a la que estan afiliados los autores")
                st.markdown("#### Autores Afiliados")
                authors = st.multiselect(label="Seleccione todos los autores que esten afiliados a la institución", options = authors_list)
                if "Otro" in authors:
                    authors2 = st.text_area(label="Ingresar un autor por linea con su scopusid separado por comas")
                st.write("Una vez que haya ingresado todos los autores afiliados a una intitución, haga click en 'Cargar Afiliaciones' y vea los datos cargados hasta el momento en el dataframe que aparecerá debajo.")
                st.write("Para cargar otra institución con sus respectivos autores repita el proceso llenando nuevamente los campos")
                cargar = st.button("Cargar Afiliaciones")
                if  cargar and not "Otro" in authors:
                    cargarInstitucion(institution,authors)
                if cargar and "Otro" in authors:
                    cargarInstitucion(institution,authors,authors2)
                if st.button("Eliminar afiliaciones cargadas"):
                    os.remove("affiliations")
                    st.success("¡Se han eliminado las afiliaciones cargadas hasta el momento! ")
                if st.button("Guardar"):
                    copyfile("affiliations", "affiliations_def")
                    st.success("¡Se han guardado los datos de esta sección! ")
                    data = pd.read_csv('affiliations_def')
                    st.dataframe(data)
                    st.write("Seguí completando los campos de otras secciones o presioná 'Enviar' en la barra lateral si ya completaste todas las secciones.")
                    
        
        if st.sidebar.button("Enviar"):
            exito = crearPaper()
    else:
        st.markdown("#### Ya se guardó el paper en la base de datos")
        with open('paper', 'r') as fp:
            paper = json.load(fp)
        st.json(paper)
        if st.button("Cargar otro Paper"):
            os.remove("paper")
            os.remove("affiliations")
            os.remove("publication")
            os.remove("financement")
            
        
    # if st.button("Ver papers"):
    #     verPapers()

def cargarInstitucion(institution,authors,authors2=""):
    affiliations = []
    for name in authors:
        if name == "Otras":
            continue
        try:
            author = Author.objects.get(name=name)
            affiliations.append([author.name,author.scopusID])
        except Author.MultipleObjectsReturned:
            st.write("Hubo un problema con el autor: "+name)
            continue
        except Author.DoesNotExist:
            st.write("Hubo un problema con el autor: "+name)
    df1 = pd.DataFrame(affiliations,columns=("Autor", "Scopus_id"))
    df1["Institución"] = institution
    if os.path.exists("affiliations"):
        affiliationsDF = pd.read_csv('affiliations')
    else:
        affiliationsDF = pd.DataFrame(data=[],columns=("Autor", "Scopus_id", "Institución"))
    if authors2 != "":    
        df2 = pd.DataFrame([x.split(',') for x in authors2.split('\n')],columns=("Autor", "Scopus_id"))
        df2["Institución"] = institution
        df1 = pd.concat([df1,df2])
    affiliationsDF = pd.concat([affiliationsDF,df1])
    affiliationsDF.to_csv(path_or_buf="affiliations",index=False)
    st.markdown("#### Autores cargados hasta el momento")
    st.dataframe(affiliationsDF)
    
        
def cargarFinanciamiento(finantial_institutions,finantial_institutions2=""):
    data = []
    for name in finantial_institutions:
        if name == "Otro":
            continue
        try:
            f_inst = Finantial_Institution.objects.get(name=name)
            data.append([f_inst.name,f_inst.country])
        except Finantial_Institution.MultipleObjectsReturned:
            st.write("Hubo un problema con la institución: "+name)
            continue
        except Finantial_Institution.DoesNotExist:
            st.write("Hubo un problema con la institución: "+name)
    finantial_institutions_df = pd.DataFrame(data,columns=("Name", "Country"))
    if finantial_institutions2!="":
        finantial_institutions_df2 = pd.DataFrame([x.split(',') for x in finantial_institutions2.split('\n')],columns=("Name", "Country"))
        finantial_institutions_df = pd.concat([finantial_institutions_df,finantial_institutions_df2])
    print( len(finantial_institutions_df.index))
    if len(finantial_institutions_df.index)>0:
        finantial_institutions_df.to_csv("financement",index=False)
        st.success("¡Se han guardado los datos de esta sección! ")
        st.dataframe(finantial_institutions_df)
        st.write("Seguí completando los campos de otras secciones o presioná 'Enviar' en la barra lateral si ya completaste todas las secciones.")
    else: st.write("Asegúrese de completar los campos antes de presionar Guardar")
    
def cargarPublicacion(title,doi,keywords,publication_date):
    data={"Titulo":title,"DOI":doi,"Keywords":keywords.split(','),"Mes_Publicacion":publication_date.month,"Año_Publicacion":publication_date.year}
    with open('publication', 'w') as fp:
        json.dump(data, fp)
    st.success("¡Se han guardado los datos de esta sección! ")
    st.json(data)
    st.write("Seguí completando los campos de otras secciones o presioná 'Enviar' en la barra lateral si ya completaste todas las secciones.")

def crearPaper():
    badflag=False
    if not os.path.exists("affiliations_def"):
        error = InputError("Faltan los autores!!")
        st.sidebar.write(error)
        badflag = True
    if not os.path.exists("publication"):
        error = InputError("Faltan los datos de publicación!!")
        st.sidebar.write(error)
        badflag = True
    if not os.path.exists("financement"): 
        error = InputError("Faltan los datos de financiamiento!!")
        st.sidebar.write(error)
        badflag = True
    if badflag: return False
    with open('publication', 'r') as fp:
        pub_data = json.load(fp)
    finan_data = pd.read_csv('financement')
    aff_data = pd.read_csv('affiliations')
    
    #manejo de instituciones financieras
    finantial_institutions_list = []
    for index, row in finan_data.iterrows():
        try:
            f_inst = Finantial_Institution.objects.get(name=row["Name"])
            finantial_institutions_list.append(f_inst)
        except Finantial_Institution.MultipleObjectsReturned:
            st.write("Hubo un problema con la institución: "+row["Name"])
            continue
        except Finantial_Institution.DoesNotExist:
            st.write("Se guardó la institución: "+row["Name"])
            fin_ins = Finantial_Institution(name = row["Name"], country = row["Country"]).save()
            finantial_institutions_list.append(fin_ins)
            
    #manejo de afiliaciones
    affiliations = []
    for index, row in aff_data.iterrows():
        #autor
        try:
            author = Author.objects.get(name=row["Autor"])
        except Author.MultipleObjectsReturned:
            st.write("Hubo un problema con el autor: "+row["Autor"])
            continue
        except Author.DoesNotExist:
            st.write("Se guardó al autor "+row["Autor"] + " con id "+ str(row["Scopus_id"]))
            author = Author(name=row["Autor"],scopusID=str(row["Scopus_id"])).save()
        #institucion
        try:
            institution = Institution.objects.get(name=row["Institución"])
        except Institution.MultipleObjectsReturned:
            st.write("Hubo un problema con la institución: "+row["Institución"])
            continue
        except Institution.DoesNotExist:
            st.write("Se guardó la institución "+row["Institución"])
            institution = Institution(name=row["Institución"]).save()
        aff = Author_Affiliation(institution=institution,author=author)
        affiliations.append(aff)
    #crea el paper
    new_paper = Paper(title=pub_data["Titulo"], doi=pub_data["DOI"], keywords=pub_data["Keywords"],
                      publication_month=pub_data["Mes_Publicacion"], publication_year=pub_data["Año_Publicacion"],
                      finantial_institutions= finantial_institutions_list,
                      author_affiliations = affiliations).save()
    with open('paper', 'w') as fp:
        json.dump(new_paper.to_json(), fp)
    st.sidebar.success("¡Se han guardado los datos de este paper! ")
    st.sidebar.json(new_paper.to_json())
    return True


def verPapers():
    st.write("Los siguientes papers se encuentran en la base de datos")
    for paper in Paper.objects:
        st.write(paper.title)   
    st.write("Los siguientes autores se encuentran en la base de datos")
    for author in Author.objects:
        st.write(author.name)
    st.write("Las siguientes instituciones se encuentran en la base de datos")
    for institution in Institution.objects:
        st.write(institution.name)