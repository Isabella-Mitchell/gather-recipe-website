from gather import db


class Category(db.Model):
    # schema for the Category model
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(40), unique=True, nullable=False)
    # recipes = db.relationship(
    # "recipe", backref="category", cascade="all, delete", lazy=True)

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return self.category_name


class User(db.Model):
    # schema for the User model
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), unique=True, nullable=False)
    user_first_name = db.Column(db.String(50), nullable=False)
    user_last_name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(260), nullable=False)

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return "#{0} - Username: {1} | First name: {2}".format(
            self.id, self.user_name, self.user_first_name
        )


# class Favourites(db.Model):
    # schema for the Favourites model
    # id = db.Column(db.Integer, primary_key=True)
    # category_id = db.Column(db.Integer, db.ForeignKey(), nullable=False)
    # in postgres task field - one to many relationship. 
    # Walkthrough > creating the database