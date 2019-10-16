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
    product_id = factory.Sequence(lambda n: n)
    customer_id = factory.Sequence(lambda n: n)
    quantity = factory.Sequence(lambda n: n)
    price = factory.Sequence(lambda n: n)
    text = factory.Faker('first_name')
    state = FuzzyChoice(choices=[0])

if __name__ == '__main__':
    for _ in range(10):
        shopcart = ShopcartFactory()
        print(shopcart.serialize())