import pika


def watch_log_file(log_file_name, connector_name, rabbit_uri, rabbit_queue_name):
    try:
        with open(log_file_name, "rw", encoding="utf-8") as log:
            last_log_size = len(log.readlines())

        while True:
            messages = []

            with open(log_file_name, "rw", encoding="utf-8") as log:
                new_log_size = len(log.readlines())
                if new_log_size >= last_log_size: log.seek(last_log_size)
                if new_log_size < last_log_size: last_log_size = 0

                new_log_lines = log.read()
                if new_log_lines:
                    last_log_size = new_log_size
                    if len(new_log_lines):
                        messages.extend(new_log_lines.split("\n"))
                        messages = [message for message in messages if message]

                if len(messages) > 0:
                    connection = pika.BlockingConnection(
                        pika.ConnectionParameters(host=rabbit_uri))
                    channel = connection.channel()

                    channel.queue_declare(queue=rabbit_queue_name)

                    for message in messages:
                        body = connector_name + ":" + message
                        channel.basic_publish(exchange="", routing_key=rabbit_queue_name, body=body)
    except Exception as e:
        print(e)
        exit(-1)


def main():
    connector_name = "LogConnector"
    log_file_name = r"juice-shop/log" # Find out !!!
    rabbit_uri = "amqp://rmuser:rmpass@localhost"
    rabbit_queue_name = "SIEMLite_LogConnectorQueue"

    watch_log_file(log_file_name, connector_name, rabbit_uri, rabbit_queue_name)


if __name__ == "__main__":
    main()
