import typing
import json
from inspect import get_annotations, isclass
from typing import get_origin, get_args


class JSONSchemaGenerator:
    """
        JSONSchemaGenerator is a utility class for generating JSON Schema representations
        of Python classes. It uses Python type annotations and specific class attributes
        to construct a JSON Schema.

        The generated schema includes details such as properties (derived from class attributes),
        required fields, and type annotations. It also supports complex types like nested
        classes and lists/dictionaries with specific type annotations.

        Attributes in the Python class can have associated descriptions for the JSON Schema,
        which are defined using a specific naming convention (e.g., _<attr_name>_description).

        Usage:
        To generate a JSON Schema, instantiate this class with a Python class as an argument
        and call the `generate` method.

        Example:
        class MyDataClass:
            my_attribute: str

        schema_generator = JSONSchemaGenerator(MyDataClass)
        print(schema_generator.generate())

        Note:
        This class is designed to be used with classes that have type annotations and
        optionally special class attributes for schema descriptions and required fields.
    """
    def __init__(self, cls):
        if not isclass(cls):
            raise TypeError("Expected a class type")
        self.cls = cls

    def generate(self):
        schema = {
            'id': f'{self.cls.__name__}_schema',
            '$schema': 'http://json-schema.org/draft-04/schema#',
            'type': 'object',
            'properties': {},
            'required': getattr(self.cls, '_required', [])
        }

        annotations = get_annotations(self.cls)
        for attr, attr_type in annotations.items():
            property_schema = {'type': self.type_to_json_type(attr_type)}

            # Check for a description attribute
            description_attr = f'_{attr}_description'
            if hasattr(self.cls, description_attr):
                property_schema['description'] = getattr(self.cls, description_attr)

            schema['properties'][attr] = property_schema

        if hasattr(self.cls, '_schema_description'):
            schema['description'] = self.cls._schema_description

        return json.dumps(schema, indent=4)

    @classmethod
    def type_to_json_type(cls, python_type):
        if python_type == str:
            return 'string'
        elif python_type == int:
            return 'integer'
        elif python_type == bool:
            return 'boolean'
        elif python_type == float:
            return 'number'
        elif get_origin(python_type) is list:
            # Handles List[type]
            item_type = get_args(python_type)[0]
            return {'type': 'array', 'items': {'type': JSONSchemaGenerator.type_to_json_type(item_type)}}
        elif get_origin(python_type) is dict:
            # Handles Dict[key_type, value_type]
            key_type, value_type = get_args(python_type)
            # Assuming keys are of type string for JSON objects
            if key_type == str:
                return {'type': 'object',
                        'additionalProperties': {'type': JSONSchemaGenerator.type_to_json_type(value_type)}}
            else:
                return 'unknown'
        elif isinstance(python_type, type):
            # Handles custom class types
            return {'$ref': f'#/definitions/{python_type.__name__}'}
        elif get_origin(python_type) is typing.Union:
            # Handles Optional[type] as Union[type, NoneType]
            args = get_args(python_type)
            if len(args) == 2 and type(None) in args:
                non_none_type = args[0] if args[1] is type(None) else args[1]
                return JSONSchemaGenerator.type_to_json_type(non_none_type)
        return 'unknown'


if __name__ == '__main__':

    # Example usage:
    class User(typing.NamedTuple):

        name: str
        email: str
        _required = ['name', 'email']
        _name_description = 'The name of the user'
        _email_description = 'The email address of the user'


    class Comment(typing.NamedTuple):
        text: str
        user: User
        _required = ['text', 'user']
        _text_description = 'The text of the comment'
        _user_description = 'The user who made the comment'
        _schema_description = 'A comment'


    comment = Comment('Hello', User('John Doe', '_`   `'))
    schema_generator = JSONSchemaGenerator(comment.__class__)
    print(schema_generator.generate())
