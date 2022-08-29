from marshmallow import (
    fields,
    Schema
)


class CommissionsSchema(Schema):
    total = fields.Float(required=True)
    order_average = fields.Float(required=True)
    promotions = fields.Dict(required=True)


class DailyOrderSummarySchema(Schema):
    date = fields.Date(required=True)
    customers = fields.Integer(required=True)
    total_discount_amount = fields.Float(required=True)
    items = fields.Integer(required=True)
    order_total_avg = fields.Float(required=True)
    discount_rate_avg = fields.Float(required=True)
    commissions = fields.Nested(CommissionsSchema, required=True)
