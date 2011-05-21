import yagi.config
import yagi.utils

yagi.config.defaults('persistence', 'driver', 'yagi.persistence.redis_driver.Driver')

def persistence_driver():
    driver = yagi.config.get('persistence', 'driver')
    return yagi.utils.import_class(driver)()


class Driver(object):
    def create(self, key, value):
        raise NotImplementedError

    def get(self, key, entity_id):
        raise NotImplementedError

    def get_all(self):
        raise NotImplementedError

    def get_all_of_type(self, key):
        raise NotImplementedError
