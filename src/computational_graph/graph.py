from typing import Union, Callable
from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError
from collections import defaultdict
import src.computational_graph.functions as fn


class ComputationalRelation(BaseModel):
    direction: tuple[str, str]
    dependencies: list[str]
    function: Callable[..., Union[float, int, None]]


class ComputationalGraph(BaseModel):
    relations: list[ComputationalRelation] = []
    constants: dict[str, Union[int, float, None]] = {}

    # private attributes
    __relations_table__: dict[str, ComputationalRelation] = {}
    __adjacency_list__: defaultdict[str, list[str]] = defaultdict(list)

    @model_validator(mode="after")
    def __instantiate_model(self):
        for relation in self.relations:
            key = self.__get_relation_key(*relation.direction)
            if key in self.__relations_table__:
                raise PydanticCustomError(
                    "`ComputationalGraph` relations must be unique.",
                    f"Found duplicate relation: `{key}`.",
                )
            else:
                self.__relations_table__[key] = relation
                self.__adjacency_list__[relation.direction[0]].append(
                    relation.direction[1]
                )

        compute_constants = set()
        for node, val in self.constants.items():
            if val is not None:
                compute_constants.add(node)

        self.__traverse_graph(list(self.constants.keys())[0], compute_constants)

    # dunder method overrides
    def __getitem__(self, name: str) -> Union[float, int]:
        if name not in self.constants:
            raise PydanticCustomError(
                "Unknown constant error.",
                f"Constant `{name}` does not exist in `ComputationalGraph`.",
            )
        return self.constants[name]

    def __setitem__(self, name: str, value: Union[float, int]):
        if name not in self.constants:
            raise PydanticCustomError(
                "Unknown constant error.",
                f"Constant `{name}` does not exist in `ComputationalGraph`.",
            )
        self.constants[name] = value
        self.__traverse_graph(name)

    def update_value(
        self, name: str, value: Union[int, float], compute_constants: set[str]
    ):
        if name not in self.constants:
            raise PydanticCustomError(
                "Unknown constant error.",
                f"Constant `{name}` does not exist in `ComputationalGraph`.",
            )
        self.constants[name] = value
        compute_constants.add(name)
        self.__traverse_graph(name, compute_constants)

    def __get_relation_key(self, start: str, end: str):
        return f"{start}->{end}"

    def __traverse_graph(self, start: str, compute_constants: set[str]):
        visited_nodes = set(start)
        node_queue = [start]

        while len(node_queue) > 0:
            curr_node = node_queue.pop()
            visited_nodes.add(curr_node)  # mark visited
            adjacent_nodes = self.__adjacency_list__[curr_node]

            if curr_node not in compute_constants:
                # check for relations with adjacent nodes
                for adj_node in adjacent_nodes:
                    relation_key = self.__get_relation_key(adj_node, curr_node)
                    if relation_key in self.__relations_table__:
                        relation = self.__relations_table__[relation_key]
                        dependency_values = [
                            self.constants[name] for name in relation.dependencies
                        ]
                        node_value = relation.function(*dependency_values)
                        if node_value is not None:
                            self.constants[curr_node] = node_value

            for node in adjacent_nodes:
                if node not in visited_nodes:
                    node_queue.insert(0, node)


if __name__ == "__main__":

    graph = ComputationalGraph(
        constants={"a": 2, "b": 4, "c": None},
        relations=[
            ComputationalRelation(
                direction=["a", "c"], dependencies=["a", "b"], function=fn.c_from_ab
            ),
            ComputationalRelation(
                direction=["b", "c"], dependencies=["a", "b"], function=fn.c_from_ab
            ),
            ComputationalRelation(
                direction=["c", "a"], dependencies=["c", "b"], function=fn.a_from_cb
            ),
            ComputationalRelation(
                direction=["c", "b"], dependencies=["c", "a"], function=fn.b_from_ca
            ),
        ],
    )

    print(graph.constants)

    graph.update_value("c", 8, set("b"))

    print(graph.constants)

    graph.update_value("b", 22, set("c"))

    print(graph.constants)
