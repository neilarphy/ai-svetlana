from pydantic import BaseModel
from typing import List

class Person(BaseModel):
    name: str
    position: str

class Attachment(BaseModel):
    description: str
    pages: int
    copies: int
    note: str | None = None

class Executor(Person):
    phone: str | None = None

class Recipient(Person):
    type: str | None = None
    contact: str | None = None

class GenerateRequest(BaseModel):
    document_type: str
    recipient: Person | None = None
    recipients: List[Recipient] | None = None
    sender: Person
    user_prompt: str
    attachments_string: str | None = None
    approvers: List[Person] | None = None
    executor: Executor | None = None
    subject: str | None = None
