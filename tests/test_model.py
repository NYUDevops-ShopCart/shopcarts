"""
Test cases for Shopcart Model

Test cases can be run with:
  nosetests
  coverage report -m
"""
import unittest
import os
import json
from werkzeug.exceptions import NotFound
from service.models import Shopcart, DataValidationError, DB
from service import app

DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:password@localhost:3306/shopcarts')

if 'VCAP_SERVICES' in os.environ:
    print('Getting database from VCAP_SERVICES')
    vcap_services = json.loads(os.environ['VCAP_SERVICES'])
    DATABASE_URI = vcap_services['dashDB For Transactions'][0]['credentials']['uri']

######################################################################
#  T E S T   C A S E S
######################################################################
class TestShopcart(unittest.TestCase):
    """ Shopcart Model Tests"""

    @classmethod
    def setUpClass(cls):
        """ These run once per Test suite """
        app.debug = False
        # Set up the test database
        app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        Shopcart.init_db(app)
        DB.drop_all()    # clean up the last tests
        DB.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        DB.drop_all()
        DB.session.remove()
        DB.session.close()

    def test_serialize_a_shopcart(self):
        """ Test serialization of a Shopcart """
        shopcart = Shopcart(product_id = 1, customer_id=1,quantity=2,price=45.66,text="Headphones",state=1)
        data = shopcart.serialize()
        self.assertNotEqual(data, None)
        self.assertIn('id', data)
        self.assertEqual(data['id'], None)
        self.assertIn('product_id', data)
        self.assertEqual(data['product_id'], 1)
        self.assertIn('customer_id', data)
        self.assertEqual(data['customer_id'], 1)
        self.assertIn('quantity', data)
        self.assertEqual(data['quantity'], 2)
        self.assertIn('price', data)
        self.assertEqual(data['price'], "45.66")
        self.assertIn('text', data)
        self.assertEqual(data['text'], "Headphones")
        self.assertIn('state', data)
        self.assertEqual(data['state'], 1)

    def test_deserialize_a_shopcart(self):
        """ Test deserialization of a Shopcart """
        data = {"id": 1, "product_id": 1, "customer_id": 1, "quantity": 2, "price": "45.66", 
        "text": "Headphones","state":1}
        shopcart = Shopcart()
        shopcart.deserialize(data)
        self.assertNotEqual(shopcart, None)
        self.assertEqual(shopcart.id, None)
        self.assertEqual(shopcart.product_id,1)
        self.assertEqual(shopcart.customer_id,1)
        self.assertEqual(shopcart.quantity, 2)
        self.assertEqual(shopcart.price,"45.66")
        self.assertEqual(shopcart.text,"Headphones")
        self.assertEqual(shopcart.state,None)
    
    def test_deserialize_a_shopcart(self):
        """ Test deserialization of an invalid dictionary Shopcart """
        data = {"id": 1, "product_id": 1,"quantity": 2, "price": "45.66", 
        "text": "Headphones","state":1}
        shopcart = Shopcart()
        self.assertRaises(DataValidationError, shopcart.deserialize,data)
    
    def test_find_by_customer_id_pos(self):
        """ Find a shopcart by customer_id """
        Shopcart(product_id=3, customer_id=10, quantity=2, price=5.0, text="pen", state=1).save()
        Shopcart(product_id=4, customer_id=11, quantity=1, price=150.30, text="book", state=0).save()
        Shopcart(product_id=5, customer_id=11, quantity=2, price=12.91, text="hat", state=1).save()
        shopcart = Shopcart.find_by_customer_id(11)
        self.assertEqual(shopcart.count(), 2)
        self.assertEqual(shopcart[0].product_id, 4)
        self.assertEqual(shopcart[0].customer_id, 11)
        self.assertEqual(shopcart[0].quantity, 1)
        self.assertEqual(float(shopcart[0].price), 150.30)
        self.assertEqual(shopcart[0].text, "book")
        self.assertEqual(shopcart[0].state, 0)
        self.assertEqual(shopcart[1].product_id, 5)
        self.assertEqual(shopcart[1].customer_id, 11)
        self.assertEqual(shopcart[1].quantity, 2)
        self.assertEqual(float(shopcart[1].price), 12.91)
        self.assertEqual(shopcart[1].text, "hat")
        self.assertEqual(shopcart[1].state, 1)
    
    def test_find_by_customer_id_neg(self):
        """ Shouldn't find a shopcart by customer_id """
        Shopcart(product_id=3, customer_id=10, quantity=2, price=5.0, text="pen", state=1).save()
        shopcart = Shopcart.find_by_customer_id(11)
        self.assertEqual(shopcart.count(), 0)

    def test_query_by_target_price_pos(self):
        """ Find a shopcart by customer_id """
        Shopcart(product_id=4, customer_id=11, quantity=1, price=150.30, text="book", state=0).save()
        Shopcart(product_id=5, customer_id=11, quantity=2, price=12.91, text="hat", state=1).save()
        shopcart = Shopcart.query_by_target_price(11, 30)
        self.assertEqual(shopcart.count(), 1)
        self.assertEqual(shopcart[0].product_id, 5)
        self.assertEqual(shopcart[0].customer_id, 11)
        self.assertEqual(shopcart[0].quantity, 2)
        self.assertEqual(float(shopcart[0].price), 12.91)
        self.assertEqual(shopcart[0].text, "hat")
        self.assertEqual(shopcart[0].state, 1)
    
    def test_query_by_target_price_neg(self):
        """ Shouldn't find a shopcart by customer_id """
        Shopcart(product_id=4, customer_id=11, quantity=1, price=150.30, text="book", state=0).save()
        shopcart = Shopcart.query_by_target_price(10, 30)
        self.assertEqual(shopcart.count(), 0)

    def test_find_by_customer_id_and_product_id(self):
    	""" Test find by customer id and product id """
    	Shopcart(product_id= 1, customer_id= 1).save()
    	item = Shopcart.find_by_customer_id_and_product_id(1, 1)
    	self.assertEqual(item.customer_id, 1)
    	self.assertEqual(item.product_id, 1)

    def test_delete(self):
    	""" Delete a item """
    	item = Shopcart(product_id = 3, customer_id = 4)
    	item.save()
    	self.assertEqual(len(Shopcart.all()) , 1)
    	# delete item and make sure it isn't in the database 
    	item.delete()
    	self.assertEqual(len(Shopcart.all()), 0)

    def test_find_by_cart_id_pos(self):
        """ Test find a shopcart item by cart_id """
        Shopcart(product_id=3, customer_id=10, quantity=2, price=5.0, text="pen", state=1).save()
        Shopcart(product_id=4, customer_id=11, quantity=1, price=150.30, text="book", state=0).save()
        shopcart = Shopcart.find_by_cart_id(2)
        self.assertEqual(shopcart.count(), 1)
        self.assertEqual(shopcart[0].product_id, 4)
        self.assertEqual(shopcart[0].customer_id, 11)
        self.assertEqual(shopcart[0].quantity, 1)
        self.assertEqual(float(shopcart[0].price), 150.30)
        self.assertEqual(shopcart[0].text, "book")
        self.assertEqual(shopcart[0].state, 0)

    def test_find_by_product_id_pos(self):
        """ Test find a shopcart item by product_id """
        Shopcart(product_id=3, customer_id=10, quantity=2, price=5.0, text="pen", state=1).save()
        Shopcart(product_id=4, customer_id=11, quantity=1, price=150.30, text="book", state=0).save()
        shopcart = Shopcart.find_by_product_id(4)
        self.assertEqual(shopcart.count(), 1)
        self.assertEqual(shopcart[0].product_id, 4)
        self.assertEqual(shopcart[0].customer_id, 11)
        self.assertEqual(shopcart[0].quantity, 1)
        self.assertEqual(float(shopcart[0].price), 150.30)
        self.assertEqual(shopcart[0].text, "book")
        self.assertEqual(shopcart[0].state, 0)
    
    def test_remove_all(self):
        """Remove all shopcart items"""
        Shopcart(product_id=3, customer_id=10, quantity=2, price=5.0, text="pen", state=1).save()
        Shopcart(product_id=4, customer_id=12, quantity=2, price=5.0, text="paper", state=1).save()
        self.assertEqual(len(Shopcart.all()),2)
        Shopcart.remove_all()
        self.assertEqual(len(Shopcart.all()),0)