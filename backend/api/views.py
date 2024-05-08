# isort: off
from api.filters import IngredientsFilter, RecipeFilter
from api.messages_constants import (FAVORITE_ERRORS, RECIPE_ERRORS,
                                    SHOP_CART_ERRORS, SHOPPING_CART)
from api.pagination import LimitPagination
from api.permissions import IsAuthorOrRead
from api.serializers import (FollowSerializer, IngredientMesurmentSerializer,
                             MainRecipeSerializer, ReadRecipeSerializer,
                             ShopCartSerializer, TagSerializer,
                             UserRecipeSerializer)
from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from djoser.conf import settings
from djoser.views import UserViewSet
from food.models import Favorite, IngredientMesurment, Recipe, Shopcart, Tag
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import SAFE_METHODS, AllowAny, IsAuthenticated
from rest_framework.response import Response
from users.models import Follow

PERMISSIONS_USER: list[str] = ['me', 'subscribe', 'subscriptions']
User = get_user_model()


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrRead]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter
    pagination_class = LimitPagination

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'favorite':
            return ReadRecipeSerializer
        if self.action == 'shop_cart':
            return ShopCartSerializer
        if self.request.method in SAFE_METHODS:
            return ReadRecipeSerializer
        return MainRecipeSerializer

    def perform_create(self, serializer):
        return serializer.save(
            author=self.request.user
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(['get'], detail=False)
    def download_shopping_cart(self, request):
        list_ingred: str = (f'\n{SHOPPING_CART["welcome"]}'
                            f' {request.user.username}\n')
        user = request.user
        user = get_object_or_404(
            User, username=user.username
        )
        recipes_cart = Recipe.objects.filter(
            shopcart__user=user,)
        ingredients = recipes_cart.values_list(
            'ingredients__ingredient__name',
            'ingredients__ingredient__measurement_unit').annotate(
                amount_sum=Sum('ingredients__amount'))
        for ingred in ingredients:
            list_ingred += (f'\n{ingred[0]} {ingred[2]}{ingred[1]}')
        list_ingred += (f'\n\n{SHOPPING_CART["ending"]}')
        return HttpResponse(list_ingred, content_type='text/plain',
                            status=status.HTTP_200_OK)

    @action(['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk, *args, **kwargs):
        user = request.user
        user = get_object_or_404(
            User, username=user.username
        )
        try:
            recipe_for_favorite = Recipe.objects.get(
                pk=pk
            )
        except Exception:
            return Response(
                {'ERROR': RECIPE_ERRORS['no recipe']},
                status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            try:
                favorite_recipe = Favorite.objects.get(
                    user=user, recipe=recipe_for_favorite
                )
            except Exception:
                return Response(
                    {'ERROR': RECIPE_ERRORS['no recipe']},
                    status=status.HTTP_400_BAD_REQUEST)
            favorite_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            Favorite.objects.create(user=user, recipe=recipe_for_favorite)
        except Exception:
            return Response({'ERROR': FAVORITE_ERRORS['dublicate']},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(recipe_for_favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(['post', 'delete'], detail=True,
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk, *args, **kwargs):
        user = request.user
        user = get_object_or_404(
            User, username=user.username
        )
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Exception:
            return Response(
                {'ERROR': RECIPE_ERRORS['no recipe']},
                status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            try:
                shopcart_recipe = Shopcart.objects.get(
                    user=user, recipe=recipe)
            except Exception:
                return Response(
                    {'ERROR': RECIPE_ERRORS['no recipe']},
                    status=status.HTTP_400_BAD_REQUEST)
            shopcart_recipe.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            Shopcart.objects.create(user=user, recipe=recipe)
        except Exception:
            return Response({'ERROR': SHOP_CART_ERRORS['dublicate']},
                            status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    pagination_class = None


class IngredientMesurmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = IngredientMesurmentSerializer
    queryset = IngredientMesurment.objects.all()
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = IngredientsFilter


class MainUser(UserViewSet):
    pagination_class = LimitPagination

    def get_serializer_class(self):
        if self.action == 'subscriptions':
            return UserRecipeSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in PERMISSIONS_USER:
            self.permission_classes = settings.PERMISSIONS.me
        return super().get_permissions()

    def perform_create(self, serializer, *args, **kwargs):
        serializer.is_valid(raise_exception=True)
        return super().perform_create(serializer, *args, **kwargs)

    @action(['get'], detail=False)
    def subscriptions(self, request, *args, **kwargs):
        user = User.objects.get(
            username=request.user.username
        )
        self.queryset = User.objects.filter(main__follower=user)
        page = self.paginate_queryset(self.queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(['post', 'delete'], detail=False)
    def subscribe(self, request, user_id, *args, **kwargs):
        user = User.objects.get(
            username=request.user.username
        )
        self.queryset = user.main.all()
        self.serializer_class = FollowSerializer
        serializer = self.get_serializer(data={'user_id': user_id})
        serializer.is_valid(raise_exception=True)
        user_for_subscription = get_object_or_404(
            User, id=user_id
        )
        if request.method == 'DELETE':
            instance = get_object_or_404(
                Follow, user=user_for_subscription, follower=user
            )
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        serializer.save(follower=user, user=user_for_subscription)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
