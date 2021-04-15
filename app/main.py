from fastapi import FastAPI

from app.models.bot import Bot

app = FastAPI()

db = []


@app.get('/')
async def index():
    return {'message': 'hello, world!'}


@app.get('/bots')
async def get_bots():
    return db


@app.post('/bots')
async def add_bot(bot: Bot):
    db.append(bot.dict())

    return db[-1]


@app.post('/bots/{bot_id}')
async def get_bot(bot_id: str):
    return {}


@app.delete('/bots/{bot_id}')
async def delete_bot(bot_id: str):
    return {}
