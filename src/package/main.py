from src.package.concretions.pizza_json_table import PizzaJsonRow, PizzaJsonTable
from src.package.concretions.pizza_topping_json_table import (
    PizzaToppingJsonTable,
    PizzaToppingJsonRow,
    PizzaToppingJsonTableInitArgs,
)


tomato_topping = PizzaToppingJsonRow(topping_name="tomato", quantity=2)
cheese_topping = PizzaToppingJsonRow(topping_name="cheese", quantity=2)
peperoni_topping = PizzaToppingJsonRow(topping_name="peproni", quantity=5)

pizza_topping_table = PizzaToppingJsonTable(
    rows=[cheese_topping, tomato_topping, peperoni_topping]
)


pizza_1 = PizzaJsonRow(bread="Pan Crust", toppings=["Tomato", "Peperoni"])
pizza_2 = PizzaJsonRow(bread="Pan Crust", toppings=["Basil", "Tomato"])
pizza_3 = PizzaJsonRow(bread="Sourdough", toppings=["Cheese", "Peperoni"])

pizza_json_table = PizzaJsonTable(
    rows=[pizza_1, pizza_2, pizza_3],
    dependency_model_init_args={
        "pizza_topping": PizzaToppingJsonTableInitArgs(data_id=2)
    },
    dependency_versions={"pizza_topping": "Tomato;Cheese;Basil"},
)
print(pizza_json_table.dependency_tables["pizza_topping"].version)
