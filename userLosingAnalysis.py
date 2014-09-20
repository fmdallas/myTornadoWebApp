
import sys
import bisect


def average(seq):
    assert len(seq) != 0
    return sum(seq) / len(seq)


def distribution(seq):
    distributions = dict()
    for val in seq:
        distributions[val] = distributions.get(seq, 0) + 1
    return distributions


class Record(object):
    """record of users"""


class AppUser(Record):
    """application users"""


class Table(object):
    """records list"""

    def __init__(self):
        self.records = []

    def __len__(self):
        return len(self.records)

    def read_file(self, filePath, fields, cls, n=None):
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
                fieldValue = 0  #'NA'
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
        val = getattr(self.records[0], field)
        if not isinstance(val, (int, float)):
            raise TypeError('field %s is not valid type' % field)
        records = [getattr(record, field) for record in self.records]
        print average(records),'here'
        return average(records)

    def get_distribution(self, field):
        records = [getattr(record, field) for record in self.records]
        return distribution(records)

    def get_sorted_records(self, field, reverse=True):  #descending order on default
        records = [(getattr(record, field), record) for record in self.records]
        records.sort()
        if reverse:
            records.reverse()
        return records

    def _get_bisect_index(self, field):  #get bisect index of field
        value = self.get_average(field)
        records = self.get_sorted_records(field)
        recordsValueSeq = [val for val, record in records]
        index = bisect.bisect(recordsValueSeq, value)
        return index

    def get_bisect_records(self, field, left=True):  #return left bisect data on default
        sortedRecords = self.get_sorted_records(field)
        index = self._get_bisect_index(field)
        # print "-->",sortedRecords[:index]
        if left:
            return sortedRecords[:index]
        return sortedRecords[index:]


class AppUsers(Table):
    """the application user table"""

    def __init__(self, filePath, fields, cls=AppUser):
        super(AppUsers, self).__init__()
        self.read_file(filePath, fields, cls)

    def separate_user_group(self, fields):  #fields list to separate user to different groups
        self.userGroups = dict()
        for field in fields:
            self.userGroups.setdefault(field, {})
            lower = self.get_bisect_records(field)  #val,object
            upper = self.get_bisect_records(field, False)  #val,object
            self.userGroups[field]['lower'] = lower
            self.userGroups[field]['upper'] = upper
        return self.userGroups

    def get_user_model(self, fields, combination):  # combination sequence of 'lower', 'upper'
        # usage : fields = ['access_time','freq','feeds']| combination = ['lower','upper','lower']
        userModelList = []
        fieldTypeList = zip(fields, combination)
        userGroups = self.separate_user_group(fields)
        for field, type_ in fieldTypeList:
            userModelList.append(userGroups[field].get(type_, None))
        return reduce(lambda x, y: set(x).intersection(set(y)), userModelList)


def main():
    filepath = 'userfeed.csv'
    fields = [('uid', 0, str), ('freq', 0, int), ('workyear', 6, float), ('time', 5, int)]

    app2 = AppUsers(filepath, fields)
    print app2.separate_user_group(['workyear'])['workyear']['lower']
    # print app2.get_user_model(['freq', 'workyear', 'time'], ['upper', 'upper', 'lower'])


if __name__ == '__main__':
    main()














