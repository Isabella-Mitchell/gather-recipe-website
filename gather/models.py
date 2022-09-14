from gather import db


class Category(db.Model):
    # schema for the Category model - to be removed
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return self.category_name


class Cuisine(db.Model):
    # schema for the Cuisine model
    id = db.Column(db.Integer, primary_key=True)
    cuisine_name = db.Column(db.String(40), unique=True, nullable=False)

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return self.cuisine_name


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


class Favourite(db.Model):
    # schema for the Favourite model. wanted to make user_name into foreign key but this caused bug. 
    # This hasn't pulled into Heroku properly yet
    # Also could set up cascade delete so if user is deleted, so are all favourites
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(50), nullable=False)
    recipe_id = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        # __repr__ to represent itself in the form of a string
        return "#{0} - User Name: {1} | Recipe ID: {2}".format(
            self.id, self.user_name, self.recipe_id
        )
