import sys
import csv
import time
import Pmf as _pmf
from operator import attrgetter,itemgetter

lessThan = lambda x, y: x < y
setIntersection = lambda x, y: set(x) & set(y)

TIMENOW = time.time()
# ref: http://blog.csdn.net/longshenlmj/article/details/13627537
# STRUCT_TIME:(tm_year=2011, tm_mon=9, tm_mday=27, tm_hour=10, tm_min=50, tm_sec=0, tm_wday=1, tm_yday=270, tm_isdst=-1)

def timeProcess(timeStr, ISOFORMAT="%Y-%m-%d %H:%M:%S"):
    structa = time.strptime(timeStr, ISOFORMAT)
    stampa = time.mktime(structa) # timestamp, float number
    return (TIMENOW - stampa)/(24*3600)


def separate_equally(seq, n=5):
    """
    #return index of equally distance of a sequence
    >> separate_equally([i for i in range(100)],4)
    >> ([25, 50, 75, 100], 25)
    """
    delta = len(seq) / n
    start, res = 0, []
    while (True):
        start += delta
        if start > len(seq):
            break
        res.append(start)
    return res, delta


def average(seq):
    assert len(seq) != 0
    seq = [x if isinstance(x, (int, float)) else 0 for x in seq]
    return sum(seq) * 1.0 / len(seq)


def distribution(seq):
    distributions = dict()
    for val in seq:
        distributions[val] = distributions.get(val, 0) + 1
    return distributions


class Record(object):
    """record of users"""


class AppUser(Record):
    """application users"""

    def get(self, field):
        return getattr(self, field)

    def __str__(self):
        return str(self.__dict__)


class Table(object):
    """records list"""

    def __init__(self):
        self.records = []

    def __len__(self):
        return len(self.records)

    def read_file(self, filePath, fields, cls, n=None):
        try:
            fp = csv.reader(open(filePath)) # fp = open(filePath)
        except:
            print "File path: %s doesn't exist..." % filePath
            sys.exit(0)

        for idx, line in enumerate(fp):
            if idx == 0: continue
            if idx == n: break
            record = self.make_record(line, fields, cls)
            self.add_record(record)

    def make_record(self, line, fields, cls):
        obj = cls()
        for (fieldName, idx, type_) in fields:
            try:
                fieldValue = type_(line[idx])
            except:
                fieldValue = 0 #'NA'
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

    def normalize(self, field, method=max):
        maxValue = max([getattr(obj, field) for obj in self.records])
        assert maxValue != 0
        for record in self.records:
            setattr(record, field, float(getattr(record, field) / maxValue))

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
            # (upper, lower)[lessThan(getattr(record, field), averageValue)].append(record)
            if record.get(field) > averageValue:
                upper.append(record)
            else:
                lower.append(record)
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

    def recode(self):
        for record in self.records:
            setattr(record, 'timeDelta', timeProcess(getattr(record,'ISOTIME')))

    def cal_RMF_scores(self, fieldsWeightValueSequence):
        #[(fieldName,weightValue),...]
        for record in self.records:
            totalRMF = 0
            for field, weightValue in fieldsWeightValueSequence:
                totalRMF += float(getattr(record, field)) * weightValue
            setattr(record, 'RMF_SCORE', totalRMF)
        return self


if __name__ == '__main__':

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
    COMBINATIONS = [
        ['upper', 'upper', 'upper'],
        ['upper', 'upper', 'lower'],
        ['upper', 'lower', 'upper'],
        ['upper', 'lower', 'lower'],
        ['lower', 'upper', 'upper'],
        ['lower', 'upper', 'lower'],
        ['lower', 'lower', 'upper'],
        ['lower', 'lower', 'lower']]

    def printSortedDict(dctToPrint,key=itemgetter(1)):
        with open('dept.txt','w') as wfp:
            for k,v in sorted(dctToPrint.items(),key=key,reverse=True):
                wfp.write('%s\t%s\n' %(k,v))
        wfp.close()

    def main():
        filePath = 'churnUserSourceData.csv'
        fields = [('userName', 1, str),
                  ('pageView', 2, int),
                  ('feedsNumber', 3, int),
                  ('dept', 5, str),
                  ('level_id', 6, str),
                  ('level_id_cn', 7, str),
                  ('lastAccessTime', 8, float),
                  ('ISOTIME',4, str)
        ]
        au = AppUsers(filePath, fields)

        print au.get_records()[0]
        print "-"*80
        au.recode()

        for record in au.records:
            print getattr(record,'timeDelta'),"HERE."


        # au.normalize('lastAccessTime')

        au.cal_RMF_scores([('pageView', 10), ('feedsNumber', 100), ('lastAccessTime', 1)])

        print "average feedsNumber is : ", au.get_average('feedsNumber')
        print "average pageView is :", au.get_average('pageView')
        print "average lastAccessTime is :", au.get_average('timeDelta')

        print "_"*100


        # x = au.get_distribution('dept')
        # sumList = sum(x.values())
        # for key,val in x.iteritems():
        #     x[key]=100.0*val/sumList
        #
        # printSortedDict(x)



        sequenceResult, fields = [], ['feedsNumber', 'pageView', 'lastAccessTime']
        for combination in COMBINATIONS:
            sortedSequenceOfCombination = sorted(au.get_users_models(fields, combination),key=attrgetter('RMF_SCORE','feedsNumber','pageView'),reverse=True)
            sequenceResult.append(("-".join(combination),sortedSequenceOfCombination))

        return sequenceResult, au

        # return sequenceResult

        # with open('userMedolsRecords.txt','w') as wfp:
        #     for type_, records in sequenceResult:
        #         wfp.write('\n')
        #         wfp.write('|%s|%s\n' %(type_,"-".join(fields)))
        #         for record in records:
        #             try:
        #                 for k,v in record.__dict__.items():
        #                     wfp.write('%s:%s\t' %(k,v))
        #             except:
        #                 print repr(v)
        #             wfp.write('\n')

    type_sequence,au  = main()

    print au
    # for type_, seq in type_sequence:
    #     au.set_records(list(seq))
        # print "distribution of level_id is ",
        # print sorted(au.get_distribution('level_id').items(),key=itemgetter(1))
        #
        # print "average of feedsNumber is ",
        # print au.get_average('feedsNumber')
        #
        # print "distribution of feedsNumber is ",
        # print sorted(au.get_distribution('feedsNumber').items(),key=itemgetter(1))
        #
        # print "average of pageView is ",
        # print au.get_average('pageView')
        #
        # print "distribution of pageView is ",
        # print sorted(au.get_distribution('pageView').items(),key=itemgetter(1))
        #
        # print "="*100

        #-------------------write2csv----------------------------------
        # csvWriter = csv.writer(open('%s.csv' %type_,'wb'))
        #
        # workLevel = _pmf.Pmf(au.get_distribution('level_id_cn'),type_)
        # print workLevel.name
        # # print workLevel.Print(),
        # for line in sorted(workLevel.GetDict().iteritems(),key=itemgetter(0),reverse=True):
        #     csvWriter.writerow(line)

    #
    # au.set_records(list(type_sequence[1][1]))
    # workLevel = _pmf.Pmf(au.get_distribution('level_id'),'LEVEL_ID')
    # # print workLevel.Print(),
    # print sorted(workLevel.GetDict().iteritems(),key=itemgetter(0),reverse=True)
