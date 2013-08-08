from __future__ import unicode_literals

from sqlalchemy import Column, Unicode, ForeignKey, Integer
from sqlalchemy.orm import relationship

from models import Base
from utils.models import uuid_factory, Enum


TransactionStatus = Enum('PENDING', 'SENT', 'ERROR',
                         name='charge_plan_transaction_status')


class ChargeTransaction(Base):
    __tablename__ = "charge_transactions"

    id = Column(Unicode, primary_key=True, default=uuid_factory('PAT'))
    customer_id = Column(Unicode, ForeignKey('customers.id'), nullable=False)
    processor_txn_id = Column(Unicode, nullable=False)
    amount_cents = Column(Integer, nullable=False)
    status = Column(TransactionStatus, nullable=False)

    invoices = relationship('ChargePlanInvoice', backref='transaction',
                            cascade='delete')

    @classmethod
    def create(cls, customer, amount_cents):
        transaction = cls(
            customer=customer,
            amount_cents=amount_cents,
            status=TransactionStatus.PENDING
        )
        try:
            your_id = transaction.customer.company.processor.create_charge(
                transaction.customer.processor_id, transaction.amount_cents)
            transaction.status = TransactionStatus.SENT
            transaction.your_id = your_id
        except:
            transaction.status = TransactionStatus.ERROR
            transaction.session.commit()
            raise