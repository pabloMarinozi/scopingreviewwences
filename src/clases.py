#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 13:03:16 2020

@author: pablo
"""


from mongoengine import Document,EmbeddedDocument
from mongoengine import StringField,IntField,ListField,BooleanField,URLField,ReferenceField,EmbeddedDocumentField


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
    
    
class Institution(Document):
    name = StringField(required=True, primary_key=True)
    #country = StringField(required=True)

class Finantial_Institution(Document):
    name = StringField(required=True, primary_key=True)
    country = StringField(required=True)

class Author(Document):
    name = StringField(required=True, primary_key=True)
    scopusID = StringField()

class Author_Affiliation(EmbeddedDocument):
    institution = ReferenceField(Institution)
    author = ReferenceField(Author)
    
# class Inclusion(EmbeddedDocument):
#     inclusion = BooleanField(required=True)
#     user = StringField(required=True)
#     criteria = ListField(StringField())
        
class Paper(Document):
    title = StringField(required=True)
    abstract = StringField(required=True)
    doi = StringField(required=True, primary_key=True)
    inclusion1 = BooleanField()
    user_inclusion1 = StringField()
    criteria_inclusion1 = ListField(StringField())
    inclusion2 = BooleanField()
    user_inclusion2 = StringField()
    criteria_inclusion2 = ListField(StringField())
    keywords = ListField(StringField(max_length=50))
    publication_month = IntField(min_value=1, max_value=12)
    publication_year = IntField(min_value=1950, max_value=2020)
    visual_tasks = ListField(EmbeddedDocumentField(Visual_Task))
    finantial_institutions = ListField(ReferenceField(Finantial_Institution))
    author_affiliations = ListField(EmbeddedDocumentField(Author_Affiliation))
    viticultural_aspects = StringField(max_length=50)
    research_goal = ListField(StringField())
    practical_contibution = StringField()
    

