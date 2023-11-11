import pika, json

def upload(f, fs, channel, access):  #first upload file to mongo db database using gridfs, then put message in rabbitMQ queue
    try:
        fid = fs.put(f)  #if successful, file ID object is returned
    except Exception as err:
        print(err)
        return "internal server error", 500

    message = {
        "video_fid" : str(fid),
        "mp3_fid" : None,   #will downstream be set to mp3's file ID in db
        "username" : access["username"],  #whose video it is



    }

    try:  #put message on queue
        channel.basic_publish(
            exchange = "",   #use empty exchange
            routing_key = "video",   #name of queue
            body = json.dumps(message),  #body of message, now body is JSON formatted string
            properties = pika.BasicProperties(
                delivery_mode = pika.spec.PERSISTENT_DELIVERY_MODE #in Kubernetes cluster, pod for RabbitMQ is stateful pod, if it fails want messages to still be there until removed from queue

            ),



        
        )
    except:
        fs.delete(fid)  #if no message for file on queue, file will never be processed
        print("could not put message on queue")
        return "Internal server error", 500

    




    



