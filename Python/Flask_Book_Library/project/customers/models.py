from project import db, app
import re
from sqlalchemy.orm import validates

_XSS_TAG_RE = re.compile(r"<[^>]+>")
_JS_PROTO_RE = re.compile(r"(?i)javascript:")
_ALLOWED_CHARS_RE = re.compile(r"^[\w\s\.,'’\-\(\)\/:]+$", re.UNICODE)

def _sanitize_text(value: str, *, field: str, maxlen: int, reject_on_xss: bool = False) -> str:
    if value is None:
        raise ValueError(f"{field} is required")
    if not isinstance(value, str):
        value = str(value)
    raw = value.strip()
    if reject_on_xss and (_XSS_TAG_RE.search(raw) or _JS_PROTO_RE.search(raw)):
        raise ValueError(f"Invalid characters in {field}")
    cleaned = _XSS_TAG_RE.sub("", raw)
    cleaned = _JS_PROTO_RE.sub("", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned)
    if len(cleaned) > maxlen:
        cleaned = cleaned[:maxlen]
    if not _ALLOWED_CHARS_RE.fullmatch(cleaned):
        raise ValueError(f"Invalid characters in {field}")
    return cleaned

def _validate_age(age_val) -> int:
    try:
        age = int(age_val)
    except (TypeError, ValueError):
        raise ValueError("age must be an integer")
    if not (0 <= age <= 130):
        raise ValueError("age is out of allowed range")
    return age


class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    city = db.Column(db.String(64))
    age = db.Column(db.Integer)

    def __init__(self, name, city, age):
        self.name = _sanitize_text(name, field="name", maxlen=64)
        self.city = _sanitize_text(city, field="city", maxlen=64)
        self.age = _validate_age(age)

    @validates("name", "city")
    def _validate_text_fields(self, key, value):
        maxlen = {"name": 64, "city": 64}[key]
        return _sanitize_text(value, field=key, maxlen=maxlen, reject_on_xss=True)

    @validates("age")
    def _validate_age_field(self, key, value):
        return _validate_age(value)

    def __repr__(self):
        return f"Customer(ID: {self.id}, Name: {self.name}, City: {self.city}, Age: {self.age})"


with app.app_context():
    db.create_all()
