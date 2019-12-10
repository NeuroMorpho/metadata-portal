# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
from datetime import date, datetime

from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
# from django.contrib.postgres.fields import HStoreField
from django.core.urlresolvers import reverse
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid
# Create your models here.
from django.db import models

reload(sys)  
sys.setdefaultencoding('utf-8')

from rest_framework.response import Response
from rest_framework import serializers
from . import models

from auxilary import preprocess

# list of labs in the portal
class LabSerializer(serializers.ModelSerializer):
    # owner = serializers.HiddenField(
    #     default=serializers.CurrentUserDefault()
    # ) # in case we want to have input from the api in future
    class Meta:
        model = models.Lab
        fields = ['id', 'lab_name', 'institute', 'address', 'date', 'version']
        read_only_fields = fields

class NeuronListingField(serializers.RelatedField):
    def to_representation(self, grp):
        group = dict()
        group['group_ID'] = grp.id
        group['title'] = preprocess(grp.group_name)
        group['num_neurons'] = preprocess(grp.number_of_data_files)
        group['archive'] = preprocess(grp.archive_name)
        group['species'] = preprocess(grp.species, grp.new_species)
        group['strain'] = preprocess(grp.strain, grp.new_strain)
        if grp.age_type:
            group['max_age'] = preprocess(grp.max_age)
            group['age_scale'] = preprocess(grp.age_type)[0]
            group['min_age'] = preprocess(grp.min_age)
        else:
            group['max_age'] = "Not reported"
            group['age_scale'] = "Not reported"
            group['min_age'] = "Not reported"
        if grp.min_weight == '' and grp.max_weight == '':
            group['min_weight'] = "Not reported"
            group['max_weight'] = "Not reported"
        else:
            group['min_weight'] = preprocess(grp.min_weight)
            group['max_weight'] = preprocess(grp.max_weight)
        group['age_classification'] = preprocess(grp.development_stage)
        group['gender'] = preprocess(grp.gender, grp.new_gender)
        group['region1'] = preprocess(grp.brain_region1, grp.new_brain_region1, "Not reported")
        group['region2'] = preprocess(grp.brain_region2, grp.new_brain_region2, "Not reported")
        brain = []
        if grp.brain_region3_order is not None:
            for o in grp.brain_region3_order:
                try:
                    brain.append(models.BrainRegion3.objects.get(id=o).region3)
                except:
                    pass
            group['region3'] = ', '.join(brain)
        else:
            group['region3'] = "Not reported"
        group['class1'] = preprocess(grp.cell_type1, grp.new_cell_type1, "Not reported")
        group['class2'] = preprocess(grp.cell_type2, grp.new_cell_type2, "Not reported")
        cell = []
        if grp.cell_type3_order is not None:
            for o in grp.cell_type3_order:
                try:
                    cell.append(models.CellType3.objects.get(id=o).class3)
                except:
                    pass
            group['class3'] = ', '.join(cell)
        else:
            group['class3'] = "Not reported"
        group['format'] = preprocess(grp.data_type, grp.new_data_type).split('.')[-1]
        group['protocol'] = preprocess(grp.experimental_protocol, grp.new_experimental_protocol)
        group['thickness'] = preprocess(grp.slice_tickness, grp.new_slice_tickness)
        group['slice_direction'] = preprocess(grp.slicing_direction, grp.new_slicing_direction)
        group['stain'] = preprocess(grp.stain, grp.new_stain)
        group['magnification'] = preprocess(grp.objective_magnification)
        group['objective'] = preprocess(grp.objective_type, grp.new_objective_type)
        group['reconstruction'] = preprocess(grp.reconstruction_software, grp.new_reconstruction_software)
        group['note'] = preprocess(grp.notes)
        group['expercond'] = preprocess(grp.experimental_condition, grp.new_experimental_condition)
        # group['deposition_date'] = dataset.deposition_date.strftime('%m/%d/%Y')
        # group['pmid'] = preprocess(dataset.identifier)
        group['code_intermed'] = ''
        group['shrinkage_reported'] = preprocess(grp.tissue_shrinkage)
        group['shrinkage_corrected'] = preprocess(grp.shrinkage_corrected)
        group['reported_value'] = preprocess(grp.reported_value)
        group['reported_xy'] = preprocess(grp.reported_xy)
        group['reported_z'] = preprocess(grp.reported_z)
        group['corrected_value'] = preprocess(grp.corrected_value)
        group['corrected_xy'] = preprocess(grp.corrected_xy)
        group['corrected_z'] = preprocess(grp.corrected_z)
        group['lab'] = preprocess(grp.lab)
        physical_integrity = ""
        if grp.axon and grp.dendrites and grp.dendrites_integrity and grp.axon_integrity:
            physical_integrity = "Dendrites {} & Axon {}".format(preprocess(grp.dendrites_integrity), preprocess(grp.axon_integrity))
        elif grp.dendrites and grp.dendrites_integrity:
            physical_integrity = "Dendrites {}".format(preprocess(grp.dendrites_integrity))
        elif grp.axon and grp.axon_integrity:
            physical_integrity = "Axon {}".format(preprocess(grp.axon_integrity))
        elif grp.neurites and grp.processes and grp.neurites_integrity and grp.processes_integrity:
            physical_integrity = "Neurites {} & Processes {}".format(preprocess(grp.neurites_integrity), preprocess(grp.processes_integrity))
        elif grp.processes and grp.processes_integrity:
            physical_integrity = "Processes {}".format(preprocess(grp.processes_integrity))
        elif grp.neurites and grp.neurites_integrity:
            physical_integrity = "Neurites {}".format(preprocess(grp.neurites_integrity))
        group['physical_integrity'] = physical_integrity

        return group

# list of datasets in the portal
class DatasetSerializer(serializers.ModelSerializer):
    neurons = NeuronListingField(many=True, read_only=True)
    # neurons = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = models.Dataset
        fields = ["id", "archive_name", "identifier", "authors", "url",
         "nmo_version", "date", "deposition_date", "notes", "grant_id",
          "pdf", "excel", "reconstructions", "ext", "neurons"]
        # fields = ('id', 'nmo_version', 'neurons')
        read_only_fields = fields
    def validate(self, validated_data):
        validated_data['pdf'] = 'tst'
        return validated_data
    def __init__(self, *args, **kwargs):
        # fields = kwargs.pop('fields', None)
        super(DatasetSerializer, self).__init__(*args, **kwargs)
        try:
            # pass
            self.fields['pdf'] = serializers.CharField(max_length=1000)
            self.fields['excel'] = serializers.CharField(max_length=1000)
            self.fields['reconstructions'] = serializers.CharField(max_length=1000)
        except KeyError:
            pass

# list of new terms in the portal
class NewtermsSerializer(serializers.Serializer):
    version = serializers.CharField(max_length=100)
    new_species = serializers.CharField(max_length=1000)
    new_strain = serializers.CharField(max_length=1000)
    new_brain_region1 = serializers.CharField(max_length=1000)
    new_brain_region2 = serializers.CharField(max_length=1000)
    new_brain_region3 = serializers.CharField(max_length=1000)
    new_cell_type1 = serializers.CharField(max_length=1000)
    new_cell_type2 = serializers.CharField(max_length=1000)
    new_cell_type3 = serializers.CharField(max_length=1000)
    new_stain = serializers.CharField(max_length=1000)
    new_slicing_direction = serializers.CharField(max_length=1000)
    new_reconstruction_software = serializers.CharField(max_length=1000)
    new_protocol = serializers.CharField(max_length=1000)
    new_original_format = serializers.CharField(max_length=1000)
    new_objective_type = serializers.CharField(max_length=1000)
    new_expercond = serializers.CharField(max_length=1000)
    new_thickness = serializers.CharField(max_length=1000)
    new_magnification = serializers.CharField(max_length=1000)