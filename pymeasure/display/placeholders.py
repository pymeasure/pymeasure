import string
import re

from datetime import datetime

builtin_placeholders = {'time' : lambda: datetime.now().strftime('%Hh%Mm%Ss'),
                        'date' : lambda: datetime.now().strftime('%y.%m.%d'),
                        }

class PlaceholderReplacer():
    def __init__(self, placeholder_dict = {}):

        self.placeholders = {**builtin_placeholders, **placeholder_dict}
        self.pattern = r'\<.*?\>'
    
    def translate_string(self, string):
        modified_string = string
        matches = re.findall(self.pattern, string)

        for match in matches:
            striped_match = match[1:-1]
            if striped_match in self.placeholders:

                placeholder = self.placeholders[striped_match]
                if callable(placeholder):
                    placeholder = placeholder()

            modified_string = modified_string.replace(match, placeholder)

        return modified_string
