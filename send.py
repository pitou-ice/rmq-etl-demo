import pika
import json
import pandas as pd

connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='weather-q')

with open('weather-data.csv') as csv_file:
    df = pd.read_csv(csv_file)

    third = len(df)//3 # synthetic chunking for demos sake
    sjson_1 = json.dumps(df[0:third].to_json())
    sjson_2 = json.dumps(df[third:2*third].to_json())
    sjson_3 = json.dumps(df[2*third:].to_json())

    channel.basic_publish(exchange='',routing_key='weather-q',body=sjson_1)
    channel.basic_publish(exchange='',routing_key='weather-q',body=sjson_2)
    channel.basic_publish(exchange='',routing_key='weather-q',body=sjson_3)

print(f"[x] Sent\n{len(df)} rows.")

connection.close()