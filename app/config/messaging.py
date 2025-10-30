import asyncio
import json
import os
from typing import Any, Dict, Callable

import pika

RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST")

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host=RABBITMQ_HOST))

channel = connection.channel()

QUEUES_TO_BE_ASSERTED = [
    "world.created",
    "world.updated"
]

queue_map = {}

for each in QUEUES_TO_BE_ASSERTED:
    queue_map[each] = channel.queue_declare(queue=each, durable=True, arguments={'x-queue-type': 'quorum'})


def publish_message(queue_name: str, message: Dict[str, Any]):
    if queue_name not in queue_map:
        raise AssertionError("Queue {} not found".format(queue_name))
    channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(message), properties=pika.BasicProperties(delivery_mode=pika.DeliveryMode.Persistent))


def with_json_deserializer(func: Callable[[Any], Any]):
    return lambda x: func(json.loads(x.decode("utf-8")))


def with_async(func: Callable[[Any], Any]):
    return lambda x: asyncio.run(func(x))


def with_ack(func: Callable[[Any], Any]):
    def ack(channel, method, _properties, body):
        try:
            func(body)
            channel.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            channel.basic_reject(delivery_tag=method.delivery_tag)
            raise e
    return ack


def subscribe_to_queue(queue_name: str, worker: Callable[[Dict[str, Any]], Any]):
    if queue_name not in queue_map:
        raise AssertionError("Queue {} not found".format(queue_name))
    channel.basic_consume(queue=queue_name, on_message_callback=with_ack(with_json_deserializer(with_async(worker))), auto_ack=False)


def start_all_queues():
    channel.start_consuming()
