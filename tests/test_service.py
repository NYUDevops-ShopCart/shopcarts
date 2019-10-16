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

    def test_update_shopcart(self):
    	""" Update the item in the shopcart """
    	# create an itme to update 
    	test_item = ShopcartFactory()
    	resp = self.app.post('/shopcarts/{}'.format(test_item.customer_id),
                                 json=test_item.serialize(),
                                 content_type='application/json')
    	self.assertEqual(resp.status_code, status.HTTP_201_CREATED, 'Could not create shopcart entry')

    	# update the item
    	new_item = resp.get_json()
    	new_item['quantity'] = 9999
    	resp = self.app.put('/shopcarts/{}/{}'.format(new_item['customer_id'],new_item['product_id']),
    						json= new_item,
    						content_type='application/json')
    	self.assertEqual(resp.status_code, status.HTTP_200_OK)
    	updated_item = resp.get_json()
    	self.assertEqual(updated_item['quantity'], 9999)

    def test_delete_shopcart(self):
    	""" Delete the item in the shopcart """
    	test_item = self._create_shopcarts(1)[0]
    	resp = self.app.delete('/shopcarts/{}'.format(test_item.customer_id) + '/{}'.format(test_item.product_id),
    							json=test_item.serialize(),
    							content_type='applicatoin/json')
    	self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
    	self.assertEqual(len(resp.data), 0)
    	# make sure it is deleted 
    	resp = self.app.get('/shopcarts/{}'.format(test_item.customer_id) + '/{}'.format(test_item.product_id),
    							content_type='application/json')
    	self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_shopcart(self):
        """ Create the item in the shopcart """
        # create an item 
        test_item = ShopcartFactory()
        resp = self.app.post('/shopcarts/{}'.format(test_item.customer_id), json=test_item.serialize(), content_type='application/json')
        print(test_item.quantity)
        data = resp.get_json()
        print(data)
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED, 'Could not create shopcart entry')
        self.assertEqual(data['customer_id'], test_item.customer_id, 'cutsomer_id not the same')
        self.assertEqual(data['product_id'], test_item.product_id, 'product_id not the same')
        self.assertEqual(data['quantity'], test_item.quantity, 'quantity not the same')
        self.assertEqual(data['text'], test_item.text, 'text not the same')
        test_item.quantity += 1
        # create again to update item 
        print(test_item.quantity)
        resp = self.app.post('/shopcarts/{}'.format(test_item.customer_id), json=test_item.serialize(), content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_409_CONFLICT)

    def test_retrieve_shopcart(self):
        """ Retrieve the item from the shopcart """
        # create an item 
        test_item = ShopcartFactory()
        self.app.post('/shopcarts/{}'.format(test_item.customer_id),
                            json=test_item.serialize(),
                            content_type='application/json')
        resp = self.app.get('/shopcarts/{}/{}'.format(test_item.customer_id, test_item.product_id))
        data = resp.get_json()
        self.assertEqual(resp.status_code, status.HTTP_200_OK, 'Could not retrieve shopcart entry')
        self.assertEqual(data['product_id'], test_item.product_id, 'Retrieved the wrong item')
        self.assertEqual(data['customer_id'], test_item.customer_id, 'Retrieved the wrong item')
        resp = self.app.get('/shopcarts/{}/{}'.format(-1, test_item.product_id))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND, 'Should not found anything')
        resp = self.app.get('/shopcarts/{}/{}'.format(test_item.customer_id, -1))
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND, 'Should not found anything')