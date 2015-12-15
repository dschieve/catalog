from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Category, Item, User, Base

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# for evaluation
# user_id of 1 set for each item, test user will login and be given
# the first user_id, allowing the user to edit or delete files

# Setup Soccer Items
category1 = Category(category_name="Soccer", user_id=1)
session.add(category1)
session.commit()

item1 = Item(item_name="two shinguards", item_description="pair of shinguards",
             category=category1, user_id=1)
session.add(item1)
session.commit()

item2 = Item(item_name="Shinguards", item_description="shinguards",
             category=category1, user_id=1)
session.add(item2)
session.commit()

item3 = Item(item_name="Jersey", item_description="Red and White",
             category=category1, user_id=1)
session.add(item3)
session.commit()

item4 = Item(item_name="Soccer Cleats", item_description="10 Cleats per Shoe",
             category=category1, user_id=1)
session.add(item4)
session.commit()

# Setup Basketball Items
category2 = Category(category_name="Basketball", user_id=1)
session.add(category2)
session.commit()

item5 = Item(item_name="Net", item_description="Regulation Netting",
             category=category2, user_id=1)
session.add(item5)
session.commit()

# Setup Baseball Items
category3 = Category(category_name="Baseball", user_id=1)
session.add(category3)
session.commit()

item6 = Item(item_name="Bat", item_description="White",
             category=category3, user_id=1)
session.add(item6)
session.commit()

# Setup Frisbee Items
category4 = Category(category_name="Frisbee", user_id=1)
session.add(category4)
session.commit()

item7 = Item(item_name="Frisbee",
             item_description="Black with white stripe",
             category=category4, user_id=1)
session.add(item7)
session.commit()

# Setup Snowboarding Items
category5 = Category(category_name="Snowboarding", user_id=1)
session.add(category5)
session.commit()

item8 = Item(item_name="Snowboard",
             item_description="Red with black bindings",
             category=category5, user_id=1)
session.add(item8)
session.commit()

item9 = Item(item_name="Goggles",
             item_description="UV A and B Protection",
             category=category5, user_id=1)
session.add(item9)
session.commit()

# Setup Rock CLimbing Items
category6 = Category(category_name="Rock Climbing", user_id=1)
session.add(category6)
session.commit()

item10 = Item(item_name="Gloves",
              item_description="Red with black bindings",
              category=category6, user_id=1)
session.add(item10)
session.commit()

item11 = Item(item_name="Glasses", item_description="UV A and B Protection",
              category=category6, user_id=1)
session.add(item11)
session.commit()


# Setup Foosball Items
category7 = Category(category_name="Foosball", user_id=1)
session.add(category7)
session.commit()

item12 = Item(item_name="Ball",
              item_description="Used Ball, low mileage",
              category=category7, user_id=1)
session.add(item12)
session.commit()

item13 = Item(item_name="Player", item_description="Hand Painted Player",
              category=category7, user_id=1)
session.add(item13)
session.commit()


# Setup Skating Items
category8 = Category(category_name="Skating", user_id=1)
session.add(category8)
session.commit()

item14 = Item(item_name="Skates",
              item_description="White Skates with toe pick",
              category=category8, user_id=1)
session.add(item14)
session.commit()

item15 = Item(item_name="Sweater", item_description="With spaces for badges",
              category=category8, user_id=1)
session.add(item15)
session.commit()

# Setup Hockey Items
category9 = Category(category_name="Hockey", user_id=1)
session.add(category9)
session.commit()

item16 = Item(item_name="Stick", item_description="Graphite with wood blade",
              category=category9, user_id=1)
session.add(item16)
session.commit()

item17 = Item(item_name="Elbow Pads",
              item_description="blue with white stitching",
              category=category9, user_id=1)
session.add(item17)
session.commit()
