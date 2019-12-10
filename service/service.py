import os
import sys
import logging
import requests
from flask import Flask, jsonify, request, url_for, make_response, abort, json
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound
from flask_restplus import Api, Resource, fields, reqparse, inputs

# SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Shopcart, DataValidationError, SHOPCART_ITEM_STAGE

# Import Flask application
from . import app

ORDER_HOST_URL = "http://localhost:1234"


######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(status.HTTP_400_BAD_REQUEST)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_400_BAD_REQUEST,
                   error='Bad Request',
                   message=message), status.HTTP_400_BAD_REQUEST

@app.errorhandler(status.HTTP_404_NOT_FOUND)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_404_NOT_FOUND,
                   error='Not Found',
                   message=message), status.HTTP_404_NOT_FOUND

@app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_405_METHOD_NOT_ALLOWED,
                   error='Method not Allowed',
                   message=message), status.HTTP_405_METHOD_NOT_ALLOWED

@app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = str(error)
    app.logger.warning(message)
    return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                   error='Unsupported media type',
                   message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

@app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = str(error)
    app.logger.error(message)
    return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                   error='Internal Server Error',
                   message=message), status.HTTP_500_INTERNAL_SERVER_ERROR

######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return app.send_static_file('index.html')

######################################################################
# Configure Swagger
######################################################################
api = Api(app,
          version='1.0.0',
          title='Shopcart RESTful Service',
          description='This is a sample Shopcart store server.',
          default='shopcarts',
          default_label='Shopcart operations',
          doc='/apidocs/index.html'
         )

# Define the model so that the docs reflect what can be sent
shopcart_model = api.model('Shopcart', {
    'id': fields.String(readOnly=True,
                         description='The unique id assigned internally by service'),
    'product_id': fields.String(required=True,
                          description='Product Identifier'),
    'customer_id': fields.String(required=True,
                              description='Customer Identifier'),
    'quantity': fields.Boolean(required=True,
                                description='Quantity of the product'),
    'price': fields.String(required=True,
                              description='Price'),
    'text': fields.String(required=True,
                              description='Name of the product'),
    'state': fields.String(required=True,
                              description='State of the product in shopcart.(ADDED:0 (Default), REMOVED:1, DONE:2)')
})

create_model = api.model('Shopcart', {
    'product_id': fields.String(required=True,
                          description='Product Identifier'),
    'customer_id': fields.String(required=True,
                              description='Customer Identifier'),
    'quantity': fields.Boolean(required=True,
                                description='Quantity of the product'),
    'price': fields.String(required=True,
                              description='Price'),
    'text': fields.String(required=True,
                              description='Name of the product')
})

######################################################################
# LIST ALL ITEMS IN ONE SHOP CART ---
######################################################################
@app.route('/shopcarts/<int:customer_id>', methods=['GET'])
def list_cart_iterms(customer_id):
    """ Returns list of all of the shop cart items"""
    if request.args.get('price') == None:
        app.logger.info('Request to list all items in shopcart with customer_id: %s', customer_id)
        items = []
        items = Shopcart.find_by_customer_id(customer_id)
        results = [item.serialize() for item in items]
        return make_response(jsonify(results), status.HTTP_200_OK)

    else:    
        target_price = request.args.get('price')
        app.logger.info('Request to query all items in shopcart with customer_id: %s', customer_id)
        items = []
        items = Shopcart.query_by_target_price(customer_id, target_price)
        results = [item.serialize() for item in items]
        return make_response(jsonify(results), status.HTTP_200_OK)

######################################################################
# RETRIEVE AN ITEM
######################################################################
@app.route('/shopcarts/<int:customer_id>/<int:product_id>', methods=['GET'])
def get_cart_item(customer_id, product_id):

    """
    Retrieve a single shop cart item
    """
    app.logger.info('Request for shopcart item with customer %s, product %s...',
                    customer_id, product_id)
    item = Shopcart.find_by_customer_id_and_product_id(customer_id, product_id)
    if item:
        return make_response(jsonify(item.serialize()), status.HTTP_200_OK)
    return make_response(jsonify({"error": " Product not in cart"}), status.HTTP_404_NOT_FOUND)


######################################################################
# ADD A NEW ITEM TO THE SHOP CART
######################################################################
@app.route('/shopcarts/<int:customer_id>', methods=['POST'])
def create_cart_item(customer_id):

    """
    Creates a new item entry for the cart
    """
    app.logger.info('Request to create shopcart item for costomer: %s', customer_id)
    check_content_type('application/json')
    # check if coustomer_id are the same
    if not customer_id == int(request.get_json()['customer_id']):
        # abort(400, description="coustomer id doesn't match")
        app.logger.info("coustomer id doesn't match")
        return make_response("coustomer id doesn't match", status.HTTP_400_BAD_REQUEST)
    product_id = request.get_json()['product_id']
    shopcart = Shopcart()
    # check if the item is already in this customer's cart
    if Shopcart.check_cart_exist(customer_id, product_id):
        # abort(409, description="item already in the cart")
        return make_response("item already in the cart", status.HTTP_409_CONFLICT)
    shopcart.deserialize(request.get_json())
    shopcart.save()
    message = shopcart.serialize()
    location_url = url_for('get_cart_item', customer_id=customer_id, product_id=product_id)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })

######################################################################
# UPDATE AN EXISTING SHOPCART ITEM
######################################################################
@app.route('/shopcarts/<int:customer_id>/<int:product_id>', methods=['PUT'])
def update_cart_item(customer_id, product_id, requested_quantity=None):
    app.logger.info('Request to update shopcart item with customer_id: %s, product_id: %s',
                    customer_id, product_id)
    cart_item = Shopcart.find_by_customer_id_and_product_id(customer_id, product_id)
    if not cart_item:
        app.logger.info("Customer_id and product_id for update have not been found")
        return jsonify({'message': "Customer_id and product_id for update have not been found"
                       }), status.HTTP_400_BAD_REQUEST
    if requested_quantity is None:
        requested_quantity = int(request.get_json()["quantity"])
    # bounds check
    if requested_quantity < 1:
        app.logger.info('Negative quantity requested')
        return jsonify({'message': "Invalid quantity"}), status.HTTP_400_BAD_REQUEST
    # process to update the request
    cart_item.quantity = requested_quantity
    cart_item.save()
    app.logger.info('Quantity for customer id %s and product id %s has been updated',
                    customer_id, product_id)
    return make_response(cart_item.serialize(), status.HTTP_200_OK)

######################################################################
# DELETE A SHOPCART ITEM
######################################################################
@api.route('/shopcarts/<int:customer_id>/<int:product_id>',strict_slashes=False)
@api.param('customer_id','Customer Identifier')
@api.param('product_id','Product Identifier')
class ShopcartResource(Resource):
    #------------------------------------------------------------------
    # DELETE A Shopcart Item 
    #------------------------------------------------------------------
    @api.doc('shopcart_delete')
    @api.response(204,'Item deleted')
    def delete(self, customer_id, product_id):
        """
        Delete an item from shopcart

        This endpoint will delete a item for the selected product in the shopcart
        """
        app.logger.info('Request to delete an existing shopcart item with customer id: %s and product_id: %s',
                    customer_id, product_id)
        cart_item = Shopcart.find_by_customer_id_and_product_id(customer_id, product_id)

        if cart_item:
            app.logger.info('Found item with customer id and product id and it will be deleted')
            cart_item.delete()
        # should return 204 whether item is found or not found as discussed in class
        return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# MOVE A SHOPCART ITEM TO CHECKOUT
######################################################################

@api.route('/shopcarts/<int:customer_id>/<int:product_id>/checkout',strict_slashes=False)
@api.param('customer_id','Customer Identifier')
@api.param('product_id','Product Identifier')
class ShopcartCheckout(Resource):
    # Move a product from to order SHOPCART_ITEM_STAGE
    
    @api.doc('shopcart_checkout')
    @api.response(400,'Invalid request params')
    @api.response(200,'Product moved to Order Successfully')
    def put(self,customer_id,product_id):
        """
        Purchase an item from shopcart

        This endpoint will place an order for the selected product in the shopcart
        """
        app.logger.info('Request to move product with id %s for customer with id %s to checkout',
                    product_id, customer_id)
        cart_item = Shopcart.find_by_customer_id_and_product_id(customer_id, product_id)
        if cart_item is None:
            app.logger.info("No product with id %s found for customer id %s", product_id, customer_id)
            api.abort(status.HTTP_400_BAD_REQUEST, 'No product with id [{}] found for customer id [{}].'
                .format(product_id,customer_id))
            #return make_response(jsonify(message='Invalid request params'), status.HTTP_400_BAD_REQUEST)

        try:
            post_url = "{}/orders".format(ORDER_HOST_URL)
            request_data = {}
            request_data['customer_id'] = cart_item.customer_id
            request_data['product_id'] = cart_item.product_id
            request_data['price'] = cart_item.price
            request_data['quantity'] = cart_item.quantity
            response = requests.post(url=post_url, json=request_data)
            app.logger.info("Product with id %s for customer id %s moved from shopcart to order",
                            cart_item.product_id, cart_item.customer_id)
        except Exception as ex:
            app.logger.error("Something went wrong while moving product from shopcart to order %s", ex)

        cart_item.state = SHOPCART_ITEM_STAGE['DONE']
        cart_item.save()
        app.logger.info('Shopcart with product id %s and customer id %s moved to checkout',
                        product_id, customer_id)
        return make_response(jsonify(message="Product moved to Order Successfully",
                                     data=cart_item.serialize()), status.HTTP_200_OK)

######################################################################
# DELETE ALL SHOPCART ITEMS FOR TESTING ONLY
######################################################################
@app.route('/shopcarts/reset', methods=['DELETE'])
def delete_cart_items():
    app.logger.info('Request to delete all shopcart items')
    Shopcart.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Shopcart.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print('Setting up logging...')
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.propagate = False
        app.logger.info('Logging handler established')
