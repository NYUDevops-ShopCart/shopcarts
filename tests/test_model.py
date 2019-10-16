"""
Test cases for Shopcart Model

Test cases can be run with:
  nosetests
  coverage report -m
"""
import unittest
import os
from werkzeug.exceptions import NotFound
from service.models import Shopcart, DataValidationError, db
from service import app

DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:password@localhost:3306/shopcarts')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestShopcart(unittest.TestCase):
    """ Test Cases for Pets """

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
        db.drop_all()    # clean up the last tests
        db.create_all()  # make our sqlalchemy tables

    def tearDown(self):
        db.session.remove()
        db.drop_all()

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