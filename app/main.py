from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from app import models, schemas
from app.auth import create_access_token, authenticate_user, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY
from app.database import engine, session_local

models.base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
    allow_credentials=True,
)

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='login')


def get_db():
    try:
        db = session_local()
        yield db
    finally:
        db.close()


def get_current_user(token: str = Depends(oauth2_scheme),
                     db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Could not validate credentials',
        headers={'WWW-Authenticate': 'Bearer'},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')

        if username is None:
            raise credentials_exception

        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = db.query(models.User).filter(models.User.login == token_data.username).first()

    if user is None:
        raise credentials_exception

    return schemas.User(login=user.login, password=user.password, bots=str(user.bots))


@app.get('/')
def index():
    return 'Welcome!'


@app.post('/login', response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(),
          db: Session = Depends(get_db)):
    user = authenticate_user(pwd_context, db, form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={'sub': user.login}, expires_delta=access_token_expires
    )

    return {'access_token': access_token, 'token_type': 'bearer'}


@app.get('/bots/', response_model=list[schemas.Bot])
def get_bots(db: Session = Depends(get_db),
             current_user: schemas.User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication required',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    return db.query(models.Bot).filter(models.Bot.owner_login == current_user.login).all()


@app.get('/bots/{bot_id}/', response_model=schemas.Bot)
def get_bot_by_id(bot_id: str,
                  db: Session = Depends(get_db)):
    bot = db.query(models.Bot).filter(models.Bot.bot_id == bot_id).first()

    if bot is None:
        raise HTTPException(status_code=404, detail=f'Bot with id {bot_id} not found')

    return bot


@app.post('/bots/', response_model=schemas.Bot)
def add_bot(bot: schemas.Bot,
            db: Session = Depends(get_db),
            current_user: schemas.User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication required',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    # check if bot with such id already exists
    b = db.query(models.Bot).filter(models.Bot.bot_id == bot.bot_id).first()

    if b is None:
        raise HTTPException(status_code=400, detail=f'Bot with id {bot.bot_id} already exists')

    new_bot = models.Bot(bot_id=bot.bot_id,
                         token=bot.token,
                         state=bot.state,
                         config=bot.config,
                         owner_login=current_user.login)
    db.add(new_bot)
    db.commit()
    db.refresh(new_bot)

    return new_bot


@app.delete('/bots/{bot_id}/', response_model=schemas.Bot)
def delete_bot(bot_id: str,
               db: Session = Depends(get_db),
               current_user: schemas.User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Authentication required',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    bot = db.query(models.Bot).filter(models.Bot.bot_id == bot_id).first()

    if bot is None:
        raise HTTPException(status_code=404, detail=f'Bot with id {bot_id} not found')

    db.delete(bot)
    db.commit()

    return bot


@app.get('/me/', response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user
