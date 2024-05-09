MAX_LENGTH: int = 200
COLOR_LENGTH: int = 20
COOK_VALIDATOR_MESSAGE: str = 'Минимально допустимое время 1 мин'
NAME_LENGTH: int = 128

SHOP_CART_ERRORS: dict = {
    'dublicate': 'Вы не можете добавлять одинаковые рецепты',
    'delete': 'Такого рецепта у вас в корзине товаров нет'
}

FAVORITE_ERRORS: dict = {
    'dublicate': 'Вы не можете добавлять одинаковые рецепты',
    'self add': 'Не можете добавить свой рецепт в избранное',
    'delete': 'Такого рецепта у вас в избранном нет'
}

RECIPE_ERRORS: dict = {
    'ingredients_err': 'Добавьте хотя бы один ингредиент',
    'not_such_ingred': 'Такого ингредиента не существует',
    'amount_err': 'Недопустимое количесвто',
    'dublicate': 'Не должно быть повторяющихся ингредиентов',
    'no recipe': 'Не существует такого рецпта',
    'no image': 'Добавьте картинку'
}

FOLLOW_ERRORS: dict = {
    'dublicate': 'Вы не можете подписаться дважды',
    'self sub': 'Вы не можете подписаться на самого себя',
    'delete': 'Невозможно совершить действие'
}

TAGS: dict = {
    'empty': 'Добавьте хотя бы один тег',
    'dublicate': 'Теги не должны повторяться'
}

USER_ERRORS: dict = {
    'username exists': 'Такой никнейм уже существует'
}

SHOPPING_CART: dict = {
    'welcome': 'Список продуктов для пользователя',
    'ending': 'Ваш Bebafood'
}
