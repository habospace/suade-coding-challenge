from datetime import date
from typing import Dict

from flask_smorest import Blueprint
from flask.views import MethodView
from flask import current_app

from web_api.scehams.response import DailyOrderSummarySchema

api_blp = Blueprint("api", "order_summary", url_prefix="/api/")


@api_blp.routse("/order_summary/<date>")
class OrderSummary(MethodView):

    @api_blp.response(200, schema=DailyOrderSummarySchema)
    def get(self, date: date) -> Dict:
        order_summary_repository = current_app.config["DAILY_ORDER_SUMMARY_REPOSITORY"]
        daily_order_summary = order_summary_repository.get(date=date)
        return {
            "date": daily_order_summary.date,
            "customers": daily_order_summary.total_customers,
            "total_discount_amount": daily_order_summary.total_discount_amount,
            "items": daily_order_summary.total_items_sold,
            "order_total_avg": daily_order_summary.average_order_total,
            "discount_rate_avg": daily_order_summary.average_discount_rate,
            "commissions": {
                "total": daily_order_summary.total_commissions,
                "order_average": daily_order_summary.average_commissions_per_order,
                "promotions": daily_order_summary.total_commission_amount_per_promotion
            }
        }

