from src.package.interfaces import JSONRow, JSONTable
from src.package.concretions.pizza_topping_json_table import (
    PizzaToppingJsonTable,
    PizzaToppingJsonTableInitArgs,
)
from typing import Optional


class PizzaJsonRow(JSONRow):
    bread: str
    toppings: list[str]

    def _get_row_id(self) -> str:
        return self.bread + "-" + ",".join(self.toppings)


class PizzaJsonTable(JSONTable):
    rows: list[PizzaJsonRow] = []
    dependency_model_init_args: dict[str, PizzaToppingJsonTableInitArgs]
    dependency_models: dict[str, PizzaToppingJsonTable] = {
        "pizza_topping": PizzaToppingJsonTable
    }

    def _get_rows(self) -> list[PizzaJsonRow]:
        return [PizzaJsonRow(bread="Pan Crust", toppings=["Tomato", "Peperoni"])]

    def _generate_version(self) -> str:
        return ";".join([row.id for row in self.rows])
