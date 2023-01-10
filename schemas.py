from marshmallow import Schema, fields


class TransactionSchema(Schema):
    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    amount = fields.Float(required=True)
    category = fields.Str(required=True)
    date = fields.Date(format='%Y-%m-%d', required=True)
    card_info = fields.Str(required=True)
