import os, time
from flask import Flask, request, redirect, render_template
from flask_cors import CORS, cross_origin
import shutil

import sqlite3

import json
import jsonschema
import uuid
import pika
import sys
import traceback
import warnings

from InowasFlopyAdapter.InowasFlopyCalculationAdapter import InowasFlopyCalculationAdapter

UPLOAD_FOLDER = './uploads'
MODFLOW_FOLDER = './modflow'

app = Flask ( __name__ )
CORS ( app )


# warnings.filterwarnings("ignore")

def valid_json_file(file):
    with open ( file ) as filedata:
        try:
            data = json.loads ( filedata.read () )
        except ValueError:
            return False
        return True


def read_json(file):
    with open ( file ) as filedata:
        data = json.loads ( filedata.read () )
    return data


def file_extension(filename):
    if '.' in filename:
        return '_' + filename.rsplit ( '.', 1 )[ 1 ]


@app.route ( '/', methods=[ 'GET', 'POST' ] )
@cross_origin ()
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect ( request.url )
        uploaded_file = request.files[ 'file' ]

        if uploaded_file.filename == '':
            return 'No selected file'

        temp_filename = str ( uuid.uuid4 () ) + '.' + file_extension ( uploaded_file.filename )
        temp_file = os.path.join ( app.config[ 'UPLOAD_FOLDER' ], temp_filename )
        uploaded_file.save ( temp_file )

        if not valid_json_file ( temp_file ):
            os.remove ( temp_file )
            return 'File is not a valid JSON-File'
        ##schemavalidation

        content = read_json ( temp_file )
        calculation_id = content.get ( "calculation_id" )

        target_directory = os.path.join ( app.config[ 'MODFLOW_FOLDER' ], calculation_id )
        modflow_file = os.path.join ( target_directory, 'configuration.json' )
        if os.path.exists ( modflow_file ):
            return 'calculation_id (' + calculation_id + ')is already existing'

        os.makedirs ( target_directory )
        os.rename ( temp_file, modflow_file )
        # file.save(os.path.join(target_directory, 'configuration.json'),filename)

        return json.dumps ( {
            'status': 200,
            'calculation id': calculation_id,
            'get_metadata': '/' + calculation_id
        } )

    return render_template ( 'upload.html' )


@app.route ( '/<calculation_id>' )
@cross_origin ()
def configuration(calculation_id):
    modflow_file = os.path.join ( app.config[ 'MODFLOW_FOLDER' ], calculation_id, 'configuration.json' )
    if not os.path.exists ( modflow_file ):
        return 'The file does not exist'
    with open ( modflow_file, 'r' ) as f:
        return f.read ()


if __name__ == '__main__':
    if not os.path.exists ( UPLOAD_FOLDER ):
        os.makedirs ( UPLOAD_FOLDER )

    app.secret_key = '2349978342978342907889709154089438989043049835890'
    app.config[ 'SESSION_TYPE' ] = 'filesystem'
    app.config[ 'UPLOAD_FOLDER' ] = UPLOAD_FOLDER
    app.config[ 'MODFLOW_FOLDER' ] = MODFLOW_FOLDER
    app.debug = True

    app.run ( debug=True )
