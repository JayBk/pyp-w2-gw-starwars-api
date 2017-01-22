from starwars_api.client import SWAPIClient
from starwars_api.exceptions import SWAPIClientError

# from client import *
# from exceptions import *
# from settings import *

import re

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
        fn = 'get_{}'.format(cls.RESOURCE_NAME) # get_people()
        json_data = getattr(api_client, fn)(resource_id)
        return cls(json_data)

    @classmethod
    def all(cls):
        """
        Returns an iterable QuerySet of current Model. The QuerySet will be
        later in charge of performing requests to SWAPI for each of the
        pages while looping.
        """
        return eval("{}QuerySet()".format(cls.RESOURCE_NAME.title()))
        

        
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
        self.page_number = 1
        self.item_number = 0
        self.objects = self._get_page(self.page_number)
        
        
    def _get_page(self, page_num):
        page_form = "?page={}".format(page_num)
        print(page_form)
        # fn = 'get_{}'.format(cls.RESOURCE_NAME) # get_people
        fn = 'get_people'
        json_data = getattr(api_client, fn)(page_form) #json data
        print(json_data)
        return json_data
            
    
    def __iter__(self):
        self.page_number = 1
        self.item_number = 0
        return self
        
    def __next__(self):
        """
        Must handle requests to next pages in SWAPI when objects in the current
        page were all consumed.
        """
        
        last_page = False
        
        if not last_page: # page check
            print('page: ', self.page_number)
            
            if self.item_number < len(self.objects['results']): # item check
                print('item: ', self.item_number)
                x = self.objects['results'][self.item_number]
                self.item_number += 1
                return People(x)
                
            # get next page:
            try:
                self.page_number = re.compile('\d+$').findall(self.objects['next'])[-1]
                print('Getting next page: ', self.page_number)
                self.objects = self._get_page(self.page_number)
                self.item_number = 0 # Reset item count on new page
            except:
                raise StopIteration
        else:
            raise StopIteration
        
    next = __next__


    def count(self):
        """
        Returns the total count of objects of current model.
        If the counter is not persisted as a QuerySet instance attr,
        a new request is performed to the API in order to get it.
        """
        return self.objects['count']


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


if __name__ == '__main__':
    
    qs = People.all()
    print('----')
    print(len([elem for elem in qs]))
