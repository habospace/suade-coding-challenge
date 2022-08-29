from datetime import (
    datetime
)
from typing import Dict

from werkzeug.exceptions import HTTPException
from flask_smorest import Blueprint
from flask.views import MethodView
from flask import current_app

from data_repositories.daily_order_summary_repository import SummaryNotAvailableForDateError
from web_api.errors import SubmittedDateIsNotValidError
from web_api.schemas.response import DailyOrderSummarySchema


api_blp = Blueprint("api", "order_summary", url_prefix="/api/")


@api_blp.route("/order_summary/<date>")
class OrderSummary(MethodView):

    @api_blp.response(200, schema=DailyOrderSummarySchema)
    def get(self, date: str) -> Dict:
        try:
            date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise SubmittedDateIsNotValidError(f"Submitted value '{date}' is not a valid date of format '%Y-%m-%d'.")
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


@api_blp.errorhandler(SubmittedDateIsNotValidError)
def handle_submitted_date_is_not_valid_error(error):
    return {"error": str(error)}, 400


@api_blp.errorhandler(SummaryNotAvailableForDateError)
def handle_summary_not_available_for_date_error(error):
    return {"error": str(error)}, 404


@api_blp.errorhandler(Exception)
def handle_general_exception(error):
    if isinstance(error, HTTPException):
        return {"error": str(error)}, error.code
    return {"error": str(error)}, 500
