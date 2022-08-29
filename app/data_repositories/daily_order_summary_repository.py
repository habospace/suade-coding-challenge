from decimal import Decimal
from datetime import date
from dateutil.parser import parse
from typing import Dict

import pandas as pd
from pydantic import BaseModel

# create type synonyms for better readability
PromotionId = str
TotalCommissionAmount = Decimal


class SummaryNotAvailableForDateError(Exception):
    pass


class DailyOrderSummarySchema(BaseModel):
    date: date
    total_items_sold: int
    total_customers: int
    total_discount_amount: Decimal
    average_discount_rate: Decimal
    average_order_total: Decimal
    total_commissions: Decimal
    average_commissions_per_order: Decimal
    total_commission_amount_per_promotion: Dict[PromotionId, TotalCommissionAmount]


class DailyOrderSummaryRepository:
    # Normally this class would be wrapper around the database \
    # to aggregate over the relevant tables to pull the data \
    # that make up a daily order summary. Since the data is \
    # in flat files this repository is only going wrap around \
    # the files.
    # The repository pattern requires us to define 5 methods:
    # - get
    # - add
    # - update
    # - list
    # - delete
    # It doesn't really make sense to define all 5 methods \
    # for this order summary class since this class is only \
    # for us to be able to read the data, we don't want to \
    # be able to delete/update etc. all the data that make \
    # up a daily order summary.
    # To learn more about repository the pattern see:
    # https://www.cosmicpython.com/book/chapter_02_repository.html

    def __init__(
            self, orders: pd.DataFrame,
            order_lines: pd.DataFrame,
            commissions: pd.DataFrame,
            product_promotions: pd.DataFrame,
            products: pd.DataFrame,
            promotions: pd.DataFrame
    ):
        self.orders = orders
        self.order_lines = order_lines
        self.vendor_commissions = commissions
        self.product_promotions = product_promotions
        self.products = products
        self.promotions = promotions
        # join up all the the individual datasets
        self.joined_order_data = self.__join_datasets()
        # acts on self.joined_order_data
        self.__convert_date_like_str_columns_to_date()
        # acts on self.joined_order_data
        self.__convert_numerical_columns_to_decimal()
        self.joined_order_data["commission_amount"] = self.joined_order_data.apply(
            lambda row: row.total_amount * row.rate, axis=1
        )
        # this is for caching daily summaries to avoid recalculating again
        self.daily_summary_report_cache = {}

    def __join_datasets(self) -> pd.DataFrame:
        # standardise join columns for pandas merge + to avoid having
        # multiple columns called 'id' that actually mean different things
        orders = self.orders.rename(columns={"id": "order_id"}, inplace=False)
        products = self.products.rename(
            columns={
                "id": "product_id",
                # renaming description as it's used in other datasets such as 'promotion' and 'product'
                # appending an extra '_' to make it unique because 'product_description' is duplicated
                # (saved at both 'order_line' and 'product')
                "description": "product_description_"
            }, inplace=False
        )
        promotions = self.promotions.rename(
            columns={
                "id": "promotion_id",
                "description": "promotion_description"
            }, inplace=False
        )

        joined_order_data = pd.merge(
            self.order_lines, products, on=["product_id"], how="left"
        ).merge(
            orders, on=["order_id"], how="left"
        )
        joined_order_data["date"] = joined_order_data.apply(
            lambda row: str(parse(row.created_at).date()) if pd.notnull(row.created_at) else None, axis=1
        )
        joined_order_data = joined_order_data.merge(
            self.vendor_commissions, on=["date", "vendor_id"], how="left"
        ).merge(
            self.product_promotions, on=["product_id", "date"], how="left"
        ).merge(
            promotions, on=["promotion_id"], how="left"
        )
        return joined_order_data

    def __convert_date_like_str_columns_to_date(self):
        self.joined_order_data.date = self.joined_order_data.apply(
            lambda row: parse(row.date).date(), axis=1
        )
        self.joined_order_data.created_at = self.joined_order_data.apply(
            lambda row: parse(row.created_at), axis=1
        )

    def __convert_numerical_columns_to_decimal(self):
        # Convert critical financial columns from float to Decimal for better precision for follow up calculations.
        for column in ["rate", "total_amount", "discount_rate", "discounted_amount", "full_price_amount"]:
            self.joined_order_data[column] = self.joined_order_data.apply(
                lambda row: Decimal(row[column]), axis=1
            )

    def get(self, date: date) -> DailyOrderSummarySchema:
        try:
            # try pulling the daily order summary from cache
            return self.daily_summary_report_cache[date]
        except KeyError:
            orders_at_date = self.joined_order_data[self.joined_order_data.date == date]
            if len(orders_at_date) == 0:
                raise SummaryNotAvailableForDateError(f"No orders at date: '{date}'.")
            total_items_sold = len(orders_at_date)
            total_customers = len(orders_at_date.customer_id.unique())
            total_discount_amount = orders_at_date.full_price_amount.sum() - orders_at_date.discounted_amount.sum()
            average_discount_rate = orders_at_date.discount_rate.mean()
            average_order_total = orders_at_date.total_amount.mean()
            total_commissions = orders_at_date.commission_amount.sum()
            average_commissions_per_order = orders_at_date.groupby(
                ["order_id"]
            ).agg({"commission_amount": "sum"}).reset_index().commission_amount.mean()
            # aggregate total commissions per promotion for the day
            total_commission_amount_per_promotion = {
                str(int(row.promotion_id)): row.commission_amount for _, row in orders_at_date.groupby(
                    ["promotion_id"]
                ).agg(
                    {"commission_amount": "sum"}
                ).reset_index().iterrows()
            }
            # backfill the promotions dictionary with promo codes that weren't available on the day
            total_commission_amount_per_promotion.update(
                {str(k): Decimal(0)
                 for k in set([str(i) for i in range(1, 6)]) - set(total_commission_amount_per_promotion.keys())}
            )
            order_summary = DailyOrderSummarySchema(
                date=date,
                total_items_sold=total_items_sold,
                total_customers=total_customers,
                total_discount_amount=total_discount_amount,
                average_discount_rate=average_discount_rate,
                average_order_total=average_order_total,
                total_commissions=total_commissions,
                average_commissions_per_order=average_commissions_per_order,
                total_commission_amount_per_promotion=total_commission_amount_per_promotion

            )
            # save daily order summary to cache
            self.daily_summary_report_cache[date] = order_summary
            return order_summary
