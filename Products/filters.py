import django_filters
from .models import Product, Food, Accompaniment

class ProductFilter(django_filters.FilterSet):
    # Filtering fields
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    shop_category = django_filters.UUIDFilter(field_name="shop_category__id")
    product_category = django_filters.UUIDFilter(field_name="product_category__id")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    is_pick_and_go = django_filters.BooleanFilter(field_name="is_pick_and_go")

    class Meta:
        model = Product
        fields = ["min_price", "max_price", "shop_category", "product_category", "name", "is_pick_and_go"]


class FoodFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category = django_filters.UUIDFilter(field_name="category__id")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Food
        fields = ["min_price", "max_price", "category", "name"]


class AccompanimentFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Accompaniment
        fields = ["min_price", "max_price", "name"]
