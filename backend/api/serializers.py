# isort: off
import base64

from api.messages_constants import (FAVORITE_ERRORS, FOLLOW_ERRORS,
                                    RECIPE_ERRORS, SHOP_CART_ERRORS,
                                    TAGS, USER_ERRORS, NAME_LENGTH)
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from food.models import (Favorite, IngredientCount, IngredientMesurment,
                         Recipe, Shopcart, Tag)
from rest_framework import serializers
from users.models import Follow


User = get_user_model()


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]

            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)

        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            'id',
            'name',
            'color',
            'slug'
        ]


class UserMainSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        user = self.context['request'].user
        user_check = User.objects.get(username=user.username)
        followed = User.objects.get(username=obj.username)
        return Follow.objects.filter(
            user=followed.id,
            follower=user_check.id).exists()


class UserMainCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+$',
        max_length=NAME_LENGTH,
        required=True
    )

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError(
                {'ERROR': USER_ERRORS['username exists']}
            )
        return username

    def create(self, validated_data):
        user = User(
            email=validated_data["email"],
            username=validated_data["username"],
            first_name=validated_data["first_name"],
            last_name=validated_data["last_name"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class UserRecipeSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_recipes(self, user):
        try:
            recipes_limit = int(self.context['request'].GET['recipes_limit'])
        except Exception:
            recipes_limit = None
        recipes = Recipe.objects.filter(author=user)[:recipes_limit]
        return RecipeSerializer(recipes, many=True, context=self.context).data

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        user_check = User.objects.get(username=user.username)
        followed = User.objects.get(username=obj.username)
        return Follow.objects.filter(
            user=followed.id,
            follower=user_check.id).exists()

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class ShopCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shopcart
        fields = ''

    def to_representation(self, instance):
        recipe = get_object_or_404(Recipe, pk=instance.id)
        return RecipeSerializer(instance=recipe).data

    def validate(self, obj):
        recipe_id = self.initial_data['recipe_id']
        user = get_object_or_404(
            User, username=self.context['request'].user.username)
        get_object_or_404(Recipe, id=recipe_id)
        if self.context['request'].method == 'POST':
            if Shopcart.objects.filter(
                user=user.id,
                recipe=recipe_id
            ).exists():
                raise serializers.ValidationError(
                    {'ERROR': SHOP_CART_ERRORS['dublicate']})
        if self.context['request'].method == 'DELETE':
            if not Shopcart.objects.get(
                user=user.id,
                recipe=recipe_id
            ):
                raise serializers.ValidationError(
                    {'ERROR': SHOP_CART_ERRORS['delete']}
                )
        return obj


class FavoriteSerializer(serializers.ModelSerializer):
    recipe = serializers.SerializerMethodField()

    class Meta:
        model = Favorite
        fields = ['recipe', ]

    def get_recipe(self, obj):
        recipe_id = self.initial_data['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        return RecipeSerializer(instance=recipe).data

    def validate(self, obj):
        recipe_id = self.initial_data['recipe_id']
        user = get_object_or_404(
            User, username=self.context['request'].user.username)
        get_object_or_404(Recipe, pk=recipe_id)
        if self.context['request'].method == 'POST':
            if Favorite.objects.filter(
                user=user,
                recipe=recipe_id
            ).exists():
                raise serializers.ValidationError(
                    {'ERROR': FAVORITE_ERRORS['dublicate']}
                )
            if Recipe.objects.get(pk=recipe_id).author == user:
                raise serializers.ValidationError(
                    {'ERROR': FAVORITE_ERRORS['self add']}
                )
        if self.context['request'].method == 'DELETE':
            if not Favorite.objects.filter(
                user=user,
                recipe=recipe_id
            ).exists():
                raise serializers.ValidationError(
                    {'ERROR': FAVORITE_ERRORS['delete']}
                )
        return obj


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ''

    def to_representation(self, instance):
        return UserRecipeSerializer(instance=instance.user,
                                    context=self.context).data

    def validate(self, obj):
        subscribe_user_id = self.initial_data['user_id']
        user = get_object_or_404(
            User, username=self.context['request'].user.username)
        get_object_or_404(User, id=subscribe_user_id)
        if self.context['request'].method == 'POST':
            if Follow.objects.filter(
                user=subscribe_user_id,
                follower=user.id
            ).exists():
                raise serializers.ValidationError(
                    {'ERROR': FOLLOW_ERRORS['dublicate']})
            elif subscribe_user_id == user.id:
                raise serializers.ValidationError(
                    {'ERROR': FOLLOW_ERRORS['self sub']})
        if self.context['request'].method == 'DELETE':
            if not Follow.objects.filter(
                user=subscribe_user_id,
                follower=user.id
            ).exists():
                raise serializers.ValidationError(
                    {'ERROR': FOLLOW_ERRORS['delete']})
        return obj


class IngredientMesurmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IngredientMesurment
        fields = [
            'id',
            'name',
            'measurement_unit'
        ]


class IngredientCountSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit')

    class Meta:
        model = IngredientCount
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount'
        ]


class RecipeIngredSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = IngredientCount
        fields = [
            'id',
            'amount'
        ]


class ReadRecipeSerializer(serializers.ModelSerializer):
    author = UserMainSerializer(read_only=True)
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    ingredients = IngredientCountSerializer(many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',

        ]

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        user = self.context['request'].user
        return Favorite.objects.filter(
            user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_anonymous:
            return False
        user = self.context['request'].user
        return Shopcart.objects.filter(
            user=user, recipe=obj).exists()


class MainRecipeSerializer(serializers.ModelSerializer):
    author = UserMainSerializer(read_only=True)
    ingredients = RecipeIngredSerializer(many=True)
    tags = serializers.SlugRelatedField(
        queryset=Tag.objects.all(),
        slug_field='id',
        many=True,
        required=True
    )
    image = Base64ImageField(required=True, allow_null=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, obj):
        user = self.context['request'].user
        return Favorite.objects.filter(
            user=user, recipe=obj).exists()

    def get_is_in_shopping_cart(self, obj):
        user = self.context['request'].user
        return Shopcart.objects.filter(
            user=user, recipe=obj).exists()

    def create_patch_ingred(self, recipe, ingredients):
        for ingredient in ingredients:
            try:
                current_ingredient = IngredientMesurment.objects.get(
                    pk=ingredient['id']
                )
            except Exception:
                raise serializers.ValidationError(
                    {'ERROR': RECIPE_ERRORS['not_such_ingred']}
                )
            if ingredient['amount'] <= 0:
                raise serializers.ValidationError(
                    {'ERROR': RECIPE_ERRORS['amount_err']}
                )
            ingredient_add, _ = IngredientCount.objects.get_or_create(
                ingredient=current_ingredient,
                amount=ingredient['amount']
            )
            recipe.ingredients.add(ingredient_add)
        return recipe

    def get_patch_tag(self, recipe, tags):
        for tag in tags:
            current_tag = get_object_or_404(Tag, id=tag.id)
            recipe.tags.add(current_tag)
        return recipe

    def create(self, validated_data):
        if 'ingredients' not in self.initial_data:
            raise serializers.ValidationError(
                {'ERROR': RECIPE_ERRORS['ingredients_err']}
            )
        if 'tags' not in self.initial_data:
            raise serializers.ValidationError(
                {'ERROR': TAGS['empty']}
            )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        self.create_patch_ingred(recipe=recipe, ingredients=ingredients)
        self.get_patch_tag(recipe=recipe, tags=tags)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
        if ingredients is not None:
            instance.ingredients.clear()
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get('cooking_time',
                                                   instance.cooking_time)
        instance.image = validated_data.get('image', instance.image)
        self.create_patch_ingred(recipe=instance, ingredients=ingredients)
        self.get_patch_tag(recipe=instance, tags=tags)
        instance.save()
        return instance

    def validate(self, attrs):
        INGRED_CHECK: set = set()
        if 'ingredients' not in attrs:
            raise serializers.ValidationError(
                {'ERROR': RECIPE_ERRORS['ingredients_err']}
            )
        if 'tags' not in attrs:
            raise serializers.ValidationError(
                {'ERROR': TAGS['empty']}
            )
        if len(attrs['ingredients']) == 0:
            raise serializers.ValidationError(
                {'ERROR': RECIPE_ERRORS['ingredients_err']}
            )
        for _ in attrs['ingredients']:
            INGRED_CHECK.add(_['id'])
        if len(attrs['tags']) == 0:
            raise serializers.ValidationError(
                {'ERROR': TAGS['empty']}
            )
        if len(attrs['ingredients']) != len(INGRED_CHECK):
            raise serializers.ValidationError(
                {'ERROR': RECIPE_ERRORS['dublicate']}
            )
        if len(attrs['tags']) != len(set(attrs['tags'])):
            raise serializers.ValidationError(
                {'ERROR': TAGS['dublicate']}
            )
        return attrs

    def to_representation(self, instance):
        return ReadRecipeSerializer(instance=instance,
                                    context=self.context).data
