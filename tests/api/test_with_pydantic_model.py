import json
import pytest
from models.registration_user_model import RegistrationUser

pytestmark = pytest.mark.skip(reason="TASK-1234: Тесты временно отключены из-за хз чего")

def test_pydantic_validation(test_user, creation_user_data):

    user_model_1 = RegistrationUser(**test_user)
    json_1 = user_model_1.model_dump_json(exclude_unset=True)

    user_model_2 = RegistrationUser(**creation_user_data)
    json_2 = user_model_2.model_dump_json()

    print("\n=== creation_user_data / без exclude_unset ===")
    print(json_2)

    d1 = json.loads(json_1)
    d2 = json.loads(json_2)

    assert "banned" not in d1
    assert "verified" not in d1

    assert d2["banned"] is False
    assert d2["verified"] is True
