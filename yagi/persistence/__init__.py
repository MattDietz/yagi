import yagi.config
import yagi.utils

yagi.config.defaults('persistence', 'driver', 'yagi.persistence.devnull.Driver')

def persistence_driver():
    driver = yagi.config.get('persistence', 'driver')
    return yagi.utils.import_class(driver)()


class Driver(object):
    def create(self, key, entity_uuid, value):
        pass

    def get(self, key, entity_uuid):
        pass

    def get_all(self):
        pass

    def get_all_of_type(self, key):
        pass
