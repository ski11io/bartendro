#!/usr/bin/env python

import os
from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, current_user
from flask.ext.permissions.core import Permissions
from sqlalchemy.orm import mapper, relationship, backref

SQLALCHEMY_DATABASE_FILE = 'bartendro.db'
SQLALCHEMY_DATABASE_URI = 'sqlite:///../' + SQLALCHEMY_DATABASE_FILE
SECRET_KEY = 'let our bot get you drunk!'

STATIC_PATH = "/static"
STATIC_FOLDER = "content/static"
TEMPLATE_FOLDER = "content/templates"

app = Flask(__name__,
            static_url_path = STATIC_PATH,
            static_folder = os.path.join("..", STATIC_FOLDER),
            template_folder = os.path.join("..", TEMPLATE_FOLDER))
app.config.from_object(__name__)
db = SQLAlchemy(app)



login_manager = LoginManager()
login_manager.login_view = "/login"
login_manager.setup_app(app)

permissions = Permissions(app, db, current_user)

# Import models
from bartendro.model.drink import Drink
from bartendro.model.custom_drink import CustomDrink
from bartendro.model.drink_name import DrinkName
from bartendro.model.drink_booze import DrinkBooze

from bartendro.model.booze import Booze
from bartendro.model.booze_group import BoozeGroup
from bartendro.model.booze_group_booze import BoozeGroupBooze

from bartendro.model.dispenser import Dispenser
from bartendro.model.drink_log import DrinkLog
from bartendro.model.drink_log_booze import DrinkLogBooze
from bartendro.model.shot_log import ShotLog
from bartendro.model.version import DatabaseVersion
from bartendro.model.option import Option
from bartendro.model.user import User

db.create_all()
db.session.commit()

Drink.name = relationship(DrinkName, backref=backref("drink"), cascade="save-update, merge, delete")

# TODO: This relationship should really be on Drinkbooze
Drink.drink_boozes = relationship(DrinkBooze, backref=backref("drink"))
DrinkBooze.booze = relationship(Booze, backref=backref("drink_booze")) #here cascade on delete is removed because it leads to deleting a booze completely, when a booze is removed from a drink

# This is the proper relationship from above.
#DrinkBooze.drink= relationship(Drink, backref=backref("drink_booze"))

Dispenser.booze = relationship(Booze, backref=backref("dispenser"))
BoozeGroup.abstract_booze = relationship(Booze, backref=backref("booze_group"), cascade="save-update, merge, delete")
BoozeGroupBooze.booze_group = relationship(BoozeGroup, backref=backref("booze_group_boozes"), cascade="save-update, merge, delete")
BoozeGroupBooze.booze = relationship(Booze, backref=backref("booze_group_booze"), cascade="save-update, merge, delete")
CustomDrink.drink = relationship(Drink, backref=backref("custom_drink"), cascade="save-update, merge, delete")

#TODO add backrefs here
DrinkLog.drink = relationship(Drink)
DrinkLog.user = relationship(User)
DrinkLogBooze.booze = relationship(Booze, backref=backref("drink_log_booze"))
ShotLog.booze = relationship(Booze)

# Import views
from bartendro.view import root, trending, user
from bartendro.view.admin import booze as booze_admin, drink as drink_admin, \
                                 dispenser as admin_dispenser, report, liquidlevel, options, debug
from bartendro.view.drink import drink
from bartendro.view.ws import booze as ws_booze, dispenser as ws_dispenser, drink as ws_drink, \
                              misc as ws_misc, liquidlevel, option as ws_options


# #Create users (only needed once when database is empty)
# my_admin = User("admin", "admin")
# my_admin.add_roles('admin')
# 
# my_user = User("user", "user")
# my_user.add_roles('user')
# db.session.commit()
# 
# my_user2 = User("user2", "user2")
# my_user2.add_roles('user')
# db.session.commit()
# my_user3 = User("machine", "machine1337")
# my_user3.add_roles('machine')
# db.session.commit()

@app.before_request
def before_request(exception=None):
    if not app.startup_err or request.path.startswith("/static"):
        return
    return render_template("startup_error", startup_err = app.startup_err)
