import pika, sys, os, time
from send import email

def main():
   
    #rabbit mq connection

    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host="rabbitmq")
    )

    def callback(ch, method, properties, body):  #ch is channel
        err = email.notification(body)
        if err:
            ch.basic_nack(delivery_tag=method.delivery_tag)  #negative acknowledgement, don't want to take message of queue since wasn't processed properly
        else:
            ch.basic_ack(delivery_tag=method.delivery_tag) #delivery tag is how queue identifies message




    channel = connection.channel()
    channel.basic_consume(
        queue=os.environ.get("MP3_QUEUE"),   #this is "video" queue
        on_message_callback=callback #whenever channel consumes message, call the callback function
    )

    print("Waiting for messages. To exit press CTRL + C")

    channel.start_consuming()

if __name__=="__main__":
    try:
        main()
    except KeyboardInterrupt:  #if someone presses control C stop running main function, exit
        print("Interrupted")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
            
    


