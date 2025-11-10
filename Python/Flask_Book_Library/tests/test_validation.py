import pytest
from project.books.models import Book
from project.customers.models import Customer


# ---------- BOOK TESTS ----------

def test_book_creation_sanitizes_and_validates():
    print("\n[TEST] Tworzenie książki z tagami HTML - sprawdzanie sanityzacji.")
    b = Book(
        name="<b>Clean</b>",
        author="A<script>alert(1)</script> B",
        year_published=2024,
        book_type="novel",
        status="available"
    )
    assert "<" not in b.name, "Tagi HTML w nazwie nie zostały usunięte"
    assert "<" not in b.author, "Tagi HTML w autorze nie zostały usunięte"
    assert b.year_published == 2024


def test_book_invalid_year_raises():
    print("\n[TEST] Tworzenie książki z błędnym rokiem - oczekiwany ValueError.")
    with pytest.raises(ValueError):
        Book(name="N", author="A", year_published="xxxx", book_type="t")


def test_book_year_range_too_future():
    print("\n[TEST] Rok z przyszłości - oczekiwany błąd walidacji.")
    from datetime import datetime
    future_year = datetime.utcnow().year + 5
    with pytest.raises(ValueError):
        Book(name="Future", author="Someone", year_published=future_year, book_type="novel")


def test_book_field_length_limit():
    print("\n[TEST] Zbyt długa nazwa książki - powinna zostać przycięta.")
    long_name = "X" * 100
    b = Book(name=long_name, author="A", year_published=2020, book_type="t")
    assert len(b.name) <= 64, "Nazwa książki nie została przycięta do 64 znaków"


def test_book_field_update_triggers_validation():
    print("\n[TEST] Edycja pola autora z niedozwolonymi znakami - oczekiwany ValueError.")
    b = Book(name="Good", author="OK", year_published=2020, book_type="test")
    with pytest.raises(ValueError):
        b.author = "<script>evil()</script>"


# ---------- CUSTOMER TESTS ----------

def test_customer_creation_sanitizes_and_validates():
    print("\n[TEST] Tworzenie klienta z tagami HTML - sprawdzanie sanityzacji.")
    c = Customer(name="<i>N</i>", city="Ci<script>ty</script>", age="23")
    assert "<" not in c.name
    assert "<" not in c.city
    assert c.age == 23


def test_customer_invalid_age_raises():
    print("\n[TEST] Tworzenie klienta z błędnym wiekiem - oczekiwany ValueError.")
    with pytest.raises(ValueError):
        Customer(name="N", city="C", age="old")


def test_customer_negative_age_raises():
    print("\n[TEST] Wiek ujemny - oczekiwany ValueError.")
    with pytest.raises(ValueError):
        Customer(name="Adam", city="Gdańsk", age=-5)


def test_customer_field_update_triggers_validation():
    print("\n[TEST] Edycja pola city z HTML - oczekiwany ValueError.")
    c = Customer(name="Jan", city="Warszawa", age=30)
    with pytest.raises(ValueError):
        c.city = "<script>evil()</script>"


def test_customer_field_length_limit():
    print("\n[TEST] Zbyt długa nazwa miasta - powinna zostać przycięta.")
    long_city = "X" * 200
    c = Customer(name="Tomek", city=long_city, age=20)
    assert len(c.city) <= 64, "Miasto nie zostało przycięte do 64 znaków"
