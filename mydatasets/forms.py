# from __future__ import super
from django.forms import ModelForm
from models import Dataset, Neuron
from models import CellType1, CellType2, CellType3
from models import BrainRegion1, BrainRegion2, BrainRegion3
from models import Strain

class DatasetForm(ModelForm):
  class Meta:
    model = Dataset
    exclude = ('user', 'date', 'pdf', 'excel', 'set_archive', 'review', 'reconstructions', 'public',)

class NeuronForm(ModelForm):
  class Meta:
    model = Neuron
    exclude = ('user', 'date', 'dataset',)
  def __init__(self, *args, **kwargs):
    super(NeuronForm, self).__init__(*args, **kwargs)
    # clear strain query set
    self.fields['strain'].queryset = Strain.objects.none()
    # clear cell type query set
    self.fields['cell_type2'].queryset = CellType2.objects.none()
    self.fields['cell_type3'].queryset = CellType3.objects.none()
    # clear brain region query set
    self.fields['brain_region2'].queryset = BrainRegion2.objects.none()
    self.fields['brain_region3'].queryset = BrainRegion3.objects.none()

    # update strain
    if 'species' in self.data:
      try:
        species_id = int(self.data.get('species'))
        self.fields['strain'].queryset = Strain.objects.filter(species = species_id).order_by('strain_name')
      except(ValueError, TabError):
        print 'value or tab error'
        pass
    elif self.instance.pk:
      species_id = self.instance.species_id
      self.fields['strain'].queryset = Strain.objects.filter(species = species_id).order_by('strain_name')

    # update cell type
    if 'cell_type1' in self.data:
      try:
        cell_id = int(self.data.get('cell_type1'))
        self.fields['cell_type2'].queryset = CellType2.objects.filter(class1 = cell_id).order_by('class2')
      except(ValueError, TabError):
        print 'value or tab error'
        pass
    elif self.instance.pk:
      cell_id = self.instance.cell_type1_id
      self.fields['cell_type2'].queryset = CellType2.objects.filter(class1 = cell_id).order_by('class2')
    
    
    if 'cell_type2' in self.data:
      try:
        cell1_id = int(self.data.get('cell_type1'))
        cell2_id = int(self.data.get('cell_type2'))
        self.fields['cell_type3'].queryset = CellType3.objects.filter(class1 = cell1_id, class2 = cell2_id).order_by('class3')
      except(ValueError, TabError):
        print 'value or tab error'
        pass
    elif self.instance.pk:
      cell1_id = self.instance.cell_type1_id
      cell2_id = self.instance.cell_type2_id
      self.fields['cell_type3'].queryset = CellType3.objects.filter(class1 = cell1_id, class2 = cell2_id).order_by('class3')

    # update brain region
    if 'brain_region1' in self.data:
      try:
        region_id = int(self.data.get('brain_region1'))
        self.fields['brain_region2'].queryset = BrainRegion2.objects.filter(region1 = region_id).order_by('region2')
      except(ValueError, TabError):
        print 'value or tab error'
        pass
    elif self.instance.pk:
      region_id = self.instance.brain_region1_id
      self.fields['brain_region2'].queryset = BrainRegion2.objects.filter(region1 = region_id).order_by('region2')
    
    if 'brain_region2' in self.data:
      # print 'here!'
      try:
        region1_id = int(self.data.get('brain_region1'))
        region2_id = int(self.data.get('brain_region2'))
        self.fields['brain_region3'].queryset = BrainRegion3.objects.filter(region1 = region1_id, region2 = region2_id).order_by('region3')
      except(ValueError, TabError):
        print 'value or tab error'
        pass
    elif self.instance.pk:
      region1_id = self.instance.brain_region1_id
      region2_id = self.instance.brain_region2_id
      self.fields['brain_region3'].queryset = BrainRegion3.objects.filter(region1 = region1_id, region2 = region2_id).order_by('region3')

  
