import string
import re

from datetime import datetime

builtin_placeholders = {'time' : lambda: datetime.now().strftime('%Hh%Mm%Ss'),
                        'date' : lambda: datetime.now().strftime('%y.%m.%d'),
                        }

class PlaceholderReplacer():
    """ Allows to replace sequence of characters in a string with information
    or experiment values.

    :param inputs: Reference ti the input widget
    """

    def __init__(self, inputs):
        
        self.pattern = r'\<.*?\>'
        self.inputs = inputs

        input_placeholders = self.generate_inputs_placeholders()
        self.placeholders = {**builtin_placeholders, **input_placeholders}


    def get_value(self, name):
        return str(self.inputs.get_value(name))

    def generate_inputs_placeholders(self):
        input_placeholders = self.inputs.get_placeholders()

        returned_placeholders = {}

        for placeholder in input_placeholders:
            name = input_placeholders[placeholder]
            returned_placeholders[placeholder] = lambda x=name: self.get_value(str(x))

        return returned_placeholders


    def translate_string(self, string):
        modified_string = string
        matches = re.findall(self.pattern, string)

        print(f'Matches : {matches}')

        # Look for matches using the defined pattern
        for match in matches:
            striped_match = match[1:-1]
            print('Found')
            print(f'\tMatch : {striped_match}')
            
            if striped_match in self.placeholders:
                placeholder = self.placeholders[striped_match]
                print(f'\tPlaceholder : {placeholder}')
                if callable(placeholder):
                    placeholder = str(placeholder())

                print(f'\tPlaceholder : {placeholder}')

            modified_string = modified_string.replace(match, placeholder)

        return modified_string
