import os, requests #this requests is module we use to make http calls to auth service

def login(request): #different from requests
    auth = request.authorization
    if not auth: #no authorization parameters in request
        return None, ("missing credentials", 401)   #do not return token
    
    basicAuth = (auth.username, auth.password)

    response = requests.post(
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/login",  #address for auth service
        auth=basicAuth
    )   #hitting out API auth service

    if response.status_code == 200:
        return response.text, None #response.txt is the JWT token
    else:
        return None, (response.text, response.status_code)


