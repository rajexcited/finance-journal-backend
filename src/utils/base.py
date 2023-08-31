from pydantic import BaseModel, ConfigDict
from abc import ABC


class SerializeModel(BaseModel, ABC):
    """to serailize all classes"""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)
