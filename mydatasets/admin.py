# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
import models

# Register your models here.
admin.site.register(models.Dataset, SimpleHistoryAdmin)
admin.site.register(models.Version, SimpleHistoryAdmin)
admin.site.register(models.DatasetReview, SimpleHistoryAdmin)
admin.site.register(models.Development, SimpleHistoryAdmin)
admin.site.register(models.Gender, SimpleHistoryAdmin)
admin.site.register(models.Neuron, SimpleHistoryAdmin)
admin.site.register(models.Species, SimpleHistoryAdmin)
admin.site.register(models.BrainRegion1, SimpleHistoryAdmin)
admin.site.register(models.BrainRegion2, SimpleHistoryAdmin)
admin.site.register(models.BrainRegion3, SimpleHistoryAdmin)
admin.site.register(models.CellType1, SimpleHistoryAdmin)
admin.site.register(models.CellType2, SimpleHistoryAdmin)
admin.site.register(models.CellType3, SimpleHistoryAdmin)
admin.site.register(models.StainMethod, SimpleHistoryAdmin)
admin.site.register(models.SlicingDirection, SimpleHistoryAdmin)
admin.site.register(models.Strain, SimpleHistoryAdmin)
admin.site.register(models.ReconstructionSoftware, SimpleHistoryAdmin)
admin.site.register(models.ObjectiveType, SimpleHistoryAdmin)
admin.site.register(models.ProtocolDesign, SimpleHistoryAdmin)
admin.site.register(models.ExperimentCondition, SimpleHistoryAdmin)
admin.site.register(models.OriginalFormat, SimpleHistoryAdmin)
admin.site.register(models.SlicingThickness, SimpleHistoryAdmin)
admin.site.register(models.Magnification, SimpleHistoryAdmin)
admin.site.register(models.Lab, SimpleHistoryAdmin)
