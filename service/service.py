import os
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound

# SQLAlchemy, a popular ORM that supports a
# variety of backends including SQLite, MySQL, and PostgreSQL
from flask_sqlalchemy import SQLAlchemy
from service.models import Pet, DataValidationError

# Import Flask application
from . import app

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
    return jsonify(name='Shop cart service',
                   version='1.0',
                   paths=url_for('list_pets', _external=True)
                  ), status.HTTP_200_OK

######################################################################
# LIST ALL ITEMS IN ONE SHOP CART ---
######################################################################
@app.route('/shopcart/<int:customer_id>', methods=['GET'])
def list_cart_iterms(customer_id):
    """ Returns list of all of the shop cart items"""
    app.logger.info('Request to list all items in shopcart with customer_id: %s', customer_id)
 	items = []
 	if customer_id:
        items = Shopcart.find_by_category(category)
 	results = [item.serialize() for item in items]
    return make_response(jsonify(results),status.HTTP_200_OK)

######################################################################
# RETRIEVE AN ITEM
######################################################################
@app.route('/shopcart/<int:item_id>', methods=['GET'])
def get_cart_item(item_id):
    """
    Retrieve a single shop cart item
    """
    app.logger.info('Request for shopcart item with id: %s', item_id)
    return make_response(status.HTTP_200_OK)


######################################################################
# ADD A NEW ITEM TO THE SHOP CART
######################################################################
@app.route('/shopcart', methods=['POST'])
def create_cart_item():
    """
    Creates a new item entry for the cart
    """
    app.logger.info('Request to create shopcart item')
    return make_response(status.HTTP_200_OK)



######################################################################
# UPDATE AN EXISTING SHOPCART ITEM
######################################################################
@app.route('/shopcart/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    """
    Update an existing item in the cart
    """
    app.logger.info('Request to update shopcart item with id: %s', item_id)
    return make_response(status.HTTP_200_OK)


######################################################################
# DELETE A SHOPCART ITEM
######################################################################
@app.route('/shopcart/<int:item,_id>', methods=['DELETE'])
def delete_cart_item(item_id):
    """
    Delete an existing entry present in the shopcart
    """
    app.logger.info('Request to delete an existing shopcart item with id: %s', item_id)
    return make_response(status.HTTP_200_OK)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

#def init_db():
    """ Initialies the SQLAlchemy app """
#    global app
#    Shopcart.init_db(app)

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
