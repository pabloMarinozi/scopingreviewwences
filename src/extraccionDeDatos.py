
import streamlit as st
import pandas as pd
import opciones as op
import time
import os.path
import json
from shutil import copyfile
from exceptions import InputError
from mongoengine import disconnect,connect
from clases import Paper,Visual_Task,Visual_Feature


def mostrarSeccionExtracción(user):
    disconnect()
    connect('scopingReview',host="mongodb+srv://admin:LccNwXd87QkFzvu@cluster0.w9zqf.mongodb.net/scopingReview?retryWrites=true&w=majority", alias='default')
    st.title('Extracción de Datos')
    
    col1, col2 = st.beta_columns(2)
    opciones = buscarOpcionesCargadas()
    seccion = st.sidebar.radio(label="Secciones", options=["Seleccionar artículo", "Características de la investigación", "Tareas visuales"])
    if st.sidebar.button("Enviar"): guardarExtraccion()
    if st.sidebar.button("Cargar otro paper"):
        reiniciarCarga()

    if seccion == "Seleccionar artículo":
        if os.path.exists("paper_selected"):
            st.markdown("#### Ya se ha seleccionado el paper cuyos datos extraer")
            with open('paper_selected', 'r') as fp:
                data = json.load(fp)
                st.json(data)
            if st.button("Seleccionar otro paper"):
                os.remove("paper_selected")
        else:
            st.markdown("## Seleccionar artículo  para extraer datos.")
            doi = st.text_input(label="Ingrese el doi del artículo en su formato url. Por ejemplo:https://doi.org/10.1109/CVPR.2016.609")
            if st.button(label="Buscar"):
                paper = None
                try:
                    badflag=False
                    paper = Paper.objects.get(doi=doi)
                    st.success("Se encontró un paper con título:\n"+'**"'+paper.title+'"**')
                    if paper.research_goal is not None or \
                    paper.practical_contibution is not None or \
                    paper.viticultural_aspects is not None:
                        st.error("El paper encontrado tiene cargadas las características de la investigación")
                        st.write("Objetivo de la investigación: ")
                        st.write(paper.research_goal)
                        st.write("Aporte práctico: "+ paper.practical_contibution)
                        st.write("Aspectos Vitícolas: " + paper.viticultural_aspects)
                        badflag = True
                    if paper.visual_tasks is not None:
                        st.error("El paper encontrado tiene cargadas las tareas visuales")
                        visual_to_show = []
                        for task in paper.visual_tasks:
                            visual_to_show.append(json.loads(task.to_json()))
                        st.write(visual_to_show)
                        badflag=True
                    if not badflag:
                        with open('paper_selected', 'w') as fp:
                            json.dump(paper.to_json(), fp)
                        st.write("Continue con la extracción y los datos ingresados se asociarán a este paper.")
                        st.json(paper.to_json())
                except Paper.MultipleObjectsReturned:
                    st.write("Al parecer, hay más de un paper con el doi ingresado.")
                    papers = Paper.objects(doi=doi)
                    names = []
                    for paper in papers:
                        names.append(paper.title)
                    name = st.selectbox(label="Elija el que usted quiera analizar", options=names)
                    paper = Paper.objects(doi=doi, names=name)[0]
                except Paper.DoesNotExist:
                    st.error("No existe ningun paper con el doi ingresado en la base de datos")
    
    if seccion == "Tareas visuales":
        if os.path.exists("tareas_def"):
            st.markdown("#### Ya se han cargado los datos de esta sección")
            with open('tareas_def', 'r') as fp:
                tasks = json.load(fp)
            st.json(tasks)
            if st.button("Cargar más tareas"):
                os.remove("tareas_def")
            if st.button("Eliminar datos cargados"):
                os.remove("tareas")
                os.remove("tareas_def")
        else:
            st.markdown("## Extraer datos del paper seleccionado.")
            st.markdown("### Tareas Visuales de alto Nivel")
            st.markdown("Los siguientes campos deberán completarse para **cada una** de las tareas visuales que se llevan a cabo mediante CV en el paper.")
            st.markdown("Una vez que se hayan completado los campos necesarios, presione **'Cargar Tarea'** para salvar los datos y pasar a la siguiente tarea visual (si es que hay más de una).")
            
            col1, col2 = st.beta_columns(2)
            with col1:    
                st.markdown("#### Nombre de la tarea")
                options = list(opciones["visual_tasks_list"])
                options.append("Otra")
                task = st.selectbox(label="Seleccione una tarea visual de alto nivel. Si la que se quiere ingresar no se encuentra en la lista elija 'Otra' y carguela manualmente",options=options)
                if task == "Otra":
                    task = st.text_input(label="Ingrese una tarea visual para agregar a la base de datos.")
                sub = st.radio("Subsecciones", ["Información Vitícola","Dataset","Features", "Algoritmos"])
                if st.button("Cargar tarea visual"):
                    cargarTarea(task)
                if st.button("Eliminar tareas visuales cargadas"):
                        os.remove("tareas")
                        st.success("¡Se han eliminado las tareas visuales cargadas hasta el momento! ")
                if st.button("Guardar tareas cargadas"):
                    copyfile("tareas", "tareas_def")
                    st.success("¡Se han guardado los datos de esta sección! ")
                    with open('tareas_def', 'r') as fp:
                        tasks = json.load(fp)
                    st.json(tasks.to_json())
                    st.write("Seguí completando los campos de otras secciones o presioná 'Enviar' en la barra lateral si ya completaste todas las secciones.")
                     
                    
    
            with col2: 
                if sub == "Información Vitícola":
                    if os.path.exists("viticulture"):
                        st.markdown("#### Ya se han cargado los datos de esta sección")
                        with open('viticulture', 'r') as fp:
                            data = json.load(fp)
                        st.json(data)
                        if st.button("Eliminar datos cargados"):
                            os.remove("viticulture")
                    else:
                        st.markdown("#### Objetos Vitícolas")
                        options = list(opciones["viticultural_objects_list"])
                        options.append("Otros")
                        objs = st.multiselect(label="Seleccione todos los objetos vitícolas sobre los que se aplica la tarea visual de alto nivel. Si algún objeto no se encuentra en la lista elija 'Otros' y carguelo manualmente",options=options)
                        if "Otros" in objs:
                            objs2 = st.text_input(label="Ingrese objetos vitícolas para agregar a la base de datos separados por comas")
                        st.markdown("#### Variables Vitícolas")
                        options = list(opciones["viticultural_variable_list"])
                        options.append("Otras")
                        vars = st.multiselect(label="Seleccione todas las variables vitícolas que se midieron mediante esta tarea visual. Si alguna variable vitícola no se encuentra en la lista elija 'Otras' y carguela manualmente",options=options)
                        if "Otras" in vars:
                            vars2 = st.text_input(label="Ingrese variables vitícolas para agregar a la base de datos separados por comas")
                        var_details = st.text_area(label="Ingrese algun comentario destacable sobre la manera en que se aplicó esta tarea visual a la medición de la variable en caso de ser necesario.")
                        monitor = st.checkbox("¿Se monitoriza la medición de estas variables a lo largo del tiempo?")
                        guardar = st.button("Guardar")
                        if guardar:
                            if "Otras" in vars:
                                if "Otros" in objs:
                                    cargarInfoViticola(objs,vars,var_details,monitor,objs2.split(','),vars2.split(','))
                                else:
                                    cargarInfoViticola(objs,vars,var_details,monitor,vars2=vars2.split(','))
                            else:
                                if "Otros" in objs:
                                    cargarInfoViticola(objs,vars,var_details,monitor,objs2.split(','))
                                else:
                                    cargarInfoViticola(objs,vars,var_details,monitor)
                        
                        
                if sub == "Dataset":
                    st.markdown("#### Dataset")
                    if os.path.exists("dataset"):
                        st.markdown("#### Ya se han cargado los datos de esta sección")
                        with open('dataset', 'r') as fp:
                            data = json.load(fp)
                        st.json(data)
                        if st.button("Eliminar datos cargados"):
                            os.remove("dataset")
                    else:   
                        bench = st.checkbox("¿El dataset utilizado es de benchmarking?")
                        if not bench:        
                            format = st.selectbox(label="Seleccione los elementos de los que se compone el dataset",options=list(opciones["dataset_format_list"]))
                            
                            options = list(opciones["electromagnetic_spectrum_list"])
                            options.append("Otra")
                            electromagnetic = st.selectbox(label="Indique qué sección del espectro electromagnetico se capturó en el dataset. Si ninguna de las opciones lo satisface, elija 'Otra' y carguela manualmente",options=options)
                            if electromagnetic == "Otra":
                                electromagnetic = st.text_input(label="Ingrese una sección del espectro electromagnetico para agregar a la base de datos.")
                            
                            options = list(opciones["camera_types_list"])
                            options.append("Otra")
                            camera = st.selectbox(label="Indique con qué tipo/arreglo de cámara se capturó el dataset. Si ninguna de las opciones lo satisface, elija 'Otra' y carguela manualmente",options=options)
                            if camera == "Otra":
                                camera = st.text_input(label="Ingrese una sección del espectro electromagnetico para agregar a la base de datos.")
                            
                            camera_details = st.text_area(label="Ingrese algun comentario destacable sobre el hardware utilizado en caso de que lo crea conveniente")
                    
                            options = list(opciones["data_capture_conditions_list"])
                            options.append("Otra")
                            condition = st.selectbox(label="Seleccione las condiciones en que se capturó el dataset. Si la que se quiere ingresar no se encuentra en la lista elija 'Otra' y carguela manualmente",options=options)
                            if condition == "Otra":
                                condition = st.text_input(label="Ingrese una condición de captura nueva para agregar a la base de datos.")
                                
                            dataset_details = st.text_area(label="Ingrese algun comentario destacable sobre la captura del dataset en caso de ser necesario.")                   
                        link = st.checkbox("¿Se encuentra disponible?")
                        if link:
                            link = st.text_input(label="Ingrese la url para acceder al dataset.")
                        if st.button("Guardar"):
                            if bench:
                                cargarDataset(bench,link)
                            else:
                                cargarDataset(bench,link,format,electromagnetic,camera,camera_details,condition,dataset_details)
                        
                if sub == "Features":
                    if os.path.exists("features_def"):
                        st.markdown("#### Ya se han cargado los datos de esta sección")
                        feat = pd.read_csv('features_def')
                        st.dataframe(feat)
                        if st.button("Cargar más datos"):
                            os.remove("features_def")
                        if st.button("Eliminar datos cargados"):
                            os.remove("features")
                            os.remove("features_def")
                    else:
                        st.markdown("#### Features")
                        st.markdown("Las features son representaciones de los datos visuales crudos que son más propicias para una tarea informática y se obtienen a través de un proceso a menudo creativo. ")
                        feature_type = st.selectbox("Elija un tipo de features a ingresar", options=list(opciones["visual_features_types"]))
                        if st.checkbox("Ver más info sobre los tipos de features..."):
                            st.markdown("Existen 3 tipos:")
                            st.markdown("- **Classic hand-crafted features**: Estas features están diseñadas por expertos humanos tratando de mantener invariante una propiedad específica de los datos. Estas features son fácilmente interpretables y caracterizan aspectos fundamentales de las imágenes como el color, la textura y la forma.\n- **Features latentes** : Estas features consisten en representaciones  del objeto ocultas en un subespacio de dimensionalidad inferior al de los datos crudos y son encontradas automáticamente por algoritmos de optimización.\n- **Deep Features**: Estas features consisten en representaciones jerárquicas extraídas mediante una red neuronal multicapa. En este tipo de features, el conocimiento del experto se concentra en el diseño de la red que se encargará de aprender la mejor forma de representar los datos a medida que aprende a realizar la tarea para la cual los necesita.")
                        
                        if feature_type == "Handcrafted":
                            options = list(opciones["visual_features_handcrafted_list"])
                            options.append("Otras")
                            features_hand = st.multiselect(label="Seleccione todas las handcrafted features utilizadas para esta tarea visual de alto nivel. Si alguna feature de este estilo no se encuentra en la lista elija 'Otras' y carguelas manualmente",options=options)
                            if "Otras" in features_hand:
                                features_hand2 = st.text_input(label="Ingrese handcrafted features para agregar a la base de datos **separadas por comas**")
                            if st.button("Cargar Handcrafted Features"):
                                if "Otras" in features_hand:
                                    cargarFeatures("Handcrafted",features_hand,features_hand2)
                                else: cargarFeatures("Handcrafted",features_hand)
                        elif feature_type == "Latent":
                            options = list(opciones["visual_features_latent_list"])
                            options.append("Otras")
                            features_lat = st.multiselect(label="Seleccione todas las latent features utilizadas para esta tarea visual de alto nivel. Si alguna feature de este estilo no se encuentra en la lista elija 'Otras' y carguelas manualmente",options=options)
                            if "Otras" in features_lat:
                                features_lat2 = st.text_input(label="Ingrese latent features para agregar a la base de datos **separadas por comas**")
                            if st.button("Cargar Latent Features"):
                                if "Otras" in features_lat:
                                    cargarFeatures("Latent",features_lat,features_lat2)
                                else: cargarFeatures("Latent",features_lat)
                        elif feature_type == "Deep":
                            options = list(opciones["visual_features_deep_list"])
                            options.append("Otras")
                            features_deep = st.multiselect(label="Seleccione todas las deep features utilizadas para esta tarea visual de alto nivel. Si alguna feature de este estilo no se encuentra en la lista elija 'Otras' y carguelas manualmente",options=options)
                            if "Otras" in features_deep:
                                features_deep2 = st.text_input(label="Ingrese latent features para agregar a la base de datos separadas por comas")
                            if st.button("Cargar Deep Features"):
                                if "Otras" in features_deep:
                                    cargarFeatures("Deep",features_deep,features_deep2)
                                else: cargarFeatures("Deep",features_deep)
                        if st.button("Eliminar afiliaciones cargadas"):
                            os.remove("features")
                            st.success("¡Se han eliminado las afiliaciones cargadas hasta el momento! ")
                        if st.button("Guardar"):
                            copyfile("features", "features_def")
                            st.success("¡Se han guardado los datos de esta sección! ")
                            data = pd.read_csv('features_def')
                            st.dataframe(data)
                            st.write("Seguí completando los campos de otras secciones o presioná 'Enviar' en la barra lateral si ya completaste todas las secciones.")
                        
                
                if sub == "Algoritmos":
                    if os.path.exists("algorithms"):
                        st.markdown("#### Ya se han cargado los datos de esta sección")
                        with open('algorithms', 'r') as fp:
                            data = json.load(fp)
                        st.json(data)
                        if st.button("Eliminar datos cargados"):
                            os.remove("algorithms")
                    else:
                        st.markdown("#### Algoritmos")
                        options = list(opciones["algorithms_list"])
                        options.append("Otros")
                        algs = st.multiselect(label="Seleccione todos los algoritmos de machine learning que se usaron para esta tarea visual. Si algún algoritmo no se encuentra en la lista elija 'Otros' y carguelo manualmente",options=options)
                        if "Otros" in algs:
                            algs2 = st.text_input(label="Ingrese algoritmos de machine learning para agregar a la base de datos separados por comas")
                        guardar = st.button("Guardar")
                        if guardar and not "Otros" in algs:  
                           cargarAlgoritmos(algs)
                        if guardar and "Otros" in algs:  
                           cargarAlgoritmos(algs,algs2.split(','))
                        
        
    if seccion == "Características de la investigación":
        if os.path.exists("caracteristicas"):
            st.markdown("#### Ya se han cargado los datos de esta sección")
            with open('caracteristicas', 'r') as fp:
                data = json.load(fp)
            st.json(data)
            if st.button("Eliminar datos cargados"):
                os.remove("caracteristicas")
        else:        
            st.markdown("## Extraer datos del paper seleccionado.")
            st.markdown("#### Objetivo de la investigación")
            options = list(opciones["research_goal_list"])
            options.append("Otros")
            goals = st.multiselect(label="Seleccione los objetivos que persiguieron los autores con esta investigación. Si ninguno de los objetivos de la lista lo convence, elija 'Otro' y carguelo manualmente",options=options)
            if "Otros" in goals:
                goals2 = st.text_input(label="Ingrese objetivos para agregar a la base de datos separados por comas.")
            
            st.markdown("#### Aporte práctico")
            options = list(opciones["practical_contibution_list"])
            options.append("Otro")
            practical = st.selectbox(label="Seleccione el tipo de contribución práctica de este paper. Si alguna contribución práctica no se encuentra en la lista elija 'Otras' y carguela manualmente",options=options)
            if practical == "Otro":
                practical = st.text_input(label="Ingrese una contribución práctica para agregar a la base de datos.")
            
            st.markdown("#### Aspectos Vitícolas")
            options = list(opciones["viticultural_aspects_list"])
            options.append("Otro")
            aspects = st.selectbox(label="Seleccione los aspectos vitícolas que intenta resolver este paper. Si algun aspecto no se encuentra en la lista elija 'Otros' y carguela manualmente",options=options)
            if aspects=="Otro":
                aspects = st.text_input(label="Ingrese un aspecto vitícola para agregar a la base de datos.")
            
            guardar = st.button("Guardar")
            if guardar and not "Otros" in goals:  
               cargarCaracterísticas(goals,practical,aspects)
            if guardar and "Otros" in goals:  
               cargarCaracterísticas(goals,practical,aspects,goals2.split(','))
        
def cargarInfoViticola(objs,vars,var_details,monitor,objs2=[],vars2=[]):
    if objs2:
        objs.remove("Otros")
    if vars2:
        vars.remove("Otros")
    info = {"Objetos":list(set(objs+objs2)),"Variables":list(set(vars+vars2)),"Detalles":var_details,"Monitoreo":monitor}
    with open('viticulture', 'w') as fp:
        json.dump(info, fp)
    st.success("¡Se han guardado los datos de esta sección! ")
    st.json(info)
    st.write("Seguí completando los campos de otras secciones o presioná 'Enviar' en la barra lateral si ya completaste todas las secciones.")

def cargarDataset(bench,link,format="",electromagnetic="",camera="",camera_details="",condition="",dataset_details=""):
    data = {"Benchmark":bench, "Link": link,"Formato":format, "Espectro": electromagnetic, "Cámara": camera, "Detalles_Cámara": camera_details,
            "Condiciones_Captura": condition, "Detalles_Dataset": dataset_details}
    with open('dataset', 'w') as fp:
        json.dump(data, fp)
    st.success("¡Se han guardado los datos de esta sección! ")
    st.json(data)
    st.write("Seguí completando los campos de otras secciones o presioná 'Enviar' en la barra lateral si ya completaste todas las secciones.") 

def cargarFeatures(type,features,features2=""):
    data = []
    for name in features:
        if name in {"Otras",""}:
            continue
        try:
            feature = Visual_Feature.objects.get(name=name)
            data.append([feature.name, feature.type])
        except Visual_Feature.MultipleObjectsReturned:
            st.write("Hubo un problema con la feature: "+name)
            continue
        except Visual_Feature.DoesNotExist:
            data.append([name, type])
    if os.path.exists("features"):
        featuresDF = pd.read_csv('features')
    else:
        featuresDF = pd.DataFrame(data=[],columns=("Nombre", "Tipo"))
    if features2 != "":
        f2 = features2.split(',')
        for f in f2:
            data.append([f,type])
    df = pd.DataFrame(data,columns=("Nombre", "Tipo"))
    featuresDF = pd.concat([featuresDF,df])
    featuresDF.to_csv(path_or_buf="features",index=False)
    st.dataframe(featuresDF)

def cargarAlgoritmos(algs, algs2=[]):
    if algs2:
        algs.remove("Otros")
    info = {"Algoritmos":list(set(algs+algs2))}
    with open('algorithms', 'w') as fp:
        json.dump(info, fp)
    st.success("¡Se han guardado los datos de esta sección! ")
    st.json(info)
    st.write("Seguí completando los campos de otras secciones o presioná 'Enviar' en la barra lateral si ya completaste todas las secciones.")

def cargarCaracterísticas(goals,practical,aspects,goals2=[]):
    if goals2:
        goals.remove("Otros")
    info = {"Aspectos":aspects,
            "Práctica":practical,
            "Objetivo":list(set(goals+goals2))}
    with open('caracteristicas', 'w') as fp:
        json.dump(info, fp)
    st.success("¡Se han guardado los datos de esta sección! ")
    st.json(info)
    st.write("Seguí completando los campos de otras secciones o presioná 'Enviar' en la barra lateral si ya completaste todas las secciones.")


def cargarTarea(task):
    badflag=False
    if not os.path.exists("viticulture"):
        error = InputError("Falta la información vitícola!!")
        st.write(error)
        badflag = True
    if not os.path.exists("dataset"):
        error = InputError("Faltan los datos del dataset!!")
        st.write(error)
        badflag = True
    if not os.path.exists("features_def"): 
        error = InputError("Faltan los datos de las features!!")
        st.write(error)
        badflag = True
    if not os.path.exists("algorithms"): 
        error = InputError("Faltan los datos de los algoritmos!!")
        st.write(error)
        badflag = True
    if not os.path.exists("paper_selected"): 
        error = InputError("No puede cargar tareas visuales hasta que haya seleccionado un paper.")
        st.write(error)
        badflag = True
    if badflag: return False
    with open('viticulture', 'r') as fp:
        viticulture = json.load(fp)
    with open('dataset', 'r') as fp:
        dataset = json.load(fp)
    with open('algorithms', 'r') as fp:
        algorithms = json.load(fp)
    features_df = pd.read_csv('features_def')
    features_list = []
    for index, row in features_df.iterrows():
        try:
            feat = Visual_Feature.objects.get(name=row["Nombre"])
            features_list.append(feat)
        except Visual_Feature.MultipleObjectsReturned:
            st.write("Hubo un problema con la feature: "+row["Nombre"])
            continue
        except Visual_Feature.DoesNotExist:
            st.write("Se guardó la feature: "+row["Nombre"])
            feat = Visual_Feature(name = row["Nombre"], type = row["Tipo"]).save()
            features_list.append(feat)
    link = dataset["Link"]
    if link == False:
        link = "NA"
    task = Visual_Task(name = task, viticultural_objects = viticulture["Objetos"],
                data_capture_condition=dataset["Condiciones_Captura"],
                data_capture_details=dataset["Detalles_Dataset"],
                electromagnetic_spectrum=dataset["Espectro"],
                dataset_format=dataset["Formato"],camera_types=dataset["Cámara"],
                camera_details=dataset["Detalles_Cámara"],
                benchmarking_dataset=dataset["Benchmark"],
                dataset_link=link,visual_features=features_list,
                algorithms=algorithms["Algoritmos"],
                viticultural_variable=viticulture["Variables"],
                viticultural_variable_details=viticulture["Detalles"],
                monitoring=viticulture["Monitoreo"]
                )
    if os.path.exists("tareas"):
        with open('tareas', 'r') as fp:
            tasks = json.load(fp)
    else:
        tasks = {}
    tasks[str(len(tasks))]= json.loads(task.to_json())
    with open('tareas', 'w') as fp:
        json.dump(tasks, fp)
    st.success("¡Se ha guardado la tarea "+task.name)
    st.markdown("#### Tareas visuales cargadas hasta el momento")
    st.json(tasks)

def guardarExtraccion():
    badflag=False
    if not os.path.exists("caracteristicas"):
        error = InputError("Faltan las características de la investigación!!")
        st.sidebar.write(error)
        badflag = True
    if not os.path.exists("tareas_def"):
        error = InputError("Faltan las tareas visuales!!")
        st.sidebar.write(error)
        badflag = True
    if not os.path.exists("paper_selected"): 
        error = InputError("Falta seleccionar el paper!!")
        st.sidebar.write(error)
        badflag = True
    if badflag: return False
    with open('paper_selected', 'r') as fp:
        paper_dict = json.loads(json.load(fp))
    paper = Paper.objects.get(doi=paper_dict["_id"])
    with open('caracteristicas', 'r') as fp:
        caracteristicas = json.load(fp)
    paper.research_goal = caracteristicas["Objetivo"]
    paper.viticultural_aspects = caracteristicas["Aspectos"]
    paper.practical_contibution = caracteristicas["Práctica"]
    with open('tareas_def', 'r') as fp:
        tasks = json.load(fp)
    paper.visual_tasks = []
    for key in tasks:
        task_dict = tasks[key]
        task = Visual_Task.from_json(json.dumps(task_dict))
        paper.visual_tasks.append(task)
    paper.save()
    st.sidebar.success("Se han guardado los datos extraidos en la base de datos.")
    st.sidebar.json(paper.to_json())


def reiniciarCarga():    
    os.remove("paper_selected")
    os.remove("tareas_def")
    os.remove("tareas")
    os.remove("viticulture")
    os.remove("dataset")
    os.remove("features")
    os.remove("features_def")
    os.remove("algorithms")
    os.remove("caracteristicas")

      
def buscarOpcionesCargadas():
    opciones = op.opciones.copy()
    for paper in Paper.objects():
        opciones["research_goal_list"].update(paper.research_goal)
        opciones["practical_contibution_list"].add(paper.practical_contibution)
        tasks = paper.visual_tasks
        if tasks is None: continue
        for task in tasks:
            opciones["visual_tasks_list"].add(task.name)
            opciones["data_capture_conditions_list"].add(task.data_capture_condition)
            opciones["electromagnetic_spectrum_list"].add(task.electromagnetic_spectrum)
            opciones["camera_types_list"].add(task.camera_types)
            opciones["viticultural_objects_list"].update(task.viticultural_objects)
            opciones["algorithms_list"].update(task.algorithms)
            opciones["viticultural_variable_list"].update(task.viticultural_variable)
            for feature in task.visual_features:
                if feature.type == "Handcrafted":
                    opciones["visual_features_handcrafted_list"].add(feature.name)
                elif feature.type == "Latent":
                    opciones["visual_features_latent_list"].add(feature.name)
                else: opciones["visual_features_deep_list"].add(feature.name)
    
    return opciones
    
                
        

    
        
        

        

# disconnect()
# connect('literatureReview')
# for paper in Paper.objects:
#     print(paper.doi)