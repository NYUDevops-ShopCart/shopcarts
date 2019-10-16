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
from flask import jsonify
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
            self.assertTrue(shopcart['customer_id'] == test_customer_id)
    
    def test_query_cart_items(self):
        """ Query shopcart by customer_id and show all items below the target price"""
        shopcarts = self._create_shopcarts(10)
        test_customer_id = shopcarts[0].customer_id
        test_target_price = shopcarts[0].price
        query_params_dict = {}
        query_params_dict['target_price']=str(test_target_price)
        customer_id_shopcarts = [shopcart for shopcart in shopcarts if shopcart.customer_id == test_customer_id and shopcart.price <= test_target_price]
        resp = self.app.get('/shopcarts/query/{}'.format(test_customer_id),
                            json=query_params_dict,
                            content_type= 'application/json')
        data = resp.get_json()
        self.assertEqual(len(data), len(customer_id_shopcarts))
        # check the data to be sure
        for shopcart in data:
            self.assertTrue(shopcart['customer_id'] == test_customer_id and float(shopcart['price']) <= test_target_price)

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
    							content_type='application/json')
    	self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
    	self.assertEqual(len(resp.data), 0)
    	# make sure it is deleted 
    	resp = self.app.get('/shopcarts/{}'.format(test_item.customer_id) + '/{}'.format(test_item.product_id),
    							content_type='application/json')
    	self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_checkout_shopcart(self):
        """ Checkout item in shopcart to order stage """
        shopcart_item = self._create_shopcarts(1)[0]
        self.assertEqual(shopcart_item.state,0)
        resp = self.app.put('/shopcarts/checkout/{}/{}'.format(shopcart_item.customer_id,shopcart_item.product_id),
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data= resp.get_json()
        self.assertEqual(data['data']['state'],2)
    
    def test_not_found_error_handler(self):
        """ Error handler for 404 not found """
        resp = self.app.get('/shopcarts/hello',
                            content_type='application/json')
        self.assertEqual(resp.status_code,status.HTTP_404_NOT_FOUND)
    
    def test_bad_request_error_handler(self):
        """ Error handler for 400 bad request """
        request_data={}
        request_data['quantity'] = 0
        resp = self.app.put('/shopcarts/{}/{}'.format(1,2),
                            json= request_data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_request_type_handler(self):
        """ Error handler for invalid request type 405 """
        resp = self.app.put('/shopcarts/{}'.format(1),
                            content_type='application/json')
        self.assertEqual(resp.status_code,status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_internal_server_error_handler(self):
        """ Error handler for invalid server handler 500 """
        request_data={}
        resp = self.app.get('/shopcarts/query/{}'.format(1),
                            json= request_data,
                            content_type='application/json')
        self.assertEqual(resp.status_code,status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def test_request_content_type(self):
        """ Test request header content type and 415 error handler"""
        test_item = ShopcartFactory()
        resp = self.app.post('/shopcarts/{}'.format(test_item.customer_id),
                            json=test_item.serialize(),
                            content_type='applicationnn/json')
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    
    def test_add_item_when_cart_already_exist(self):
        """ Test add item when cart already exist for given product and customer id """
        test_item = self._create_shopcarts(2)[1]
        initial_quantity = test_item.quantity
        resp = self.app.post('/shopcarts/{}'.format(test_item.customer_id),
                            json=test_item.serialize(),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        restponse_data = resp.get_json()
        self.assertEqual(initial_quantity,restponse_data['quantity'])


