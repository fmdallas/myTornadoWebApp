import sys
import time
from operator import attrgetter



TIMENOW = time.time()
# ref: http://blog.csdn.net/longshenlmj/article/details/13627537
def timeProcess(timeStr,ISOFORMAT="%Y-%m-%d %H:%M:%S"):
    structa = time.strptime(timeStr,ISOFORMAT) # STRUCT_TIME:(tm_year=2011, tm_mon=9, tm_mday=27, tm_hour=10, tm_min=50, tm_sec=0, tm_wday=1, tm_yday=270, tm_isdst=-1)
    stampa = time.mktime(structa) # timestamp
    return TIMENOW - stampa


def average(seq):
    assert len(seq) != 0
    seq = [x if isinstance(x, (int, float)) else 0 for x in seq]
    return sum(seq) * 1.0 / len(seq)


def distribution(seq):
    distributions = dict()
    for val in seq:
        distributions[val] = distributions.get(val, 0) + 1
    return distributions


lessThan = lambda x, y: x < y
setIntersection = lambda x, y: set(x) & set(y)


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
                fieldValue = 'NA'
            setattr(obj, fieldName, fieldValue)
        return obj

    def add_record(self, record):
        self.records.append(record)

    def extend_record(self, records):
        self.records.extend(records)

    def get_records(self):
        return self.records

    def set_records(self, records):
        self.records = records

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

    def get_split_user_by_mean(self, field):
        averageValue = self.get_average(field)
        records = self.get_sorted_records(field)
        upper, lower = [], []
        for record in records:
            (upper, lower)[lessThan(getattr(record, field), averageValue)].append(record)
        return upper, lower

    def get_split_users_by_mean(self, fields):
        # upper,lower list of fields
        # result: [(field1_upper,field1_lower),(field2_upper,field2_lower),...]
        upperLowerList = list()
        for field in fields:
            upperLowerList.append(self.get_split_user_by_mean(field))
        return upperLowerList

    def get_users_models(self, fields, combinations):
        UPPERLOWERDICT = {'upper': 0, 'lower': 1}
        upperLowerList = self.get_split_users_by_mean(fields)

        seq = []
        for index, combination in enumerate(combinations):
            seq.append(upperLowerList[index][UPPERLOWERDICT.get(combination)])
        return reduce(setIntersection, seq)


def main():
    filepath = 'losing_users.csv'
    fields = [('userName', 1, str),
              ('pageView', 2, int),
              ('lastAccessTime', 3, float),
              ('dept', 4, str),
              ('level_id', 5, str)]
    app2 = AppUsers(filepath, fields)
    return app2

    # sortedSet = app2.get_users_models(['workyear', 'time', 'uid'], ['upper', 'upper', 'lower'])
    # app2.set_records(list(sortedSet))
    # print app2.get_distribution('username')
    # {'': 11, 'P2': 6, 'P3': 2, 'T4': 7, 'T2': 375, 'T3': 561, 'T1': 9, 'D2': 2, 'D3': 1}


def getUserFeeds(filepath, fields, field):
    app = AppUsers(filepath, fields)
    return app.get_distribution(field)


if __name__ == '__main__':

    #return a user_feed_number pairs
    feedFilePath = "userfeed.csv"
    fields = [('username', 1, str)]
    usersFeedNumber = getUserFeeds(feedFilePath, fields, 'username')

    #return a lost users tables
    userTables = main()

    #set feed number to the corresponding user
    for userRecord in userTables.get_records():
        setattr(userRecord, 'feedNumber', usersFeedNumber.get(getattr(userRecord, 'userName'), 'NA'))
	

    # ---------------RFM MODEL REFERENCE-----------------------#
    # recency, frequency, monetary  # sequence is important    #
    # ---------------------------------------------------------#
    # upper | upper | upper | # important, high-value customer #
    # upper | lower | upper | # important, developing customer #
    # lower | upper | upper | # important, to-keep customer    #
    # lower | lower | upper | # important, to-retain customer  #
    # ---------------------------------------------------------#	
    # upper | upper | lower | # ordinary, high-value customer  #
    # upper | lower | lower | # ordinary, developing customer  #
    # lower | upper | lower | # ordinary, to-keep customer     #
    # lower | lower | lower | # ordinary, to-retain customer   #
    # ---------------------------------------------------------#


    # setup the user models here.
    combinations = [
        ['upper','upper','upper'],
        ['upper','upper','lower'],
        ['upper','lower','upper'],
        ['upper','lower','lower'],
        ['lower','upper','upper'],
        ['lower','upper','lower'],
        ['lower','lower','upper'],
        ['lower','lower','lower'],
    ]

    sequenceResult = []
    fields = ['pageView', 'feedNumber', 'lastAccessTime']
    for combination in combinations:
        sequenceResult.append(("-".join(combination),userTables.get_users_models(fields,combination)))

    # print len(sequenceResult),sequenceResult[0][1]


    for type_, sets in sequenceResult:
        userTables.set_records(list(sets))
        print userTables.get_distribution('feedNumber')

    # with open('userMedolsRecords.txt','w') as wfp:
    #     for index, combination in enumerate(combinations):
    #         wfp.write('\n %s->%s\n'%(index,combination))
    #         for item in userTables.get_users_models(['pageView', 'feedNumber', 'lastAccessTime'],combination):
    #             try:
    #                 wfp.write('%s\n' %item)
    #             except:
    #                 print "oh....error..."

