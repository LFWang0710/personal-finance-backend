from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import TransactionSchema 
from models import TransactionModel
from db import db
from sqlalchemy import func, extract
from sqlalchemy.sql import label
import json

blp = Blueprint("transactions", __name__, description="Operations on Transactions")


# Operate on a single transaction
@blp.route("/transaction/<string:transaction_id>")
class Transaction(MethodView):
    @blp.response(200, TransactionSchema)
    def get(self, transaction_id):

        transaction = TransactionModel.query.get_or_404(transaction_id)
        
        return transaction
    
    def delete(self, transaction_id):
        transaction = TransactionModel.query.get_or_404(transaction_id)
        db.session.delete(transaction)
        db.session.commit()

        return {"message": "Deleted"}

    @blp.arguments(TransactionSchema)
    @blp.response(200, TransactionSchema)
    def put(self, transaction_data, transaction_id):
        transaction = TransactionModel.query.get(transaction_id)
        
        if transaction: # if a category got updated
            if transaction.category != transaction_data['category']:
                mapping = json.load(open("categoryMapping.json"))

                mapping[transaction_data['name']] = transaction_data['category']
                # Serializing json
                json_object = json.dumps(mapping, indent=4)
                
                # Writing to sample.json
                with open("categoryMapping.json", "w") as outfile:
                    outfile.write(json_object)


            transaction.name = transaction_data['name']
            transaction.amount = transaction_data['amount']
            transaction.date = transaction_data['date']
            transaction.category = transaction_data['category']
        else:
            transaction = TransactionModel(id=transaction_id, **transaction_data)

        db.session.add(transaction)
        db.session.commit()

        return transaction


# Get all transactions and add in transaction
@blp.route("/transactions")
class Transactions(MethodView):
    @blp.response(200, TransactionSchema(many=True))
    def get(self):
        return TransactionModel.query.all()


    @blp.arguments(TransactionSchema)
    @blp.response(200, TransactionSchema)
    def post(self, transaction):
        transaction_sql = TransactionModel(**transaction)
        db.session.add(transaction_sql)
        db.session.commit()



        return transaction


# Get all transactions and add in transaction
@blp.route("/transactions/sum")
class TransactionsSum(MethodView):
    def get(self):
        sum = TransactionModel.query.with_entities(func.sum(TransactionModel.amount).label('total')).first().total
                        
        return {'sum': sum}



# Get all transactions and add in transaction
@blp.route("/transactions/sum/bymonth")
class TransactionsSum(MethodView):
    def get(self):

        sum = TransactionModel.query.with_entities(func.sum(TransactionModel.amount).label('amount'),
                                                            extract('year', TransactionModel.date).label('year'),
                                                            extract('month', TransactionModel.date).label('month')).\
                                                            group_by(extract('year', TransactionModel.date),
                                                                    extract('month', TransactionModel.date)).\
                                                            all()
        

                        
        return [{'month': f'{row.year}{-row.month}','amount': abs(row.amount)} for row in sum]


# Get all transactions and add in transaction
@blp.route("/transactions/sum/bycategory")
class TransactionsSum(MethodView):
    def get(self):
        sum = TransactionModel.query.with_entities(TransactionModel.category,
                            label('amount', func.sum(TransactionModel.amount))).group_by(TransactionModel.category).all()
        

                        
        return [{'category': row.category, 'amount': abs(row.amount)} for row in sum]