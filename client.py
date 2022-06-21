import requests


URL = 'http://127.0.0.1:5000'
# TOKEN = {'token': '47e970f9-b36e-4c06-b1ba-51054987fe26'}  # user1
TOKEN = {'token': '9d776ed5-c9b1-423f-b92b-3c30f6e52823'}  # user2


'''/user'''
# response = requests.post(
#     f'{URL}/user',
#     json={
#         'user_name': 'user2',
#         'password': 'KFSGn23',
#         'email': 'user2@test.ru'
#     }
# )
#

# response = requests.get(
#     url=f'{URL}/user/1',
#     headers=TOKEN
# )


'''/advertisement'''
# response = requests.post(
#     url=f'{URL}/advertisement',
#     json={
#         'title': 'TEST 2',
#         'description': 'Hello, from user_2',
#     },
#     headers=TOKEN
# )

# response = requests.patch(
#     url=f'{URL}/advertisement/7',
#     json={
#         'title': 'Update'
#     },
#     headers=TOKEN
# )

# response = requests.get(
#     url=f'{URL}/advertisement',
#     headers=TOKEN
# )

response = requests.delete(
    url=f'{URL}/advertisement/7',
    headers=TOKEN
)

print(response.status_code)
print(response.json())