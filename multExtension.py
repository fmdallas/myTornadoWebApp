# multiple inheritance practice

def get_valid_input(input_string, valid_options):
    input_string += "({})".format(",".join(valid_options))
    response = input(input_string)
    while response.lower() not in valid_options:
        response = input(input_string)
    return response


class Property(object):
    def __init__(self, square_feet='', beds='', baths='', **kwargs):
        super(Property, self).__init__()
        self.square_feet = square_feet
        self.num_bedrooms = beds
        self.num_baths = baths

    def display(self):
        print "PROPERTY DETAILS"
        print "=" * 10
        print "square footage: {}".format(self.square_feet)
        print "bedrooms: {}".format(self.num_bedrooms)
        print "bathrooms: {}".format(self.num_baths)

    def prompt_init():
        return dict(square_feet=input("Enter the square feet: "),
                    beds=input("Enter number of bedrooms: "),
                    baths=input("Enter number of baths: "))

    prompt_init = staticmethod(prompt_init)


class Apartment(Property):
    valid_laundries = ('coin', 'ensuite', "none")
    valid_balconies = ("yes", "no", "solariums")

    def __init__(self, balcony='', laundry='', **kwargs):
        super(Apartment, self).__init__(**kwargs)
        self.balcony = balcony
        self.laundry = laundry

    def display(self):
        super(Apartment, self).display()
        print "APARTMENT DETAILS"
        print "laundry: %s " % self.laundry
        print "balcony: %s " % self.balcony

    def prompt_init():
        parent_init = Property.prompt_init()
        laundry = get_valid_input("What laundry facilities does the property have?", Apartment.valid_laundries)
        balcony = get_valid_input("Does the property hava a balcony? ", Apartment.valid_balconies)
        parent_init.update({'laundry': laundry, 'balcony': balcony})
        return parent_init

    prompt_init = staticmethod(prompt_init)


class House(Property):
    valid_garage = ("attached", "detach", "none")
    valid_fenced = ("yes", "no")

    def __init__(self, num_stories='', garage='', fenced='', **kwargs):
        super(House, self).__init__(**kwargs)
        self.num_stories = num_stories
        self.garage = garage
        self.fenced = fenced

    def display(self):
        super(House, self).display()
        print "HOUSE DETAILS"
        print "# of stories: {}".format(self.num_stories)
        print "garage: {}".format(self.garage)
        print "fenced: {}".format(self.fenced)

    def prompt_init():
        parent_init = Property.prompt_init()
        fenced = get_valid_input("Is the yard fenced?", House.valid_fenced)
        garage = get_valid_input("Is there a garage?", House.valid_garage)
        num_stories = input('How many stories?')

        parent_init.update({'fenced': fenced, 'garage': garage, 'num_stories': num_stories})
        return parent_init

    prompt_init = staticmethod(prompt_init)


class Purchase(object):
    def __init__(self, price='', taxes='', **kwargs):
        super(Purchase, self).__init__(**kwargs)
        self.price = price
        self.taxes = taxes

    def display(self):
        super(Purchase, self).display()
        print "PURCHASE DETAILS"
        print "selling price: {}".format(self.price)
        print "estimated taxes:{}".format(self.taxes)

    def prompt_init():
        return dict(
            price=input("what's the selling price?"),
            taxes=input("what are the estimated taxes?")
        )

    prompt_init = staticmethod(prompt_init)


class Rental(object):
    def __init__(self, furnished='', rent='', utilities='', **kwargs):
        super(Rental, self).__init__(**kwargs)
        self.furnished = furnished
        self.rent = rent
        self.utilities = utilities

    def display(self):
        super(Rental, self).display()
        print "RENTAL DETAILS"
        print "rent: {}".format(self.rent)
        print "furnished: {}".format(self.furnished)
        print "utilities: {}".format(self.utilities)

    def prompt_init():
        return dict(
            rent=input("what's the monthly rent?"),
            utilites=input("what are the estimated utilities?"),
            furnished=get_valid_input("Is the property furnished?", ("yes", 'no'))
        )

    prompt_init = staticmethod(prompt_init)


class HouseRental(Rental,House):
    def prompt_init():
        init = House.prompt_init()
        init.update(Rental.prompt_init())
        print "here is init ",init
        return init
    prompt_init = staticmethod(prompt_init)

if __name__=='__main__':
    init = HouseRental.prompt_init()
    house = HouseRental(**init)
    house.display()













