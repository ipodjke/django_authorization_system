from typing import Dict, Union

from django_auth_system.conf import settings
from django_auth_system.exceptions import HaveNoRequiredFileds


class SchemaValidator:
    def validate_schema(self, schema: Dict) -> bool:
        self._check_required_schema_field(schema)
        return True

    def _check_required_schema_field(self,
                                     schema: Dict
                                     ) -> Union[HaveNoRequiredFileds, bool]:

        for field in settings.REQUIRED_SCHEMA_FIELDS:
            if field not in schema:
                raise HaveNoRequiredFileds(f'Field "{ field }" is missing in '
                                           'the model schema.')
        return True
