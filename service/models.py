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
DB = SQLAlchemy()
SHOPCART_ITEM_STAGE = {"ADDED":0, "REMOVED":1, "DONE":2}

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Shopcart(DB.Model):

    logger = logging.getLogger('flask.app')
    app = None
    # Table Schema
    id = DB.Column(DB.Integer, primary_key=True)
    product_id = DB.Column(DB.Integer)
    customer_id = DB.Column(DB.Integer)
    quantity = DB.Column(DB.Integer)
    price = DB.Column(DB.Numeric(10, 2))
    text = DB.Column(DB.String(150))
    state = DB.Column(DB.Integer)

    @classmethod
    def find_by_cart_id(cls, cart_id):
        """ Returns a item with the given cart_id
        Args:
            cart_id (Integer): the id of the row of the shopcart you want to match
        """
        cls.logger.info('Processing cart_id query for %s ...', cart_id)
        return cls.query.filter(cls.id == cart_id)

    @classmethod
    def check_cart_exist(cls, customer_id, product_id):
        """ Returns boolean with the given customer_id, product_id
        Args:
            customer_id, product_id (Integer):
            the customer_id, product_id of the row of the shopcart you want to match
        """
        cls.logger.info('Processing cart_id query for customer %s, product %s...',
                        customer_id, product_id)
        return cls.query.filter(cls.customer_id == customer_id,
                                cls.product_id == product_id).first()

    def __repr__(self):
        return '<Shopcart %r>' % (self.text)

    def save(self):
        """
        Saves a shopcart to the data store
        """
        Shopcart.logger.info('Saving %s', self.text)
        if not self.id:
            DB.session.add(self)
        DB.session.commit()

    def serialize(self):
        """
        Serializes a Shopcart into a dictionary

        """
        return {"id" : self.id,
                "product_id": self.product_id,
                "customer_id": self.customer_id,
                "quantity": self.quantity,
                "price": str(self.price),
                "text": self.text,
                "state": self.state}

    def deserialize(self, data):
        """
        Deserializes a shopcart from a dictionary

        Args:
            data (dict): A dictionary containing the shopcart data
        """
        try:
            self.quantity = data['quantity']
            self.price = data['price']
            self.text = data['text']
            self.product_id = data['product_id']
            self.customer_id = data['customer_id']
        except KeyError as error:
            raise DataValidationError('Invalid shopcart item: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid shopcart item: body of request contained' \
                                      'bad or no data')
        return self

    @classmethod
    def init_db(cls, app):
        """ Initializes the database session """
        cls.logger.info('Initializing database')
        cls.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        DB.init_app(app)
        app.app_context().push()
        DB.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Shopcarts in the database """
        cls.logger.info('Get all shopcarts')
        return cls.query.all()

    def delete(self):
        ## Remove an item from the data store
        Shopcart.logger.info('Deleting %s', self.id)
        DB.session.delete(self)
        DB.session.commit()

    @classmethod
    def find_by_product_id(cls, product_id):
        ## Find a shopcart item by its id
        cls.logger.info("Look up %s", product_id)
        return cls.query.filter(cls.product_id == product_id)

    @classmethod
    def find_by_customer_id(cls, customer_id):
        """ Returns all items with the given customer_id
        Args:
            customer_id (Integer): the id of the customer of the shopcart you want to match
        """
        cls.logger.info('Processing customer_id query for %s ...', customer_id)
        return cls.query.filter(cls.customer_id == customer_id)

    @classmethod
    def find_by_customer_id_and_product_id(cls, customer_id, product_id):
        """ Returns all items with the given customer_id
        Args:
            customer_id (Integer): the id of the customer of the shopcart you want to match
        """
        cls.logger.info('Processing customer_id & product_id query for customer %s, product %s...',
                        customer_id, product_id)
        return cls.query.filter((cls.customer_id == customer_id)
                                & (cls.product_id == product_id)).first()

    @classmethod
    def query_by_target_price(cls, customer_id, price):
        """ Returns all items with the given customer_id and below the price
        Args:
            customer_id (Integer):
            the id of the customer of the shopcart you want to match
            price(Numeric):
            the price of the items that are set as target,
            so all selected items are below that target
        """
        cls.logger.info('Processing customer query for %s and price query for %s...',
                        customer_id, price)
        return cls.query.filter((cls.customer_id == customer_id) & (cls.price <= price))
    
    @classmethod
    def remove_all(cls):
        """ Removes all documents from the database (use for testing)  """
        DB.session.query(Shopcart).delete()
        DB.session.commit()
