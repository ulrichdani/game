import sqlite3
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from starlette.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
import bcrypt
import jwt

connections = []
app = FastAPI()

SECRET_KEY = "UWU UNGA BUNGA. I AM OOMPTY DOOMPTY. I WILL FEAST ON YOUR LEFT CLAVICLE AND RIGHT TOENAILS. *starts blushing, furiously masturbating, then cums all over keyboard.* EW! I GOT MY CUMMY MUMMY JUICE ALL OVER THE TYPEWRITE! BETTER GET MOMMY TO COME LICK IT UP! BRB!"

class User(BaseModel):
    username: str
    password: str

class UserToken(BaseModel):
    token: str

db = sqlite3.connect('users.db', check_same_thread=False)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    if len(connections) == 0:
        connections.append(websocket)
        await websocket.send_text("1")
    else:
        connections.append(websocket)
        await websocket.send_text("2")
        await connections[0].send_text("2")
    
    try:
        token = await websocket.receive_text()
        user = get_user_from_token(token)
        if user == None or not get_user(user['username']):
            await websocket.send_text("INVALID AUTH!")
            del connections[connections.index(websocket)]
            await websocket.close()
            return
        else:
            await websocket.send_text("WELCOME {}!".format(user['username']))
        while True:
            data = await websocket.receive_text()
            if len(connections) == 2:
                await connections[0].send_text(data)
                await connections[1].send_text(data)
            print(data)
    except WebSocketDisconnect:
        del connections[connections.index(websocket)]
        for websocket in connections:
            await websocket.send_text("disconnected")

@app.post("/login/")
def login(data: User): 
    username = data.username
    password = data.password.encode('utf-8')
    cursor = db.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))

    user = cursor.fetchone()
    if user is None:
        return JSONResponse(content={"error": "user not found"}, status_code=404)

    hashed_password = user[0]
    if bcrypt.checkpw(password, hashed_password):
        # Generate user token
        token = jwt.encode({"username": username}, SECRET_KEY, algorithm="HS256")
        return JSONResponse(content={"token": token}, status_code=200)
    else:
        return JSONResponse(content={"error": "invalid password"}, status_code=401)

@app.post("/register/")
def register(data: User):
    username = data.username
    password = data.password.encode('utf-8')
    
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    if user is not None:
        return JSONResponse(content={"error": "user already exists"}, status_code=422)
    
    create_user(username, password)
    return JSONResponse(content={"message": "user created"}, status_code=201)

@app.post("/stats/")
def stats(data: UserToken):
    username = get_user_from_token(data.token)['username']
    cursor = db.cursor()
    cursor.execute("SELECT elo, wins, losses, ties, games FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    cursor.close()
    return JSONResponse(content={"elo": user[0], "wins": user[1], "losses": user[2], "ties": user[3], "games": user[4]}, status_code=200)

@app.post("/username/")
def username(data: UserToken):
    print(data)
    username = get_user_from_token(data.token)['username']
    if get_user(username) is None:
        return JSONResponse(content={"error": "user not found"}, status_code=404)
    return JSONResponse(content={"username": username}, status_code=200)

def win_game(username):
    cursor = db.cursor()
    cursor.execute("SELECT elo, wins, losses, ties, games FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    elo = user[0]
    wins = user[1]
    games = user[4]
    elo += 10
    wins += 1
    games += 1
    cursor.execute("UPDATE users SET elo = ?, wins = ?, games = ? WHERE username = ?", (elo, wins, games, username))
    db.commit()
    cursor.close()

def lose_game(username):
    cursor = db.cursor()
    cursor.execute("SELECT elo, losses, games FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    elo = user[0]
    losses = user[1]
    games = user[2]
    elo -= 10
    losses += 1
    games += 1
    cursor.execute("UPDATE users SET elo = ?, losses = ?, games = ? WHERE username = ?", (elo, losses, games, username))
    db.commit()
    cursor.close()

@app.post("/game/win")
def game(data: UserToken):
    username = get_user_from_token(data.token)['username']
    win_game(username)
    return JSONResponse(content={"message": "game won"}, status_code=200)

@app.post("/game/lose")
def game(data: UserToken):
    username = get_user_from_token(data.token)['username']
    lose_game(username)
    return JSONResponse(content={"message": "game lost"}, status_code=200)

def create_user(username, password):
    hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())
    cursor = db.cursor()
    cursor.execute("INSERT INTO users (username, password, elo, wins, losses, ties, games) VALUES (?, ?, 1000, 0, 0, 0, 0)", (username, hashed_password))
    db.commit()
    cursor.close()

def init_database():
    cursor = db.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT, elo UNSIGNED BIG INT, wins UNSIGNED BIG INT, losses UNSIGNED BIG INT, ties UNSIGNED BIG INT, games UNSIGNED BIG INT, PRIMARY KEY (username))''')
    db.commit()
    cursor.close()

def get_user_from_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return None
    
def get_user(username):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    cursor.close()
    return user

if __name__ == "__main__":
    init_database()
    uvicorn.run("main:app", host="0.0.0.0", port=8000, workers=1)

