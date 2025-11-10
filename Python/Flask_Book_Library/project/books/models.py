from project import db, app
import re
from sqlalchemy.orm import validates
from datetime import datetime

# Book model
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

def _validate_year(year_val) -> int:
    try:
        year = int(year_val)
    except (TypeError, ValueError):
        raise ValueError("year_published must be an integer")
    current_year = datetime.utcnow().year
    if not (0 < year <= current_year + 1):
        raise ValueError("year_published is out of allowed range")
    return year


class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, index=True)
    author = db.Column(db.String(64))
    year_published = db.Column(db.Integer)
    book_type = db.Column(db.String(20))
    status = db.Column(db.String(20), default='available')

    def __init__(self, name, author, year_published, book_type, status='available'):
        self.name = _sanitize_text(name, field="name", maxlen=64)
        self.author = _sanitize_text(author, field="author", maxlen=64)
        self.year_published = _validate_year(year_published)
        self.book_type = _sanitize_text(book_type, field="book_type", maxlen=20)
        self.status = _sanitize_text(status if status else "available", field="status", maxlen=20)

    @validates("name", "author", "book_type", "status")
    def _validate_text_fields(self, key, value):
        maxlen = {"name": 64, "author": 64, "book_type": 20, "status": 20}[key]
        return _sanitize_text(value, field=key, maxlen=maxlen, reject_on_xss=True)

    @validates("year_published")
    def _validate_year_field(self, key, value):
        return _validate_year(value)

    def __repr__(self):
        return f"Book(ID: {self.id}, Name: {self.name}, Author: {self.author}, Year Published: {self.year_published}, Type: {self.book_type}, Status: {self.status})"


with app.app_context():
    db.create_all()
