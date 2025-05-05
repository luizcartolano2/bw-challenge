from computed import computed_property


class Circle:
    def __init__(self, radius=1):
        self.radius = radius

    @computed_property('radius')
    def diameter(self):
        print("computing diameter...")
        return self.radius * 2

    @diameter.setter
    def diameter(self, value):
        self.radius = value / 2

    @diameter.deleter
    def diameter(self):
        self.radius = 0

    @computed_property('radius')
    def area(self):
        print("computing area...")
        return 3.1415 * self.radius ** 2


if __name__ == '__main__':
    circle = Circle()
    print(circle.diameter)
    print(circle.diameter)

    circle.diameter = 3
    print(circle.radius)
    print(circle.diameter)

    del circle.diameter
    print(circle.radius)

    print(circle.diameter)


    # c = Circle(3)
    # print(c.area)  # computes and caches
    # print(c.area)  # cached
    # c.radius = 4  # invalidates cache
    # print(c.area)  # recomputes
