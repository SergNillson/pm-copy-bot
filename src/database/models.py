"""
Модели базы данных для хранения информации о сделках и позициях.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class TrackedTrade(Base):
    """
    Сделки отслеживаемого трейдера.
    Хранит все сделки, которые совершил целевой трейдер.
    """
    __tablename__ = 'tracked_trades'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    trader_address = Column(String, nullable=False)  # Адрес трейдера
    market_id = Column(String, nullable=False)  # ID рынка на Polymarket
    market_title = Column(String)  # Название рынка
    outcome = Column(String)  # YES или NO
    amount = Column(Float, nullable=False)  # Размер ставки в USD
    price = Column(Float)  # Цена входа
    transaction_hash = Column(String, unique=True)  # Хеш транзакции
    
    def __repr__(self):
        return f"<TrackedTrade {self.market_title} - ${self.amount}>"


class PaperTrade(Base):
    """
    Виртуальные сделки в режиме paper trading.
    Копии сделок трейдера, адаптированные под баланс пользователя.
    """
    __tablename__ = 'paper_trades'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    tracked_trade_id = Column(Integer)  # Ссылка на оригинальную сделку трейдера
    market_id = Column(String, nullable=False)
    market_title = Column(String)
    outcome = Column(String)  # YES или NO
    amount = Column(Float, nullable=False)  # Размер виртуальной ставки
    price = Column(Float)  # Цена входа
    status = Column(String, default='open')  # open, closed
    pnl = Column(Float, default=0.0)  # Profit/Loss
    closed_at = Column(DateTime)  # Когда закрыли позицию
    
    def __repr__(self):
        return f"<PaperTrade {self.market_title} - ${self.amount} ({self.status})>"


class Position(Base):
    """
    Текущие открытые позиции.
    Хранит информацию о всех активных ставках.
    """
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    paper_trade_id = Column(Integer)  # Ссылка на paper trade
    market_id = Column(String, nullable=False)
    market_title = Column(String)
    outcome = Column(String)
    amount = Column(Float, nullable=False)  # Размер позиции
    entry_price = Column(Float)  # Цена входа
    current_price = Column(Float)  # Текущая цена
    unrealized_pnl = Column(Float, default=0.0)  # Нереализованная прибыль/убыток
    opened_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<Position {self.market_title} - ${self.amount}>"


class BalanceHistory(Base):
    """
    История изменения баланса.
    Записывает каждое изменение виртуального баланса.
    """
    __tablename__ = 'balance_history'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    balance = Column(Float, nullable=False)  # Баланс на момент времени
    change = Column(Float, default=0.0)  # Изменение баланса
    reason = Column(String)  # Причина изменения (trade_open, trade_close, etc.)
    
    def __repr__(self):
        return f"<Balance ${self.balance} at {self.timestamp}>"