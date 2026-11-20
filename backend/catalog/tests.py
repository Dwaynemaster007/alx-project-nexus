from decimal import Decimal

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Category, Product


class CatalogApiTests(APITestCase):
    def setUp(self):
        phones = Category.objects.create(title='Phones', slug='phones')
        laptops = Category.objects.create(title='Laptops', slug='laptops')
        self.phone = Product.objects.create(name='Phone One', description='A phone', price=Decimal('100'), category=phones, stock_quantity=5)
        Product.objects.create(name='Phone Two', description='Another phone', price=Decimal('300'), category=phones, stock_quantity=0)
        Product.objects.create(name='Laptop One', description='A laptop', price=Decimal('900'), category=laptops, stock_quantity=2)

    def names(self, response):
        return sorted(p['name'] for p in response.data['results'])

    def test_list_is_paginated(self):
        response = self.client.get('/api/products/', {'limit': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 3)
        self.assertEqual(len(response.data['results']), 2)

    def test_filters_search_and_ordering(self):
        self.assertEqual(self.names(self.client.get('/api/products/', {'category_slug': 'phones'})), ['Phone One', 'Phone Two'])
        self.assertEqual(self.names(self.client.get('/api/products/', {'min_price': 200, 'max_price': 500})), ['Phone Two'])
        self.assertEqual(self.names(self.client.get('/api/products/', {'search': 'laptop'})), ['Laptop One'])
        ordered = self.client.get('/api/products/', {'ordering': '-price'}).data['results']
        self.assertEqual([p['name'] for p in ordered], ['Laptop One', 'Phone Two', 'Phone One'])

    def test_categories_are_a_plain_list(self):
        response = self.client.get('/api/categories/')
        self.assertEqual([c['slug'] for c in response.data], ['laptops', 'phones'] if response.data[0]['slug'] == 'laptops' else ['phones', 'laptops'])

    def test_reviews_update_average_rating(self):
        url = f'/api/products/{self.phone.id}/reviews/'
        self.assertEqual(self.client.post(url, {'name': 'Ann', 'rating': 4, 'comment': 'Good'}, format='json').status_code, status.HTTP_201_CREATED)
        self.client.post(url, {'name': 'Ben', 'rating': 5, 'comment': 'Great'}, format='json')
        self.assertEqual(len(self.client.get(url).data), 2)
        self.assertEqual(self.client.get(f'/api/products/{self.phone.id}/').data['average_rating'], 4.5)

    def test_only_admins_can_change_products(self):
        payload = {'name': 'Tablet', 'description': 'New', 'price': '250.00', 'category': self.phone.category_id, 'stock_quantity': 1}
        self.assertIn(self.client.post('/api/products/', payload, format='json').status_code, (401, 403))
        admin = get_user_model().objects.create_superuser('admin', 'admin@example.com', 'Str0ng-pass!')
        self.client.force_authenticate(admin)
        self.assertEqual(self.client.post('/api/products/', payload, format='json').status_code, status.HTTP_201_CREATED)
