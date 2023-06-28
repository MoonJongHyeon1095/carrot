from faker import Faker
import requests
from datetime import datetime

def create_fake_item():
    fake = Faker()

    # Generate fake insertAt value as millisecond timestamp
    current_time = datetime.now()
    timestamp = int(current_time.timestamp() * 1000)
    insertAt = timestamp

    # Generate fake data
    title = fake.word()
    price = fake.random_int(min=10, max=100)
    description = fake.text()
    place = fake.city()


    # Upload a sample image (replace 'image.jpg' with the actual image file)
    files = {'image': open('sample.png', 'rb')}


    # Create a dictionary payload
    payload = {
        'title': title,
        'price': price,
        'description': description,
        'place': place,
        'insertAt': insertAt
    }



    # Send POST request to the API
    response = requests.post('http://127.0.0.1:8000/items', data=payload, files=files)

    # Check the response
    if response.status_code == 200:
        print('Fake item created successfully.')
    else:
        print('Failed to create fake item.')

# Call the create_fake_item function 1000 times
for _ in range(10):
    create_fake_item()