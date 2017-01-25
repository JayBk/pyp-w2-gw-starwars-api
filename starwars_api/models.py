from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

api_client = SWAPIClient()


class BaseModel(object):

    def __init__(self, json_data):
        """
        Dynamically assign all attributes in `json_data` as instance
        attributes of the Model.
        """
        for key, value in json_data.items():
            setattr(self, key, value)

    @classmethod
    def get(cls, resource_id):
        """
        Returns an object of current Model requesting data to SWAPI using
        the api_client.
        """
        func = 'get_{}'.format(cls.RESOURCE_NAME)
        json_data = getattr(api_client, func)(resource_id)
        return cls(json_data)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        query = '{}QuerySet'.format(cls.__name__)  #cls.__name__ == either "People" or "Films", so instead of doing cls.RESOURCE_NAME.title() we can use this... 
        return eval(query)()                       # RESOURCE_NAME == "people" or "films" to you'd have to do .tile() and make the first letter capital to get the actual class name.
                                      

class People(BaseModel):
    """Representing a single person"""
    RESOURCE_NAME = 'people'

    def __init__(self, json_data):
        super(People, self).__init__(json_data)

    def __repr__(self):
        return 'Person: {0}'.format(self.name)


class Films(BaseModel):
    RESOURCE_NAME = 'films'

    def __init__(self, json_data):
        super(Films, self).__init__(json_data)

    def __repr__(self):
        return 'Film: {0}'.format(self.title)


class BaseQuerySet(object):

    def __init__(self):
        self.objects = []        
        self.page, self.counter = 0, 0  # We need to +1 to self.counter when checking it with len(self.objects). Otherwise it will be > because we are always adding 1 it at the end of the while loop, and then checking it before we add another 
        self.for_count = None

    def __iter__(self):
        return self

    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        while self:  # (while True)
            if self.counter+1 > len(self.objects):  # We need to check if we +1 to self.element that if it is > the length of self.object, we try to get the next page, but except the apierror, and
                try: # if we do end up getting an error, stop the iteration. I don't think we were handline the errors right before :/
                    self.get_next_page()
                except SWAPIClientError:
                    raise StopIteration()
            elem = self.objects[self.counter]
            self.counter += 1
            return elem

    def get_next_page(self):
        self.page += 1
        next_page = 'get_{}'.format(self.RESOURCE_NAME)
        json_data = getattr(api_client, next_page)(page=self.page)
        self.no_inst_results = json_data['results']
        self.for_count = json_data['count']  # We can use this For the count() function or use return len([item for item in self])
        make_obj  = eval(self.RESOURCE_NAME.title())  # Easiest way is to use the RESOURCE_NAME and make the first letter capital which will make it People() or Films(), 
        for data in json_data['results']:           # Here we iterate through json_data['results'] taking each entry and appending it to a list, and while we do that, we instantiate it so that
            inst_data = make_obj(data)          # This is what I meant when we first started to save 
            self.objects.append(inst_data)  # this way we will not get the AttributeError like we were before, because now were going through everything in results and calling People(data) or Films(data) on it so that it ends up having the attributes...

    next = __next__

    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        # literally just have to do EXACTLY what it says above^^^...
        if not self.for_count:  #  If the counter is not persisted as a QuerySet instance attr,
            self.get_next_page()  # a new request is performed to the API in order to get it.
        return self.for_count  #  Returns the total count of objects of current model.
        # or we can do: return len([item for item in self])


class PeopleQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'people'

    def __init__(self):
        super(PeopleQuerySet, self).__init__()

    def __repr__(self):
        return 'PeopleQuerySet: {0} objects'.format(str(len(self.objects)))


class FilmsQuerySet(BaseQuerySet):
    RESOURCE_NAME = 'films'

    def __init__(self):
        super(FilmsQuerySet, self).__init__()

    def __repr__(self):
        return 'FilmsQuerySet: {0} objects'.format(str(len(self.objects)))
