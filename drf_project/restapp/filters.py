from django_filters import rest_framework as filters
from .models import CopyNote


class CopyNoteFilter(filters.FilterSet):
       copied_from = filters.filters.CharFilter(field_name='copied_from__name', lookup_expr='exact')
       copied_to = filters.filters.CharFilter(field_name='copied_to__name', lookup_expr='exact')

       class Meta:
              model = CopyNote
              fields = ['copied_from', 'copied_to']
