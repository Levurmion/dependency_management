from src.package.interfaces import JSONRow, JSONTable
from pydantic import BaseModel
from typing import Optional


database = {
    1: [
        {"topping_name": "Tomato", "quantity": 5},
        {"topping_name": "Cheese", "quantity": 8},
        {"topping_name": "Basil", "quantity": 9},
    ],
    2: [
        {"topping_name": "Pepperoni", "quantity": 5},
        {"topping_name": "Cheese", "quantity": 10},
        {"topping_name": "Ham", "quantity": 22},
    ],
    3: [
        {"topping_name": "Egg", "quantity": 4},
        {"topping_name": "Sausage", "quantity": 18},
        {"topping_name": "Basil", "quantity": 9},
    ],
}


class PizzaToppingJsonTableInitArgs(BaseModel):
    data_id: int


class PizzaToppingJsonRow(JSONRow):
    topping_name: str
    quantity: int

    def _get_row_id(self) -> str:
        return self.topping_name


class PizzaToppingJsonTable(JSONTable):
    init_args: Optional[PizzaToppingJsonTableInitArgs] = None
    rows: list[PizzaToppingJsonRow] = []

    def _get_rows(self) -> list:
        if "init_args" in self.model_fields_set:
            data = database[self.init_args.data_id]
            return [PizzaToppingJsonRow(**row) for row in data]
        else:
            return []

    def _generate_version(self) -> str:
        return ";".join([row.id for row in self.rows])
