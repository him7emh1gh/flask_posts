from flask_posts.models import UserModel

def test_new_user():
  user = UserModel("qwa@mail.ru", "password")
  assert user.email == "qwa@mail.ru"
  assert user.token != "password"
