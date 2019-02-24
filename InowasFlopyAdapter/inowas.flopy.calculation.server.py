#!/usr/bin/env python

import json
import os
import pika
import sys
import traceback
import warnings

from InowasFlopyAdapter.InowasFlopyCalculationAdapter import InowasFlopyCalculationAdapter

warnings.filterwarnings("ignore")


def get_config_parameter(name):
    if os.environ[name]:
        return os.environ[name]

    raise Exception('Parameter with name ' + name + ' not found in environment-variables.')


def process(content):
    author = content.get("author")
    project = content.get("project")
    calculation_id = content.get("calculation_id")
    model_id = content.get("model_id")
    m_type = content.get("type")
    version = content.get("version")
    data = content.get("data")

    print('Summary:')
    print('Author: %s' % author)
    print('Project: %s' % project)
    print('Model Id: %s' % model_id)
    print('Calculation Id: %s' % calculation_id)
    print('Type: %s' % m_type)
    print('Version: %s' % version)

    if m_type == 'flopy_calculation':

        print("Running flopy calculation for model-id '{0}' with calculation-id '{1}'".format(model_id, calculation_id))
        target_directory = os.path.join(datafolder, calculation_id)
        print('The target directory is %s' % target_directory)

        print('Write config to %s' % os.path.join(target_directory, 'configuration.json'))
        if not os.path.exists(target_directory):
            os.makedirs(target_directory)

        with open(os.path.join(target_directory, 'configuration.json'), 'w') as outfile:
            json.dump(content, outfile)

        data['mf']['mf']['modelname'] = 'mf'
        data['mf']['mf']['model_ws'] = target_directory

        if 'mt' in data:
            data['mt']['mt']['modelname'] = 'mt'
            data['mt']['mt']['model_ws'] = target_directory

        try:
            flopy = InowasFlopyCalculationAdapter(version, data, calculation_id)
            response = {}
            response['status_code'] = "200"
            response['model_id'] = model_id
            response['calculation_id'] = calculation_id
            response['data'] = flopy.response()
            response['message'] = flopy.response_message()
            response = str(response).replace('\'', '"')
            return response
        except:
            response = {}
            response['status_code'] = "500"
            response['model_id'] = model_id
            response['calculation_id'] = calculation_id
            response['message'] = traceback.format_exc(limit=1)
            response = json.dumps(response)
            return response

    return dict(
        status_code=500,
        model_id=model_id,
        calculation_id=calculation_id,
        message="Internal Server Error. Request data does not fit. \"m_type\" should have the content "
                "\"flopy_calculation\" "
    )


def on_request(ch, method, props, body):
    content = json.loads(body.decode("utf-8"))
    ch.basic_ack(delivery_tag=method.delivery_tag)
    response = process(content)

    write_channel.basic_publish(
        exchange='',
        routing_key='flopy_calculation_finished_queue',
        body=response,
        properties=pika.BasicProperties(
            delivery_mode=2  # make message persistent
        ))


print(os.environ)

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=get_config_parameter('RABBITMQ_HOST'),
        port=int(get_config_parameter('RABBITMQ_PORT')),
        virtual_host=get_config_parameter('RABBITMQ_VIRTUAL_HOST'),
        credentials=pika.PlainCredentials(
            get_config_parameter('RABBITMQ_USER'),
            get_config_parameter('RABBITMQ_PASSWORD')
        ),
        heartbeat_interval=0
    ))

read_channel = connection.channel()
read_channel.queue_declare(queue=get_config_parameter('CALCULATION_QUEUE'), durable=True)

write_channel = connection.channel()
write_channel.queue_declare(queue=get_config_parameter('CALCULATION_FINISHED_QUEUE'), durable=True)

datafolder = os.path.realpath(sys.argv[1])

scriptfolder = os.path.dirname(os.path.realpath(__file__))
binfolder = os.path.join(scriptfolder, 'bin')

read_channel.basic_qos(prefetch_count=1)
read_channel.basic_consume(on_request, queue=get_config_parameter('CALCULATION_QUEUE'))

print(" [x] Awaiting RPC requests")
read_channel.start_consuming()
