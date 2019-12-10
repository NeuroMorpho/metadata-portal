# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from datetime import date


class Dataset(models.Model):
    """containing datasets"""
    name = models.TextField()
    identifier = models.IntegerField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)
    user = models.ForeignKey(User, default=1)
    date = models.DateField(default=date.today)

    def __unicode__(self):
        return u"%" % self.name


class Species(models.Model):
    species   = models.CharField(max_length=25)
    def __str__(self):
        return self.species

class Gender(models.Model):
    gender   = models.CharField(max_length=25)
    species = models.ForeignKey(Species)
    def __str__(self):
        return "%s/%s"%(self.gender, self.species)

class Development(models.Model):
    develop_stage   = models.CharField(max_length=25)
    species = models.ForeignKey(Species, null=True)
    def __str__(self):
        return "%s/%s"%(self.develop_stage, self.species)

class Neuron(object):
    """docstring for Neuron"""
    name = models.TextField()
    description = models.TextField(blank=True, null=True)
    number_of_neurons = models.IntegerField(default=1, validators=[MaxValueValidator(100), MinValueValidator(1)])
    species = models.ForeignKey(Species, null=True)
    gender = models.ForeignKey(Gender, null=True)
    min_age  = models.IntegerField(default=1, validators=[MaxValueValidator(100), MinValueValidator(1)])
    max_age  = models.IntegerField(default=1, validators=[MaxValueValidator(100), MinValueValidator(1)])
    development_stage = models.ForeignKey(Development, null=True)

    # fixed info
    date  = models.DateField(default=date.today)
    dataset = models.ForeignKey(Dataset, null=True, related_name='datasets')
    user  = models.ForeignKey(User, default=1)


    def __unicode__(self):
        return u"%" % self.name
        

class Review(models.Model):
    comment = models.TextField(blank=True, null=True)
    user = models.ForeignKey(User, default=1)
    date = models.DateField(default=date.today)

    class Meta:
        abstract = True

class DatasetReview(Review):
    dataset = models.ForeignKey(Dataset)