from __future__ import annotations

from pydantic import BaseModel, model_validator
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional, Type, Tuple, Any
from .json_row import JSONRow

R = TypeVar("R", bound=JSONRow)


class JSONTable(BaseModel, ABC, Generic[R]):
    rows: list[R] = []
    init_args: Optional[BaseModel] = None
    dependency_models: dict[str, Type[JSONTable]] = {}
    dependency_model_init_args: dict[str, BaseModel] = {}
    dependency_tables: dict[str, JSONTable] = {}
    dependency_versions: dict[str, str] = {}
    version: Optional[str] = None

    @model_validator(mode="after")
    def _initialize_table(self):
        if "rows" not in self.model_fields_set:
            self.rows = self._get_rows()
        if "version" not in self.model_fields_set:
            self.version = self._generate_version()
        self._validate_row_ids_unique()
        self._initialize_dependency_tables()
        self._validate_dependency_versions_up_to_date()
        return self

    def _validate_dependency_versions_up_to_date(self):
        """
        Validate that dependencies are up-to-date as the specified `dependency_versions`.
        """
        for key, current_version in self.dependency_versions.items():
            assert (
                current_version == self.dependency_tables[key].version
            ), f"Detected dependency: `{key}` version mismatch."

    def _validate_row_ids_unique(self):
        """
        Validate that row `ids` are unique.
        """
        ids = set()
        for row in self.rows:
            assert row.id not in ids, "Row `ids` must be unique."
            ids.add(row.id)

    def _initialize_dependency_tables(self):
        self.dependency_tables = {
            key: Model(init_args=self.dependency_model_init_args[key])
            for key, Model in self.dependency_models.items()
        }

    @abstractmethod
    def _get_rows(self) -> list[R]:
        """
        This is the default method of initializing the table when no `rows`
        were explicitly passed during instantiation.
        """
        pass

    @abstractmethod
    def _generate_version(self) -> str:
        """
        This is the default method of versioning a table when `version` was
        not explicitly passed during instantiation.
        """
        pass
