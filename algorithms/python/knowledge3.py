from lxml import html

class Failure(Exception):
    pass

class Borg(object):
    _shared_state = {}
    def __new__(cls, *a, **k):
        obj = object.__new__(cls, *a, **k)
        obj.__dict__ = cls._shared_state
        return obj

    def __hash__(self):
        return 42 # randomly chosen number from a dice with one face

    def __eq__(self, other):
        try:
            return self.__dict__ is other.__dict__
        except AttributeError:
            return False

def name_getter(question):
    def _list_of(url):
        parser = html.parse(url)
        return [el.text for el in parser.xpath('//td/table/tr/td[1]')
                if el.text]
    url_db = dict(
        male_names='http://names.mongabay.com/male_names.htm',
        female_names='http://names.mongabay.com/female_names.htm',
        surnames='http://names.mongabay.com/most_common_surnames.htm'
    )
    try:
        url = url_db[question]
    except KeyError:
        raise Failure
    return _list_of(url)

class Knowledge(Borg):
    # (question, fetcher)
    find_answer = dict(
        male_names=name_getter,
        female_names=name_getter,
        surnames=name_getter
    )

    def __getattr__(self, key):
        try:
            finder = self.find_answer[key]
        except KeyError:
            raise Failure
        value = finder(key)
        setattr(self, key, value)
        return value

    @property
    def known_questions(self):
        return self.find_answer.keys()