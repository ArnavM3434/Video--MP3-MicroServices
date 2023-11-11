import pika, json, tempfile, os
from bson.objectid import ObjectId
import moviepy.editor #to convert videos to mp3

def start(message, fs_videos, fs_mp3s, channel):
    message = json.loads(message) #turns it into python object (dictionary)

    #create temporary file that is empty, which we will then write video contents to
    tf = tempfile.NamedTemporaryFile() #will make temp file in temp directory
    #video contents
    out = fs_videos.get(ObjectId(message["video_fid"]))  #objectID converts string to ID object
    #add video contents to empty file
    tf.write(out.read())
    # create audio from temp video file
    audio = moviepy.editor.VideoFileClip(tf.name).audio #tf.name resolves to path of temporary file
    tf.close() #now temp file will automatically deleted

    #write audio to a file
    tf_path = tempfile.gettempdir() + f"/{message['video_fid']}.mp3" #directory where temp files are getting stored + name of file
    audio.write_audiofile(tf_path) #now writing audio to the file

    #save file to mongo
    f = open(tf_path, "rb") #just want to read it
    data = f.read()
    fid = fs_mp3s.put(data)
    f.close()
    os.remove(tf_path) #need to delete this ourselves since tempfile did not make it, the write_audiofile module did

    message["mp3_fid"] = str(fid)

    try:
        channel.basic_publish(
            exchange="",
            routing_key=os.environ.get("MP3_QUEUE"),  #this will be be the name of the mp3 queue
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
            ),

        )
    except Exception as err:
        fs_mp3s.delete(fid)
        return "failed to publish message" 


    


