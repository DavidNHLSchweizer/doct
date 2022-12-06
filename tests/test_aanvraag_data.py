import datetime
from aanvraag_data import AanvraagDocumentInfo, AanvraagInfo


#tests AanvraagDocumentInfo
ATTRIBS = ['datum', 'student', 'studnr', 'telno', 'email', 'bedrijf', 'titel']
def test_AanvraagDocumentInfo_init_empty():
    adi = AanvraagDocumentInfo()
    assert adi
    assert adi.datum == ''
    assert adi.student == ''
    assert adi.studnr == ''
    assert adi.telno == ''
    assert adi.email == ''
    assert adi.bedrijf == ''
    assert adi.titel == ''
    assert not adi.valid()

TESTCASE = {'datum': '3-4-1999', 'student':'Erica Zwanepoel', 'studnr':'123456', 'telno':'06-12345678', 'email':'erica.zwanepoel@testcases.com', 'bedrijf':'Braakware', 'titel': 'Automatisch drankorgel'}

def _get_adi(testcase):
    return AanvraagDocumentInfo(datum=testcase['datum'], student=testcase['student'], studnr=testcase['studnr'], telno=testcase['telno'], email=testcase['email'], bedrijf=testcase['bedrijf'], titel=testcase['titel']) 

def _test_equal(adi, testcase):
    assert adi.datum == testcase['datum']
    assert adi.student == testcase['student']
    assert adi.studnr == testcase['studnr']
    assert adi.telno == testcase['telno']
    assert adi.email == testcase['email']
    assert adi.bedrijf == testcase['bedrijf']
    assert adi.titel == testcase['titel']

def test_AanvraagDocumentInfo_init_no_kwds():
    adi = AanvraagDocumentInfo(TESTCASE['datum'], TESTCASE['student'], TESTCASE['studnr'], TESTCASE['telno'], TESTCASE['email'], TESTCASE['bedrijf'], TESTCASE['titel']) 
    _test_equal(adi, TESTCASE)
    assert adi.valid()

def test_AanvraagDocumentInfo_init_kwds():
    adi = _get_adi(TESTCASE)
    _test_equal(adi, TESTCASE)
    assert adi.valid()

def test_AanvraagDocumentInfo_str():
    adi = _get_adi(TESTCASE)
    titel = TESTCASE['titel']
    assert str(adi) == f'{TESTCASE["student"]}({TESTCASE["studnr"]}) - {TESTCASE["datum"]}: {TESTCASE["bedrijf"]} - "{titel}"'

def test_AanvraagDocumentInfo_eq():
    adi1 = _get_adi(TESTCASE)
    adi2 = _get_adi(TESTCASE)
    assert adi1 == adi2

def test_AanvraagDocumentInfo_neq():    
    adi1 = _get_adi(TESTCASE)
    for attr in ATTRIBS:
        attr_value_1 = getattr(adi1, attr)
        adi2 = _get_adi(TESTCASE)
        setattr(adi2, attr, attr_value_1 + 'Nope')
        assert adi1 != adi2        

def test_AanvraagDocumentInfo_valid():
    pass
#tests AanvraagInfo
def test_AanvraagInfo_init_no_timestamp():
    adi = _get_adi(TESTCASE)
    ai = AanvraagInfo(adi)
    now = datetime.datetime.now()
    assert ai
    assert ai.docInfo == adi
    assert now > ai.timestamp
    assert (now - ai.timestamp).total_seconds() * 1000 < 400
    
def get_test_timestamp():
    return datetime.datetime(year=2000, month=6,day=9,hour=17,minute=42, second=34,microsecond=123)

def test_AanvraagInfo_init_timestamp():
    adi = _get_adi(TESTCASE)
    timestamp = get_test_timestamp()
    ai = AanvraagInfo(adi, timestamp)
    assert ai
    assert ai.docInfo == adi
    assert timestamp == ai.timestamp

def test_AanvraagInfo_str():
    adi = _get_adi(TESTCASE)
    timestamp = get_test_timestamp()
    ai = AanvraagInfo(adi, timestamp)    
    assert str(ai) == f'{str(adi)} [{str(timestamp)}]'

def test_AanvraagInfo_eq():
    adi1 = _get_adi(TESTCASE)
    ai1 = AanvraagInfo(adi1, get_test_timestamp())
    adi2 = _get_adi(TESTCASE)
    ai2 = AanvraagInfo(adi2, get_test_timestamp())
    assert ai1 == ai2

def test_AanvraagInfo_neq_docinfo():
    adi1 = _get_adi(TESTCASE)
    ai1 = AanvraagInfo(adi1, get_test_timestamp())
    adi2 = _get_adi(TESTCASE)
    adi2.datum='negen uur savonds'
    ai2 = AanvraagInfo(adi2, get_test_timestamp())
    assert ai1 != ai2

def test_AanvraagInfo_neq_timestamp():
    adi1 = AanvraagDocumentInfo(datum='datum', student='student', studnr='studnr', telno='telno', email='email', bedrijf='bedrijf', titel='titel')       
    ai1 = AanvraagInfo(adi1, get_test_timestamp())
    adi2 = AanvraagDocumentInfo(datum='datum', student='student', studnr='studnr', telno='telno', email='email', bedrijf='bedrijf', titel='titel')       
    ai2 = AanvraagInfo(adi2, datetime.datetime.now())
    assert ai1 != ai2

