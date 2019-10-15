"""
Shopcarts API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""
import unittest
import os
import logging
from flask_api import status    # HTTP Status Codes
from unittest.mock import MagicMock, patch
from service.models import Shopcart, DataValidationError, db
from .shopcart_factory import ShopcartFactory
from service.service import app, init_db, initialize_logging

DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:password@localhost:3306/shopcarts')
######################################################################
#  T E S T   C A S E S
######################################################################
class TestShopcartServer(unittest.TestCase):
    """ Shopcart Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        app.debug = False
        initialize_logging(logging.INFO)
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        init_db()
        db.drop_all()    # clean up the last tests
        db.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['text'], 'Shop cart service')

    def _create_shopcarts(self, count):
        """ Factory method to create shopcarts in bulk """
        shopcarts = []
        for _ in range(count):
            test_shopcart = ShopcartFactory()

            resp = self.app.post('/shopcarts/{}'.format(test_shopcart.customer_id),
                                 json=test_shopcart.serialize(),
                                 content_type='application/json')
            self.assertEqual(resp.status_code, status.HTTP_201_CREATED, 'Could not create test shopcart')
            new_shopcart = resp.get_json()
            test_shopcart.id = new_shopcart['id']
            shopcarts.append(test_shopcart)
        return shopcarts
    
    def test_list_cart_iterms(self):
        """ List all items of the shopcart for a customer"""
        shopcarts = self._create_shopcarts(10)
        test_customer_id = shopcarts[0].customer_id
        customer_id_shopcarts = [shopcart for shopcart in shopcarts if shopcart.customer_id == test_customer_id]
        resp = self.app.get('/shopcarts/{}'.format(test_customer_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(customer_id_shopcarts))
        # check the data to be sure
        for shopcart in data:
            self.assertEqual(shopcart['customer_id'], test_customer_id)
    
    def test_query_cart_items(self):
        """ Query shopcart by customer_id and show all items below the target price"""
        shopcarts = self._create_shopcarts(5)
        test_customer_id = shopcarts[0].customer_id
        test_target_price = shopcarts[0].price
        customer_id_shopcarts = [shopcart for shopcart in shopcarts if shopcart.customer_id == test_customer_id and shopcart.price <= test_customer_price]
        resp = self.app.get('/shopcarts/query/{}'.format(test_customer_id),
                            json='target_price':test_target_price,
                            content_type= 'application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), len(customer_id_shopcarts))
        # check the data to be sure
        for shopcart in data:
            self.assertTrue(shopcart.customer_id == test_customer_id & shopcart.price <= test_target_price)
    