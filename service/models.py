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

class Shopcart(db.Model):

    logger = logging.getLogger('flask.app')
    app = None
    # Table Schema
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer)
    customer_id = db.Column(db.Integer)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Numeric(10,2))
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

    def __repr__(self):
        return '<Shopcart %r>' % (self.name)

    def save(self):
        """
        Saves a shopcart to the data store
        """
        Shopcart.logger.info('Saving %s', self.text)
        if not self.id:
            db.session.add(self)
        db.session.commit()

    def serialize(self):
        """ 
        Serializes a Pet into a dictionary 
        
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
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    @classmethod
    def all(cls):
        """ Returns all of the Pets in the database """
        cls.logger.info('Get all shopcarts')
        return cls.query.all()

    def delete(self):
        ## Remove an item from the data store
        Shopcart.logger.info('Deleting %s', self.id)
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_product_id(cls, product_id):
        ## Find a shopcart item by its id
        cls.logger.info("Look up %s", product_id)
        return cls.query.get(product_id) 