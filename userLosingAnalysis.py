import sys
from operator import attrgetter


def average(seq):
    assert len(seq) != 0
    seq = [x if isinstance(x, (int, float)) else 0 for x in seq]
    return sum(seq) * 1.0 / len(seq)


def distribution(seq):
    distributions = dict()
    for val in seq:
        distributions[val] = distributions.get(seq, 0) + 1
    return distributions


class Record(object):
    """record of users"""


class AppUser(Record):
    """application users"""

    def __str__(self):
        return str(self.__dict__)


class Table(object):
    """records list"""

    def __init__(self):
        self.records = []

    def __len__(self):
        return len(self.records)

    def read_file(self, filePath, fields, cls, n=20):
        import csv

        try:
            # fp = open(filePath)
            fp = csv.reader(open(filePath))
        except:
            print "File path: %s doesn't exist..." % filePath
            sys.exit(0)

        for idx, line in enumerate(fp):
            if idx == n:
                break
            record = self.make_record(line, fields, cls)
            self.add_record(record)
            # fp.close()

    def make_record(self, line, fields, cls):
        obj = cls()
        for (fieldName, idx, type_) in fields:
            try:
                fieldValue = type_(line[idx])
            except:
                fieldValue = 'NA'
            setattr(obj, fieldName, fieldValue)
        return obj

    def add_record(self, record):
        self.records.append(record)

    def extend_record(self, records):
        self.records.extend(records)

    def recode(self):
        """override this method in subclass"""
        pass

    def get_average(self, field):
        records = [getattr(record, field) for record in self.records]
        return average(records)

    def get_distribution(self, field):
        records = [getattr(record, field) for record in self.records]
        return distribution(records)

    def get_bisect_records(self, field, left=True):  #return left bisect data on default
        sortedRecords = self.get_sorted_records(field)
        index = len(sortedRecords) / 2
        if left:
            return sortedRecords[:index]
        return sortedRecords[index:]

    # ref: https://wiki.python.org/moin/HowTo/Sorting
    def get_sorted_records(self, field, reverse=True):
        return sorted(self.records, key=attrgetter(field), reverse=reverse)

    def get_multiple_sorted_records(self, fields, reverse=True):
        return sorted(self.records, key=attrgetter(*fields), reverse=reverse)


class AppUsers(Table):
    """the application user table"""

    def __init__(self, filePath, fields, cls=AppUser):
        super(AppUsers, self).__init__()
        self.read_file(filePath, fields, cls)

    def get_user_upper(self, field):
        averageValue = self.get_average(field)
        return [obj for obj in self.records if getattr(obj, field) > averageValue]

    def get_user_lower(self, field):
        averageValue = self.get_average(field)
        return [obj for obj in self.records if getattr(obj, field) < averageValue]

    def get_user_models(self, fields, combinations):
        fclist = []
        for field, combination in zip(fields, combinations):
            if combination == 'lower':
                fieldCombin = self.get_user_lower(field)
                fclist.append(fieldCombin)
            elif combination == 'upper':
                fieldCombin = self.get_user_upper(field)
                fclist.append(fieldCombin)
            else:
                raise ValueError('Chose <upper> or <lower>')
        return reduce(lambda x, y: set(x) & set(y), fclist)


def main():
    filepath = 'userfeed.csv'
    fields = [('uid', 0, int), ('freq', 7, str), ('workyear', 6, float), ('time', 5, int)]
    app2 = AppUsers(filepath, fields)

    for item in app2.get_user_models(['freq', 'time', 'uid'], ['upper', 'lower', 'upper']):
        print item

    print "*" * 20

    for item in app2.get_multiple_sorted_records(['freq', 'time', 'uid']):
        print item


if __name__ == '__main__':
    main()