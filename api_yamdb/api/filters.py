import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    genre = django_filters.Filter(
        field_name='genre__slug',
        lookup_expr='icontains'
    )
    category = django_filters.Filter(
        field_name='category__slug',
        lookup_expr='icontains'
    )

    class Meta:
        fields = ('genre', 'name', 'year', 'category')
        model = Title
