from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Category
from .serializers import CategorySerializer
from rest_framework import status

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()  # Fetch all categories for the viewset
    serializer_class = CategorySerializer

    def get_queryset(self):
        if self.action == 'list':
            # Only show top-level categories in the list endpoint
            return Category.objects.filter(parent__isnull=True)
        return super().get_queryset()

    @action(detail=False, methods=['post'])
    def drag_and_drop(self, request):
        """
        Drag and drop functionality for moving subcategories.
        - category_id: ID of the target parent category to move the subcategory into (can be null for top-level)
        - subcategory_id: ID of the subcategory being moved
        """
        category_id = request.data.get('category_id')  # Target category (new parent)
        subcategory_id = request.data.get('subcategory_id')  # Subcategory being moved

        # Ensure subcategory_id is provided
        if subcategory_id:
            try:
                # Fetch the subcategory being moved
                subcategory = Category.objects.get(id=subcategory_id)

                # Check if the category is being moved to itself
                if subcategory_id == category_id:
                    return Response({"error": "A category cannot be moved to itself."}, status=status.HTTP_400_BAD_REQUEST)

                # Check if the target category is a child of the subcategory being moved (to prevent circular references)
                if category_id and self.is_child_category(subcategory, category_id):
                    return Response({"error": "A category cannot be moved under one of its own children."}, status=status.HTTP_400_BAD_REQUEST)

                if category_id is None:
                    # If category_id is null, move the subcategory to the top-level (parent = null)
                    subcategory.parent = None
                else:
                    # Fetch the target category and move the subcategory under it
                    category = Category.objects.get(id=category_id)
                    subcategory.parent = category

                # Save the changes
                subcategory.save()

                return Response({"message": "Subcategory moved successfully"}, status=status.HTTP_200_OK)

            except Category.DoesNotExist:
                return Response({"error": "Subcategory or Category not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"error": "Invalid data provided"}, status=status.HTTP_400_BAD_REQUEST)

    def is_child_category(self, parent_category, target_id):
        """
        Check recursively if the target category is a child of the parent category.
        """
        if parent_category.id == target_id:
            return True
        # Recursively check subcategories of the current parent category
        for child in Category.objects.filter(parent=parent_category):
            if self.is_child_category(child, target_id):
                return True
        return False
