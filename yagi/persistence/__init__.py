import yagi.config
import yagi.utils

yagi.config.defaults('persistence',
                     'driver',
                     'yagi.persistence.devnull.Driver')


class InvalidEntityUUID(KeyError):
    pass


def persistence_driver():
    driver = yagi.config.get('persistence', 'driver')
    return yagi.utils.import_class(driver)()


class Driver(object):
    def create(self, key, entity_uuid, value):
        pass

    def get(self, key, entity_uuid):
        return []

    def get_all(self):
        return []

    def get_all_of_type(self, key):
        return []

    def count(self, type_key=None):
        return 1

    def pages(self, pagesize, length):
        if not pagesize:
            return 1
        pages = (length // pagesize) + 1 if length % pagesize \
                                         else length // pagesize
        return pages if pages >= 1 else 1
