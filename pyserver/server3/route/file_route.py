# -*- coding: UTF-8 -*-
"""
Blueprint for file

Author: Zhaofeng Li
Date: 2017.05.22
"""
from copy import deepcopy

from bson import ObjectId
from flask import Blueprint
from flask import jsonify
from flask import make_response
from flask import redirect
from flask import request
from flask import send_from_directory

from server3.repository import config
from server3.service import file_service
from server3.utility import json_utility
from server3.constants import PREDICT_FOLDER

UPLOAD_FOLDER = config.get_file_prop('UPLOAD_FOLDER')

PREFIX = '/file'
UPLOAD_URL = '/uploads/'
REQUEST_FILE_NAME = 'uploaded_file'

file_app = Blueprint("file_app", __name__, url_prefix=PREFIX)


@file_app.route('/files', methods=['POST'])
def upload_file():
    data = dict(request.form.items())
    user_ID = data.pop('user_ID')
    data_set_name = data.pop('data_set_name')
    is_private = data.pop('if_private')
    description = data.pop('description')
    ds_type = data.pop('type')
    names = data.pop('names', None)
    # convert string to bool
    is_private = str(is_private).lower() == 'true'

    if request.method == 'POST':
        # check if the post request has the file part
        if REQUEST_FILE_NAME not in request.files:
            return jsonify({'response': 'no file part'}), 400
        file = request.files[REQUEST_FILE_NAME]
        if file.filename == '':
            return jsonify({'response': 'no selected file'}), 400
        if file and file_service.allowed_file(file.filename):
            url_base = PREFIX + UPLOAD_URL
            saved_file = file_service.add_file(data_set_name, file, url_base,
                                               user_ID, is_private,
                                               description, ds_type,
                                               names=names, **data)
            file_json = json_utility.convert_to_json(saved_file.to_mongo())
            return jsonify({'response': file_json})
        else:
            return jsonify({'response': 'file is not allowed'}), 400


# @file_app.route('/files', methods=['GET'])
# def list_files_by_user_ID():
#     user_ID = request.args.get('user_ID')
#     if not user_ID:
#         jsonify({'response': 'insufficient args'}), 400
#     try:
#         public_files, owned_files = file_service.list_files_by_user_ID(user_ID,
#                                                                        -1)
#         public_files = json_utility.me_obj_list_to_json_list(public_files)
#         owned_files = json_utility.me_obj_list_to_json_list(owned_files)
#         result = {
#             'public_files': public_files,
#             'owned_files': owned_files
#         }
#     except Exception as e:
#         return make_response(jsonify({'response': '%s: %s' % (str(
#             Exception), e.args)}), 400)
#     return make_response(jsonify({'response': result}), 200)


@file_app.route('/files', methods=['GET'])
def list_files_by_user_ID():
    user_ID = request.args.get('user_ID')
    extension = request.args.get('extension')
    predict = request.args.get('predict')
    predict = str(predict).lower() == 'true'
    if not user_ID:
        return jsonify({'response': 'insufficient args'}), 400
    public_files, owned_files = \
        file_service.list_file_by_extension(user_ID,
                                            extension=extension,
                                            predict=predict,
                                            order=-1)
    public_files = json_utility.me_obj_list_to_json_list(public_files)
    owned_files = json_utility.me_obj_list_to_json_list(owned_files)
    result = {
        'public_files': public_files,
        'owned_files': owned_files
    }
    return jsonify({'response': result})


@file_app.route('/files/<string:file_id>', methods=['DELETE'])
def remove_file_by_id(file_id):
    try:
        result = file_service.remove_file_by_id(ObjectId(file_id))
    except Exception as e:
        return jsonify({'response': '%s: %s' % (str(Exception), e.args)})
    return jsonify({'response': result})


@file_app.route(UPLOAD_URL + '<user_ID>/<filename>')
def uploaded_file(user_ID, filename):
    predict = request.args.get('predict')
    predict = str(predict).lower() == 'true'
    path = '{}{}/'.format(UPLOAD_FOLDER, user_ID)
    if predict:
        path += PREDICT_FOLDER
    print(path)
    return send_from_directory(path, filename)


@file_app.route('/predict', methods=['POST'])
def upload_predict_image():
    # user_ID = request.form.get('user_ID')
    # if not user_ID:
    #     return jsonify({'response': 'no user_ID'}), 400
    user_ID = request.args.get('user_ID')
    if request.method == 'POST':
        # check if the post request has the file part
        if REQUEST_FILE_NAME not in request.files:
            return jsonify({'response': 'no file part'}), 400
        file = request.files[REQUEST_FILE_NAME]
        if file.filename == '':
            return jsonify({'response': 'no selected file'}), 400
        if file and file_service.allowed_file(file.filename):
            url_base = PREFIX + UPLOAD_URL
            saved_file = file_service.add_file(file.filename, file, url_base,
                                               user_ID, is_private=True,
                                               ds_type='image', predict=True,
                                               **request.form)
            file_json = json_utility.convert_to_json(saved_file.to_mongo())
            return jsonify({'response': file_json})
        else:
            return jsonify({'response': 'file is not allowed'}), 400
