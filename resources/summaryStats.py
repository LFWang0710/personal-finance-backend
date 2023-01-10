from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from schemas import TransactionSchema 
from models import TransactionModel
from db import db
from sqlalchemy import func, extract
from sqlalchemy.sql import label
from datetime import datetime


blp = Blueprint("summaryStats", __name__, description="Summary Stats of transactions")


# Get all transactions and add in transaction
@blp.route("/summary")
class TransactionsSum(MethodView):
    def get(self):
        
        ## Getting Monthly Trend
        trend_data = TransactionModel.query.with_entities(func.sum(TransactionModel.amount).label('amount'),
                                                            extract('year', TransactionModel.date).label('year'),
                                                            extract('month', TransactionModel.date).label('month')).\
                                                            group_by(extract('year', TransactionModel.date),
                                                                    extract('month', TransactionModel.date)).\
                                                            all()
        
        trend_data = [{'month': f'{row.year}{-row.month}','amount': round(abs(row.amount), 2)} for row in trend_data]


        ## Getting category data all time
        category_data = TransactionModel.query.with_entities(TransactionModel.category,
                            label('amount', func.sum(TransactionModel.amount))).group_by(TransactionModel.category).all()

        category_data = [{'category': row.category, 'amount': abs(row.amount)} for row in category_data]
        categories =  [i['category'] for i in category_data]


        currentMonth = datetime.now().month
        currentYear = datetime.now().year
        currentSum = [month['amount'] for month in trend_data if month['month'] == f'{currentYear}-{currentMonth}'][0]

        ## Getting Monthly category data
        category_data_all = TransactionModel.query.with_entities(
                            TransactionModel.category,
                            label('amount', func.sum(TransactionModel.amount)),
                             extract('year', TransactionModel.date).label('year'),
                            extract('month', TransactionModel.date).label('month')).group_by(TransactionModel.category,
                                                                                extract('year', TransactionModel.date),
                                                                                extract('month', TransactionModel.date)  ).all()

        category_data_all = [{'category': row.category, 'amount': abs(row.amount), "month": f"{row.year}-{row.month}"} for row in category_data_all]

        category_data_all_dict = {}

        for data in category_data_all:
            if data['month'] not in category_data_all_dict:
                category_data_all_dict[data['month']] = [{'category': category, 'amount': 0} for category in categories]
                for d in category_data_all_dict[data['month']]:
                    if d['category'] == data['category']:
                        d['amount'] = data['amount']

            else:
                for d in category_data_all_dict[data['month']]:
                    if d['category'] == data['category']:
                        d['amount'] = data['amount']


                        
        return {
            "trendData": trend_data,
            "categoryData": category_data,
            "categoriesUnique": [d['category'] for d in category_data],
            "currentMonthExpense": abs(currentSum),
            "categoryDataAll": category_data_all_dict,
            "currentYearMonth": f'{currentYear}-{currentMonth}',

        }



