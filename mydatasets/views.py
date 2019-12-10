# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import re
import csv
import os
# Create your views here.
from datetime import date, datetime

# zip file
import zipfile
import re
from collections import Counter
from itertools import chain

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
# for upload
from django.core.files.storage import FileSystemStorage
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import (get_object_or_404, redirect, render,
                              render_to_response)
from django.views.generic import DetailView, UpdateView
from django.views.generic.edit import CreateView

import auxilary
from auxilary import dataset_to_csv, proof, manage_worker, preProcess, send_msg
from forms import DatasetForm, NeuronForm
from models import (BrainRegion1, BrainRegion2, BrainRegion3, CellType1,
                    CellType2, CellType3, Dataset, Development ,DatasetReview, Neuron,
                    Species, Version, Strain, StainMethod, SlicingDirection,
                    ReconstructionSoftware, ProtocolDesign, OriginalFormat,
                    ObjectiveType, ExperimentCondition, Magnification, SlicingThickness, Lab)

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.core.urlresolvers import resolve
from django.contrib import messages
from django.http import JsonResponse
import timeit
from django.contrib.postgres.search import TrigramSimilarity, TrigramDistance




class DatasetDetail(DetailView):
  model = Dataset
  template_name = 'mydatasets/dataset_detail.html'

  def get_context_data(self, **kwargs):
    context = super(DatasetDetail, self).get_context_data(**kwargs)
    return context

def dataset_detail(request, pk):
    template = 'mydatasets/dataset_detail.html'
    dataset = get_object_or_404(Dataset, pk=pk)
    neuron = Neuron.objects.filter(dataset=pk).order_by('-id')
    edited_neuron = Neuron.objects.filter(dataset=pk).order_by('-edit_date')[:5]
    paginator = Paginator(neuron, 25)
    page = request.GET.get('page')
    if dataset.ext:
        folders = zip(dataset.folders_names, dataset.folders_file_counts)
    else:
        folders = False
    try:
        neurons = paginator.page(page)
    except PageNotAnInteger:
        neurons = paginator.page(1)
    except EmptyPage:
        neurons = paginator.page(paginator.num_pages)
    context = {
        'request': request,
        'dataset': dataset,
        'neurons': neurons,
        'edited_neuron':edited_neuron,
        'page': page,
        'folders': folders,
    }
    return render(request, template, context)

def dataset_detail_advanced(request, pk):
    template = 'mydatasets/dataset_detail_a.html'
    dataset = get_object_or_404(Dataset, pk=pk)
    neuron = Neuron.objects.filter(dataset=pk).order_by('-id')
    edited_neuron = Neuron.objects.filter(dataset=pk).order_by('-edit_date')[:5]
    if dataset.ext:
        folders = zip(dataset.folders_names, dataset.folders_file_counts)
    else:
        folders = False
    context = {
        'request': request,
        'dataset': dataset,
        'neurons': neuron,
        'edited_neuron':edited_neuron,
        # 'page': page,
        'folders': folders,
    }
    return render(request, template, context)

class DatasetCreate(CreateView):
  model = Dataset
  template_name = 'mydatasets/form.html'
  form_class = DatasetForm
#   print 'test'
  def get_success_url(self):
    # print "a dataset is successfully posted!"
    return reverse('mydatasets:dataset_detail', kwargs={'pk': self.object.pk})


# add a new dataset
@login_required
def add_dataset(request):
    # print 'here'
    if request.method == 'POST':
        form = DatasetForm(data = request.POST)
        if form.is_valid():
            # print form.cleaned_data['grant_id']
            dataset = form.save(commit=False)
            # print 'depo: ', dataset.deposition_date
            dataset.user = request.user
            dataset.grant_id = preProcess(dataset.grant_id)
            if request.user.id == 5: # nmo-author
                # print request.user.id
                dataset.public = True
            dataset.save()
            # form.save_m2m()
            
            # send email:
            send_msg(request.user, dataset.archive_name, str(request.build_absolute_uri()).replace('create2/$', str(dataset.pk)))
            # print '-----------the ting:', dataset.pk, str(request.build_absolute_uri()).replace('create2', str(dataset.pk))
            return redirect('mydatasets:dataset_detail', pk=dataset.pk)
        else:
            print 'form is not valid!'
    else:
        form = DatasetForm()
    context = {'form':form, 'add': True, 'dataset':True}

    # return
    return render(request, 'mydatasets/form.html', context)

# edit a dataset
@login_required
def edit_dataset(request, pk):
    dataset = get_object_or_404(Dataset, pk=pk)
    # print 'info: ', preProcess(dataset.grant_id)
    dataset.grant_id = preProcess(dataset.grant_id)
    if dataset.user != request.user and not request.user.is_superuser:
        raise PermissionDenied
    if request.method == 'POST':
        form = DatasetForm(instance = dataset, data = request.POST)
        if form.is_valid():
            form.save()
            return redirect('mydatasets:dataset_detail', pk=pk)
    else:
        form = DatasetForm(instance=dataset)
    context = {'form': form, 'add': False, 'dataset':True}
    return render(request, 'mydatasets/form.html', context)

# get list of all datasets
def dataset_list(request):
    template = 'mydatasets/dataset_list.html'
    ready, ongoing = None, None
    if request.user.is_superuser:
        dataset = Dataset.objects.filter(set_archive=False).order_by('-date')
        ready = len(Dataset.objects.filter(set_archive=False, review=True))
        ongoing = len(dataset) - ready - 1 # ignore the sample one
    elif request.user.is_anonymous():
        dataset = Dataset.objects.filter(set_archive=False, public=True).order_by('-date')
        # dataset = Dataset.objects.filter(set_archive=False, user=request.user).order_by('-date')
    else:
        dataset = Dataset.objects.filter(set_archive=False, public=True).order_by('-date')
        dataset |= Dataset.objects.filter(set_archive=False, user=request.user).order_by('-date')

    # paginator = Paginator(dataset, 15)
    # page = request.GET.get('page')
    # try:
    #     datasets = paginator.page(page)
    # except PageNotAnInteger:
    #     datasets = paginator.page(1)
    # except EmptyPage:
    #     datasets = paginator.page(paginator.num_pages)
    context = {
            'datasets': dataset,
            'ready': ready,
            'ongoing':ongoing,
            # 'page': page,
        }
    return render(request, template, context)

# get list of archive datasets
def archive_list(request):
    template = 'mydatasets/dataset_list.html'
    datasets = Dataset.objects.filter(set_archive=True).order_by('-date')
    context = {
            'datasets': datasets,
            # 'page': page,
            'archive': True,
        }
    return render(request, template, context)


class NeuronCreate(CreateView):
  model = Neuron
  template_name = 'mydatasets/form.html'
  form_class = NeuronForm

  def get_success_url(self):
      return reverse('mydatasets:dataset_detail', kwargs={'pk': self.kwargs['pk']})

  def form_valid(self, form): # this funtion is needed for saving purpus
      form.instance.user = self.request.user
      form.instance.dataset = Dataset.objects.get(id=self.kwargs['pk'])
      return super(NeuronCreate, self).form_valid(form)

class NeuronUpdate(UpdateView):
  model = Neuron
  template_name = 'mydatasets/form.html'
  form_class = NeuronForm

  def get_success_url(self):
    #   print self.object.dataset_id
    #   print "a group of neuron is successfully updated!"
      return reverse('mydatasets:dataset_detail', kwargs={'pk': self.object.dataset_id})

# add a new group
@login_required
def add_neuron(request, pk):
    dataset_name = Dataset.objects.get(id=pk).archive_name
    if request.method == 'POST':
        form = NeuronForm(data = request.POST)
        # print form.visible_fields
        if form.is_valid():
            neuron = form.save(commit=False)
            neuron.user = request.user
            neuron.dataset = Dataset.objects.get(id=pk)
            neuron.save()
            # neuron.save_m2m()
            # return redirect('mydatasets:dataset_detail', pk=pk)
            return neuron_detail(request, pk=neuron.pk, pkr=pk) # stay in the nueron page
    else:
        form = NeuronForm()
        # print 'test'
        # print form.axon_integrity
    context = {'form':form, 'add': True, 'neuron':True, 'pk':0, 'pkr':pk, 'dataset_name':dataset_name}
    return render(request, 'mydatasets/metadata_form.html', context)

def neuron_detail(request, pk, pkr):
    template_name='mydatasets/neuron_detail.html'
    neuron = get_object_or_404(Neuron, pk=pk, dataset_id=pkr)
    neuron_list = Neuron.objects.filter(dataset=pkr).order_by('-id') #.values_list('id', flat=True)
    context = {'neuron': neuron, 'neuron_list': neuron_list}
    return render(request, template_name, context)

# add a new group - for authors, without login and just via a link!
def add_neuron_author(request, pk):
    # depricated
    pass

# edit a neuron group
@login_required 
def edit_neuron(request, pk, pkr):
    if pk == '0': # new group is not saved yet!
        return add_neuron(request, pkr)
    propagate = request.POST.get('propagate', False)
    save_and_next = request.POST.get('save_and_next', False)
    neuron = get_object_or_404(Neuron, pk=pk, dataset_id=pkr)
    neuron.edit_date = datetime.now()
    if neuron.user != request.user and not request.user.is_superuser:
        print 'an author is making change in dataset {}, group {}'.format(pkr, pk)
    if request.method == 'POST':
        form = NeuronForm(instance = neuron, data = request.POST)
        if form.is_valid():
            form.save() # commit changes
            if propagate:
                groups = Neuron.objects.filter(dataset=pkr)
                for grp in groups:
                    if grp.id == neuron.id:
                        continue # skip the current one
                    for entry in form.changed_data:
                        grp.__setattr__( entry, form.cleaned_data[entry])
                    grp.save()
                messages.success(request, 'The change is propagated to {} groups!'.format(len(groups)))
                form = NeuronForm(instance=neuron)
                context = {'form': form, 'add': False, 'neuron':True, 'pk':pk, 'pkr':pkr, 'dataset_name':neuron.dataset.archive_name, 'group':neuron}
                return render(request, 'mydatasets/metadata_form.html', context)
            if save_and_next:  # save and next button
                print 'next!, ', save_and_next
                index = None
                neurons = Neuron.objects.filter(dataset=pkr).order_by('-id') # 
                for idx, itm in enumerate(neurons):
                    if itm == neuron:
                        index = idx
                if index == len(neurons)-1:
                    return redirect('mydatasets:dataset_detail', pk=pkr)
                tmp_neur = neurons[index+1]
                return redirect('mydatasets:neuron_edit', pk=tmp_neur.id, pkr=pkr)
            # return to normal
            # return redirect('mydatasets:dataset_detail', pk=pkr)
            return neuron_detail(request, pk=pk, pkr=pkr) # stay in neuron
    else:
        form = NeuronForm(instance=neuron)
    context = {'form': form, 'add': False, 'neuron':True, 'pk':pk, 'pkr':pkr, 'dataset_name':neuron.dataset.archive_name, 'group':neuron}
    return render(request, 'mydatasets/metadata_form.html', context)

# @login_required 
def prepopulate(request, pk, pkr):
    # find previous neuron for overpopulate
    print 'propagate'
    index = None
    neuron = get_object_or_404(Neuron, pk=pk, dataset_id=pkr)
    neurons = Neuron.objects.filter(dataset=pkr).order_by('-id') # 
    for idx, itm in enumerate(neurons):
        if itm == neuron:
            index = idx
    if 0 == index:
        tmp_neur = neurons[index]
    else:
        tmp_neur = neurons[index-1]
    form = NeuronForm(instance=tmp_neur)
    context = {'form': form, 'add': False, 'neuron':True, 'pk':pk, 'pkr':pkr}
    return render(request, 'mydatasets/metadata_form.html', context)

# propagate changes to all groups
# this function is not called, kept just in case -- to be removed in future
@login_required
def change_propagate(request, pk, pkr):
    # print pkr, pk
    neuron = get_object_or_404(Neuron, pk=pk, dataset_id=pkr)
    if neuron.user != request.user and not request.user.is_superuser:
        raise PermissionDenied
    if request.method == 'POST':
        # print 'edit ', request.method
        form = NeuronForm(instance = neuron, data = request.POST)
        # print form.changed_data
        if form.is_valid():
            form.save() # commit changes
            groups = Neuron.objects.filter(dataset=pkr)
            for grp in groups:
                if grp.id == neuron.id:
                    continue # skip the current one
                for entry in form.changed_data:
                    grp.__setattr__( entry, form[entry].value())
                    # print grp[entry].value()
                    grp.save()
                    # grp.save_m2m()
            # return to normal
            return redirect('mydatasets:dataset_detail', pk=pkr)
    else:
        # print 'else - edit ', request.method
        form = NeuronForm(instance=neuron)
    context = {'form': form, 'add': False, 'neuron':True, 'neuron':True, 'pk':pk, 'pkr':pkr}
    # print 'val= ', form['brain_region3'].value(), 'type= ', type(form['brain_region3'].value())
    # for f in form.fields['species'].choices: 
    #     print f[0], f[0] == int(form['species'].value())
    return render(request, 'mydatasets/metadata_form.html', context)

# proof entry
@login_required
def proof_entry(request, pk, pkr):
    return proof(request, pk, pkr)

@login_required
def bulk_proof(request, pkr):
    return auxilary.bulk_proof(request, pkr)

@login_required
def bulk_modify(request, pkr):
    return auxilary.bulk_modify(request, pkr)

# duplicate a dataset
@login_required
def dataset_duplicate(request, pkr):
    my_dataset = Dataset.objects.get(id=pkr)
    neurons = Neuron.objects.filter(dataset=my_dataset).all()
    parent_id, my_dataset.id = my_dataset.id ,None
    my_dataset.archive_name = xstr(my_dataset.archive_name) + " [DUPLICATED]"
    my_dataset.date = datetime.now()
    my_dataset.review = False
    my_dataset.set_archive = False
    my_dataset.public = False
    my_dataset.pdf = None
    my_dataset.excel = None
    my_dataset.save()
    for neuron in neurons:
        neuron.id = None
        neuron.dataset = my_dataset
        neuron.save()
        # neuron.save_m2m()
    return HttpResponseRedirect(reverse('mydatasets:dataset_list'))

# change review status
@login_required
def dataset_status(request, pk):
    my_dataset = Dataset.objects.get(id=pk)
    if my_dataset.review:
        my_dataset.review = False
    else:
        my_dataset.review = True
    my_dataset.save()
    return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(my_dataset.id,)))

# change archive status
@login_required
def dataset_archive_status(request, pk):
    my_dataset = Dataset.objects.get(id=pk)
    if my_dataset.set_archive:
        my_dataset.set_archive = False
    else:
        my_dataset.set_archive = True
    my_dataset.save()
    return HttpResponseRedirect(reverse('mydatasets:dataset_list'))
    # return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(my_dataset.id,)))

# change public status
@login_required
def dataset_public_status(request, pk):
    my_dataset = Dataset.objects.get(id=pk)
    if my_dataset.public:
        my_dataset.public = False
    else:
        my_dataset.public = True
    my_dataset.save()
    return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(my_dataset.id,)))

# duplicate a group of neuron
@login_required
def neuron_duplicate(request, pk, pkr):
    my_neuron = Neuron.objects.get(pk=pk)
    # print 'before ', my_neuron.cell_type3.all()
    cell3, brain3 = my_neuron.cell_type3.all(), my_neuron.brain_region3.all()
    my_neuron.id = None # to save a new
    my_neuron.group_name = xstr(my_neuron.group_name) + " [Duplicated]"
    my_neuron.save()
    my_neuron.cell_type3.add(*cell3)
    my_neuron.brain_region3.add(*brain3)
    my_neuron.save()
    # my_neuron.save_m2m()
    # print 'after ', my_neuron.cell_type3.all()
    return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(my_neuron.dataset_id,)))

# delete a group of neuron
@login_required
def neuron_delete(request, pk, pkr):
    my_neuron = Neuron.objects.get(pk=pk)
    my_neuron.delete()
    return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(my_neuron.dataset_id,)))

# delete all groups of neurons
@login_required
def neuron_groups_delete(request, pk):
    my_dataset = Dataset.objects.get(id=pk)
    neurons = Neuron.objects.filter(dataset=my_dataset).all()
    for neuron in neurons:
        neuron.delete()
    return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(pk,)))

# delete reconstruction file
@login_required
def reconstruction_delete(request, pk):
    my_dataset = Dataset.objects.get(id=pk)
    my_dataset.reconstructions = ""
    my_dataset.ext = ""
    my_dataset.folders_names = []
    my_dataset.folders_file_counts = []
    my_dataset.save()
    return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(pk,)))

# make groups based on the file
@login_required
def make_groups(request, pk):
    my_dataset = Dataset.objects.get(id=pk)
    ext = my_dataset.ext
    folder_names = my_dataset.folders_names
    folder_counts = my_dataset.folders_file_counts
    for fol, cnt in zip(folder_names, folder_counts):
        Neuron.objects.create(user = request.user, group_name = fol, number_of_data_files=cnt, dataset = my_dataset, description = "").save()
        # print 'making groups'
    return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(pk,)))

# delete a datasets
@login_required
def delete_dataset(request, pk):
    # print('deleting a dataset')
    dataset = get_object_or_404(Dataset, pk=pk)
    # print 'dataset is successfully retrieved!', dataset
    dataset.delete()
    return HttpResponseRedirect(reverse('mydatasets:dataset_list'))

# generate csv file from a datasets
@login_required
def generate_csv(request, pk):
    return dataset_to_csv(request, pk)

# search
def search(request):
    template = 'mydatasets/search_results.html'
    if 'q' in request.GET and request.GET['q']:
        query = request.GET['q']
        if query == 'all' or query == 'All':
            datasets = Dataset.objects.all()
        else:
            datasets = Dataset.objects.filter(Q(archive_name__icontains=query) | Q(identifier__icontains=query) | Q(authors__icontains=query))
        context = {
            'datasets': datasets,
            'query': query,
        }
        return render(request, template, context)
    else:
        context = {
            # 'datasets': [],
            'query': '?',
        }
        return render(request, template, context)
        # return HttpResponse('nothing found!')

# add a new review
@login_required
def review(request, pk):
  dataset = get_object_or_404(Dataset, pk=pk)
  review = DatasetReview(
      comment=request.POST['comment'],
      user=request.user,
      dataset=dataset)
  review.save()
  return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(dataset.id,)))

@login_required
def delete_review(request, pkr, pk):
    dataset = get_object_or_404(Dataset, pk=pkr)
    review = get_object_or_404(DatasetReview, pk=pk)
    review.delete()
    # review.save()
    return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(dataset.id,)))

# about page
def about(request):
    template = 'mydatasets/about.html'
    versions = Version.objects.all().order_by('-date')
    context = {
        'request':  request,
        'versions': versions,
    }
    return render(request, template, context)

# load secondry, (smart filtering)
def second_level(request):
    multi_select = False
    # print 'in changing function!'
    template = 'mydatasets/next_level.html'
    level_id = request.GET.get('SelectValue')
    parent1 = request.GET.get('parent1')
    # print level_id, type(level_id), parent1, type(parent1)
    SelectName = request.GET.get('SelectName')
    if SelectName == 'cell_type1':
        next_level = CellType2.objects.filter(class1 = level_id).order_by('class2')
    elif SelectName == 'cell_type2':
        next_level = CellType3.objects.filter(class1 = parent1, class2 = level_id).order_by('class3')
        multi_select = True
    elif SelectName == 'brain_region1':
        next_level = BrainRegion2.objects.filter(region1 = level_id).order_by('region2')
        # print "{} are filtered!".format(len(next_level))
        # multi_select = True
    elif SelectName == 'brain_region2':
        next_level = BrainRegion3.objects.filter(region1 = parent1, region2 = level_id).order_by('region3')
        multi_select = True
    elif SelectName == 'species':
        next_level = Strain.objects.filter(species = level_id).order_by('strain_name')
        # print "{} are filtered!".format(len(next_level))
    else:
        next_level = []
    context = {
        'request': request,
        'next_level': next_level,
        'multi_select': multi_select,
    }
    return render(request, template, context)

# count the number of groups to be affected
def count_groups(request):
    template = 'mydatasets/next_level.html'
    dataset_id = request.GET.get('dataset_id', None)
    neurons = Neuron.objects.filter(dataset=dataset_id)
    group_count = len(neurons)
    # print group_count
    context = {
        # 'request': request,
        'group_count': group_count,
    }
    return JsonResponse(context)

# help page
# @login_required
def help(request):
    template = 'mydatasets/help.html'
    context = {}
    return render(request, template, context)

# generate list of labs
@login_required
def labs(request):
    if request.method == 'GET':
        version = request.GET.get('version', None)
    labs = Lab.objects.all()
    if version is not None:
        labs = Lab.objects.filter(version=version)
    template = 'mydatasets/labs.html'
    context = {}
    context['labs'] = labs
    context['request'] = request
    return render(request, template, context)

def search(request):
    start = timeit.default_timer()
    if request.method == 'GET':
        query = request.GET.get('query', '')
    template = 'mydatasets/search.html'

    dist = 0.75
    sp = Species.objects.annotate(distance=TrigramDistance('species', query),).filter(distance__lte=dist).order_by('distance')
    st = Strain.objects.annotate(distance=TrigramDistance('strain_name', query),).filter(distance__lte=dist).order_by('distance')
    dv = Development.objects.annotate(distance=TrigramDistance('age_class', query),).filter(distance__lte=dist).order_by('distance')
    b1 = BrainRegion1.objects.annotate(distance=TrigramDistance('region1', query),).filter(distance__lte=dist).order_by('distance')
    b2 = BrainRegion2.objects.annotate(distance=TrigramDistance('region2', query),).filter(distance__lte=dist).order_by('distance')
    b3 = BrainRegion3.objects.annotate(distance=TrigramDistance('region3', query),).filter(distance__lte=dist).order_by('distance')
    c1 = CellType1.objects.annotate(distance=TrigramDistance('class1', query),).filter(distance__lte=dist).order_by('distance')
    c2 = CellType2.objects.annotate(distance=TrigramDistance('class2', query),).filter(distance__lte=dist).order_by('distance')
    c3 = CellType3.objects.annotate(distance=TrigramDistance('class3', query),).filter(distance__lte=dist).order_by('distance')
    sd = SlicingDirection.objects.annotate(distance=TrigramDistance('slicing_direction', query),).filter(distance__lte=dist).order_by('distance')
    sm = StainMethod.objects.annotate(distance=TrigramDistance('stain', query),).filter(distance__lte=dist).order_by('distance')
    rs = ReconstructionSoftware.objects.annotate(distance=TrigramDistance('reconstruction_software', query),).filter(distance__lte=dist).order_by('distance')
    ot = ObjectiveType.objects.annotate(distance=TrigramDistance('objective_type', query),).filter(distance__lte=dist).order_by('distance')
    pd = ProtocolDesign.objects.annotate(distance=TrigramDistance('protocol', query),).filter(distance__lte=dist).order_by('distance')
    ec = ExperimentCondition.objects.annotate(distance=TrigramDistance('expercond', query),).filter(distance__lte=dist).order_by('distance')
    of = OriginalFormat.objects.annotate(distance=TrigramDistance('original_format', query),).filter(distance__lte=dist).order_by('distance')
    mg = Magnification.objects.annotate(distance=TrigramDistance('magnification', query),).filter(distance__lte=dist).order_by('distance')
    sk = SlicingThickness.objects.annotate(distance=TrigramDistance('slice_thickness', query),).filter(distance__lte=dist).order_by('distance')
    lb = Lab.objects.annotate(distance=TrigramDistance('lab_name', query),).filter(distance__lte=dist).order_by('distance')
    
    # for s in sp:
    #     print s.distance

    # data = chain(sp, st, dv, b1, b2, b3, c1, c2, c3,\
    #     sd, sm, rs, ot, pd, ec, of, mg, sk, lb)

    sorted_data = sorted(chain(sp, st, dv, b1, b2, b3, c1, c2, c3, sd, sm, rs, ot, pd, ec, of, mg, sk, lb), key=lambda obj: obj.distance)

    context = {}
    context['data'] = sorted_data
    context['request'] = request
    context['query'] = query
    context['runtime'] = timeit.default_timer() - start
    context['hits'] = len(list(chain(sp, st, dv, b1, b2, b3, c1, c2, c3, sd, sm, rs, ot, pd, ec, of, mg, sk, lb)))
    return render(request, template, context)

# generate list of new terms
@login_required
def version_new_terms(request):
    if request.method == 'GET':
        version = request.GET.get('version', '7.5')
        # print version
    template = 'mydatasets/new_terms.html'
    data = {}
    
    new_species = Species.objects.filter(version=version).order_by('species')
    for n in new_species:
        id = list(Neuron.objects.filter(species=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_strain  = Strain.objects.filter(version=version).order_by('strain_name')
    for n in new_strain:
        id = list(Neuron.objects.filter(strain=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_region1 = BrainRegion1.objects.filter(version=version).order_by('region1')
    for n in new_region1:
        id = list(Neuron.objects.filter(brain_region1=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_region2 = BrainRegion2.objects.filter(version=version).order_by('region2')
    for n in new_region2:
        id = list(Neuron.objects.filter(brain_region2=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_region3 = BrainRegion3.objects.filter(version=version).order_by('region3')
    for n in new_region3:
        id = list(Neuron.objects.filter(brain_region3=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_class1 = CellType1.objects.filter(version=version).order_by('class1')
    for n in new_class1:
        id = list(Neuron.objects.filter(cell_type1=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_class2 = CellType2.objects.filter(version=version).order_by('class2')
    for n in new_class2:
        id = list(Neuron.objects.filter(cell_type2=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_class3 = CellType3.objects.filter(version=version).order_by('class3')
    for n in new_class3:
        id = list(Neuron.objects.filter(cell_type3=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_stain  = StainMethod.objects.filter(version=version).order_by('stain')
    for n in new_stain:
        id = list(Neuron.objects.filter(stain=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_slicing_direction = SlicingDirection.objects.filter(version=version).order_by('slicing_direction')
    for n in new_slicing_direction:
        id = list(Neuron.objects.filter(slicing_direction=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_reconstruction_software = ReconstructionSoftware.objects.filter(version=version).order_by('reconstruction_software')
    for n in new_reconstruction_software:
        id = list(Neuron.objects.filter(reconstruction_software=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_protocol  = ProtocolDesign.objects.filter(version=version).order_by('protocol')
    for n in new_protocol:
        id = list(Neuron.objects.filter(experimental_protocol=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_original_format = OriginalFormat.objects.filter(version=version).order_by('original_format')
    for n in new_original_format:
        id = list(Neuron.objects.filter(data_type=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_objective_type = ObjectiveType.objects.filter(version=version).order_by('objective_type')
    for n in new_objective_type:
        id = list(Neuron.objects.filter(objective_type=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_expercond = ExperimentCondition.objects.filter(version=version).order_by('expercond')
    for n in new_expercond:
        id = list(Neuron.objects.filter(experimental_condition=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_thickness = SlicingThickness.objects.filter(version=version).order_by('slice_thickness')
    for n in new_thickness: #typo here:
        id = list(Neuron.objects.filter(slice_tickness=n).values_list('dataset_id', flat=True).distinct())
        # print id
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    new_magnification = Magnification.objects.filter(version=version).order_by('magnification')
    for n in new_magnification:
        id = list(Neuron.objects.filter(objective_magnification=n).values_list('dataset_id', flat=True).distinct())
        datasets = Dataset.objects.filter(id__in=id)
        data[str(n)] = datasets
    context = {
        # 'request': request,
        'version': version,
        'new_species': new_species,
        'new_strain':  new_strain,
        'new_region1': new_region1,
        'new_region2': new_region2,
        'new_region3': new_region3,
        'new_class1':  new_class1,
        'new_class2':  new_class2,
        'new_class3':  new_class3,
        'new_stain':   new_stain,
        'new_slicing_direction': new_slicing_direction,
        'new_reconstruction_software': new_reconstruction_software,
        'new_protocol': new_protocol,
        'new_original_format': new_original_format,
        'new_objective_type': new_objective_type,
        'new_expercond': new_expercond,
        'new_thickness': new_thickness,
        'new_magnification':new_magnification,
    }
    # print context
    context['data'] = data
    context['request'] = request
    return render(request, template, context)

# upload
@login_required # so that authors can enter data!
def upload(request, pk):
    # print 'running', request.FILES['pdf']
    filepath = request.FILES.get('pdf', False) or request.FILES.get('excel', False) or request.FILES.get('reconstructions', False)
    # my_dataset = Dataset.objects.get(id=pk)
    my_dataset = Dataset.objects.get(id=pk)
    neurons = Neuron.objects.filter(dataset=my_dataset).all()
    path = 'media/' + str(my_dataset.identifier) + '-' + my_dataset.archive_name + '/' # location='/media/[photos...]'
    if request.method == 'POST' and filepath:
        file_type = request.POST.get('filetype')
        # print type(file_type)
        fs = FileSystemStorage(location=path)
        if file_type == 'pdf':
            myfile = request.FILES['pdf']
            filename = fs.save(myfile.name, myfile)
            adr = fs.url(filename)
            my_dataset.pdf = adr.replace('/media/', path)
            # print my_dataset.pdf
        elif file_type == 'excel':
            myfile = request.FILES['excel']
            filename = fs.save(myfile.name, myfile)
            my_dataset.excel = fs.url(filename).replace("/media/", path)
            # print 'excel!'
        elif file_type == 'reconstructions':
            myfile = request.FILES['reconstructions']
            filename = fs.save(myfile.name, myfile)
            my_dataset.reconstructions = fs.url(filename).replace("/media/", path)
            my_dataset.ext = ""
            my_dataset.folders_names = []
            my_dataset.folders_file_counts = []
            my_dataset.save()
            messages.success(request, 'Reconstruction file was uploaded successfully!')
            # create groups based on the files
#            if len(neurons) == 0:
            try:
                zip = zipfile.ZipFile(myfile)
                folder_names = zip.namelist()
                ext, fol_names, fol_counts = extract_info(folder_names)
                my_dataset.ext = ext
                my_dataset.folders_names = fol_names
                my_dataset.folders_file_counts = fol_counts
                # print ext, fol_names, fol_counts
                my_dataset.save()
                messages.success(request, 'Experimental groups are successfully extracted based on the uploaded file!')
            except Exception as e:
                messages.error(request, 'Error while making the groups! Please upload a single zip file cointaining different groups of your experiment!')
                print('error while making groups')
                print('error: ' + str(e))
            # print 'reconst upload!
        # print fs.url(filename)
        my_dataset.save()
    return HttpResponseRedirect(reverse('mydatasets:dataset_detail', args=(my_dataset.id,)))

def xstr(s):
    if s is None:
        return ''
    return str(s)

# clean and update tables
@login_required
def manage(request):
    template = 'mydatasets/update.html'
    if request.method == 'GET':
        action = request.GET.get('action', 'None')
        table  = request.GET.get('table', 'None')
    try:
        msg = manage_worker(action, table, )
    except Exception as e:
        print("type error: " + str(e))
        msg = 'An error has occurred! [{}]'.format(str(e))
    # Species.objects.all().delete()
    context = {'msg':msg, }
    return render(request, template, context)

def extract_info(fol_list):
    # returns extention, folder name, and number of files
    if len(fol_list) == 0:
        return 
    fol_list = [s for s in fol_list if '.' in s]
    if len(fol_list) == 0:
        print 'files dont have any extention'
        return 
    ext = fol_list[0].split('.')[-1]
    fol_list = [re.findall(r'/(.*?)/', s)[0] for s in fol_list]
    fol_counts = dict(Counter(fol_list))
    # return ext, fol_counts # dict return
    return ext, fol_counts.keys(), fol_counts.values() # list return

def handler404(request):
    return render(request, '404.html', status=404)

def handler500(request):
    return render(request, '500.html', status=500)


