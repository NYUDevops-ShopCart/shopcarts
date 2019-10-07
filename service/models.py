"""
Models for Shopcart Service
All of the models are stored in this module

Models
------
Shopcart
Attributes:
-----------
id - (integer) auto increment
product_id - (TBD) from the product API
customer_id - (TBD) from the customer API
quantity - (integer) quantity of the items
price - (float) per item
text - (string) description of the item
state - (integer) ADDED(0),REMOVED(1),DONE(2)
"""
import logging
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Shopcart(db.model):

	logger = logging.getLogger('flask.app')
    app = None

    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    #ADD for product id
    #ADD for customer id
    quantity = db.Column(db.Integer)
    price = db.Column(db.Double)
    text = db.Column(db.String(150))
    state = db.Column(db.Integer)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """ Returns all items with the given customer_id
        Args:
            customer_id (Integer): the id of the customer of the shopcart you want to match
        """
        cls.logger.info('Processing customer_id query for %s ...', customer_id)
        return cls.query.filter(cls.customer_id == customer_id)

    


