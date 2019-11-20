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
import json
from flask_api import status    # HTTP Status Codes
from unittest.mock import MagicMock, patch
from flask import jsonify
from service.models import Shopcart, DataValidationError, DB
from .shopcart_factory import ShopcartFactory
from service.service import app, init_db, initialize_logging

DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:password@localhost:3306/shopcarts')
if 'VCAP_SERVICES' in os.environ:
    print('Getting database from VCAP_SERVICES')
    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap_services['dashDB For Transactions'][0]['credentials']['uri']
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
        DB.drop_all()    # clean up the last tests
        DB.create_all()  # create new tables
        self.app = app.test_client()

    def tearDown(self):
        DB.drop_all()
        DB.session.remove()
        DB.session.close()

    def test_index(self):
        """ Test the Home Page """
        resp = self.app.get('/')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertIn(b'Shopcart REST API Service', resp.data)

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

    def test_query_cart_iterms(self):
        """ Query all items of the shopcart for a customer which price is below 20 dollars"""
        shopcarts = self._create_shopcarts(10)
        test_customer_id = shopcarts[0].customer_id
        test_target_price = shopcarts[0].price
        customer_id_shopcarts = [shopcart for shopcart in shopcarts if shopcart.customer_id == test_customer_id]
        resp = self.app.get('/shopcarts/{}?price={}/'.format(test_customer_id, test_target_price))
        data = resp.get_json()
        self.assertEqual(len(data), len(customer_id_shopcarts))
        # check the data to be sure
        for shopcart in data:
            self.assertTrue(shopcart['customer_id'] == test_customer_id and float(shopcart['price']) <= test_target_price)

    def test_get_cart_item_pos(self):
        """ Retrieve a single shop cart item """
        test_shopcart = self._create_shopcarts(1)[0]
        resp = self.app.get('/shopcarts/{}/{}'.format(test_shopcart.customer_id, test_shopcart.product_id),
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data['customer_id'], test_shopcart.customer_id)
        self.assertEqual(data['product_id'], test_shopcart.product_id)

    def test_get_cart_item_neg(self):
        """ Get a single shop cart item that is not found """
        resp = self.app.get('/shopcarts/0/0')
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

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

        # bounds check
        new_item2 = updated_item
        new_item2['quantity'] = -1
        resp = self.app.put('/shopcarts/{}/{}'.format(new_item2['customer_id'], new_item2['product_id']),
                            json=new_item2,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        resp = self.app.get('/shopcarts/{}/{}'.format(new_item2['customer_id'], new_item2['product_id']),
                            content_type='aaplication/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_item2 = resp.get_json()
        self.assertEqual(new_item2['quantity'], 9999)

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

    def test_checkout_shopcart(self):
        """ Checkout item in shopcart to order stage """
        shopcart_item = self._create_shopcarts(1)[0]
        self.assertEqual(shopcart_item.state,0)
        resp = self.app.put('/shopcarts/{}/{}/checkout'.format(shopcart_item.customer_id,shopcart_item.product_id),
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data= resp.get_json()
        self.assertEqual(data['data']['state'],2)
    
    def test_checkout_shopcart_bad_request(self):
        """ Checkout item in shopcart to order stage when item does not exist"""
        resp = self.app.put('/shopcarts/{}/{}/checkout'.format(564,546),
                                content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_delete_all_shopcart(self):
    	""" Delete all items in the shopcart table"""
    	test_item = self._create_shopcarts(1)[0]
    	resp = self.app.delete('/shopcarts/reset',
    							content_type='applicatoin/json')
    	self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
    	self.assertEqual(len(resp.data), 0)

    @patch('service.models.Shopcart.find_by_customer_id')
    def test_bad_request(self, bad_request_mock):
        """ Test a Bad Request error from Find by Customer ID """
        bad_request_mock.side_effect = DataValidationError()
        resp = self.app.get('/shopcarts/{}'.format(1))
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
    
    @patch('service.models.Shopcart.find_by_customer_id')
    def test_mock_search_data(self, shopcart_find_by_customer_id_mock):
        """ Test showing how to mock data """
        shopcart_find_by_customer_id_mock.return_value = [MagicMock(serialize=lambda: {'customer_id': 1})]
        resp = self.app.get('/shopcarts/{}'.format(1))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
    
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
    
    def test_request_content_type(self):
        """ Test request header content type and 415 error handler"""
        test_item = ShopcartFactory()
        resp = self.app.post('/shopcarts/{}'.format(test_item.customer_id),
                            json=test_item.serialize(),
                            content_type='applicationnn/json')
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_internal_server_error_handler(self):
        """ Error handler for invalid server handler 500 """
        request_data={}
        resp = self.app.post('/shopcarts/{}'.format(1),
                            json= request_data,
                            content_type='application/json')
        self.assertEqual(resp.status_code,status.HTTP_500_INTERNAL_SERVER_ERROR)

