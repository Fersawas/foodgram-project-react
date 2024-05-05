from django.urls import path, include

from djoser.views import TokenDestroyView, TokenCreateView

from rest_framework import routers

from api.views import (RecipeViewSet, TagViewSet,
                       MainUser, IngredientMesurmentViewSet)


router = routers.SimpleRouter()

router.register(r'users', MainUser, basename='users')
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'ingredients', IngredientMesurmentViewSet,
                basename='ingredients_mesure')

urlpatterns = [
    path('', include(router.urls)),
    path('recipes/<int:recipe_id>/shopping_cart/',
         RecipeViewSet.as_view({'post': 'shopping_cart',
                                'delete': 'shopping_cart'})),
    path('recipes/download_shopping_cart/',
         RecipeViewSet.as_view({'get': 'download_shopping_cart'})),
    path('recipes/<int:recipe_id>/favorite/',
         RecipeViewSet.as_view({'post': 'favorite', 'delete': 'favorite'})),
    path('users/<int:user_id>/subscribe/',
         MainUser.as_view({'post': 'subscribe', 'delete': 'subscribe'})),
    path('users/set_password/', MainUser.as_view({'post': 'reset_password'}),
         name='reset_password'),
    path('auth/token/login/', TokenCreateView.as_view()),
    path('auth/token/logout/', TokenDestroyView.as_view())
]
