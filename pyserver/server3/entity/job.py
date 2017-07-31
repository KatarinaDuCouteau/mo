#!/usr/bin/python
# -*- coding: UTF-8 -*-
"""
# @author   : Tianyi Zhang
# @version  : 1.0
# @date     : 2017-05-24 11:00pm
# @function : Getting all of the job of statics analysis
# @running  : python
# Further to FIXME of None
"""

from mongoengine import Document
from mongoengine import ReferenceField
from mongoengine import ListField
from mongoengine import IntField
from mongoengine import DateTimeField
from mongoengine import DictField
from mongoengine import CASCADE

# from server3.entity import StagingDataSet
# from server3.entity import Toolkit
# from server3.entity import Model
# from server3.entity import Project

STATUS = (
    (0, 'start'),
    (100, 'processing'),
    (200, 'completed'),
    (300, 'interrupted')
)


class Job(Document):
    model = ReferenceField('Model')
    toolkit = ReferenceField('Toolkit')
    staging_data_set = ReferenceField('StagingDataSet')
    status = IntField(choices=STATUS, required=True)
    fields = ListField()
    create_time = DateTimeField(required=True)
    updated_time = DateTimeField()
    project = ReferenceField('Project', reverse_delete_rule=CASCADE)
    params = DictField()
    file = ReferenceField('File')
