from fastapi import FastAPI, UploadFile, Form, Response
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.staticfiles import StaticFiles
from typing import Annotated
import sqlite3

# 기본적으로 check_same_thread는 True며, 만들고 있는 스레드 만 이 연결을 사용할 수 있습니다. 
# False로 설정하면 반환된 연결을 여러 스레드에서 공유할 수 있습니다. 
# 여러 스레드에서 같은 연결을 사용할 때, 데이터 손상을 피하려면 쓰기 연산을 사용자가 직렬화해야 합니다.
conn = sqlite3.connect('db.db', check_same_thread=False)
cur = conn.cursor()

app = FastAPI()

@app.post('/items')
async def create_items(
    image: UploadFile,
    title: Annotated[str, Form()],
    price: Annotated[int, Form()],
    description: Annotated[str, Form()],
    place: Annotated[str, Form()],
    insertAt: Annotated[int,Form()]
):
    image_bytes = await image.read()
    cur.execute(f"""
                INSERT INTO items(title,image,price,description,place,insertAt)
                VALUES ('{title}','{image_bytes.hex()}',{price},'{description}','{place}',{insertAt})
                """)
    conn.commit()
    return '200'

@app.get('/items')
async def get_items():
    # 칼럼명 같이 가져오기
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    rows = cur.execute(f"""
                       SELECT * from items;
                       """).fetchall()
    
    return JSONResponse(
        jsonable_encoder(dict(row) for row in rows)
        )

@app.get('/images/{item_id}')
async def get_image(item_id):
    cur = conn.cursor()
    image_bytes = cur.execute(f"""
                              SELECT image from items WHERE id={item_id}
                              """).fetchone()[0] #튜플에서 불필요한 메타데이터 버리기
    return Response(content=bytes.fromhex(image_bytes))

app.mount("/", StaticFiles(directory="front", html=True), name="front")