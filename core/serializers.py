from django.conf.urls import url, include
from django.contrib.auth.models import User
from rest_framework import serializers
from core.models import Availability


# Serializers define the API representation.
class AvailabilitySerializer(serializers.ModelSerializer):
    '''Includes simple default implementations for the create() and update() methods.'''
    class Meta:
        model = Availability
        fields = ('id', 'start_date', 'resource', 'quantity')
