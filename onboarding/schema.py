from pydantic import BaseModel
from typing import List


class UserContext(BaseModel):
    business_name: str
    business_type: str
    location: str

    goals: List[str]
    key_constraints: List[str]

    target_audience: str
    brand_voice: str

    available_documents: List[str]
