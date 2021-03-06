# -*- coding: UTF-8 -*-
from mongoengine import DynamicDocument
from mongoengine import ReferenceField

# from server3.entity import StagingDataSet


class StagingData(DynamicDocument):
    staging_data_set = ReferenceField('StagingDataSet', required=True)
