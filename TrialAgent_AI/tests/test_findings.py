import pytest
from pydantic import ValidationError
from backend.analysis.finding_classifier import Finding
@pytest.mark.parametrize('severity',['Critical','High','Medium','Low','Informational'])
def test_severities(severity): assert Finding(title='Review',description='Test',category='Safety',agent='Safety',severity=severity).severity==severity
def test_invalid_severity():
 with pytest.raises(ValidationError): Finding(title='x',description='x',category='x',agent='x',severity='Invalid')
