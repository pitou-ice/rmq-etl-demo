import pika
import json
import pandas as pd
from io import StringIO


column_mappings = json.load(open('column-mappings.json'))


def ingest_data(ch, method, properties, body):
    data = json.loads(body)
    df = pd.read_json(StringIO(data))
    
    df = df.rename(columns=column_mappings)
    print("[x] Renamed columns")

    df = df[['location','latitude','longitude','temperature']]
    print("[x] Trimmed columns")

    print(f"[x] Received df({len(df)} rows)\n{df.sample(5)}")
    print(f"[X] Done")

    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == '__main__':
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='weather-q')
        
        channel.basic_qos(prefetch_count=1) # don't dispatch new data to worker until it has processed and ack the previous one
        channel.basic_consume(queue='weather-q', on_message_callback=ingest_data)

        print('[*] Waiting for data. Press CTRL+C to exit')
        channel.start_consuming()
    
    except KeyboardInterrupt:
        print('Interrupted')
        exit(0)