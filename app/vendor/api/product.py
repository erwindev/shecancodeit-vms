import sys
from datetime import datetime
from flask import jsonify, request
from flask_restplus import Api, Resource, Namespace, fields
from app.vendor.dao.product import ProductDao
from app.vendor.models.product import Product as ProductModel
from app.vendor.util.decorator import token_required


class ProductDto:
    api = Namespace('product', description='product related operations')
    product = api.model('product', {
        'id': fields.String(),
        'vendor_id': fields.String(),
        'product_name': fields.String(required=True),
        'department': fields.String(required=True),
        'budget_owner': fields.String(required=True),
        'expiration_date': fields.String(required=True),
        'payment_method': fields.String(required=True),
        'product_type': fields.String(required=True),
        'status': fields.String(),
        'create_date': fields.DateTime(),
        'updated_date': fields.DateTime(),
        'user_by': fields.String(required=True)        
    })      


api = ProductDto.api

@api.route("/vendor/<vendor_id>")
@api.param('vendor_id', 'The Vendor identifier')
@api.expect(api.parser().add_argument('Authorization', location='headers'))
class ProductList(Resource):

    @api.doc('list_of_product')
    @api.marshal_list_with(ProductDto.product, envelope='productlist')
    @token_required
    def get(self, vendor_id):
        """ Get all products """
        try:
            productlist = ProductDao.get_all_by_vendor(vendor_id)
            product_ret_list = []
            for product in productlist:
                product_ret_list.append(product.to_json())
            return product_ret_list
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Internal Server Error'
            }, 500


    @api.response(201, 'Product successfully created.')
    @api.doc('create a new product')
    @api.expect(ProductDto.product, validate=True)
    @token_required
    def post(self, vendor_id):
        """Insert a product"""
        try:
            product_data = request.json

            new_product = ProductModel()
            new_product.vendor_id = vendor_id
            new_product.product_name = product_data['product_name']
            new_product.department = product_data['department']
            new_product.budget_owner = product_data['budget_owner']
            new_product.product_owner = product_data['product_owner']
            new_product.expiration_date = datetime.strptime(product_data['expiration_date'],"%Y-%m-%d").date()
            new_product.payment_method = product_data['payment_method']
            new_product.product_type = product_data['product_type']
            new_product.status = product_data['status']
            new_product.user_by = product_data['user_by']
            new_product = ProductDao.save_product(new_product)
            response_object = {
                'status': 'success',
                'message': 'Product successfully added.'
            }
            return response_object, 201
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Internal Server Error'
            }, 500

    @api.response(201, 'Product successfully updated.')
    @api.doc('update a new product')
    @api.expect(ProductDto.product, validate=False)
    @token_required
    def put(self, vendor_id):
        """Update a product"""
        try:
            product_data = request.json

            existing_product = ProductModel()
            existing_product.id = product_data['id']
            existing_product.vendor_id = vendor_id
            if 'product_name' in product_data:
                existing_product.product_name = product_data['product_name']
            
            if 'department' in product_data:
                existing_product.department = product_data['department']

            if 'budget_owner' in product_data:
                existing_product.budget_owner = product_data['budget_owner']

            if 'product_owner' in product_data:
                existing_product.product_owner = product_data['product_owner']
            
            if 'expiration_date' in product_data:
                new_product.expiration_date = datetime.strptime(product_data['expiration_date'],"%Y-%m-%d").date()

            if 'payment_method' in product_data:
                existing_product.payment_method = product_data['payment_method']
            
            if 'product_type' in product_data:
                existing_product.product_type = product_data['product_type']

            if 'status' in product_data:
                existing_product.status = product_data['status']     

            if 'user_by' in product_data:
                existing_product.user_by = product_data['user_by']                             

            existing_product = ProductDao.update_product(existing_product)
            response_object = {
                'status': 'success',
                'message': 'Product successfully updated.'
            }
            return response_object, 201
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Internal Server Error'
            }, 500



@api.route('/<product_id>')
@api.param('product_id', 'The Product identifier')
@api.response(404, 'Product not found.')
@api.expect(api.parser().add_argument('Authorization', location='headers'))
class Product(Resource):

    @api.doc('get a product')
    @api.marshal_with(ProductDto.product)
    @token_required
    def get(self, product_id):
        """Get a product given its identifier"""
        product = ProductDao.get_by_id(product_id)
        if not product:
            response_object = {
                'status': 'fail',
                'message': 'Product not found.'
            }
            return response_object, 404
        else:
            return product


@api.errorhandler(Exception)
def generic_exception_handler(e: Exception):
    exc_type, exc_value, exc_traceback = sys.exc_info()

    if exc_traceback:
        traceback_details = {
            'filename': exc_traceback.tb_frame.f_code.co_filename,
            'lineno': exc_traceback.tb_lineno,
            'name': exc_traceback.tb_frame.f_code.co_name,
            'message': str(exc_value),
        }
        return {
            'status': 'error',
            'message': traceback_details['message']
        }, 500
    else:
        return {
            'status': 'error',
            'message': 'Internal Server Error'
        }, 500    
