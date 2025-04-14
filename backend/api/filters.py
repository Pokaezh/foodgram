from rest_framework import filters

class NameFilter(filters.SearchFilter):
    search_param = 'name'