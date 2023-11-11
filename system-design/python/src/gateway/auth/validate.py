import os, requests

def token(request):
    if not "Authorization" in request.headers:
        return None, ("missing credentials", 401)

    token = request.headers["Authorization"]

    if not token:
        return None, ("missing credentials", 401)

    response = requests.post(    #call auth service API's validate endpoint
        f"http://{os.environ.get('AUTH_SVC_ADDRESS')}/validate",
        headers={"Authorization": token},

    


    )

    if response.status_code == 200:
        return response.text, None #response.txt is decoded token with user info and privileges
    else:
        return None, (response.text, response.status_code)

