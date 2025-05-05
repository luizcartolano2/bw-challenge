"""Computed property descriptor with dependency tracking and caching.

This module provides a `ComputedProperty` descriptor class that implements computed
properties with the following features:
- Automatic caching of computed values
- Dependency tracking (invalidates cache when dependencies change)
- Support for getters, setters, and deleters
- Proper documentation inheritance

The descriptor is designed to be used as a decorator similar to Python's built-in
@property, but with additional functionality for managing dependencies between
properties.
"""


class ComputedProperty:
    """
    A descriptor for computed properties with support for caching, dependencies, and setters/getters.

    Attributes:
        dependencies (tuple): A tuple of attributes that this computed property depends on.
        func_get (callable): The getter function for the computed property.
        func_set (callable): The setter function for the computed property.
        func_del (callable): The deleter function for the computed property.
        __doc__ (str): The documentation string for the computed property.
    """
    def __init__(self, *dependencies, fget=None, fset=None, fdel=None, doc=None):
        """
        Initialize the computed property.

        Args:
            *dependencies (str): The names of attributes this property depends on.
            func_get (callable, optional): The function to get the computed property value.
            func_set (callable, optional): The function to set the computed property value.
            func_del (callable, optional): The function to delete the computed property.
            doc (str, optional): Documentation for the computed property.

        """
        self.dependencies = dependencies
        self.func_get = fget
        self.func_set = fset
        self.func_del = fdel
        self.__doc__ = doc if doc else (fget.__doc__ if fget else None)

    def __set_name__(self, owner, name):
        """
        Set the name of the computed property and register its dependencies.

        This method is called when the computed property is assigned to a class.
        It also sets up a cache for the computed property and ensures that the
        `__setattr__` method is overridden to clear cached values when dependencies change.

        Args:
            owner (type): The owner class where the computed property is defined.
            name (str): The name of the computed property.
        """
        self.__name__ = name
        self._cache_name = f"__cached_{name}"

        # Register computed property dependencies
        if not hasattr(owner, "__computed_dependency_map__"):
            owner.__computed_dependency_map__ = {}

        for dep in self.dependencies:
            owner.__computed_dependency_map__.setdefault(dep, []).append(name)

        # Override __setattr__ to handle changes to dependent attributes
        if not hasattr(owner, "__wrap_computed_setattr__"):
            original_setattr = owner.__setattr__

            def custom_setattr(obj, key, value):
                original_setattr(obj, key, value)
                affected = obj.__class__.__computed_dependency_map__.get(key, [])
                for attr in affected:
                    cache_name = f"__cached_{attr}"
                    if hasattr(obj, cache_name):
                        delattr(obj, cache_name)

            owner.__setattr__ = custom_setattr
            owner.__wrap_computed_setattr__ = True

    def __get__(self, obj, objtype=None):
        """
        Get the value of the computed property.

        If the value has already been computed and cached, return the cached value.
        Otherwise, compute the value using the getter function and cache it.

        Args:
            obj (object): The object that owns the computed property.
            objtype (type, optional): The class of the object.

        Returns:
            The computed value of the property.

        Raises:
            AttributeError: If there is no getter function for this property.
        """
        if obj is None:
            return self
        if self.func_get is None:
            raise AttributeError(f"No getter for {self.__name__}")
        if hasattr(obj, self._cache_name):
            return getattr(obj, self._cache_name)
        result = self.func_get(obj)
        setattr(obj, self._cache_name, result)
        return result

    def __set__(self, obj, value):
        """
        Set the value of the computed property.

        This method invokes the setter function and clears the cached value.

        Args:
            obj (object): The object that owns the computed property.
            value (any): The value to set.

        Raises:
            AttributeError: If there is no setter function for this property.
        """
        if self.func_set is None:
            raise AttributeError(f"No setter for {self.__name__}")
        self.func_set(obj, value)
        if hasattr(obj, self._cache_name):
            delattr(obj, self._cache_name)

    def __delete__(self, obj):
        """
        Delete the computed property.

        This method invokes the deleter function and removes the cached value.

        Args:
            obj (object): The object that owns the computed property.

        Raises:
            AttributeError: If there is no deleter function for this property.
        """
        if self.func_del is None:
            raise AttributeError(f"No deleter for {self.__name__}")
        self.func_del(obj)
        if hasattr(obj, self._cache_name):
            delattr(obj, self._cache_name)

    def getter(self, fget):
        """
        Set the getter function for the computed property.

        Args:
            fget (callable): The function to get the computed property value.

        Returns:
            ComputedProperty: A new instance of the computed property with the updated getter.
        """
        return ComputedProperty(*self.dependencies, fget=fget, fset=self.func_set, fdel=self.func_del, doc=self.__doc__)

    def setter(self, fset):
        """
        Set the setter function for the computed property.

        Args:
            fset (callable): The function to set the computed property value.

        Returns:
            ComputedProperty: A new instance of the computed property with the updated setter.
        """
        return ComputedProperty(*self.dependencies, fget=self.func_get, fset=fset, fdel=self.func_del, doc=self.__doc__)

    def deleter(self, fdel):
        """
        Set the deleter function for the computed property.

        Args:
            fdel (callable): The function to delete the computed property.

        Returns:
            ComputedProperty: A new instance of the computed property with the updated deleter.
        """
        return ComputedProperty(*self.dependencies, fget=self.func_get, fset=self.func_set, fdel=fdel, doc=self.__doc__)
