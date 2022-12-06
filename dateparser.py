from datetime import date, datetime
import re
import locale


def _try_return_date(day_str, month_str, year_str, formats, _locale='nl_NL')->date:
    old_loc,_ = locale.getlocale(locale.LC_TIME)
    if old_loc != _locale:
        locale.setlocale(locale.LC_TIME, _locale)
    try:
        for format in formats:
            try:
                if tm := datetime.strptime(f'{day_str}-{month_str}-{year_str}', format):
                    return tm #date(tm.year, tm.month, tm.day)
            except ValueError:
                pass
    finally:
        if old_loc != _locale:            
            locale.setlocale(locale.LC_TIME, old_loc)
    return None

def try_return_date(day_str, month_str, year_str, formats)->date:
    LOCALES = ['nl_NL', 'en_US']
    for _locale in LOCALES:
        if result := _try_return_date(day_str, month_str, year_str, formats, _locale):
            return result
    return None

class DateParser:
    INT_DATE_REGEX='(?P<day>\d\d)[-/\w](?P<month>\d\d)[-/\w](?P<year>\d\d\d\d)(?P<rest>.*)'
    STR_DATE_REGEX='(?P<day>\d\d)[-\/\s]+(?P<month>[a-zA-Z]{3,9})[-\/\s]+(?P<year>\d\d\d\d)(?P<rest>.*)'
    def __init__(self):
        self.int_pattern = re.compile(DateParser.INT_DATE_REGEX)
        self.str_pattern = re.compile(DateParser.STR_DATE_REGEX)
        self.rest = ''        
    def __parse_date_int(self, s:str)->tuple[date, str]:
        if match:=self.int_pattern.match(s):
            try:
                return (try_return_date(match.group('day'), match.group('month'), match.group('year'), ['%d-%m-%Y']), match.group('rest'))
            except ValueError as E:
                print(f'Invalid date: {s}: {E}')
        return None
    def __parse_date_str(self, s:str)->tuple[date, str]:
        if match:=self.str_pattern.match(s):
            try:
                return (try_return_date(match.group('day'), match.group('month').capitalize(), match.group('year'), ['%d-%b-%Y', '%d-%B-%Y']), match.group('rest'))
            except ValueError as E:
                print(f'Invalid date: {s}: {E}')
        return None
    def split_and_parse(self, s: str)->tuple[date,str]:
        try:
            if (result := self.__parse_date_int(s)):
                return result
            elif (result := self.__parse_date_str(s)):
                return result
        except TypeError:
            pass
        return None,None
    def parse_date(self, s: str)-> date:
        result,_ = self.split_and_parse(s)
        return result

if __name__=='__main__':     
    TESTCASES= ['2022/10/31', '22/11/2022', '01-11-2022', '28-11-2022 / Versie 1', '08 november 2022', '08 maart 2022', '08 mar 2022', '21 november 2022 / v1', '30-02-2022','01-13-2022', '08 branuari 2022']
    DP = DateParser()
    for case in TESTCASES:
        d,r = DP.split_and_parse(case)
        if d:
            print(f'{case}: {d.strftime("%d-%m-%Y")} {r}')
        else:
            print(f'{case}: NONE  {r}')

