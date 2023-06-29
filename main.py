from fastapi import FastAPI, UploadFile, Form, Response, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from fastapi_login import LoginManager
from fastapi_login.exceptions import InvalidCredentialsException
from typing import Annotated
import sqlite3
import asyncio

# 기본적으로 check_same_thread는 True며, 만들고 있는 스레드 만 이 연결을 사용할 수 있습니다. 
# False로 설정하면 반환된 연결을 여러 스레드에서 공유할 수 있습니다. 
# 여러 스레드에서 같은 연결을 사용할 때, 데이터 손상을 피하려면 쓰기 연산을 사용자가 직렬화해야 합니다.
conn = sqlite3.connect('db.db', check_same_thread=False)
cur = conn.cursor()

cur.execute(f"""
            CREATE TABLE IF NOT EXISTS items (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                image BLOB,
                price INTEGER NOT NULL,
                description TEXT,
                place TEXT NOT NULL,
                insertAT INTEGER NOT NULL
            )
            """)

cur.execute(f"""
            CREATE TABLE IF NOT EXISTS users (
	          id TEXT PRIMARY KEY,
	          name TEXT NOT NULL,
	          email TEXT NOT NULL,
	          password TEXT NOT NULL
            )
            """)

app = FastAPI()

SECRET = "test"
manager = LoginManager(SECRET, '/login.html')

# ??????????? 
@manager.user_loader()
def query_user(id_datum):
    #id가 문자열로 들어올 경우와 그렇지 않을 경우
    WHERE_STATEMENTS = f'id="{id_datum}"'
    if type(id_datum) == dict:
        WHERE_STATEMENTS = f'id="{id_datum["id"]}"'
    
    # 칼럼명 같이 가져오기
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    user = cur.execute(f"""
                       SELECT * from users WHERE {WHERE_STATEMENTS}
                       """).fetchone()

    return user

@app.post('/login')
def login(id: Annotated[str, Form()],
          password: Annotated[str, Form()]):
    user = query_user(id)
    if not user:
        raise InvalidCredentialsException
    elif password != user['password']:
        raise InvalidCredentialsException
    print(password)
    print( user['password'])
    # 왜 sub라는 이름으로 그 안에 또 객체로 넣어야 하는가? 문서확인 요망
    access_token = manager.create_access_token(data={
        'sub':{
            'id':user['id'],
            'name':user['name'],
            'email':user['email'],
        }
    })
    return {'access_token':access_token}
    

@app.post('/signup')
def signup(id: Annotated[str, Form()],
           password: Annotated[str, Form()],
           name: Annotated[str, Form()],
           email: Annotated[str, Form()]):
    cur.execute(f"""
                INSERT INTO users(id,name,email,password)
                VALUES ('{id}','{name}','{email}','{password}')
                """)
    conn.commit()
    return '200'

#Annotated[str, Form()]은 str 유형의 변수에 Form()이라는 메타데이터를 추가하는 것  
#FastAPI 프레임워크는 pydantic을 내부적으로 사용하여 요청 파라미터 유효성 검사와 데이터 변환을 처리  
#Annotated를 통한 메타데이터 추가는 유효성 검사 및 데이터 변환 파이프라인을 구축하는 데 도움을 주는 것으로 볼 수 있습니다. 이를 통해 코드의 안정성과 신뢰성을 높일 수 있습니다.
@app.post('/items')
async def create_items(
    image: UploadFile,
    title: Annotated[str, Form()], 
    price: Annotated[int, Form()],
    description: Annotated[str, Form()],
    place: Annotated[str, Form()],
    insertAt: Annotated[int,Form()]
    # request: Request
):
    async def insert_item():
        image_bytes = await image.read()
        cur.execute(f"""
                INSERT INTO items(title,image,price,description,place,insertAt)
                VALUES ('{title}','{image_bytes.hex()}',{price},'{description}','{place}',{insertAt})
                """)
        conn.commit()
        
        # 병렬로 실행할 비동기 함수들을 gather에 전달하여 실행
    results = await asyncio.gather(insert_item())
    print(results)
    return '200'
    # async def insert_item(request):
    #      # Extract data from request
    #     form_data = await request.form()
        
    #     image_bytes = await form_data['image'].read()
    #     title = form_data['title']
    #     price = int(form_data['price'])
    #     description = form_data['description']
    #     place = form_data['place']
    #     insertAt = int(form_data['insertAt'])
        
    #     cur.execute(f"""
    #         INSERT INTO items(title,image,price,description,place,insertAt)
    #         VALUES ('{title}','{image_bytes.hex()}',{price},'{description}','{place}',{insertAt})
    #     """)
    #     conn.commit()

    # queue = asyncio.Queue()
    # tasks = []

    # # 요청을 큐에 추가
    # while True:
    #     form_data = await request.form()
    #     if not form_data:
    #         break
    #     await queue.put(form_data)

    # # 코루틴을 생성하고 실행
    # for _ in range(10):  # 병렬로 실행할 코루틴 수
    #     task = asyncio.create_task(insert_item(queue.get()))
    #     tasks.append(task)

    
    # # 모든 코루틴의 실행 완료를 기다림
    # await asyncio.gather(*tasks)

    # return '200'
    

@app.get('/items') #page: int = 1기본값으로 1을 가지며, 해당 파라미터가 전달되지 않았을 때 사용되는 값
async def get_items(page: int = 1, user=Depends(manager)):
    print('page:', page)
    conn.execute("BEGIN TRANSACTION")  # 트랜잭션 시작
    # 칼럼명 같이 가져오기
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    # 전체 데이터 수 계산
    total_rows = cur.execute("SELECT COUNT(*) FROM items").fetchone()[0]

    # 페이지당 행 수와 총 페이지 수 계산
    items_per_page = 10
    total_pages = (total_rows / items_per_page) if (total_rows % items_per_page == 0) else (total_rows / items_per_page + 1) #items_per_page
    offset = (page - 1) * items_per_page
    # 유효한 페이지 범위 확인
    if page < 1 or page > total_pages:
        conn.execute("ROLLBACK")  # 트랜잭션 롤백
        return JSONResponse(status_code=400, content={"message": "Invalid page number."})
    
    rows = cur.execute(f"""
                       SELECT * from items ORDER BY insertAt DESC LIMIT ? OFFSET ?;
                       """, (items_per_page, offset)).fetchall()
    
    conn.execute("COMMIT")  # 트랜잭션 커밋
    
    return JSONResponse(
        jsonable_encoder(dict(row) for row in rows)
        )

@app.get('/images/{item_id}')
async def get_image(item_id):
    cur = conn.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image from items WHERE id={item_id}
                              """).fetchone()[0] #튜플에서 불필요한 메타데이터 버리기
    return Response(content=bytes.fromhex(image_bytes), media_type='image/*')

app.mount("/", StaticFiles(directory="front", html=True), name="front")