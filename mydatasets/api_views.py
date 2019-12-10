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

from rest_framework import viewsets
from . import models
from . import serializers
from .permissions import IsOwner
from rest_framework.response import Response
from rest_framework import status
from rest_framework import views
import json



class LabViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.Lab.objects.all()
    serializer_class = serializers.LabSerializer
    # permission_classes = [IsOwner]
    def post(self,request):
        return Response({"Success": "The metadata dosen't accept inputs via API at this time!"}, status=status.HTTP_201_CREATED)

class DatasetViewset(viewsets.ReadOnlyModelViewSet):
    queryset = models.Dataset.objects.all()
    serializer_class = serializers.DatasetSerializer
    # permission_classes = [IsOwner]
    def post(self,request):
        return Response({"Success": "The metadata dosen't accept inputs via API at this time!"}, status=status.HTTP_201_CREATED)
    def get_queryset(self):
        # qs = super().get_queryset()
        qs = models.Dataset.objects.all()
        # version = str(self.request.query_params.get('version')).lower()
        version = self.request.query_params.get('version', None)
        if version is None:
            return qs
        try:
            return qs.filter(nmo_version=version)
        except:
            # pass
            return qs

class NewTermsViewset(viewsets.ViewSet):
    # queryset = []
    serializer_class = serializers.NewtermsSerializer
    def list(self, request):
        version = self.request.query_params.get('version', '7.5')
        terms = extract_new_terms(version)
        new_terms = [{"version":terms['version'],
         "new_species": terms['new_species'],
         "new_strain": terms['new_strain'],
         "new_brain_region1": terms['new_brain_region1'],
         "new_brain_region2": terms['new_brain_region2'],
         "new_brain_region3": terms['new_brain_region3'],
         "new_cell_type1": terms['new_cell_type1'],
         "new_cell_type2": terms['new_cell_type2'],
         "new_cell_type3": terms['new_cell_type3'],
         "new_stain": terms['new_stain'],
         "new_stain": terms['new_stain'],
         "new_slicing_direction": terms['new_slicing_direction'],
         "new_reconstruction_software": terms['new_reconstruction_software'],
         "new_protocol": terms['new_protocol'],
         "new_original_format": terms['new_original_format'],
         "new_objective_type": terms['new_objective_type'],
         "new_expercond": terms['new_expercond'],
         "new_thickness": terms['new_thickness'],
         "new_magnification": terms['new_magnification'],
         }]
        results = serializers.NewtermsSerializer(new_terms, many=True).data
        return Response(results)


def extract_new_terms(ver = '7.6'):
    terms = dict({'version':ver})
    # species
    new_species = models.Species.objects.filter(version=ver).order_by('species')
    terms['new_species'] = ''
    for n in new_species:
        id = list(models.Neuron.objects.filter(species=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_species'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_species'] = terms['new_species'].rstrip('; ')
    # strain
    new_strain = models.Strain.objects.filter(version=ver).order_by('strain_name')
    terms['new_strain'] = ''
    for n in new_strain:
        id = list(models.Neuron.objects.filter(strain=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_strain'] += str("<{}>{} ({})".format(str(n.species), str(n), ", ".join(dataset_names))) + "; "
    terms['new_strain'] = terms['new_strain'].rstrip('; ')
    # brain region 1
    new_brain_region1 = models.BrainRegion1.objects.filter(version=ver).order_by('region1')
    terms['new_brain_region1'] = ''
    for n in new_brain_region1:
        id = list(models.Neuron.objects.filter(brain_region1=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_brain_region1'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_brain_region1'] = terms['new_brain_region1'].rstrip('; ')
    # brain region 2
    new_brain_region2 = models.BrainRegion2.objects.filter(version=ver).order_by('region2')
    terms['new_brain_region2'] = ''
    for n in new_brain_region2:
        id = list(models.Neuron.objects.filter(brain_region2=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_brain_region2'] += str("<{}>{} ({})".format(n.region1,str(n), ", ".join(dataset_names))) + "; "
    terms['new_brain_region2'] = terms['new_brain_region2'].rstrip('; ')
    # brain region 3
    new_brain_region3 = models.BrainRegion3.objects.filter(version=ver).order_by('region3')
    terms['new_brain_region3'] = ''
    for n in new_brain_region3:
        id = list(models.Neuron.objects.filter(brain_region3=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_brain_region3'] += str("<{}>{} ({})".format("{}/{}".format(n.region1,n.region2), n, ", ".join(dataset_names))) + "; "
    terms['new_brain_region3'] = terms['new_brain_region3'].rstrip('; ')
    # cell type 1
    new_cell_type1 = models.CellType1.objects.filter(version=ver).order_by('class1')
    terms['new_cell_type1'] = ''
    for n in new_cell_type1:
        id = list(models.Neuron.objects.filter(cell_type1=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_cell_type1'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_cell_type1'] = terms['new_cell_type1'].rstrip('; ')
    # cell type 2
    new_cell_type2 = models.CellType2.objects.filter(version=ver).order_by('class2')
    terms['new_cell_type2'] = ''
    for n in new_cell_type2:
        id = list(models.Neuron.objects.filter(cell_type2=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_cell_type2'] += str("<{}>{} ({})".format(n.class1, str(n), ", ".join(dataset_names))) + "; "
    terms['new_cell_type2'] = terms['new_cell_type2'].rstrip('; ')
    # cell type 3
    new_cell_type3 = models.CellType3.objects.filter(version=ver).order_by('class3')
    terms['new_cell_type3'] = ''
    for n in new_cell_type3:
        id = list(models.Neuron.objects.filter(cell_type3=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_cell_type3'] += str("<{}>{} ({})".format("{}/{}".format(n.class1,n.class2), n, ", ".join(dataset_names))) + "; "
    terms['new_cell_type3'] = terms['new_cell_type3'].rstrip('; ')
    # stain
    new_stain = models.StainMethod.objects.filter(version=ver).order_by('stain')
    terms['new_stain'] = ''
    for n in new_stain:
        id = list(models.Neuron.objects.filter(stain=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_stain'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_stain'] = terms['new_stain'].rstrip('; ')
    # slicing direction
    new_slicing_direction = models.SlicingDirection.objects.filter(version=ver).order_by('slicing_direction')
    terms['new_slicing_direction'] = ''
    for n in new_slicing_direction:
        id = list(models.Neuron.objects.filter(slicing_direction=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_slicing_direction'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_slicing_direction'] = terms['new_slicing_direction'].rstrip('; ')
    # reconstruction software
    new_reconstruction_software = models.ReconstructionSoftware.objects.filter(version=ver).order_by('reconstruction_software')
    terms['new_reconstruction_software'] = ''
    for n in new_reconstruction_software:
        id = list(models.Neuron.objects.filter(reconstruction_software=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_reconstruction_software'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_reconstruction_software'] = terms['new_reconstruction_software'].rstrip('; ')
    # protocol
    new_protocol = models.ProtocolDesign.objects.filter(version=ver).order_by('protocol')
    terms['new_protocol'] = ''
    for n in new_protocol:
        id = list(models.Neuron.objects.filter(experimental_protocol=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_protocol'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_protocol'] = terms['new_protocol'].rstrip('; ')
    # original format
    new_original_format = models.OriginalFormat.objects.filter(version=ver).order_by('original_format')
    terms['new_original_format'] = ''
    for n in new_original_format:
        id = list(models.Neuron.objects.filter(data_type=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_original_format'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_original_format'] = terms['new_original_format'].rstrip('; ')
    # objective type
    new_objective_type = models.ObjectiveType.objects.filter(version=ver).order_by('objective_type')
    terms['new_objective_type'] = ''
    for n in new_objective_type:
        id = list(models.Neuron.objects.filter(objective_type=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_objective_type'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_objective_type'] = terms['new_objective_type'].rstrip('; ')
    # experiment condition
    new_expercond = models.ExperimentCondition.objects.filter(version=ver).order_by('expercond')
    terms['new_expercond'] = ''
    for n in new_expercond:
        id = list(models.Neuron.objects.filter(experimental_condition=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_expercond'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_expercond'] = terms['new_expercond'].rstrip('; ')
    # slicing thickness
    new_thickness = models.SlicingThickness.objects.filter(version=ver).order_by('slice_thickness')
    terms['new_thickness'] = ''
    for n in new_thickness: #typo here:
        id = list(models.Neuron.objects.filter(slice_tickness=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_thickness'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_thickness'] = terms['new_thickness'].rstrip('; ')
    # magnification
    new_magnification = models.Magnification.objects.filter(version=ver).order_by('magnification')
    terms['new_magnification'] = ''
    for n in new_magnification: #typo here:
        id = list(models.Neuron.objects.filter(objective_magnification=n).values_list('dataset_id', flat=True).distinct())
        datasets = models.Dataset.objects.filter(id__in=id)
        dataset_names = []
        for d in datasets:
            dataset_names.append(str(d))
        terms['new_magnification'] += str("{} ({})".format(str(n), ", ".join(dataset_names))) + "; "
    terms['new_magnification'] = terms['new_magnification'].rstrip('; ')
    
    return terms