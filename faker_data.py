from models import User,Post,Like,Comment,Friend,db
from faker import Faker
import random

fake = Faker()

def generate_users():
    for n in range(10): 
        user = Users(username = fake.user_name(),full_name = fake.name(),email = fake.email(),
            password = fake.password(),created = fake.date_time())
        db.session.add(user)
    db.session.commit()