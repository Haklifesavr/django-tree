from rest_framework import serializers
from .models import Category

class CategorySerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'subcategories', 'parent']

    def get_subcategories(self, obj):
        """
        Recursively get all subcategories for the given category.
        """
        subcategories = Category.objects.filter(parent=obj)
        return CategorySerializer(subcategories, many=True).data
