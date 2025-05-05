""" Docstring for the computed_property_decorator module.

Example usage:
- @computed_property
  def get_price(self):
      return self._price * self.tax_rate

- @computed_property("price", "tax_rate")
  def get_price_with_discount(self):
      return self._price * self.tax_rate * (1 - self.discount_rate)
"""
from .computed_property import ComputedProperty


def computed_property(*args):
    """
    A decorator to define a computed property for a class.

    This decorator can be used in two ways:
    1. Without arguments, in which case it is used to define a computed property with just a getter.
    2. With arguments, allowing additional dependencies to be specified for the computed property.

    Args:
        *args:
            - If one argument is provided, and it is callable, it is treated as the getter function.
            - If multiple arguments are provided, they are treated as dependencies for the computed property.

    Returns:
        - If used without arguments, it returns an instance of `ComputedProperty` with the provided getter.
        - If used with arguments, it returns a wrapper function that accepts a getter and returns an instance of `ComputedProperty` with the specified dependencies and getter.
    """
    # Case: @computed_property used without arguments
    if len(args) == 1 and callable(args[0]):
        return ComputedProperty(fget=args[0])
    else:
        # Case: @computed_property(...) used with arguments
        def wrapper(fget):
            return ComputedProperty(*args, fget=fget)
        return wrapper
