from django.conf.urls import url
from django.utils import timezone
from django.views.generic import DetailView, ListView, UpdateView

from models import Dataset, Neuron
from forms import DatasetForm, NeuronForm
from views import *
from views import DatasetCreate, NeuronCreate, DatasetDetail, NeuronUpdate
from views import neuron_duplicate
from views import add_dataset, edit_dataset
from views import add_neuron, edit_neuron
from views import add_neuron_author
from views import generate_csv
from views import neuron_delete
from views import delete_dataset
from views import search
from views import review
from views import delete_review
from views import dataset_list
from views import dataset_detail
from views import dataset_detail_advanced
from views import about
from views import dataset_duplicate
from views import proof_entry
from views import dataset_status
from views import upload
from views import change_propagate
from views import dataset_archive_status
from views import archive_list
from views import version_new_terms
from views import manage
from views import dataset_public_status
from views import prepopulate
from views import neuron_groups_delete
from views import reconstruction_delete
from views import make_groups
from views import labs
from views import help
from views import count_groups
from views import neuron_detail
from views import bulk_proof
from views import bulk_modify
from views import search
from views import handler404, handler500

# from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy


urlpatterns = [

	# list all the available datasets and sort them based on time
	url(r'^$', dataset_list, name='dataset_list'),

	# Search in dataset
	url(r'^search/?$', search, name = 'search'),

	# dataset details, ex.: /mydatasets/dataset/1/
    url(r'^datasets/(?P<pk>\d+)/$', dataset_detail, name='dataset_detail'),
	
	# dataset details, ex.: /mydatasets/dataset/1/
    url(r'^datasets2/(?P<pk>\d+)/$', dataset_detail_advanced, name='dataset_detail_advanced'),

	# dataset neuron details, ex: /mydatasets/dataset/1/neurons/1/
    # url(r'^datasets/(?P<pkr>\d+)/neuron/(?P<pk>\d+)/\$',
    #     DetailView.as_view(
    #     	model=Neuron,
    #     	template_name='mydatasets/neuron_detail.html'),
    #     name='neuron_detail'),
    url(r'^datasets/(?P<pkr>\d+)/neuron/(?P<pk>\d+)/\$', neuron_detail, name='neuron_detail'),

	# Create a dataset, /mydatasets/dataset/create/
    url(r'^datasets/create/\$', DatasetCreate.as_view(), name='dataset_create'),
    url(r'^datasets/create2/\$', add_dataset, name='add_dataset'),

	# Edit dataset details, ex.: /datasets/dataset/1/edit/
    url(r'^datasets/(?P<pk>\d+)/edit/\$',
        UpdateView.as_view(
        	model = Dataset,
        	template_name = 'mydatasets/form.html',
        	form_class = DatasetForm,
            success_url=reverse_lazy('dataset_list')
            ),
        name='dataset_edit'),
	url(r'^datasets/(?P<pk>\d+)/edit2/\$', edit_dataset, name='edit_dataset' ),

	# duplicate a group of neurons, ex.: /mydatasets/datasets/1/duplicate/
	url(r'^datasets/(?P<pkr>\d+)/duplicate/$',
		dataset_duplicate,
		name='dataset_duplicate'),

	# Create a group of neurons, ex.: /mydatasets/datasets/1/neurons/create/
	url(r'^datasets/(?P<pk>\d+)/neurons/create/$', add_neuron, name='neuron_create'),
	url(r'^datasets/(?P<pk>\d+)/neurons/create2/$', add_neuron_author, name='neuron_create2'),

	# remove all groups
	url(r'^datasets/(?P<pk>\d+)/neurons/deleteall/$', neuron_groups_delete, name='neuron_groups_delete'),

	# remove reconstruction file
	url(r'^datasets/(?P<pk>\d+)/neurons/remove-reconstruction/$', reconstruction_delete, name='reconstruction_delete'),

	# make groups
	url(r'^datasets/(?P<pk>\d+)/neurons/make-groups/$', make_groups, name='make_groups'),

	# Edit dataset neuron details, ex.: /mydatasets/datasets/1/neurons/1/edit/
	url(r'^datasets/(?P<pkr>\d+)/neurons/(?P<pk>\d+)/edit/$', edit_neuron, name='neuron_edit'),
	# make changes and propagate them to other groups
	url(r'^datasets/(?P<pkr>\d+)/neurons/(?P<pk>\d+)/propagate/$', change_propagate, name='change_propagate'),
	# prepopulate the current from from the inforamtion of previous group
	url(r'^datasets/(?P<pkr>\d+)/neurons/(?P<pk>\d+)/prepopulate/$', prepopulate, name='prepopulate'),

	# proof new entry
	url(r'^datasets/(?P<pkr>\d+)/neurons/(?P<pk>\d+)/proof/$', proof_entry, name='proof_entry'),
	
	# bulk proof 
	url(r'^datasets2/(?P<pkr>\d+)/bulk-proof/$', bulk_proof, name='bulk_proof'),
	
	# bulk modify
	url(r'^datasets2/(?P<pkr>\d+)/bulk-modify/$', bulk_modify, name='bulk_modify'),

	# Create a dataset review, ex.: /mydatasets/datasets/1/reviews/create/
	# Unlike the previous patterns, this one is implemented using a method view instead of a class view
    url(r'^datasets/(?P<pk>\d+)/reviews/create/$', review, name='create_review'),
    # delete a review
	url(r'^datasets/(?P<pkr>\d+)/reviews/(?P<pk>\d+)/delete/$', delete_review, name='delete_review'),

	# upload
	url(r'^datasets/(?P<pk>\d+)/upload-files/$', upload, name='upload'),

	# duplicate a group of neurons, ex.: /mydatasets/datasets/1/neurons/1/duplicate/
	url(r'^datasets/(?P<pkr>\d+)/neurons/(?P<pk>\d+)/duplicate/$',
		neuron_duplicate,
		name='neuron_duplicate'),
	
	# delete a group of neurons, ex.: /mydatasets/datasets/1/neurons/1/delete/
	url(r'^datasets/(?P<pkr>\d+)/neurons/(?P<pk>\d+)/delete/$',
		neuron_delete,
		name='neuron_delete'),
    
	# generate csv url
	url(r'^datasets/(?P<pk>\d+)/generatecsv/\$', generate_csv, name='generate_csv' ),
    
	# change dataset status
	url(r'^datasets/(?P<pk>\d+)/change-status/\$', dataset_status, name='dataset_status' ),
    
	# change dataset archive status
	url(r'^datasets/(?P<pk>\d+)/change-archive-status/\$', dataset_archive_status, name='dataset_archive_status' ),
    
	# change dataset public status
	url(r'^datasets/(?P<pk>\d+)/change-public-status/\$', dataset_public_status, name='dataset_public_status' ),
    
	# delete a dataset
	url(r'^datasets/(?P<pk>\d+)/delete-dataset/\$', delete_dataset, name='delete_dataset' ),
    
	# about page
	url(r'^about/$', about, name='about' ),
    
	# archive page
	url(r'^archives/$', archive_list, name='archive_list' ),
    
	# clean up
	url(r'^manage/$', manage, name='manage' ),
    
	# new terms page
	url(r'^new_terms/$', version_new_terms, name='version_new_terms' ),
	
	# search page
	url(r'^search/$', search, name='search' ),
    
	# lab list page
	url(r'^labs/$', labs, name='labs' ),
    
	# help page
	url(r'^help/$', help, name='help' ),

	# load celltype level 2
	url('ajax/second_level/', second_level, name = 'second_level'),

	# count groups
	url('ajax/count_groups/', count_groups, name = 'count_groups'),

]

handler404 = handler404
handler500 = handler500