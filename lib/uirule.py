import json


# ============== CLAUSES ==============
# Define the Clause class to represent a clause containing a condition and a property type
class Clause:
    def __init__(self, condition, property_type):
        self.condition = condition          # Condition associated with the clause
        self.property_type = property_type  # Property type (like CSS or Properties)

    # Convert the Clause object to a dictionary
    def as_dict(self):
        return {
            "condition": self.condition.as_dict(),
            "action": {
                self.property_type.as_dict()['kind']: self.property_type.as_dict()['value']
            }
        }

    def as_list(self):
        return [self.as_dict()]

    # Convert the Clause object to JSON format
    def as_json(self):
        return json.dumps(self.as_dict(), indent=3)

    # Overload the '&' operator to create an AND clause
    def __and__(self, other):
        return AndClause(self, other)


class AndClause():
    def __init__(self, *args):
        self.args = args

    # Convert the AndClause object to a combined dictionary
    def as_dict(self):
        combined_list = []
        for arg in self.args:

            if isinstance(arg, AndClause):
                for a in arg.as_dict():
                    combined_list.append(a)
            elif isinstance(arg, Clause):
                combined_list.append(arg.as_dict())

        return combined_list

    def as_list(self):
        # In fact, as_dict is a list
        return self.as_dict()

    def as_json(self):
        return json.dumps(self.as_dict(), indent=3)

    def __and__(self, other):
        return AndClause(self, other)


# ============== CONDITIONS ==============
# Define the Condition class to represent a condition in the query
class Condition:
    def __init__(self, kind, field, value):
        self.field = field
        self.kind = kind
        self.value = value

    # Convert the Condition object to a dictionary
    def as_dict(self):
        return {
            self.field: {
                "kind": self.kind,
                "value": self.value,
            }
        }

    # Overload the '&' operator to create an AND condition
    def __and__(self, other):
        return AndCondition(self, other)

    # Overload the '|' operator to create an OR condition
    def __or__(self, other):
        return OrCondition(self, other)


class AndCondition():
    def __init__(self, *args):
        self.args = args

    # Convert the AndCondition object to a combined dictionary
    def as_dict(self):
        combined_dict = {"operand": "AND"}
        for arg in self.args:
            combined_dict.update(arg.as_dict())
        return combined_dict


class OrCondition():
    def __init__(self, *args):
        self.args = args

    # Convert the OrCondition object to a combined dictionary
    def as_dict(self):
        combined_dict = {"operand": "OR"}
        for arg in self.args:
            combined_dict.update(arg.as_dict())
        return combined_dict


# ============== CONDITION TYPES ==============
# Define specific types of conditions
class Exact(Condition):
    def __init__(self, field, value):
        super().__init__("exact", field, value)


class In(Condition):
    def __init__(self, field, value):
        super().__init__("in", field, value)


class Not(Condition):
    def __init__(self, field, value):
        super().__init__("not", field, value)


# ============== EFFECTS ==============
# Define specific effects (Css and Property)
class Css:
    def __init__(self, effect, action):
        self.effect = effect  # Effect associated with the CSS
        self.action = action

    # Convert the Css object to a dictionary
    def as_dict(self):
        return {
            "kind": "css",
            "value": {
                self.effect: self.action
            }
        }


class Property:
    def __init__(self, effect, action):
        self.effect = effect
        self.action = action

    # Convert the Property object to a dictionary
    def as_dict(self):
        return {
            "kind": "property",
            "value": {
                self.effect: self.action
            }
        }


class Value:
    def __init__(self, target, target_value):
        self.target = target
        self.target_value = target_value

    # Convert the Property object to a dictionary
    def as_dict(self):
        return {
            "kind": "value",
            "value": {
                self.target: self.target_value
            }
        }
