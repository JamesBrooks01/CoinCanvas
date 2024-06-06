from models import db, User


def get_data(user):
    data = db.session.execute(db.select(User).filter_by(user_email=user)).scalar_one_or_none()
    return data

def get_all_users():
    data = db.session.execute(db.select(User)).all()
    return data

def create_user(user):
    formatted_query = []
    new_user = User(user_email=user, user_queries=formatted_query)
    db.session.add(new_user)
    db.session.commit() 

def delete_user(user):
    result = User.query.filter_by(user_email=user).first()
    db.session.delete(result)
    db.session.commit()

def update_user(user,query):
    db.session.execute(db.update(User).where(User.user_email==user).values(user_queries=query))
    db.session.commit()