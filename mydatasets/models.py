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
from simple_history.models import HistoricalRecords


reload(sys)  
sys.setdefaultencoding('utf-8')

class Lab(models.Model):
    """Labratoar information"""
    # history
    history = HistoricalRecords()
    lab_name = models.CharField(max_length=100)
    institute = models.CharField(max_length=500, blank=True, null=True)
    address = models.CharField(max_length=500, blank=True, null=True)
    date = models.DateTimeField('date added', default=datetime.now, blank=True)
    version    = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        ordering = ('lab_name', )
    def __unicode__(self):
        return "%s / %s / %s"%(self.lab_name, self.institute, self.address)
    @property
    def search(self):
        return "<Lab> %s / %s / %s"%(self.lab_name, self.institute, self.address)

class Version(models.Model):
    """keep track of release versions"""
    title = models.CharField(max_length=500)
    features = models.TextField(blank=True, null=True)
    date = models.DateTimeField('date created', default=datetime.now, blank=True)
    def features_as_list(self):
        return self.features.split('\n')
    def __unicode__(self):
        return "%s - %s"%(self.title, self.features[0:50] + '...')

# modify uploading location
def upload_location(instance, filename):
    print 'changing location'
    print "{}/{}".format(instance.archive_name, filename)
    return "files/"
    return "{}/{}".format(instance.archive_name, filename)

class Dataset(models.Model):
    """containing datasets"""
    # history
    history = HistoricalRecords()
    # name = models.CharField(max_length=500)
    # code = models.CharField(max_length=50, null=True, blank=True, default='uuid.uuid4')
    archive_name = models.CharField(max_length=500, blank=True, null=True)
    identifier = models.IntegerField('PMID', blank=True, null=True)
    authors = models.CharField(max_length=500, blank=True, null=True)
    url = models.URLField('URL', blank=True, null=True)
    nmo_version = models.CharField('NMO Version', max_length=500, blank=True)
    date = models.DateTimeField('date created', default=datetime.now, blank=True)
    deposition_date = models.DateField('deposition date', default=datetime.now, blank=True)
    notes = models.TextField(blank=True)
    grant_id = models.TextField(blank=True)
    # management fields
    user = models.ForeignKey(User, default=1)
    review = models.BooleanField(default=False, blank=True)
    set_archive = models.BooleanField(default=False, blank=True)
    public = models.BooleanField(default=False, blank=True)
    # file fields
    pdf = models.FileField(max_length=500, upload_to=upload_location, blank=True)
    excel = models.FileField(max_length=500, upload_to=upload_location, blank=True)
    reconstructions = models.FileField(max_length=500, upload_to=upload_location, blank=True)
    recon_link = models.CharField('upload location', max_length=1000, blank=True)
    ext = models.CharField(max_length=50, blank=True, null=True)
    folders_names       = ArrayField(models.CharField(max_length=500, blank=True), blank=True, null=True)
    folders_file_counts = ArrayField(models.CharField(max_length=500, blank=True), blank=True, null=True)
    def clean_grant_id(self):
        string = self.cleaned_data['grant_id']
        string = re.sub('[^A-Za-z0-9 ]+', '', string)
        string = re.sub('\s\s+', ' ', string)
        if len(message) >= 5000:
            raise ValidationError('Too many characters ...')
        return string
    def __unicode__(self):
        return "%s - %s"%(self.identifier, self.archive_name)
    def name(self):
        return "%s%s"%(self.archive_name)
    def id(self):
        return "%s%s"%(self.identifier)

class Species(models.Model):
    # history
    history = HistoricalRecords()
    species    = models.CharField(unique=True, max_length=500)
    species_id = models.IntegerField(blank=True, null=True)
    version    = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.species
    class Meta:
        ordering = ('species', )
    @property
    def search(self):
        return "<Species> {}".format(self.species)
    
class Gender(models.Model):
    # history
    history = HistoricalRecords()
    gender  = models.CharField(unique=True, max_length=500)
    version   = models.CharField(max_length=100, blank=True, null=True)
    # species = models.ForeignKey(Species)
    def __str__(self):
        return "{}".format(self.gender)
    class Meta:
        ordering = ('gender', )

class Development(models.Model):
    # history
    history = HistoricalRecords()
    age_class_id   = models.IntegerField(blank=True, null=True)
    age_class   = models.CharField(unique=True, max_length=500, blank=True, null=True)
    version   = models.CharField(max_length=100, blank=True, null=True)
    # species = models.ForeignKey(Species, null=True)
    def __str__(self):
        return "{}".format(self.age_class)
    class Meta:
        ordering = ('age_class', )
    @property
    def search(self):
        return "<DevelopmentStage> {}".format(self.age_class)

class BrainRegion1(models.Model):
    # history
    history = HistoricalRecords()
    region1_id = models.IntegerField(blank=True, null=True)
    region1 = models.CharField(unique=True, max_length = 500)
    version   = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return "{}".format(self.region1)
    class Meta:
        ordering = ('region1', )
    @property
    def search(self):
        return "<BrainRegion> {}".format(self.region1)

class BrainRegion2(models.Model):
    # history
    history = HistoricalRecords()
    region1 = models.ForeignKey(BrainRegion1, null=True, blank=True)
    region2_id = models.IntegerField(blank=True, null=True)
    region2 = models.CharField(max_length = 500)
    version   = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        ordering = ('region2', )
        unique_together = ('region1', 'region2', )
    def __str__(self):
        return "{}".format(self.region2)
    @property
    def level(self):
        return "({}) {}".format(self.region1, self.region2)
    @property
    def search(self):
        return "<BrainRegion> ({}) {}".format(self.region1, self.region2)

class BrainRegion3(models.Model):
    # history
    history = HistoricalRecords()
    region1 = models.ForeignKey(BrainRegion1, null=True, blank=True)
    region2 = models.ForeignKey(BrainRegion2, null=True, blank=True)
    region3_id = models.IntegerField(blank=True, null=True)
    region3 = models.CharField(max_length = 500)
    version   = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        ordering = ('region3', )
        unique_together = ('region1', 'region2', 'region3', )
    def __str__(self):
        return "{}".format(self.region3)
    @property
    def level(self):
        return "({} ➡ {}) {}".format(self.region1, self.region2, self.region3)
    @property
    def search(self):
        return "<BrainRegion> ({} ➡ {}) {}".format(self.region1, self.region2, self.region3)

class CellType1(models.Model):
    # history
    history = HistoricalRecords()
    class1_id = models.IntegerField(blank=True, null=True)
    class1 = models.CharField(unique=True, max_length = 500)
    version   = models.CharField(max_length=100, blank=True,  null=True)
    def __str__(self):
        return "{}".format(self.class1)
    class Meta:
        ordering = ('class1', )
    @property
    def search(self):
        return "<CellType> {}".format(self.class1)

class CellType2(models.Model):
    # history
    history = HistoricalRecords()
    class1 = models.ForeignKey(CellType1, null=True, blank=True)
    class2_id = models.IntegerField(blank=True, null=True)
    class2  = models.CharField(max_length = 500)
    version = models.CharField(max_length=100, blank=True,  null=True)
    class Meta:
        ordering = ('class2', )
        unique_together = ('class1', 'class2', )
    def level(self):
        return "{}-{}".format(self.class1, self.class2)
    def __str__(self):
        return "{}".format(self.class2)
    @property
    def level(self):
        return "({}) {}".format(self.class1, self.class2)
    @property
    def search(self):
        return "<CellType> ({}) {}".format(self.class1, self.class2)

class CellType3(models.Model):
    # history
    history = HistoricalRecords()
    class1 = models.ForeignKey(CellType1, null=True, blank=True)
    class2 = models.ForeignKey(CellType2, null=True, blank=True)
    class3_id = models.IntegerField(blank=True, null=True)
    class3 = models.CharField(max_length = 500)
    version   = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        ordering = ('class3', )
        unique_together = ('class1', 'class2', 'class3', )
    def __str__(self):
        return "{}".format(self.class3)
    @property
    def level(self):
        return "({} ➡ {}) {}".format(self.class1, self.class2, self.class3)
    @property
    def search(self):
        return "<CellType> ({} ➡ {}) {}".format(self.class1, self.class2, self.class3)

class SlicingDirection(models.Model):
    # history
    history = HistoricalRecords()
    direction_id = models.IntegerField(null=True, blank=True)
    slicing_direction = models.CharField(unique=True, max_length = 500)
    version   = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return unicode("{}".format(self.slicing_direction))
    class Meta:
        ordering = ('slicing_direction', )
    @property
    def search(self):
        return unicode("<SlicingDirection> {}".format(self.slicing_direction))

class StainMethod(models.Model):
    # history
    history = HistoricalRecords()
    stain_id = models.IntegerField(null=True, blank=True)
    stain = models.CharField(unique=True, max_length = 500)
    version   = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return "{}".format(self.stain)
    class Meta:
        ordering = ('stain', )
    @property
    def search(self):
        return "<StainMethod> {}".format(self.stain)

class Strain(models.Model):
    # history
    history = HistoricalRecords()
    species = models.ForeignKey(Species, blank=True, null=True, on_delete=models.SET_NULL)
    strain_id = models.IntegerField(null=True, blank=True)
    strain_name = models.CharField(max_length = 500, null=True, blank=True)
    # scientific_name = models.CharField(max_length = 500, null=True, blank=True)
    version   = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ('strain_name', )
        unique_together = ('strain_name', 'species', )
    def __str__(self):
        return "{}".format(self.strain_name)
    @property
    def level(self):
        return "({}) {}".format(self.species, self.strain_name)
    @property
    def search(self):
        return "<Strain> ({}) {}".format(self.species, self.strain_name)

class ReconstructionSoftware(models.Model):
    # history
    history = HistoricalRecords()
    reconstruction_id = models.IntegerField(null=True, blank=True)
    reconstruction_software = models.CharField(unique=True, max_length = 500, null=True, blank=True)
    version   = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return "{}".format(self.reconstruction_software)
    class Meta:
        ordering = ('reconstruction_software', )
    @property
    def search(self):
        return "<Software> {}".format(self.reconstruction_software)


class ObjectiveType(models.Model):
    # history
    history = HistoricalRecords()
    objective_id = models.IntegerField(null=True, blank=True)
    objective_type = models.CharField(unique=True, max_length = 500, null=True, blank=True)
    version   = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return "{}".format(self.objective_type)
    class Meta:
        ordering = ('objective_type', )
    @property
    def search(self):
        return "<ObjectiveType> {}".format(self.objective_type)

class ProtocolDesign(models.Model):
    # history
    history = HistoricalRecords()
    protocol_id = models.IntegerField(null=True, blank=True)
    protocol = models.CharField(unique=True, max_length = 500, null=True, blank=True)
    version   = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return "{}".format(self.protocol)
    class Meta:
        ordering = ('protocol', )
    @property
    def search(self):
        return "<Protocol> {}".format(self.protocol)

class ExperimentCondition(models.Model):
    # history
    history = HistoricalRecords()
    expercond_id = models.IntegerField(null=True, blank=True)
    expercond = models.CharField(unique=True, max_length = 500, null=True, blank=True)
    version   = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return "{}".format(self.expercond)
    class Meta:
        ordering = ('expercond', )
    @property
    def search(self):
        return "<ExperimentalCondition> {}".format(self.expercond)

class OriginalFormat(models.Model):
    # history
    history = HistoricalRecords()
    original_format_id = models.IntegerField(null=True, blank=True)
    original_format = models.CharField(unique=True, max_length = 500, null=True, blank=True)
    version   = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return "{}".format(self.original_format)
    class Meta:
        ordering = ('original_format', )
    @property
    def search(self):
        return "<Format> {}".format(self.original_format)

class Magnification(models.Model):
    # history
    history = HistoricalRecords()
    magnification_id = models.IntegerField(null=True, blank=True)
    magnification = models.CharField(unique=True, max_length = 500, null=True, blank=True)
    version   = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return "{}".format(self.magnification)
    class Meta:
        ordering = ('magnification', )
    @property
    def search(self):
        return "<Magnification> {}".format(self.magnification)

class SlicingThickness(models.Model):
    # history
    history = HistoricalRecords()
    thickness_id = models.IntegerField(null=True, blank=True)
    slice_thickness = models.CharField(unique=True, max_length = 500, null=True, blank=True)
    version   = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return "{}".format(self.slice_thickness)
    class Meta:
        ordering = ('slice_thickness', )
    @property
    def search(self):
        return "<Thickness> {}".format(self.slice_thickness)

class Neuron(models.Model):
    """docstring for Neuron"""
    # history
    history = HistoricalRecords()
    # fixed info
    date  = models.DateField(default=date.today)
    edit_date = models.DateTimeField('date editted', default=datetime.now, blank=True)
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, null=True, related_name='neurons')
    user  = models.ForeignKey(User, default=1)

    # Subject
    group_name = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    number_of_neurons = models.IntegerField(validators=[MaxValueValidator(1000000), MinValueValidator(1)], blank=True, null=True)

    species = models.ForeignKey(Species, max_length=500, null=True, blank=True, on_delete=models.SET_NULL)
    new_species = models.CharField(max_length=500, null=True, blank=True)
    scientific_name = models.CharField(max_length=500, null=True, blank=True)
    strain = models.ForeignKey(Strain, blank=True, null=True, on_delete=models.SET_NULL)
    new_strain = models.CharField(max_length=500, null=True, blank=True)
    # new_strain_hits = ArrayField(models.CharField(max_length=200, blank=True), blank=True, null=True)
    gender_choices = (('Female', 'Female'), ('Hermaphrodite', 'Hermaphrodite'), ('Male', 'Male'), ('Male/Female', 'Male/Female'), ('Not reported', 'Not reported'))
    gender  = models.CharField(max_length=100, choices=gender_choices, blank=True, null=True)
    new_gender  = models.CharField(max_length=100, blank=True, null=True)
    development_stage = models.ForeignKey(Development, blank=True, null=True, on_delete=models.SET_NULL)
    new_development_stage = models.CharField(max_length=500, null=True, blank=True)
    # min_age  = models.FloatField(default=0, validators=[MaxValueValidator(1000000), MinValueValidator(0)], blank=True)
    # max_age  = models.FloatField(default=0, validators=[MaxValueValidator(1000000), MinValueValidator(0)], blank=True)
    min_age  = models.CharField(max_length=55, blank=True, default='')
    max_age  = models.CharField(max_length=55, blank=True, default='')
    age_choices = (('Days', 'Days'), ('Month', 'Month'), ('Years', 'Years'))
    age_type = models.CharField(max_length=100, choices=age_choices, blank=True, null=True)
    new_age_type = models.CharField(max_length=500, null=True, blank=True)
    min_weight  = models.CharField(max_length=55, blank=True, default='')
    max_weight  = models.CharField(max_length=55, blank=True, default='')
    # min_weight  = models.IntegerField(default=0, validators=[MaxValueValidator(1000000), MinValueValidator(0)], blank=True)
    # max_weight  = models.IntegerField(default=0, validators=[MaxValueValidator(1000000), MinValueValidator(0)], blank=True)
    subject_comments = models.TextField(blank=True, null=True)
    # weight_choices = (('ounces', 'ounces'), ('pounds', 'pounds'))
    # weight_type = models.CharField(max_length=50, choices=weight_choices, null=True)

    # anatomy
    brain_region1 = models.ForeignKey(BrainRegion1, blank=True, null=True, on_delete=models.SET_NULL)
    brain_region2 = models.ForeignKey(BrainRegion2, blank=True, null=True, on_delete=models.SET_NULL)
    brain_region3 = models.ManyToManyField(BrainRegion3, blank=True)
    brain_region3_order = ArrayField(models.CharField(max_length=100, blank=True), blank=True, null=True)
    cell_type1 = models.ForeignKey(CellType1, blank=True, null=True, on_delete=models.SET_NULL)
    cell_type2 = models.ForeignKey(CellType2, blank=True, null=True, on_delete=models.SET_NULL)
    cell_type3 = models.ManyToManyField(CellType3, blank=True)
    cell_type3_order = ArrayField(models.CharField(max_length=100, blank=True), blank=True, null=True)
    # new anatomy
    new_brain_region1 = models.CharField(max_length=500, null=True, blank=True)
    new_brain_region2 = models.CharField(max_length=500, null=True, blank=True)
    new_brain_region3 = models.TextField(blank=True,  null=True)
    new_cell_type1 = models.CharField(max_length=500, null=True, blank=True)
    new_cell_type2 = models.CharField(max_length=500, null=True, blank=True)
    new_cell_type3 = models.TextField(blank=True, null=True)
    anatomy_comments = models.TextField(blank=True, null=True)

    # experiment and reconstruction
    experimental_protocol = models.ForeignKey(ProtocolDesign, blank=True, null=True, on_delete=models.SET_NULL)
    new_experimental_protocol = models.CharField(max_length=500, null=True, blank=True)
    experimental_condition = models.ForeignKey(ExperimentCondition, blank=True, null=True, on_delete=models.SET_NULL)
    new_experimental_condition = models.CharField(max_length=500, null=True, blank=True)
    fixation_method = models.CharField(max_length=500, null=True, blank=True)
    stain = models.ForeignKey(StainMethod, blank=True, null=True, on_delete=models.SET_NULL)
    new_stain = models.CharField(max_length=500, null=True, blank=True)
    # slice_tickness = models.CharField(max_length=500, null=True, blank=True)
    slice_tickness = models.ForeignKey(SlicingThickness, blank=True, null=True, on_delete=models.SET_NULL)
    new_slice_tickness = models.CharField(max_length=500, null=True, blank=True)
    slicing_direction = models.ForeignKey(SlicingDirection, blank=True, null=True, on_delete=models.SET_NULL)
    new_slicing_direction = models.CharField(max_length=500, null=True, blank=True)
    reconstruction_software = models.ForeignKey(ReconstructionSoftware, blank=True, null=True, on_delete=models.SET_NULL)
    new_reconstruction_software = models.CharField(max_length=500, null=True, blank=True)
    objective_type = models.ForeignKey(ObjectiveType, blank=True, null=True, on_delete=models.SET_NULL)
    new_objective_type = models.CharField(max_length=500, null=True, blank=True)
    # objective_magnification = models.IntegerField(validators=[MaxValueValidator(1000000), MinValueValidator(0)], blank=True, null=True)
    objective_magnification = models.ForeignKey(Magnification, blank=True, null=True, on_delete=models.SET_NULL)
    new_objective_magnification = models.CharField(max_length=500, null=True, blank=True)
    experiment_comments = models.TextField(blank=True, null=True)
    
    # shrinkage
    shrinkage_choices = (('Reported', 'Reported'), ('Not reported', 'Not reported'), ('Not applicable', 'Not applicable'))
    tissue_shrinkage  = models.CharField(max_length=500, choices=shrinkage_choices, null=True, blank=True, default='Not reported')
    reported_choices  = (('Y', 'Yes'), ('N', 'No'))
    shrinkage_corrected = models.CharField(max_length=500, choices=reported_choices, null=True, blank=True)
    reported_value = models.CharField(max_length=500, null=True, blank=True)
    reported_xy = models.CharField(max_length=500, null=True, blank=True)
    reported_z = models.CharField(max_length=500, null=True, blank=True)
    corrected_value = models.CharField(max_length=500, null=True, blank=True)
    corrected_xy = models.CharField(max_length=500, null=True, blank=True)
    corrected_z = models.CharField(max_length=500, null=True, blank=True)

    # data
    number_of_data_files  = models.IntegerField(validators=[MaxValueValidator(1000000), MinValueValidator(1)], null=True, blank=True)
    numerical_units_choices = (('micrometer', 'micrometer'), ('pixel', 'pixel'))
    numerical_units = models.CharField(max_length=500, choices=numerical_units_choices, null=True, blank=True)
    pixel_size  = models.CharField(max_length=500, null=True, blank=True)
    data_type = models.ForeignKey(OriginalFormat, blank=True, null=True, on_delete=models.SET_NULL)
    new_data_type = models.CharField(max_length=500, null=True, blank=True)
    data_comments = models.TextField(blank=True, null=True)

    # contributor info
    archive_name = models.CharField(max_length=500, null=True, blank=True)
    lab = models.ForeignKey(Lab, blank=True, null=True, on_delete=models.SET_NULL)
    lab_name = models.CharField(max_length=500, null=True, blank=True)
    institute = models.CharField(max_length=500, null=True, blank=True)
    address = models.CharField(max_length=500, null=True, blank=True)
    related_publications = models.TextField(blank=True)
    # related_publications = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True)
    contributor_comments = models.TextField(blank=True, null=True)

    # neuron description
    soma = models.BooleanField(default=False, blank=True)
    axon = models.BooleanField(default=False, blank=True)
    dendrites = models.BooleanField(default=False)
    neurites = models.BooleanField(default=False)
    processes = models.BooleanField(default=False)
    other_descriptions = models.CharField(max_length=500, null=True, blank=True)
    description_comments = models.TextField(blank=True, null=True)

    # morphological attributes
    dimension = models.CharField(max_length=100, choices=(('2D', '2D'), ('3D', '3D')), null=True, blank=True)
    angles = models.CharField(max_length=500, null=True, choices=(('Yes', 'Yes'), ('No', 'No')), blank=True)
    diameter = models.CharField(max_length=500, null=True, choices=(('Yes', 'Yes'), ('No', 'No')), blank=True)
    other_attributes = models.CharField(max_length=500, null=True, blank=True)
    morphological_comments = models.TextField(blank=True, null=True)

    # integrity
    integrity_choices = (('Complete', 'Complete'), ('Moderate', 'Moderately-Complete'), ('Incomplete', 'Incomplete'))
    axon_integrity = models.CharField(max_length=100, choices=integrity_choices, null=True, blank=True)
    dendrites_integrity = models.CharField(max_length=100, choices=integrity_choices, null=True, blank=True)
    neurites_integrity = models.CharField(max_length=100, choices=integrity_choices, null=True, blank=True)
    processes_integrity = models.CharField(max_length=100, choices=integrity_choices, null=True, blank=True)
    integrity_comments = models.TextField(blank=True, null=True)

    def region3_as_list(self):
        return to_list(self.new_brain_region3)
    def cell3_as_list(self):
        return to_list(self.new_cell_type3)
    def subject_com(self):
        return to_list(self.subject_comments)
    def anatomy_com(self):
        return to_list(self.anatomy_comments)
    def experiment_com(self):
        return to_list(self.experiment_comments)
    def data_com(self):
        return to_list(self.data_comments)
    def contributor_com(self):
        return to_list(self.contributor_comments)
    def description_com(self):
        return to_list(self.description_comments)
    def morphological_com(self):
        return to_list(self.morphological_comments)
    def integrity_com(self):
        return to_list(self.integrity_comments)
    def __unicode__(self):
        return "%s"%(self.group_name)


class Review(models.Model):
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, default=1)
    date = models.DateField(default=date.today)

    class Meta:
        abstract = True

    def __str__(self):
        return "({}) {}: {}".format(self.date, self.user, self.comment)


class DatasetReview(Review):
    dataset = models.ForeignKey(Dataset)

def to_list(text):
    if text is None or len(text) == 0:
        return None
    string_list = [s.strip() for s in text.split('\n')]
    return string_list

