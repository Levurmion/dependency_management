from typing import Union, Callable, Any, Optional
from pydantic import BaseModel, model_validator, field_validator
from pydantic_core import PydanticCustomError
from collections import defaultdict
import src.computational_graph.functions as fn
import inspect
from copy import deepcopy


class VariableFn(BaseModel):
    function: Callable[..., Any]
    deps: list[str] = []

    @model_validator(mode="after")
    def __set_deps(self):
        self.deps = [dep for dep in inspect.signature(self.function).parameters.keys()]
        return self


class Variable(BaseModel):
    name: str
    value: Any = None
    functions: list[VariableFn] = []
    verification_fn: Optional[Callable[[Any, Any], bool]] = None

    @field_validator("functions", mode="before")
    @classmethod
    def __init_variable_fn(cls, functions: list[Callable[..., Any]]):
        return [VariableFn(function=fn) for fn in functions]

    @property
    def all_dependencies(self) -> list[str]:
        all_dependencies = set()
        for fn in self.functions:
            for dep in fn.deps:
                all_dependencies.add(dep)
        return list(all_dependencies)


class ComputationalGraph(BaseModel):
    variables: list[Variable] = []

    __variables_table__: dict[str, Variable] = {}
    __adjacency_table__: defaultdict[str, list[str]] = defaultdict(list)
    __default_constants__: set[str] = set()

    @model_validator(mode="after")
    def __setup_computational_graph(self):
        for variable in self.variables:
            if variable.name in self.__variables_table__:
                raise PydanticCustomError(
                    "`ComputationalGraph` variables must be unique.",
                    f"Found duplicate variable: `{variable.name}`.",
                )
            self.__variables_table__[variable.name] = variable

            if len(variable.all_dependencies) == 0:
                # if a variable has no dependencies, it will be set as a default constant
                self.__default_constants__.add(variable.name)
            else:
                for dep in variable.all_dependencies:
                    # a directed edge from dependency -> variable
                    self.__adjacency_table__[dep].append(variable.name)

        first_variable = self.variables[0]
        self.__traverse_graph(first_variable.name, deepcopy(self.__default_constants__))

    def __getitem__(self, name: str) -> Optional[Variable]:
        if name not in self.__variables_table__:
            return None
        return self.__variables_table__[name]

    def __str__(self):
        graph_values = {var.name: var.value for var in self.variables}
        return graph_values.__str__()

    def update_variable(
        self, name: str, value: Any, constants: list[str] = [], propagate: bool = True
    ):
        if name not in self.__variables_table__:
            raise PydanticCustomError(
                "Can only update declared variables.",
                f"Variable `{name}` not found in `ComputationalGraph`.",
            )
        self.__variables_table__[name].value = value
        if propagate:
            constants_set = set(constants).union(self.__default_constants__)
            constants_set.add(name)
            self.__traverse_graph(name, constants_set)

    def __traverse_graph(self, start: str, constants: set[str]):
        """
        We traverse the graph using BFS to capture the hierarchy of dependencies
        from the starting variable.
        """
        # initialize BFS with a queue
        visited_nodes = set(start)
        node_queue = [start]

        while len(node_queue) > 0:
            curr_node = node_queue.pop()
            visited_nodes.add(curr_node)  # mark visited

            # try to compute this node if it's not set as a constant
            if curr_node not in constants:
                variable = self.__variables_table__[curr_node]
                variable_fns = variable.functions

                possible_variable_values = []
                for variable_fn in variable_fns:
                    # only use the formula where all of its dependencies were set as constants
                    if all([dep in constants for dep in variable_fn.deps]):
                        dep_values = [
                            self.__variables_table__[dep].value
                            for dep in variable_fn.deps
                        ]
                        possible_variable_values.append(
                            variable_fn.function(*dep_values)
                        )

                # if we have multiple possible values, we need to make sure they all agree
                if len(possible_variable_values) == 1:
                    variable.value = possible_variable_values[0]
                elif len(possible_variable_values) > 1:
                    verification_fn = (
                        variable.verification_fn
                        if variable.verification_fn is not None
                        else self.__default_verification_fn
                    )
                    for i in range(0, len(possible_variable_values) - 1):
                        if not verification_fn(
                            possible_variable_values[i], possible_variable_values[i + 1]
                        ):
                            self.__raise_value_inconsistency_error(
                                variable.name, variable_fns, possible_variable_values
                            )

                # mark as a constant for downstream calculations
                constants.add(curr_node)

            adjacent_nodes = self.__adjacency_table__[curr_node]

            for node in adjacent_nodes:
                if node not in visited_nodes:
                    node_queue.insert(0, node)

    def __default_verification_fn(self, obj_A: Any, obj_B: Any) -> bool:
        return obj_A == obj_B

    def __raise_value_inconsistency_error(
        self, variable_name: str, variable_fns: list[VariableFn], variable_values: list
    ):
        raise ValueError(
            f"Value inconsistency detected between functions computing variable: `{variable_name}`!",
            *[
                f"{variable_fn.function.__name__} = {variable_values[idx]}"
                for idx, variable_fn in enumerate(variable_fns)
            ],
        )


if __name__ == "__main__":
    graph = ComputationalGraph(
        variables=[
            Variable(name="a", functions=[]),
            Variable(name="b", functions=[fn.b_from_ca]),
            Variable(
                name="c",
                functions=[fn.c_from_ab, fn.c_from_de],
                verification_fn=lambda a, b: a == b,
            ),
            Variable(name="d", functions=[]),
            Variable(
                name="e",
                functions=[fn.e_from_cd, fn.e_from_fg],
                verification_fn=lambda a, b: a == b,
            ),
            Variable(name="f", functions=[]),
            Variable(name="g", functions=[fn.g_from_ef]),
        ]
    )

    graph.update_variable("a", 2)

    print(graph)

    graph.update_variable("b", 3)

    print(graph)

    graph.update_variable("d", 2)

    print(graph)

    graph.update_variable("f", 2, ["e"])
    print(graph)

    graph.update_variable("g", 24)
    print(graph)
