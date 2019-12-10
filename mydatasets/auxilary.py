# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# general imports
import re
import os
from django.shortcuts import render, render_to_response
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, date

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404
from django.views.generic import DetailView
from django.views.generic.edit import CreateView

from django.views.generic import UpdateView
from django.db.models import Q

from forms import DatasetForm, NeuronForm

from models import DatasetReview, Neuron, Version
from models import Dataset, Species, Gender
from models import Development, SlicingDirection, StainMethod
from models import Strain, ReconstructionSoftware, ObjectiveType
from models import ProtocolDesign, ExperimentCondition, OriginalFormat
from models import CellType1, CellType2, CellType3
from models import BrainRegion1, BrainRegion2, BrainRegion3
from models import SlicingThickness, Magnification
from models import Lab
from models import User
# from models import ExperimentalCondition
import csv
from django.conf import settings
from django.contrib import messages
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


import sqlite3
from sqlite3 import Error
from sshtunnel import SSHTunnelForwarder
# import MySQLdb as db
import pandas as pd
import psycopg2
import sys

# database connection values
# ssh variables
host = ''
localhost = ''
ssh_username = ''
ssh_password = ''

# database variables
user = ''
password = ''
database = ''

# adjust entries
def preprocess(entry, new_entry=None, default=""):
    # blanks should not be considered as not reported!
    # 7.5 fix
    if entry == "Moderately-Complete":
        return "Moderate"
    not_reported = "Not reported"
    if entry is None or len(str(entry)) == 0:
        if new_entry:
            return str(new_entry) + "*"
        return default
    return str(entry)

# generate csv file from a datasets
def dataset_to_csv(request, pk):
    not_reported = "Not reported"
    dataset = get_object_or_404(Dataset, pk=pk)
    if len(dataset.archive_name) > 0:
        file_name = preprocess(dataset.archive_name)
    else:
        file_name = "new_dataset"
    asterisked = False
    # info = tuple(open(os.path.join(settings.BASE_DIR, 'mydatasets/info.txt'), 'r').read().splitlines())
    info = list(open(os.path.join(settings.BASE_DIR, 'mydatasets/info.txt'), 'r').read().splitlines())
    to_write = [info]
    neurons = Neuron.objects.filter(dataset=dataset).order_by('-id')
    for grp in neurons: # 4 each row
        # title
        title = preprocess(grp.group_name)
        # number of neurons
        num_neurons = preprocess(grp.number_of_data_files)
        # neuron name
        neuron_name = ''
        # archive name
        archive = preprocess(grp.archive_name)
        # species
        species = preprocess(grp.species, grp.new_species)
        # stain
        strain = preprocess(grp.strain, grp.new_strain)
        # age setting
        if grp.age_type:
            max_age = preprocess(grp.max_age)
            age_scale = preprocess(grp.age_type)[0]
            min_age = preprocess(grp.min_age)
        else:
            max_age = age_scale = min_age = not_reported
        # weight setting
        if grp.min_weight == '' and grp.max_weight == '':
            min_weight = max_weight = not_reported
        else:
            min_weight = preprocess(grp.min_weight)
            max_weight = preprocess(grp.max_weight)
        # gender and age class
        age_classification = preprocess(grp.development_stage)
        gender = preprocess(grp.gender, grp.new_gender)
        # brain region
        region1 = preprocess(grp.brain_region1, grp.new_brain_region1, not_reported)
        region2 = preprocess(grp.brain_region2, grp.new_brain_region2, not_reported)
        # brain = [str(b) for b in grp.brain_region3.all()]
        # brain = BrainRegion3.objects.filter(id__in=grp.brain_region3_order)
        # print brain
        brain = []
        if grp.brain_region3_order is not None:
            for o in grp.brain_region3_order:
                if any(o in s for s in ['None', 'none']):
                    continue
                try:
                    brain.append(BrainRegion3.objects.get(id=o).region3)
                except BrainRegion3.DoesNotExist:
                    print '{}, Brain region 3 order and class mismatch!'.format(grp.group_name)
        else:
            brain = []# [str(b) for b in grp.brain_region3.all()] # consistancy with older archives! not anymore
        if grp.new_brain_region3 is not None:
            new_brain = grp.new_brain_region3.splitlines()
            for n in new_brain:
                if n in ['\n', '\r\n'] or n.isspace(): continue
                brain.append(n + '*')
        if len(brain) == 1:
            region3  = preprocess(brain[0], '', not_reported)
            region3B = not_reported
        elif len(brain) == 2:
            region3  = preprocess(brain[0], '', not_reported)
            region3B = preprocess(brain[1])
        elif len(brain) > 2:
            region3  = preprocess(brain[0], '', not_reported)
            region3B = ", ".join(brain[1:])
        else:
            region3 = preprocess(None, grp.new_brain_region3, not_reported)
            region3B = not_reported
        # cell type
        class1 = preprocess(grp.cell_type1, grp.new_cell_type1, not_reported)
        class2 = preprocess(grp.cell_type2, grp.new_cell_type2, not_reported)
        # cell = [str(c) for c in grp.cell_type3.all()]
        cell = []
        if grp.cell_type3_order is not None:
            for o in grp.cell_type3_order:
                if any(o in s for s in ['None', 'none']):
                    continue
                try:
                    cell.append(CellType3.objects.get(id=o).class3)
                except CellType3.DoesNotExist:
                    print '{}, celltype3 order and class mismatch!'.format(grp.group_name)
        else:
            cell = []# [str(c) for c in grp.cell_type3.all()] # consistancy! not anymore
        if grp.new_cell_type3 is not None:
            new_cell3 = grp.new_cell_type3.splitlines()
            for n in new_cell3:
                if n in ['\n', '\r\n'] or n.isspace(): continue
                cell.append(n + '*')
            # print new_cell3
        if len(cell) == 1:
            class3 = preprocess(cell[0], '', not_reported)
            class3B = not_reported
            class3C = not_reported
        elif len(cell) == 2:
            class3 = preprocess(cell[0], '', not_reported)
            class3B = preprocess(cell[1])
            class3C = not_reported
        elif len(cell) > 2:
            class3 = preprocess(cell[0], '', not_reported)
            class3B = preprocess(cell[1])
            class3C = ", ".join(cell[2:])
        else:
            class3 = preprocess(None, grp.new_cell_type3, not_reported)
            class3B = class3C = not_reported
        format = preprocess(grp.data_type, grp.new_data_type).split('.')[-1]
        protocol = preprocess(grp.experimental_protocol, grp.new_experimental_protocol)
        thickness = preprocess(grp.slice_tickness, grp.new_slice_tickness)
        slice_direction = preprocess(grp.slicing_direction, grp.new_slicing_direction)
        stain = preprocess(grp.stain, grp.new_stain)
        magnification = preprocess(grp.objective_magnification)
        objective = preprocess(grp.objective_type, grp.new_objective_type)
        reconstruction = preprocess(grp.reconstruction_software, grp.new_reconstruction_software)
        URL_reference = ''
        note = preprocess(grp.notes)
        celltype = ''
        expercond = preprocess(grp.experimental_condition, grp.new_experimental_condition)
        deposition_date = dataset.deposition_date.strftime('%m/%d/%Y')
        upload_date =  ''
        pmid = preprocess(dataset.identifier)
        code_intermed = ''
        shrinkage_reported = preprocess(grp.tissue_shrinkage)
        shrinkage_corrected = preprocess(grp.shrinkage_corrected)
        reported_value = preprocess(grp.reported_value)
        reported_xy = preprocess(grp.reported_xy)
        reported_z = preprocess(grp.reported_z)
        corrected_value = preprocess(grp.corrected_value)
        corrected_xy = preprocess(grp.corrected_xy)
        corrected_z = preprocess(grp.corrected_z)
        if grp.lab is not None and grp.lab_name == None and grp.institute == None and grp.address == None :
            acknowledgement =''
            address1 = ''
            address2 = ''
        elif grp.lab is not None and grp.lab_name is not None:
            acknowledgement = preprocess(grp.lab_name)
            address1 = preprocess(grp.institute)
            address2 = preprocess(grp.address)
        else:
            acknowledgement = preprocess(grp.lab_name) + '*'
            address1 = preprocess(grp.institute) + '*'
            address2 = preprocess(grp.address) + '*'
        # customize integrity
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
        else:
            physical_integrity = ""

        # write the above parameters into file! each row 4
        params = [ title, num_neurons, neuron_name, archive, \
        species, strain, max_age, age_scale, \
        min_age, min_weight, max_weight, age_classification, \
        gender, region1, region2, region3, \
        region3B, class1, class2, class3, \
        class3B, class3C, format, protocol, \
        thickness, slice_direction, stain, magnification, \
        objective, reconstruction, URL_reference, note, \
        celltype, expercond, deposition_date, upload_date, \
        pmid, code_intermed, shrinkage_reported, shrinkage_corrected, \
        reported_value, reported_xy, reported_z, corrected_value, \
        corrected_xy, corrected_z, acknowledgement, address1, \
        address2, physical_integrity]
        to_write.append(params)
        # check and see if there is any new terms before generating the csv file
        if (asterisked == False):
            # print asterisked
            for term in params:
                if '*' in term:
                    asterisked = True
                    break
                    # print 'asterisked', asterisked
    # write into csv
    response = HttpResponse(content_type = 'text/csv')
    if asterisked:
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(str(file_name)+str('_tmp'))
    else:
        response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(str(file_name))
    writer = csv.writer(response)
    nmo_csv_format = zip(*to_write)
    for line in nmo_csv_format:
        writer.writerow(line)

    return response

# proof new entry
def proof(request, pk, pkr):
    if request.method == 'POST':
        table  = request.POST['table']
        entry  = request.POST['entry']
        parent = request.POST['parent']
        parent1 = request.POST['parent1']
        lab = request.POST['lab']
        institute = request.POST['institute']
        address = request.POST['address']
    else:
        table  = ''
        entry  = ''
        parent = ''
        parent1 = ''
        lab = ''
        institute = ''
        address = ''

    dataset = get_object_or_404(Dataset, id=pkr)
    version = dataset.nmo_version
    if table == "Strain":
        par  = Species.objects.get(species=parent)
        Strain.objects.update_or_create(strain_name=entry, species=par, version=version)
        new = Strain.objects.get(strain_name=entry, species=par)
        neurons = Neuron.objects.filter(species=par, new_strain=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.strain = new
            nrn.new_strain = ''
            nrn.save()
    elif table == "Species":
        Species.objects.update_or_create(species=entry, version=version)
        new = Species.objects.get(species=entry)
        neurons = Neuron.objects.filter(new_species=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.species = new
            nrn.new_species = ''
            nrn.save()
    elif table == "Development":
        Development.objects.update_or_create(age_class=entry, version=version)
        new = Development.objects.get(age_class=entry)
        neurons = Neuron.objects.filter(new_development_stage=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.development_stage = new
            nrn.new_development_stage = ''
            nrn.save()
    elif table == "BrainRegion1":
        BrainRegion1.objects.update_or_create(region1=entry, version=version)
        new = BrainRegion1.objects.get(region1=entry)
        neurons = Neuron.objects.filter(new_brain_region1=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.brain_region1 = new
            nrn.new_brain_region1 = ''
            nrn.save()
    elif table == "BrainRegion2":
        par = BrainRegion1.objects.get(region1=parent)
        BrainRegion2.objects.update_or_create(region2=entry, region1=par, version=version)
        new = BrainRegion2.objects.get(region2=entry, region1=par)
        neurons = Neuron.objects.filter(brain_region1=par, new_brain_region2=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.brain_region2 = new
            nrn.new_brain_region2 = ''
            nrn.save()
    elif table == "BrainRegion3":
        par1 = BrainRegion1.objects.get(region1=parent1)
        par  = BrainRegion2.objects.get(region2=parent, region1=par1)
        BrainRegion3.objects.update_or_create(region3=entry, region2=par, region1=par1, version=version)
        new = BrainRegion3.objects.get(region3=entry, region2=par, region1=par1)
        neurons = Neuron.objects.filter(brain_region2=par, brain_region1=par1, new_brain_region3__icontains=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            # print new.id
            nrn.brain_region3.add(new) 
            nrn.brain_region3_order.append(new.id)
            nrn.new_brain_region3 = nrn.new_brain_region3.replace(entry, '')
            nrn.new_brain_region3 = os.linesep.join([s for s in nrn.new_brain_region3.splitlines() if s])
            nrn.save()
    elif table == "CellType1":
        CellType1.objects.update_or_create(class1=entry, version=version)
        new = CellType1.objects.get(class1=entry)
        neurons = Neuron.objects.filter(new_cell_type1=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.cell_type1 = new
            nrn.new_cell_type1 = ''
            nrn.save()
    elif table == "CellType2":
        par = CellType1.objects.get(class1=parent)
        CellType2.objects.update_or_create(class2=entry, class1=par, version=version)
        new = CellType2.objects.get(class2=entry, class1=par)
        neurons = Neuron.objects.filter(cell_type1=par, new_cell_type2=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.cell_type2 = new
            nrn.new_cell_type2 = ''
            nrn.save()
    elif table == "CellType3":
        par1 = CellType1.objects.get(class1=parent1)
        par = CellType2.objects.get(class2=parent, class1=par1)
        CellType3.objects.update_or_create(class3=entry, class2=par, class1=par1, version=version)
        new = CellType3.objects.get(class3=entry, class2=par, class1=par1)
        neurons = Neuron.objects.filter(cell_type2=par, cell_type1=par1, new_cell_type3__icontains=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.cell_type3.add(new)
            nrn.cell_type3_order.append(new.id)
            nrn.new_cell_type3 = nrn.new_cell_type3.replace(entry, '')
            nrn.new_cell_type3 = os.linesep.join([s for s in nrn.new_cell_type3.splitlines() if s])
            nrn.save()
    elif table == "ProtocolDesign":
        ProtocolDesign.objects.update_or_create(protocol=entry, version=version)
        new = ProtocolDesign.objects.get(protocol=entry)
        neurons = Neuron.objects.filter(new_experimental_protocol=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.experimental_protocol = new
            nrn.new_experimental_protocol = ''
            nrn.save()
    elif table == "ExperimentalCondition": 
        ExperimentCondition.objects.update_or_create(expercond=entry, version=version)
        new = ExperimentCondition.objects.get(expercond=entry)
        neurons = Neuron.objects.filter(new_experimental_condition=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.experimental_condition = new
            nrn.new_experimental_condition = ''
            nrn.save()
    elif table == "StainMethod":
        StainMethod.objects.update_or_create(stain=entry, version=version)
        new = StainMethod.objects.get(stain=entry)
        neurons = Neuron.objects.filter(new_stain=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.stain = new
            nrn.new_stain = ''
            nrn.save()
    elif table == "SlicingDirection":
        SlicingDirection.objects.update_or_create(slicing_direction=entry, version=version)
        new = SlicingDirection.objects.get(slicing_direction=entry)
        neurons = Neuron.objects.filter(new_slicing_direction=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.slicing_direction = new
            nrn.new_slicing_direction = ''
            nrn.save()
    elif table == "ReconstructionSoftware":
        ReconstructionSoftware.objects.update_or_create(reconstruction_software=entry, version=version)
        new = ReconstructionSoftware.objects.get(reconstruction_software=entry)
        neurons = Neuron.objects.filter(new_reconstruction_software=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.reconstruction_software = new
            nrn.new_reconstruction_software = ''
            nrn.save()
    elif table == "ObjectiveType":
        ObjectiveType.objects.update_or_create(objective_type=entry, version=version)
        new = ObjectiveType.objects.get(objective_type=entry)
        neurons = Neuron.objects.filter(new_objective_type=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.objective_type = new
            nrn.new_objective_type = ''
            nrn.save()
    elif table == "OriginalFormat":
        OriginalFormat.objects.update_or_create(original_format=entry, version=version)
        new = OriginalFormat.objects.get(original_format=entry)
        neurons = Neuron.objects.filter(new_data_type=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.data_type = new
            nrn.new_data_type = ''
            nrn.save()
    elif table == "SlicingThickness":
        SlicingThickness.objects.update_or_create(slice_thickness=entry, version=version)
        new = SlicingThickness.objects.get(slice_thickness=entry)
        neurons = Neuron.objects.filter(new_slice_tickness=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.slice_tickness = new
            nrn.new_slice_tickness = ''
            nrn.save()
    elif table == "Magnification":
        Magnification.objects.update_or_create(magnification=entry, version=version)
        new = Magnification.objects.get(magnification=entry)
        neurons = Neuron.objects.filter(new_objective_magnification=entry).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.objective_magnification = new
            nrn.new_objective_magnification = ''
            nrn.save()
    elif table == "Lab":
        Lab.objects.update_or_create(lab_name=lab, institute=institute, address=address, version=version)
        new = Lab.objects.get(lab_name=lab, institute=institute, address=address, version=version)
        neurons = Neuron.objects.filter(lab_name=lab, institute=institute, address=address).order_by('-id')
        messages.success(request, 'Term "{}" is successfully added to {}!'.format(str(entry), table))
        messages.success(request, '{} group(s) are affected!'.format(len(neurons)))
        for nrn in neurons:
            nrn.lab = new
            nrn.save()
    
    neuron = get_object_or_404(Neuron, pk=pk, dataset_id=pkr)
    neuron_list = Neuron.objects.filter(dataset=pkr).order_by('-id')
    context = {'neuron':neuron, 'neuron_list': neuron_list}
    return render(request, 'mydatasets/neuron_detail.html', context)

# bulk modify
def bulk_modify(request, pkr):
    dataset = get_object_or_404(Dataset, id=pkr)
    if request.method == 'POST':
        find  = request.POST['find']
        replace  = request.POST['replace']
        case_sensitive = request.POST.get('case_sensitive', False)
        checks = request.POST.getlist('checks[]')
        col_checks = request.POST.getlist('col_checks[]')
        # print 'checks', checks
    else:
        find, replace, case_sensitive  = '', '', ''
    if case_sensitive:
        flag = 1
    else:
        flag = 2

    neuron_list = Neuron.objects.filter(dataset=pkr).order_by('-id')
    version = dataset.nmo_version
    check_list = ['', '-', ' ', 'None', 'none', 'not reported', None]
    for neuron in neuron_list:
        # Group name
        entry = str(neuron.group_name).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'gp' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.group_name = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # Species
        entry = str(neuron.new_species).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'sp' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_species = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # Strain
        entry = str(neuron.new_strain).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'st' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_strain = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # Developmental Stage
        entry = str(neuron.new_development_stage).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'ds' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_development_stage = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # min age
        entry = str(neuron.min_age).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'ag' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.min_age = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # max age
        entry = str(neuron.max_age).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'ag' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.max_age = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # min weight
        entry = str(neuron.min_weight).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'wt' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.min_weight = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # min weight
        entry = str(neuron.max_weight).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'wt' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.max_weight = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_brain_region1
        entry = str(neuron.new_brain_region1).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'b1' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_brain_region1 = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_brain_region2
        entry = str(neuron.new_brain_region2).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'b2' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_brain_region2 = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_brain_region3
        entry = str(neuron.new_brain_region3).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'b3' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_brain_region3 = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_cell_type1
        entry = str(neuron.new_cell_type1).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'c1' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_cell_type1 = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_cell_type2
        entry = str(neuron.new_cell_type2).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'c2' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_cell_type2 = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_cell_type3
        entry = str(neuron.new_cell_type3).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'c3' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_cell_type3 = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_experimental_protocol
        entry = str(neuron.new_experimental_protocol).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'ep' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_experimental_protocol = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_experimental_condition
        entry = str(neuron.new_experimental_condition).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'ec' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_experimental_condition = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_stain
        entry = str(neuron.new_stain).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'str' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_stain = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_slice_tickness
        entry = str(neuron.new_slice_tickness).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'sth' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_slice_tickness = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_slicing_direction
        entry = str(neuron.new_slicing_direction).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'sd' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_slicing_direction = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_reconstruction_software
        entry = str(neuron.new_reconstruction_software).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'rs' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_reconstruction_software = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_objective_type
        entry = str(neuron.new_objective_type).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'ot' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_objective_type = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_objective_magnification
        entry = str(neuron.new_objective_magnification).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'om' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_objective_magnification = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # new_data_type
        entry = str(neuron.new_data_type).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'dt' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.new_data_type = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # lab_name
        entry = str(neuron.lab_name).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'ci' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.lab_name = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # institute
        entry = str(neuron.institute).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'ci' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.institute = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
        # address
        entry = str(neuron.address).strip()
        if entry.lower().find(find.lower()) >=0 and entry.lower() not in check_list and len(find) and str(neuron.id) in checks and 'ci' in col_checks:
            try:
                new_entry = re.sub(find, replace, entry, flags=flag)
                neuron.address = new_entry
                neuron.save()
                messages.success(request, 'Term "{}" in ({}) is successfully changed to "{}".'.format(entry, neuron.group_name, new_entry))
            except Exception as e:
                messages.error(request, 'Error while modifing {}! ({})'.format(entry, str(e)))
    
    # return to the page
    context = {'request': request,'dataset': dataset, 'neurons': neuron_list}
    return render(request, 'mydatasets/dataset_detail_a.html', context)

# bulk proof
def bulk_proof(request, pkr):
    # messages.success(request, 'Successful Request!')
    table  = ''
    entry  = ''
    parent = ''
    parent1 = ''
    lab = ''
    institute = ''
    address = ''

    dataset = get_object_or_404(Dataset, id=pkr)
    neuron_list = Neuron.objects.filter(dataset=pkr).order_by('-id')
    if not request.user.groups.filter(name = "Proof").exists():
        messages.error(request, 'This user ({}) does not have Proof privileges!'.format(request.user))
        context = {'request': request,'dataset': dataset, 'neurons': neuron_list}
        return render(request, 'mydatasets/dataset_detail_a.html', context)
    version = dataset.nmo_version
    check_list = ['', '-', ' ', 'None', 'none', 'not reported', None]
    for neuron in neuron_list:
        # Species
        entry = str(neuron.new_species).strip()
        neurons = Neuron.objects.filter(new_species=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons)>0:
            try:
                Species.objects.update_or_create(species=entry, version=version)
                new = Species.objects.get(species=entry)
                messages.success(request, 'Species "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.species = new
                    nrn.new_species = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # Strain
        entry = str(neuron.new_strain).strip()
        par  = Species.objects.filter(species=neuron.species).first()
        neurons = Neuron.objects.filter(species=par, new_strain=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons)>0:
            try:
                Strain.objects.update_or_create(strain_name=entry, species=par, version=version)
                new = Strain.objects.get(strain_name=entry, species=par)
                messages.success(request, 'Strain "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.strain = new
                    nrn.new_strain = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # Development
        entry = str(neuron.new_development_stage).strip()
        neurons = Neuron.objects.filter(new_development_stage=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons)>0:
            try:
                Development.objects.update_or_create(age_class=entry, version=version)
                new = Development.objects.get(age_class=entry)
                messages.success(request, 'Development "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.development_stage = new
                    nrn.new_development_stage = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # Brain region 1
        entry = str(neuron.new_brain_region1).strip()
        neurons = Neuron.objects.filter(new_brain_region1=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                BrainRegion1.objects.update_or_create(region1=entry, version=version)
                new = BrainRegion1.objects.get(region1=entry)
                messages.success(request, 'Brain region1 "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.brain_region1 = new
                    nrn.new_brain_region1 = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # Brain region 2
        entry = str(neuron.new_brain_region2).strip()
        par = BrainRegion1.objects.filter(region1=neuron.brain_region1).first()
        neurons = Neuron.objects.filter(brain_region1=par, new_brain_region2=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                BrainRegion2.objects.update_or_create(region2=entry, region1=par, version=version)
                new = BrainRegion2.objects.get(region2=entry, region1=par)
                messages.success(request, 'Brain region2 "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.brain_region2 = new
                    nrn.new_brain_region2 = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # Brain region 3
        entry = str(neuron.new_brain_region3).strip()
        par1 = BrainRegion1.objects.filter(region1=neuron.brain_region1).first()
        par  = BrainRegion2.objects.filter(region2=neuron.brain_region2, region1=par1).first()
        neurons = Neuron.objects.filter(brain_region2=par, brain_region1=par1, new_brain_region3__icontains=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                BrainRegion3.objects.update_or_create(region3=entry, region2=par, region1=par1, version=version)
                new = BrainRegion3.objects.get(region3=entry, region2=par, region1=par1)
                messages.success(request, 'Brain region3 "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    # print new.id
                    nrn.brain_region3.add(new) 
                    nrn.brain_region3_order.append(new.id)
                    nrn.new_brain_region3 = nrn.new_brain_region3.replace(entry, '')
                    nrn.new_brain_region3 = os.linesep.join([s for s in nrn.new_brain_region3.splitlines() if s])
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # celltype 1
        entry = str(neuron.new_cell_type1).strip()
        neurons = Neuron.objects.filter(new_cell_type1=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                CellType1.objects.update_or_create(class1=entry, version=version)
                new = CellType1.objects.get(class1=entry)
                messages.success(request, 'Celltype1 "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.cell_type1 = new
                    nrn.new_cell_type1 = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # celltype 2
        entry = str(neuron.new_cell_type2).strip()
        par = CellType1.objects.filter(class1=neuron.cell_type1).first()
        neurons = Neuron.objects.filter(cell_type1=par, new_cell_type2=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                CellType2.objects.update_or_create(class2=entry, class1=par, version=version)
                new = CellType2.objects.get(class2=entry, class1=par)
                messages.success(request, 'Celltype2 "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.cell_type2 = new
                    nrn.new_cell_type2 = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # celltype 3
        entry = str(neuron.new_cell_type3).strip()
        par1 = CellType1.objects.filter(class1=neuron.cell_type1).first()
        par = CellType2.objects.filter(class2=neuron.cell_type2, class1=par1).first()
        neurons = Neuron.objects.filter(cell_type2=par, cell_type1=par1, new_cell_type3__icontains=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                CellType3.objects.update_or_create(class3=entry, class2=par, class1=par1, version=version)
                new = CellType3.objects.get(class3=entry, class2=par, class1=par1)
                messages.success(request, 'Celltype2 "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.cell_type3.add(new)
                    nrn.cell_type3_order.append(new.id)
                    nrn.new_cell_type3 = nrn.new_cell_type3.replace(entry, '')
                    nrn.new_cell_type3 = os.linesep.join([s for s in nrn.new_cell_type3.splitlines() if s])
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # ProtocolDesign
        entry = str(neuron.new_experimental_protocol).strip()
        neurons = Neuron.objects.filter(new_experimental_protocol=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                ProtocolDesign.objects.update_or_create(protocol=entry, version=version)
                new = ProtocolDesign.objects.get(protocol=entry)
                messages.success(request, 'ProtocolDesign "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.experimental_protocol = new
                    nrn.new_experimental_protocol = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # Experimental condition
        entry = str(neuron.new_experimental_condition).strip()
        neurons = Neuron.objects.filter(new_experimental_condition=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                ExperimentCondition.objects.update_or_create(expercond=entry, version=version)
                new = ExperimentCondition.objects.get(expercond=entry)
                messages.success(request, 'ExperimentalCondition "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.experimental_condition = new
                    nrn.new_experimental_condition = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # StainMethod
        entry = str(neuron.new_stain).strip()
        neurons = Neuron.objects.filter(new_stain=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                StainMethod.objects.update_or_create(stain=entry, version=version)
                new = StainMethod.objects.get(stain=entry)
                messages.success(request, 'StainMethod "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.stain = new
                    nrn.new_stain = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # SlicingDirection
        entry = str(neuron.new_slicing_direction).strip()
        neurons = Neuron.objects.filter(new_slicing_direction=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                SlicingDirection.objects.update_or_create(slicing_direction=entry, version=version)
                new = SlicingDirection.objects.get(slicing_direction=entry)
                messages.success(request, 'SlicingDirection "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.slicing_direction = new
                    nrn.new_slicing_direction = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # ReconstructionSoftware
        entry = str(neuron.new_reconstruction_software).strip()
        neurons = Neuron.objects.filter(new_reconstruction_software=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                ReconstructionSoftware.objects.update_or_create(reconstruction_software=entry, version=version)
                new = ReconstructionSoftware.objects.get(reconstruction_software=entry)
                messages.success(request, 'ReconstructionSoftware "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.reconstruction_software = new
                    nrn.new_reconstruction_software = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # ObjectiveType
        entry = str(neuron.new_objective_type).strip()
        neurons = Neuron.objects.filter(new_objective_type=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                ObjectiveType.objects.update_or_create(objective_type=entry, version=version)
                new = ObjectiveType.objects.get(objective_type=entry)
                messages.success(request, 'ObjectiveType "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.objective_type = new
                    nrn.new_objective_type = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # OriginalFormat
        entry = str(neuron.new_data_type).strip()
        neurons = Neuron.objects.filter(new_data_type=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                OriginalFormat.objects.update_or_create(original_format=entry, version=version)
                new = OriginalFormat.objects.get(original_format=entry)
                messages.success(request, 'OriginalFormat "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.data_type = new
                    nrn.new_data_type = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # SlicingThickness
        entry = str(neuron.new_slice_tickness).strip()
        neurons = Neuron.objects.filter(new_slice_tickness=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                SlicingThickness.objects.update_or_create(slice_thickness=entry, version=version)
                new = SlicingThickness.objects.get(slice_thickness=entry)
                messages.success(request, 'SlicingThickness "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.slice_tickness = new
                    nrn.new_slice_tickness = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # Magnification
        entry = str(neuron.new_objective_magnification).strip()
        neurons = Neuron.objects.filter(new_objective_magnification=entry).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                entry = str(neuron.new_objective_magnification).strip()
                Magnification.objects.update_or_create(magnification=entry, version=version)
                new = Magnification.objects.get(magnification=entry)
                messages.success(request, 'Magnification "{}" is successfully added and {} group(s) are affected!'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.objective_magnification = new
                    nrn.new_objective_magnification = ''
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
        # Lab
        entry = str(neuron.lab_name).strip()
        neurons = Neuron.objects.filter(lab_name=neuron.lab_name, institute=neuron.institute, address=neuron.address).order_by('-id')
        if entry.lower() not in check_list and len(neurons) > 0:
            try:
                Lab.objects.update_or_create(lab_name=neuron.lab_name, institute=neuron.institute, address=neuron.address, version=version)
                new = Lab.objects.get(lab_name=neuron.lab_name, institute=neuron.institute, address=neuron.address, version=version)
                messages.success(request, 'Lab "{}" is successfully added and {} group(s) are affected! (Please note that Lab name stays in the table after approval for the consistancies with NMO)'.format(str(entry), len(neurons)))
                for nrn in neurons:
                    nrn.lab = new
                    nrn.save()
            except Exception as e:
                messages.error(request, 'Error while adding {} to the database! ({})'.format(entry, str(e)))
    
    # neuron = get_object_or_404(Neuron, pk=pk, dataset_id=pkr)
    neuron_list = Neuron.objects.filter(dataset=pkr).order_by('-id')
    context = {'request': request,'dataset': dataset, 'neurons': neuron_list}
    return render(request, 'mydatasets/dataset_detail_a.html', context)

# remove and update values in the tables
def manage_worker(action, table):
    msg = ''
    if action == 'Clean!':
        if table == "Strain":
            Strain.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "Species":
            Species.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "Development":
            Development.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "BrainRegion1":
            BrainRegion1.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "BrainRegion2":
            BrainRegion2.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "BrainRegion3":
            BrainRegion3.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "CellType1":
            CellType1.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "CellType2":
            CellType2.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "CellType3":
            CellType3.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "ProtocolDesign":
            ProtocolDesign.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "ExperimentCondition": 
            ExperimentCondition.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "StainMethod":
            StainMethod.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "SlicingDirection":
            SlicingDirection.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "ReconstructionSoftware":
            ReconstructionSoftware.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "ObjectiveType":
            ObjectiveType.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)

        elif table == "OriginalFormat":
            OriginalFormat.objects.all().delete()
            msg = '{} succesfully cleaned!'.format(table)
    # if the action is update
    elif action == 'Update!':
        if table == "Strain":
            try:
                # print 'debugging Strain!'
                relations = query("SELECT distinctrow species_id, strain_id FROM nmdbDev.{}".format('neuron'))
                relation_dict = {}
                for idx, row in relations.iterrows():
                    key, val = row['species_id'], row['strain_id']
                    if key in relation_dict:
                        relation_dict[key].append(val)
                    else:
                        relation_dict[row['species_id']] = [val]
                        # relation_dict[row['species_id']] = [row['species_id']] # bug, fixed!
                species = query("SELECT * FROM nmdbDev.{}".format('species'))
                species_dict = species.set_index('species_id').to_dict()['species']
                strain = query("SELECT * FROM nmdbDev.{}".format('animal_strain'))
                strain_dict = strain.set_index('strain_id').to_dict()['strain_name']
                for key, val in relation_dict.iteritems():
                    try:
                        strains = map(strain_dict.get, val)
                        # insert
                        for idx, strain in enumerate(strains):
                            if strain == 'Not reported' or strain == '':
                                continue
                            spc = species_dict[key]
                            spc_id  = Species.objects.get(species=spc)
                            strain_id = val[idx]
                            Strain.objects.update_or_create(species=spc_id, strain_id=strain_id, strain_name=strain)
                    except Exception as e:
                        print str(e)
                msg = '{} {} succesfully updated!'.format(len(strain_dict), table)
            except Exception as e:
                print("type error: " + str(e))
                msg = "An error occured while update! [{}]".format(str(e))

        elif table == "Species":
            try:
                nmo_table = update_table(nmo_tbl='species', dev='False')
                for idx, row in nmo_table.iterrows():
                    items = [None if x=='' else x for x in row.tolist()]
                    obj = Species.objects.filter(species=items[1]).first()
                    if obj != None:
                        # sp.version=sp.version)
                        obj.species=items[1]
                        obj.species_id=items[0]
                        obj.save()
                    else:
                        Species.objects.update_or_create(species_id=items[0], species=items[1])
                msg = '{} {} succesfully updated!'.format(len(nmo_table), table)
            except Exception as e:
                print("type error: " + str(e))
                msg = "An error occured while update! [{}]".format(str(e))

        elif table == "Development":
            nmo_table = update_table(nmo_tbl='age_classification', dev='False')
            for idx, row in nmo_table.iterrows():
                items = [None if x=='' else x for x in row.tolist()]
                Development.objects.update_or_create(age_class_id=items[0], age_class=items[1])
            msg = '{} {} succesfully updated!'.format(len(nmo_table), table)
            # Development.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)

        elif table == "BrainRegion1":
            # BrainRegion1.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)
            msg = 'please update using the old method!'

        elif table == "BrainRegion2":
            # BrainRegion2.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)
            msg = 'please update using the old method!'

        elif table == "BrainRegion3":
            # BrainRegion3.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)
            msg = 'please update using the old method!'

        elif table == "CellType1":
            # CellType1.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)
            msg = 'please update using the old method!'

        elif table == "CellType2":
            # CellType2.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)
            msg = 'please update using the old method!'

        elif table == "CellType3":
            # CellType3.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)
            msg = 'please update using the old method!'

        elif table == "ProtocolDesign":
            nmo_table = update_table(nmo_tbl='protocol_design', dev='False')
            for idx, row in nmo_table.iterrows():
                items = [None if x=='' else x for x in row.tolist()]
                obj = ProtocolDesign.objects.filter(protocol=items[1]).first()
                if obj != None:
                    obj.protocol=items[1]
                    obj.protocol_id=items[0]
                    obj.save()
                else:
                    ProtocolDesign.objects.update_or_create(protocol_id=items[0], protocol=items[1])
            msg = '{} {} succesfully updated!'.format(len(nmo_table), table)
            # ProtocolDesign.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)

        elif table == "ExperimentCondition":
            nmo_table = update_table(nmo_tbl='experimentcondition', dev='False')
            for idx, row in nmo_table.iterrows():
                items = [None if x=='' else x for x in row.tolist()]
                obj = ExperimentCondition.objects.filter(expercond=items[1]).first()
                if obj != None:
                    obj.expercond=items[1]
                    obj.expercond_id=items[0]
                    obj.save()
                else:
                    ExperimentCondition.objects.update_or_create(expercond_id=items[0], expercond=items[1])
            msg = '{} {} succesfully updated!'.format(len(nmo_table), table)
            # ExperimentCondition.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)

        elif table == "StainMethod":
            nmo_table = update_table(nmo_tbl='staining_method', dev='False')
            for idx, row in nmo_table.iterrows():
                items = [None if x=='' else x for x in row.tolist()]
                obj = StainMethod.objects.filter(stain=items[1]).first()
                if obj != None:
                    obj.stain=items[1]
                    obj.stain_id=items[0]
                    obj.save()
                else:
                    StainMethod.objects.update_or_create(stain_id=items[0], stain=items[1])
            msg = '{} {} succesfully updated!'.format(len(nmo_table), table)
            # StainMethod.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)

        elif table == "SlicingDirection":
            nmo_table = update_table(nmo_tbl='slicing_direction', dev='False')
            for idx, row in nmo_table.iterrows():
                items = [None if x=='' else x for x in row.tolist()]
                obj = SlicingDirection.objects.filter(slicing_direction=items[1]).first()
                if obj != None:
                    obj.slicing_direction=items[1]
                    obj.direction_id=items[0]
                    obj.save()
                else:
                    SlicingDirection.objects.update_or_create(direction_id=items[0], slicing_direction=items[1])
            msg = '{} {} succesfully updated!'.format(len(nmo_table), table)
            # SlicingDirection.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)

        elif table == "ReconstructionSoftware":
            nmo_table = update_table(nmo_tbl='reconstruction', dev='False')
            for idx, row in nmo_table.iterrows():
                items = [None if x=='' else x for x in row.tolist()]
                obj = ReconstructionSoftware.objects.filter(reconstruction_software=items[1]).first()
                if obj != None:
                    obj.reconstruction_software=items[1]
                    obj.reconstruction_id=items[0]
                    obj.save()
                else:
                    ReconstructionSoftware.objects.update_or_create(reconstruction_id=items[0], reconstruction_software=items[1])
            msg = '{} {} succesfully updated!'.format(len(nmo_table), table)
            # ReconstructionSoftware.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)

        elif table == "ObjectiveType":
            nmo_table = update_table(nmo_tbl='objective_type', dev='False')
            for idx, row in nmo_table.iterrows():
                items = [None if x=='' else x for x in row.tolist()]
                obj = ObjectiveType.objects.filter(objective_type=items[1]).first()
                if obj != None:
                    obj.objective_type=items[1]
                    obj.objective_id=items[0]
                    obj.save()
                else:
                  ObjectiveType.objects.update_or_create(objective_id=items[0], objective_type=items[1])
            msg = '{} {} succesfully updated!'.format(len(nmo_table), table)
            # ObjectiveType.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)

        elif table == "OriginalFormat":
            nmo_table = update_table(nmo_tbl='original_format', dev='False')
            for idx, row in nmo_table.iterrows():
                items = [None if x=='' else x for x in row.tolist()]
                obj = OriginalFormat.objects.filter(original_format=items[1]).first()
                if obj != None:
                    obj.original_format=items[1]
                    obj.original_format_id=items[0]
                    obj.save()
                else:
                    OriginalFormat.objects.update_or_create(original_format_id=items[0], original_format=items[1])
            msg = '{} {} succesfully updated!'.format(len(nmo_table), table)
            # OriginalFormat.objects.all().delete()
            # msg = '{} succesfully updated!'.format(table)
    return msg


def update_table(**kwargs):
    """
    get latest changes from nmo database and, 
    update the local dataset with the latest changes
    """
         
    current_nmo = query("SELECT * FROM nmdbDev.{}".format(kwargs['nmo_tbl']))
    col_names = ", ".join(list(current_nmo))
    # if kwargs['dev']:  print 'column names:', col_names, '\n', '======================='
    return current_nmo
    # items = [None if x=='' else x for x in row.tolist()]


def query(q):
    with SSHTunnelForwarder(
        (host, 22),
        ssh_username=ssh_username,
        ssh_password=ssh_password,
        remote_bind_address=(localhost, 3306)
    ) as server:
        conn = db.connect(host=localhost,
                               port=server.local_bind_port,
                               user=user,
                               passwd=password,
                               db=database)

        return pd.read_sql_query(q, conn)

# filter special characters, unwanted spaces, and enters from a string
def preProcess(string):
    string = re.sub('[^A-Za-z0-9 (.,:)[-]]+', '', string)
    string = re.sub('\s\s+', ' ', string)
    return string

# send email
def send_msg(user, archive_name, url):
    # gmail credentials:
    email = 'ADD YOURS'
    password = 'ADD YOURS'

    # find users from the admin view
    send_to_emails = list(User.objects.filter(groups__name='Email-alert').values_list('email', flat=True))
    # print list(qs)
    
    subject = 'New Archive! ({})'.format(archive_name)
    messageHTML = """<p>
        <span style="color: #496dd0">{}</span> added a new dataset in the portal. <br>
        Here is the url: {}
    </p>""".format(user, url)
    messagePlain = 'A new archive has been added in the portal. Please view the main page. http://cng-nmo-meta.orc.gmu.edu'

    msg = MIMEMultipart('alternative')
    msg['From'] = email
    msg['To'] = ', '.join(send_to_emails)
    msg['Subject'] = subject

    msg.attach(MIMEText(messagePlain, 'plain'))
    msg.attach(MIMEText(messageHTML, 'html'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(email, password)
        text = msg.as_string() # You now need to convert the MIMEMultipart object to a string to send
        server.sendmail(email, send_to_emails, text)
        server.quit()
    except Exception as e:
        print("type error: " + str(e))
        msg = "An error occured while sending email! [{}]".format(str(e))
