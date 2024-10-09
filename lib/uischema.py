from pydantic import BaseModel
from lib.uifields import UIField

import logging
logger = logging.getLogger('django')


# Extend Base model
class UISchemaBaseModel(BaseModel):

    @staticmethod
    def layout():
        return [[]]

    @staticmethod
    def note():
        return None

    @classmethod
    def get_base_ui_element(cls, field_name):
        # Creates and returns a basic UI element.
        return {
            "type": "Control",
            "scope": f"#/properties/{field_name}",
        }

    @classmethod
    def get_base_ui_row(cls):
        # Creates and returns a basic UI element.
        return {
            "type": "HorizontalLayout",
            "elements": [],
        }

    @classmethod
    def add_custom_ui_elements(cls):
        # Adds custom UI elements based on model fields
        elements = {}
        for field_name, field in cls.model_fields.items():
            element = cls.get_base_ui_element(field_name)
            if isinstance(field.default_factory, UIField):
                element.update(field.default_factory.generate_field_ui_schema())
            elements[field_name] = element
        return elements

    @classmethod
    def apply_layout_config(cls, elements):
        # Applies layout configuration to the model layout.
        model_layout = {"type": "VerticalLayout", "elements": []}
        layout = cls.layout()

        editable_elements = {}

        if layout is None:
            model_layout["elements"].append(cls.get_base_ui_row())
        elif layout != [[]]:
            for layout_row in layout:
                row = cls.get_base_ui_row()
                for layout_element in layout_row:
                    row["elements"].append(elements[layout_element])

                    layout_element_is_editable = elements[layout_element]['options']['editable']
                    editable_elements[layout_element] = layout_element_is_editable

                model_layout["elements"].append(row)
        else:
            row = cls.get_base_ui_row()
            row['elements'] = [element for element in elements.values() if element['scope'] != '#/properties/prompt']
            model_layout["elements"].append(row)

        if cls.note():
            model_layout['note'] = cls.note()

        model_layout['editable_elements'] = editable_elements

        return model_layout

    @classmethod
    def model_ui_schema(cls):
        # Generates the UI schema for the model.
        elements = cls.add_custom_ui_elements()
        return cls.apply_layout_config(elements)
