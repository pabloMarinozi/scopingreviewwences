#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 13:03:16 2020

@author: pablo
"""

from mongoengine import Document,EmbeddedDocument
from mongoengine import StringField,IntField,ListField,BooleanField,URLField,ReferenceField,EmbeddedDocumentField

#Clases creadas para mongodb
class Visual_Feature(Document):
    name = StringField(required=True, primary_key=True)
    type = StringField(required=True)  

class Visual_Task(EmbeddedDocument):
    name = StringField(required=True)
    viticultural_objects = ListField(StringField(max_length=50))
    data_capture_condition = StringField(required=True)
    data_capture_details = StringField()   
    electromagnetic_spectrum = StringField(required=True)
    dataset_format = StringField(required=True)
    camera_types = StringField(required=True)
    camera_details = StringField() 
    benchmarking_dataset = BooleanField(required=True)
    dataset_link = StringField()
    visual_features = ListField(ReferenceField(Visual_Feature))
    algorithms = ListField(StringField(max_length=50))
    viticultural_variable = ListField(StringField(max_length=50))
    viticultural_variable_details = StringField()
    monitoring = BooleanField(required=True)
    variety = ListField(StringField())
    driving_systems = ListField(StringField())
    
class Institution(Document):
    name = StringField(required=True, primary_key=True) #affiliation[]
    #country = StringField(required=True)

class Finantial_Institution(Document):
    doi = StringField()   #['funder']['DOI']
    name = StringField(required=True, primary_key=True)
    #country = StringField()

class Author(Document):
    orcid = StringField()
    authenticated_orcid = BooleanField()
    name = StringField(required=True, primary_key=True) #concatenar
    familyName = StringField()
    firstName = StringField()
    #scopusID =StringField() #hay q sacarlo

class Author_Affiliation(EmbeddedDocument):
    institution = ReferenceField(Institution)
    author = ReferenceField(Author)
    sequence = StringField(max_length=15)  #first or additional 
    
# class Inclusion(EmbeddedDocument):
#     inclusion = BooleanField(required=True)
#     user = StringField(required=True)
#     criteria = ListField(StringField())
        
class Paper(Document):
    title = StringField(required=True)    
    abstract = StringField(required=True)
    doi = StringField(required=True, primary_key=True)
    on_revision = StringField()
    inclusion1 = BooleanField()
    user_inclusion1 = StringField()
    criteria_inclusion1 = ListField(StringField())
    comments1 = StringField()
    inclusion2 = BooleanField()
    user_inclusion2 = StringField()
    criteria_inclusion2 = ListField(StringField())
    comments2 = StringField()
    keywords = ListField(StringField(max_length=50))
    publication_month = IntField(min_value=1, max_value=12)
    publication_year = IntField(min_value=1950, max_value=2020)
    visual_tasks = ListField(EmbeddedDocumentField(Visual_Task))
    finantial_institutions = ListField(ReferenceField(Finantial_Institution))
    author_affiliations = ListField(EmbeddedDocumentField(Author_Affiliation))
    viticultural_aspects = StringField(max_length=50)
    research_goal = ListField(StringField())
    practical_contibution = StringField()
    isOnlyReference = BooleanField()
    citationsSearched = BooleanField()
    citedBy = ListField(StringField())
    #isLoadedBefore = BooleanField()
    bibliographyIsLoaded = BooleanField()
    references = ListField(StringField())
    #research_goal = ListField(StringField()) VARIETALES
    #research_goal = ListField(StringField()) SISTEMAS DE CONDUCCION