from sqlalchemy.orm import Session
from .models import User


class UserRepository:
    def create_user(self, db: Session, username: str, email: str, password: str):
        user = User(username=username, email=email, password=password, is_active=True)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    def read_users(self, db: Session):
        return db.query(User).all()

    def read_users_id(self, db: Session, user_id: int):
        return db.get(User, user_id)

    def delete_user(self, db: Session, user_id: int):
        user = self.read_users_id(db, user_id)
        if user:
            db.delete(user)
            db.commit()
        return user
