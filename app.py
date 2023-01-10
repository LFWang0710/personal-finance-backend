from flask import Flask
from flask_smorest import Api
from resources.transaction import blp as TransactionBlueprint
from resources.summaryStats import blp as SummaryBlueprint

from db import db
from models import TransactionModel
from flask_cors import CORS
import pandas as pd 
from datetime import datetime

import json

from data_prepreocess import preprocess_and_combine


transactions = preprocess_and_combine()

dates = transactions.date.values
names = transactions.name.values
categories = transactions.category_cleaned.values
amounts = transactions.amount.values
card_infos = transactions.card_info.values

def create_app():
    app = Flask(__name__)
    CORS(app)

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Personal Finance App Server"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAI_SWAGGER_UI_URL"] = "https://cdn.jsdekivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)


    api = Api(app)

    @app.before_first_request
    def create_tables():
        db.drop_all()
        db.create_all()
        
        for i in range(transactions.shape[0]):

            categoryMapping = json.load(open('categoryMapping.json'))
            db.session.add(TransactionModel(**{
                "name": names[i],
                "amount": amounts[i],
                "category": categoryMapping.get(names[i], categories[i]),
                "date": datetime.strptime(dates[i], "%Y-%m-%d"),
                "card_info": card_infos[i]
            }))
        
        db.session.commit()

        

        


    api.register_blueprint(TransactionBlueprint)
    api.register_blueprint(SummaryBlueprint)


    return app