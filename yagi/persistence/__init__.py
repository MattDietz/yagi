import yagi.config
import yagi.utils

def persistence_driver():
    driver = yagi.config.get('persistence', 'driver')
    return yagi.utils.import_class(driver)()

