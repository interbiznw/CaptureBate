class CBModel:
    'ChaturBate Model'
    name = ''
    gender = 'unknown'

    def __init__(self, name, gender):
        self.name = name
        self.gender = gender

    def __repr__(self):
        return '{} ({})'.format(self.name, self.gender)

    def __eq__(self, other):
        return self.name == other.name
