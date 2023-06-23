from fastapi import FastAPI, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from typing import Annotated

app = FastAPI()

@app.post('/items')
def create_items(
    image: UploadFile,
    title: Annotated[str, Form()],
    price: Annotated[int, Form()],
    description: Annotated[str, Form()],
    place: Annotated[str, Form()],
):
    print(image, title, price, description, place)
    return '200'

app.mount("/", StaticFiles(directory="front", html=True), name="front")