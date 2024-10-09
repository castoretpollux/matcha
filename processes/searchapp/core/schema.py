from typing import Dict
from pydantic import BaseModel


class LoginPayload(BaseModel):

    namespace: str
    user_id: int
    user_name: str
    group_mapping: Dict[int, str]
    is_superuser: bool
    is_staff: bool
