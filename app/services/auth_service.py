from app.models.user import User


def get_user_from_auth() -> User:
    return User(name="test", _id="user_id")
