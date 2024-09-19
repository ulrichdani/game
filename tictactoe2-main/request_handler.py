import requests

HOST = "164.92.255.66"
PORT = 8000
IP = f"{HOST}:{PORT}"

preset_token = None

def login(username, password):
    response = requests.post(f"http://{IP}/login/", json={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["token"]
    return None

def register(username, password):
    response = requests.post(f"http://{IP}/register/", json={"username": username, "password": password})
    if response.status_code == 201:
        return True
    return False

def get_stats(token = preset_token):
    if token is None:
        token = preset_token
    response = requests.post(f"http://{IP}/stats/", json={"token": token})
    if response.status_code == 200:
        return response.json()
    return None

def get_username(token = preset_token):
    if token is None:
        token = preset_token
    response = requests.post(f"http://{IP}/username/", json={"token": token})
    if response.status_code == 200:
        return response.json()["username"]
    return None

def win_game(token = preset_token):
    if token is None:
        token = preset_token
    response = requests.post(f"http://{IP}/game/win", json={"token": token})
    if response.status_code == 200:
        return True
    return False

def lose_game(token = preset_token):
    if token is None:
        token = preset_token
    response = requests.post(f"http://{IP}/game/lose", json={"token": token})
    if response.status_code == 200:
        return True
    return False
