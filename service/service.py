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
# @app.errorhandler(DataValidationError)
# def request_validation_error(error):
#     """ Handles Value Errors from bad data """
#     return bad_request(error)

# @app.errorhandler(status.HTTP_400_BAD_REQUEST)
# def bad_request(error):
#     """ Handles bad reuests with 400_BAD_REQUEST """
#     message = str(error)
#     app.logger.warning(message)
#     return jsonify(status=status.HTTP_400_BAD_REQUEST,
#                    error='Bad Request',
#                    message=message), status.HTTP_400_BAD_REQUEST

# @app.errorhandler(status.HTTP_404_NOT_FOUND)
# def not_found(error):
#     """ Handles resources not found with 404_NOT_FOUND """
#     message = str(error)
#     app.logger.warning(message)
#     return jsonify(status=status.HTTP_404_NOT_FOUND,
#                    error='Not Found',
#                    message=message), status.HTTP_404_NOT_FOUND

# @app.errorhandler(status.HTTP_405_METHOD_NOT_ALLOWED)
# def method_not_supported(error):
#     """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
#     message = str(error)
#     app.logger.warning(message)
#     return jsonify(status=status.HTTP_405_METHOD_NOT_ALLOWED,
#                    error='Method not Allowed',
#                    message=message), status.HTTP_405_METHOD_NOT_ALLOWED

# @app.errorhandler(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
# def mediatype_not_supported(error):
#     """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
#     message = str(error)
#     app.logger.warning(message)
#     return jsonify(status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
#                    error='Unsupported media type',
#                    message=message), status.HTTP_415_UNSUPPORTED_MEDIA_TYPE

# @app.errorhandler(status.HTTP_500_INTERNAL_SERVER_ERROR)
# def internal_server_error(error):
#     """ Handles unexpected server error with 500_SERVER_ERROR """
#     message = str(error)
#     app.logger.error(message)
#     return jsonify(status=status.HTTP_500_INTERNAL_SERVER_ERROR,
#                    error='Internal Server Error',
#                    message=message), status.HTTP_500_INTERNAL_SERVER_ERROR

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
    'id': fields.Integer(readOnly=True,
                         description='The unique id assigned internally by service'),
    'product_id': fields.Integer(required=True,
                                 description='Product Identifier'),
    'customer_id': fields.Integer(required=True,
                                   description='Customer Identifier'),
    'quantity': fields.Integer(required=True,
                                description='Quantity of the product'),
    'price': fields.Float(required=True,
                          description='Price'),
    'text': fields.String(required=True,
                          description='Name of the product'),
    'state': fields.Integer(required=True,
                            description='State of the product in shopcart.(ADDED:0 (Default), REMOVED:1, DONE:2)')
})

create_model = api.model('Shopcart', {
    'product_id': fields.Integer(required=True,
                                 description='Product Identifier'),
    'customer_id': fields.Integer(required=True,
                                  description='Customer Identifier'),
    'quantity': fields.Integer(required=True,
                                description='Quantity of the product'),
    'price': fields.Float(required=True,
                           description='Price'),
    'text': fields.String(required=True,
                              description='Name of the product')
})

shopcart_args = reqparse.RequestParser()
shopcart_args.add_argument('price', type=float, required=False, help='List shocpart items (cheapter than target_price if there exists one)')

######################################################################
# RETRIEVE; DELETE; UPDATE
######################################################################
@api.route('/shopcarts/<int:customer_id>/<int:product_id>', strict_slashes=False)
@api.param('customer_id','Customer Identifier')
@api.param('product_id','Product Identifier')
class ShopcartItem(Resource):
    #------------------------------------------------------------------
    # Retrieve A Shopcart Item 
    #------------------------------------------------------------------
    @api.doc('get_shopcart_item')
    @api.response(404, 'Item not found')
    def get(self, customer_id, product_id):
        """
        Retrieve a single shop cart item
        """
        app.logger.info('Request for shopcart item with customer %s, product %s...',
                    customer_id, product_id)
        item = Shopcart.find_by_customer_id_and_product_id(customer_id, product_id)
        if item:
            return item.serialize(), status.HTTP_200_OK
        api.abort(status.HTTP_404_NOT_FOUND, "Product not in cart")

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

    #------------------------------------------------------------------
    # UPDATE AN EXISTING PET
    #------------------------------------------------------------------
    @api.doc('shopcart_update')
    @api.response(200,'Product Updated Successfully')
    @api.response(400,'Invalid Request')
    @api.expect(shopcart_model)
    #@api.marshal_with(shopcart_model)
    def put(self, customer_id, product_id):
        """
        Update an item from shopcart
        This endpoint will update a item for the selected product in the shopcart
        """
        app.logger.info('Request to update shopcart item with customer_id: %s, product_id: %s', customer_id, product_id)
        cart_item = Shopcart.find_by_customer_id_and_product_id(customer_id, product_id)
        
        if not cart_item:
            app.logger.info("Customer_id and product_id for update have not been found")
            api.abort(status.HTTP_400_BAD_REQUEST, 'No product with id [{}] found for customer id [{}].'
                .format(product_id,customer_id))

        app.logger.debug('Payload = %s', api.payload)
        data = api.payload
        update_cart_item = Shopcart()
        update_cart_item.deserialize(data)

        try:
            requested_quantity = int(update_cart_item.quantity)
            app.logger.info("requested_quantity = %s", requested_quantity)
        except ValueError:
            app.logger.info('Non-integer quantity requested')
            api.abort(status.HTTP_400_BAD_REQUEST, 'Non-integer quantity given')
        
        # bounds check
        if requested_quantity < 1:
            app.logger.info('Negative quantity requested')
            api.abort(status.HTTP_400_BAD_REQUEST, 'No positive product with id [{}] found for customer id [{}].'
                .format(product_id,customer_id))
    
        # process to update the request
        cart_item.quantity = requested_quantity
        app.logger.info("cart_item.quantity = %s", cart_item.quantity)
        cart_item.state = SHOPCART_ITEM_STAGE['ADDED']
        cart_item.save()
        app.logger.info('Quantity for customer id %s and product id %s has been updated',
                    customer_id, product_id)
        return cart_item.serialize(), status.HTTP_200_OK
        

######################################################################
# CREATE; LIST; QUERY
######################################################################
@api.route('/shopcarts/<int:customer_id>', strict_slashes=False)
@api.param('customer_id','Customer Identifier')
class ShopcartResource(Resource):
    @api.doc('create_item')
    @api.expect(create_model)
    @api.response(400, "Coustomer id doesn't match")
    @api.response(409, 'Item already in the cart')
    def post(self, customer_id):
        """
        Creates a new item entry for the cart
        """
        app.logger.info('Request to create shopcart item for costomer: %s', customer_id)
        check_content_type('application/json')
        if not customer_id == int(api.payload['customer_id']):
            app.logger.info("Coustomer id doesn't match")
            abort(400, description="Coustomer id doesn't match")
        product_id = api.payload['product_id']
        if Shopcart.check_cart_exist(customer_id, product_id):
            abort(409, description="Item already in the cart")
        shopcart = Shopcart()
        shopcart.deserialize(api.payload)
        shopcart.save()
        location_url = api.url_for(ShopcartItem, customer_id = customer_id,
                                    product_id = product_id, _extrenal = True)
        return shopcart.serialize(), status.HTTP_201_CREATED, {'Location': location_url}

    @api.doc('shopcart_list')
    @api.expect(shopcart_args, validate=True)
    @api.marshal_list_with(shopcart_model)
    # @app.route('/shopcarts/<int:customer_id>', methods=['GET'])
    def get(self, customer_id):
        """ Returns list of all of the shop cart items"""
        if request.args.get('price') == None:
            app.logger.info('Request to list all items in shopcart with customer_id: %s', customer_id)
            items = []
            items = Shopcart.find_by_customer_id(customer_id)
            results = [item.serialize() for item in items]
            #if results is None or len(results) == 0:
            #    api.abort(404, "No items for this customer.")
            return results, status.HTTP_200_OK

        else:
            target_price = request.args.get('price')
            print(target_price)
            app.logger.info('Request to query all items in shopcart with customer_id: %s', customer_id)
            items = []
            items = Shopcart.query_by_target_price(customer_id, target_price)
            results = [item.serialize() for item in items]
            print(results)
            #if results is None or len(results) == 0:
            #    api.abort(404, "No items for this customer.")
            return results, status.HTTP_200_OK

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
