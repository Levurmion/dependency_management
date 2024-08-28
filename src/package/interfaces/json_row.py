from pydantic import BaseModel, field_validator, model_validator, ValidationInfo
from abc import ABC, abstractmethod
from typing import Optional


class JSONRow(BaseModel, ABC):
    id: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @model_validator(mode="after")
    def _set_row_id(self) -> str:
        if "id" not in self.model_fields_set:
            self.id = self._get_row_id()
        return self

    @abstractmethod
    def _get_row_id(self) -> str:
        """
        This is the default method that you can set to give a row object
        a unique `id` if not explicitly set during instantiation.
        """
        pass
