# Zadanie 1 - DDD

## Opis
Celem zadania jest zamodelowanie fragmentu aplikacji bankowej zgodnie z zasadami Domain Driven Design.  
Model obejmuje trzy konteksty: Account Management, Transfer oraz Auth

---

## Definiowanie Bounded Context

**Account Management Context**  
Odpowiada za klientów, proces KYC i konta bankowe wraz z saldem.  
Tylko ten kontekst może modyfikować saldo konta.  

**Transfer Context**  
Obsługuje przelewy między kontami - inicjacja, autoryzacja, rozliczenie.  
Nie zmienia sald bezpośrednio - korzysta z usług Account Management.  

**Auth Context**  
Uwierzytelnia użytkowników i utrzymuje sesje potrzebne do autoryzacji operacji.

---

## Agregaty, encje i obiekty wartości 

**BankAccount (Account Management)**  
- accountId: UUID  
- accountNumber: string (IBAN; np. dla PL regex `^PL\d{26}$`)  
- ownerId: UUID (Client.clientId)  
- balance: Decimal(18,2)

**Client (Account Management)**  
- clientId: UUID  
- name: string  
- phoneNumber: string (E.164, np. `+48123456789`)

**KYC (Account Management)**  
- kycId: UUID  
- clientId: UUID (Client.clientId)  
- status: enum { PENDING, VERIFIED, REJECTED }

**Transfer (Transfer Context)**  
- transferId: UUID  
- fromAccountId: UUID (BankAccount.accountId)  
- toAccountNumber: string (IBAN)  
- amount: TransferAmount  
- status: enum { INITIATED, AUTHORIZED, SETTLED, REJECTED }

**TransferAmount (Value Object, Transfer Context)**  
- amount: Decimal(18,2)  // > 0  
- currency: string (ISO-4217, np. PLN, EUR)

**Session (Auth Context)**  
- sessionId: UUID  
- userId: UUID (Client.clientId)  
- token: string (np. JWT)  
- createdAt: DateTime (UTC)  
- expiresAt: DateTime (UTC)  
- isActive: bool


---

## Przyjęte założenia
- Identyfikatory w formacie UUID  
- IBAN zgodny z ISO (dla PL: `^PL\d{26}$`)  
- Kwoty typu Decimal(18,2), > 0  
- Waluty: ISO-4217 (PLN, EUR itd.)  
- Tylko Account Management zmienia saldo  
- Operacje wymagają aktywnej sesji w Auth Context  

---

## Schemat modelu

![ddd.png](ddd.png)