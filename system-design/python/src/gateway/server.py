import os, gridfs, pika, json #gridfs will let us store larger files in MongoDB, pika is what we use to interface with RabbitMQ queue
from flask import Flask, request, send_file
from flask_pymongo import PyMongo #we'll use MongoDB to store files
from auth import validate #we'll be making auth package
from auth_svc import access
from storage import util #we'll make storage package
from bson.objectid import ObjectId

server = Flask(__name__)
 #videos is the database, host minikube internal gives access to localhost within Kubernetes cluster, 27017 is port for MongoDB

mongo_video = PyMongo(server,
                      uri = "mongodb://host.minikube.internal:27017/videos"
                      ) #PyMongo wraps flask server, lets us interface with MongoDB

mongo_mp3 = PyMongo(server,
                      uri = "mongodb://host.minikube.internal:27017/mp3s"
                      ) #PyMongo wraps flask server, lets us interface with MongoDB

fs_videos = gridfs.GridFS(mongo_video.db) #mongo_video.db will be the videos database, gridfs will let us use MongoDB's gridfs
fs_mp3s = gridfs.GridFS(mongo_mp3.db) #mongo_mp3.db will be the mp3s database, gridfs will let us use MongoDB's gridfs

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq")) #mkes sonnection with RabbitMQ synchronous, rabbitmq is name of the host we will use in Kubernetes
channel = connection.channel()

@server.route("/login", methods = ["POST"])  #communicates with auth service to log user in and get token
def login():
    token, err = access.login(request)  #we will make module called access that will have login function

    if not err:
        return token
    else:
        return err

@server.route("/upload", methods = ["POST"]) #to upload videos
def upload():
    access, err = validate.token(request) #access is decoded token as JSON string

    if err:
        return err
    access = json.loads(access)  #turn JSON string into python object

    if access["admin"]:  #admin claim resolves to true, will give access
        #want to make sure there is file in first place
        if len(request.files) > 1 or len(request.files) < 1:  #only will allow one file to be uploaded
            return "exactly 1 file required", 400

        for _, f in request.files.items():  #_ is key, f is value (file) in request.files.items() dictionary, this for loop should only happen once
            err = util.upload(f, fs_videos, channel, access)
            if err:
                print(err)

                return err

        return "success!", 200

    else:
        return "Not authorized", 401


@server.route("/download", methods = ["GET"])  #retrieve the converted video
def download():
    access, err = validate.token(request) #access is decoded token as JSON string
    if err:
        return err
    access = json.loads(access)  #turn JSON string into python object

    if access["admin"]:  #admin claim resolves to true, will give access
        fid_string = request.args.get("fid")
        if not fid_string:
            return "fid is required", 400
        try:
            out = fs_mp3s.get(ObjectId(fid_string))
            return send_file(out, download_name=f'{fid_string}.mp3')
        except Exception as err:
            print(err)
            return "Internal server error", 500      
    
    return "Not authorized", 401
    

     


if __name__ == "__main__":
    server.run(host = "0.0.0.0", port = 8080) #port = 8080 in whichever OS this code is running
    












