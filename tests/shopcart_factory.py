"""
Test Factory to make fake objects for testing
"""
import factory
from factory.fuzzy import FuzzyChoice
from service.models import Shopcart

class ShopcartFactory(factory.Factory):
    class Meta:
        model = Shopcart
    id = factory.Sequence(lambda n: n)
    '''product_id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    '''
    product_id = FuzzyChoice(choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    customer_id = FuzzyChoice(choices=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20])
    quantity = factory.Sequence(lambda n: n)
    price = factory.Sequence(lambda n: n)
    text = factory.Faker('first_name')
    state = FuzzyChoice(choices=[0,1,2])

if __name__ == '__main__':
    for _ in range(10):
        shopcart = ShopcartFactory()
        print(shopcart.serialize())