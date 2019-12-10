"""
API settings
"""

import os
from django.contrib.messages import constants as messages

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

from rest_framework import routers
from mydatasets import api_views as myapp_views

router = routers.DefaultRouter()

router.register(r'labs', myapp_views.LabViewset)
router.register(r'datasets', myapp_views.DatasetViewset)
router.register(r'newterms', myapp_views.NewTermsViewset, basename='NewTermsViewset')