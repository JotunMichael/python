import tempfile
import os

from PIL import Image

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer


# APP:ID_OF_URL_IN_APP
RECIPES_URL = reverse('recipe:recipe-list')

# Helper Functions


def image_upload_url(recipe_id):
    """Return URL for recipe image upload"""
    # custom URL for Endpoint
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


def detail_url(recipe_id):
    """Return recipe detail URL"""
    # /api/recipe/recipes
    # /api/recipe/recipes/1/
    return reverse('recipe:recipe-detail', args=[recipe_id])


def sample_tag(user, name='Main course'):
    """Create and return a sample tag"""
    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Cinnamon'):
    """Create and return a sample ingredient"""
    return Ingredient.objects.create(user=user, name=name)


def sample_recipe(user, **params):  # arguments to dictionary pass **params
    """Create and return a sample recipe"""
    # default fields setup pass params to dic and dic to params below
    defaults = {
        'title': 'Sample recipe',
        'time_minutes': 10,
        'price': 5.00,
    }
    # overrides **params dictionary keys or if don't exist create
    defaults.update(params)

    # convert dictionary "default to arguments"
    return Recipe.objects.create(user=user, **defaults)
    # reverse effect when calling func conversion vs when passing params


# Per Class Unique Test same file
# Class as big container function lifeCycle begin end
# mem locations garbage collection


class PublicRecipeApiTests(TestCase):
    """Test unauthenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()

    def test_required_auth(self):
        """Test the authentication is required"""
        res = self.client.get(RECIPES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTests(TestCase):
    """Test authenticated recipe API access"""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'test@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving list of recipes"""
        # Create2recipes without store them somewhere(no access direct)justInDB
        # and retrieve them below from db by id (for same user 2 recipes)
        sample_recipe(user=self.user)
        # sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        # data as a list return/pass below
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = get_user_model().objects.create_user(
            'other@test.com',
            'password123'
        )
        # Create2User recipes without store them somewhere(no access direct)
        # not shared recipes read docstring above
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.filter(user=self.user)
        # No API inconsistent needs list not object one
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail"""
        recipe = sample_recipe(user=self.user)
        # add many to many this way
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        url = detail_url(recipe.id)
        res = self.client.get(url)

        # single object not list view
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'Chocolate cheesecake',
            'time_minutes': 30,
            'price': 5.00
        }
        res = self.client.post(RECIPES_URL, payload)

        # create object in API HTTP code
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Dessert')
        payload = {
            'title': 'Avocado lime cheesecake',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 60,
            'price': 20.00
        }
        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients"""
        ingredient1 = sample_ingredient(user=self.user, name='Prawns')
        ingredient2 = sample_ingredient(user=self.user, name='Ginger')
        payload = {
            'title': 'Thai prawn red curry',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time_minutes': 20,
            'price': 7.00
        }

        res = self.client.post(RECIPES_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)

        def test_create_basic_recipe(self):
            """Test creating recipe"""
            payload = {
                'title': 'Chocolate cheesecake',
                'time_minutes': 30,
                'price': 5.00
            }
            res = self.client.post(RECIPES_URL, payload)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            recipe = Recipe.objects.get(id=res.data['id'])
            for key in payload.keys():
                # recipe.title, recipe.time_minutes, recipe.price for key
                # and NOT recipe.key for loop because
                self.assertEqual(payload[key], getattr(recipe, key))

        def test_create_recipe_with_tags(self):
            """Test creating a recipe with tags"""
            tag1 = sample_tag(user=self.user, name='Vegan')
            tag2 = sample_tag(user=self.user, name='Dessert')
            payload = {
                'title': 'Avocado lime cheesecake',
                'tags': [tag1.id, tag2.id],
                'time_minutes': 60,
                'price': 20.00
            }
            res = self.client.post(RECIPES_URL, payload)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            recipe = Recipe.objects.get(id=res.data['id'])
            tags = recipe.tags.all()
            self.assertEqual(tags.count(), 2)
            # check if one value (expected) is in another value (actual)
            self.assertIn(tag1, tags)
            self.assertIn(tag2, tags)

        def test_create_recipe_with_ingredients(self):
            """Test creating recipe with ingredients"""
            ingredient1 = sample_ingredient(user=self.user, name='Prawns')
            ingredient2 = sample_ingredient(user=self.user, name='Ginger')
            payload = {
                'title': 'Thai prawn red curry',
                'ingredients': [ingredient1.id, ingredient2.id],
                'time_minutes': 20,
                'price': 7.00
            }

            res = self.client.post(RECIPES_URL, payload)

            self.assertEqual(res.status_code, status.HTTP_201_CREATED)
            recipe = Recipe.objects.get(id=res.data['id'])
            ingredients = recipe.ingredients.all()
            self.assertEqual(ingredients.count(), 2)
            # check if one value (expected) is in another value (actual)
            self.assertIn(ingredient1, ingredients)
            self.assertIn(ingredient2, ingredients)

            # test already out of the box no need for updates (in modelViewSet)
            # patch updates obj modified fields only leaving untouched others
            # put overrides omitted info to obj
            def test_partial_update_recipe(self):
                """Test updating a recipe with patch"""
                recipe = sample_recipe(user=self.user)
                recipe.tags.add(sample_tag(user=self.user))
                # add new tag to already recipe created (replace/override)
                new_tag = sample_tag(user=self.user, name='Curry')

                payload = {'title': 'Chicken tikka', 'tags': [new_tag.id]}
                url = detail_url(recipe.id)
                self.client.patch(url, payload)

                # var gets new updates from DB if changed
                recipe.refresh_from_db()
                self.assertEqual(recipe.title, payload['title'])
                tags = recipe.tags.all()
                self.assertEqual(len(tags), 1)
                self.assertIn(new_tag, tags)

            def test_full_update_recipe(self):
                """Test updating a recipe with put"""
                recipe = sample_recipe(user=self.user)
                recipe.tags.add(sample_tag(user=self.user))

                payload = {
                    'title': 'Spaghetti carbonara',
                    'time_minutes': 25,
                    'price': 5.00
                }
                url = detail_url(recipe.id)
                self.client.put(url, payload)

                recipe.refresh_from_db()
                self.assertEqual(recipe.title, payload['title'])
                self.assertEqual(recipe.time_minutes, payload['time_minutes'])
                self.assertEqual(recipe.price, payload['price'])
                tags = recipe.tags.all()
                self.assertEqual(len(tags), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            'user@test.com',
            'testpass'
        )
        self.client.force_authenticate(self.user)
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to recipe"""
        url = image_upload_url(self.recipe.id)
        # save path to DB as hard link anchor
        with tempfile.NamedTemporaryFile(suffix='.jpg') as ntf:
            img = Image.new('RGB', (10, 10))
            img.save(ntf, format='JPEG')
            # reset read header to Start of File
            ntf.seek(0)
            # pass form with data and not json obj form by default
            res = self.client.post(url, {'image': ntf}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.recipe.id)
        res = self.client.post(url, {'image': 'notimage'}, format='multipart')

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
