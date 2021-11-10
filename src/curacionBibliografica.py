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

def mostrarPantallaCuracionBibliografica():
    conectarBd()
    papers = Paper.objects(Q(inclusion1=True) & Q(inclusion2=True) & Q(bibliographyIsLoaded__exists=False))
    count_papers = len(papers)
    if count_papers > 0:
        st.success("Se encontraron disponibles " + str(count_papers) + " papers para cargar.")
        st.markdown("## ¿Desea realizar la carga ahora?")
        cargar = st.button("Cargar")
        if cargar:
            automatizarCarga(papers)
    else:
        st.error("No hay papers disponibles para cargar en este momento.")

def automatizarCarga(papers):
    papers_before = len(Paper.objects)
    authors_before = len(Author.objects)
    inst_before = len(Institution.objects)
    fin_inst_before = len(Finantial_Institution.objects)
    total = len(papers)
    inicio_msg = st.success("Se iniciará la carga de información bibliográfica de **"+str(total)+"** papers.")
    my_bar = st.progress(.0)
    loaded = 0
    exitos = []
    fallos = []

    for paper in papers:
        with open('mensajes.txt', 'a') as f:
            try:
                test=get_entity(paper.doi, EntityType.PUBLICATION, OutputType.JSON)
                exitos.append(test['title'][0])
                #st.write(test['title'][0])
            except:
                fallos.append(paper.title)
                f.write('Fallo la Busqueda del Paper \n')
            if test['created']['date-parts'][0][1] is not None:
                paper.publication_month = test['created']['date-parts'][0][1]
                paper.save()
            if test['created']['date-parts'][0][0] is not None:
                paper.publication_year = test['created']['date-parts'][0][0]
            
            #Guardando Autores y autores affiliation
            if 'author' in test:
                affiliation_list =[]
                for autor in test['author']:
                    try:
                        name_author = autor['given'] + ' ' + autor['family']
                    except:
                        continue
                    try:
                        author_ = Author.objects.get(name = name_author)
                    except Author.MultipleObjectsReturned:
                        f.write("Hubo un problema con el Autor: " + name_author + "\n")
                        continue
                    except Author.DoesNotExist:
                        if 'ORCID' in autor and 'authenticated-orcid' in autor:
                            author_ = Author(orcid = autor['ORCID'], authenticated_orcid = autor['authenticated-orcid'], 
                                            name = name_author, familyName= autor['family'], firstName = autor['given']).save()
                            f.write("Se guardó el Autor: " + name_author + "\n")
                        else:
                            author_ = Author(name = name_author, familyName= autor['family'], firstName = autor['given']).save()
                            f.write("Se guardó el Autor: " + name_author + "\n")

                    if autor['affiliation'] != []:
                        for institucion in autor['affiliation']:
                            try:
                                institution_ = Institution.objects.get(name = institucion['name'])
                            except Institution.MultipleObjectsReturned:
                                f.write("Hubo un problema con la Institución : " + institucion['name'] + "\n")
                                continue
                            except Institution.DoesNotExist:
                                f.write("Se guardó la Institución : " + institucion['name'] + "\n")
                                institution_ = Institution(name = institucion['name']).save()
                            affiliation = Author_Affiliation(institution = institution_ , author = author_, sequence = autor['sequence'])
                            affiliation_list.append(affiliation)
                    else:
                        affiliation = Author_Affiliation(author = author_, sequence = autor['sequence'])
                        affiliation_list.append(affiliation)

                paper.author_affiliations = affiliation_list

            #Obteniendo Finantial_Institution
            funder_list = []
            if 'funder' in test:
                for funder_ in test['funder']:
                    try: 
                        if 'DOI' in funder_:
                            funder = Finantial_Institution.objects.get(doi = funder_['DOI'])
                        else:
                            funder = Finantial_Institution.objects.get(name = funder_['name'])
                    except Finantial_Institution.MultipleObjectsReturned:
                        f.write("Hubo un problema con la institución financiera: " + funder_['name'] + "\n")
                        continue
                    except Finantial_Institution.DoesNotExist:
                        if 'DOI' in funder_:
                            funder = Finantial_Institution(doi = funder_['DOI'], name = funder_['name']).save()
                            f.write("Se guardó la Institución : " + funder_['name'] + "\n")
                        else:
                            funder = Finantial_Institution(name = funder_['name']).save()
                            f.write("Se guardó la Institución : " + funder_['name'] + "\n")
                    funder_list.append(funder)
                paper.finantial_institutions = funder_list
            else:
                f.write("El paper " + paper.doi + " no fue financiado por ninguna institución. \n")

            #Obteniendo reference
            reference_list = []
            if 'reference' in test:
                for reference_ in test['reference']:
                    try:
                        if 'DOI' in reference_:
                            paper_ref = Paper.objects.get(doi = reference_['DOI'])
                        else:
                            continue
                    except Paper.MultipleObjectsReturned:
                        f.write("Hubo un problema con el paper de referencia: "+ reference_['DOI']+ "\n")
                        continue
                    except Paper.DoesNotExist:
                        if 'article-title' in reference_ and 'DOI' in reference_: 
                            paper_ref = Paper(doi = reference_['DOI'], title = reference_['article-title'] , abstract = ' ', isOnlyReference=True).save()
                            f.write("Se guardó el paper de referencia: " + reference_['DOI']+ "\n")
                        else:
                            f.write("Paper de referencia no tiene title: "+ "\n")
                    reference_list.append(reference_['DOI'])
            else:
                    f.write("Paper de referencia no tiene DOI: "+ "\n")
                    
            paper.references = reference_list
            paper.bibliographyIsLoaded = True
            paper.save()
            f.close()
        loaded+=1
        my_bar.progress(loaded/total)
    my_bar.empty()
    inicio_msg.empty()
    papers_after = len(Paper.objects)
    authors_after = len(Author.objects)
    inst_after = len(Institution.objects)
    fin_inst_after = len(Finantial_Institution.objects)
    exitosDF = pd.DataFrame()
    exitosDF["Título"] = pd.Series(exitos)
    fallosDF = pd.DataFrame()
    fallosDF["Título"] = pd.Series(fallos)
    st.success("Se procesaron exitosamente **"+str(len(exitos))+"** papers")
    st.success("Se ingresaron **"+ str(papers_after-papers_before) + " nuevas referencias** a la base de datos")
    st.success("Se ingresaron **"+ str(authors_after-authors_before) + " nuevos autores** a la base de datos")
    st.success("Se ingresaron **"+ str(inst_after-inst_before) + " nuevas instituciones** a la base de datos")
    st.success("Se ingresaron **"+ str(fin_inst_after-fin_inst_before) + " nuevas instituciones financiadoras** a la base de datos")
    st.dataframe(exitosDF)
    st.error("La API CrossRef no tenía registros de **"+str(len(fallos))+"** papers")
    st.dataframe(fallosDF)      



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
            #data.append([f_inst.name,f_inst.country])
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
    
def cargarPublicacion(title,abstract,doi,keywords,publication_date):
    data={"Titulo":title,"DOI":doi, "Abstract": abstract, "Keywords":keywords.split(','),"Mes_Publicacion":publication_date.month,"Año_Publicacion":publication_date.year}
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
            #fin_ins = Finantial_Institution(name = row["Name"], country = row["Country"]).save()
            #finantial_institutions_list.append(fin_ins)
            
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
    new_paper = Paper(title=pub_data["Titulo"], abstract=pub_data["Abstract"], doi=pub_data["DOI"], keywords=pub_data["Keywords"],
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