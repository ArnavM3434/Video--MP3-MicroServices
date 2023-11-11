import jwt, datetime, os
from flask import Flask, request #we'll use Flask to create our server
from flask_mysqldb import MySQL # allows us to query MySQL database

#jwt is json web token

server = Flask(__name__)
mysql = MySQL(server)

#config
server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")
server.config["MYSQL_USER"] = os.environ.get("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_PASSWORD")
server.config["MYSQL_PORT"] = int(os.environ.get("MYSQL_PORT"))
server.config["MYSQL_DB"] = os.environ.get("MYSQL_DB")

#print(server.config["MYSQL_HOST"])

@server.route("/login", methods = ["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "missing credentials", 401
    
    #check db for username and password
    cur = mysql.connection.cursor() #use cursor to execute queries
    res = cur.execute(
        "SELECT email, password FROM user WHERE email=%s", (auth.username,)
    )

    if res > 0: #user exists in database
        user_row = cur.fetchone() #resolves to tuple (from previous query?)
        email = user_row[0]
        password = user_row[1]

        if auth.username != email or auth.password != password:
            return "invalid credentials", 401
        else:
            return createJWT(auth.username, os.environ.get("JWT_SECRET"), True)
        
    else:
        return "invalid credentials", 401
    
@server.route("/validate", methods = ["POST"])
def validate():
    encoded_jwt = request.headers["Authorization"]
    if not encoded_jwt:
        return "missing credentials", 401
    encoded_jwt = encoded_jwt.split(" ")[1]  #Bearer <credentials>
    try:
        decoded = jwt.decode(
            encoded_jwt, os.environ.get("JWT_SECRET"), algorithms = ["HS256"]
        )
    except: #try fails
        return "Not authorized", 403
    
    return decoded, 200

    
def createJWT(username, secret, authz): #authz tells us whether or not user is administrator
    return jwt.encode(
        {
            "username" : username,
            "exp": datetime.datetime.now(tz = datetime.timezone.utc)
            + datetime.timedelta(days = 1),
            "iat": datetime.datetime.utcnow(),   #when it was issued
            "admin" : authz,


        },
        secret,
        algorithm = "HS256"


    )




#configure entrypoint
if __name__ == "__main__":  #when we run file using python command, name variable resolves to main. When we run file using python command want server to run
    server.run(host="0.0.0.0", port=5000)






    

    