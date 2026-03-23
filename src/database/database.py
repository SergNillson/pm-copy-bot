"""
Модуль для работы с базой данных.
Управляет подключением, создает таблицы и предоставляет методы для работы с данными.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from src.database.models import Base, TrackedTrade, PaperTrade, Position, BalanceHistory
from datetime import datetime


class Database:
    """
    Класс для управления базой данных SQLite.
    """
    
    def __init__(self, db_path: str):
        """
        Инициализация подключения к базе данных.
        
        Args:
            db_path: Путь к файлу базы данных SQLite
        """
        # Создаем директорию для БД, если её нет
        db_dir = os.path.dirname(db_path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Создаем движок SQLite
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        
        # Создаем все таблицы
        Base.metadata.create_all(self.engine)
        
        # Создаем фабрику сессий
        self.Session = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        """Возвращает новую сессию для работы с БД."""
        return self.Session()
    
    # === Методы для работы с отслеживаемыми сделками ===
    
def add_tracked_trade(self, trader_address: str, market_id: str, market_title: str,
                         outcome: str, amount: float, price: float, tx_hash: str) -> TrackedTrade:
        """
        Добавляет сделку трейдера в БД.
        """
        session = self.get_session()
        try:
            trade = TrackedTrade(
                trader_address=trader_address,
                market_id=market_id,
                market_title=market_title,
                outcome=outcome,
                amount=amount,
                price=price,
                transaction_hash=tx_hash
            )
            session.add(trade)
            session.commit()
            return trade
        finally:
            session.close()
    
def get_tracked_trade_by_hash(self, tx_hash: str) -> TrackedTrade:
        """Получает сделку по хешу транзакции."""
        session = self.get_session()
        try:
            return session.query(TrackedTrade).filter_by(transaction_hash=tx_hash).first()
        finally:
            session.close()
    
    # === Методы для работы с виртуальными сделками ===
    
def add_paper_trade(self, tracked_trade_id: int, market_id: str, market_title: str,
                       outcome: str, amount: float, price: float) -> PaperTrade:
        """
        Добавляет виртуальную сделку.
        """
        session = self.get_session()
        try:
            trade = PaperTrade(
                tracked_trade_id=tracked_trade_id,
                market_id=market_id,
                market_title=market_title,
                outcome=outcome,
                amount=amount,
                price=price
            )
            session.add(trade)
            session.commit()
            return trade
        finally:
            session.close()
    
def close_paper_trade(self, trade_id: int, pnl: float):
        """
        Закрывает виртуальную сделку.
        """
        session = self.get_session()
        try:
            trade = session.query(PaperTrade).filter_by(id=trade_id).first()
            if trade:
                trade.status = 'closed'
                trade.pnl = pnl
                trade.closed_at = datetime.utcnow()
                session.commit()
        finally:
            session.close()
    
def get_open_paper_trades(self):
        """Возвращает все открытые виртуальные сделки."""
        session = self.get_session()
        try:
            return session.query(PaperTrade).filter_by(status='open').all()
        finally:
            session.close()
    
    # === Методы для работы с позициями ===
    
def add_position(self, paper_trade_id: int, market_id: str, market_title: str,
                    outcome: str, amount: float, entry_price: float) -> Position:
        """
        Добавляет новую позицию.
        """
        session = self.get_session()
        try:
            position = Position(
                paper_trade_id=paper_trade_id,
                market_id=market_id,
                market_title=market_title,
                outcome=outcome,
                amount=amount,
                entry_price=entry_price,
                current_price=entry_price
            )
            session.add(position)
            session.commit()
            return position
        finally:
            session.close()
    
def update_position(self, position_id: int, current_price: float, unrealized_pnl: float):
        """
        Обновляет цену и P&L позиции.
        """
        session = self.get_session()
        try:
            position = session.query(Position).filter_by(id=position_id).first()
            if position:
                position.current_price = current_price
                position.unrealized_pnl = unrealized_pnl
                session.commit()
        finally:
            session.close()
    
def remove_position(self, position_id: int):
        """Удаляет позицию (когда она закрыта)."""
        session = self.get_session()
        try:
            position = session.query(Position).filter_by(id=position_id).first()
            if position:
                session.delete(position)
                session.commit()
        finally:
            session.close()
    
def get_all_positions(self):
        """Возвращает все открытые позиции."""
        session = self.get_session()
        try:
            return session.query(Position).all()
        finally:
            session.close()
    
    # === Методы для работы с балансом ===
    
def add_balance_record(self, balance: float, change: float = 0.0, reason: str = None):
        """
        Добавляет запись об изменении баланса.
        """
        session = self.get_session()
        try:
            record = BalanceHistory(
                balance=balance,
                change=change,
                reason=reason
            )
            session.add(record)
            session.commit()
            return record
        finally:
            session.close()
    
def get_current_balance(self) -> float:
        """
        Возвращает текущий баланс (последняя запись).
        Если записей нет, возвращает None.
        """
        session = self.get_session()
        try:
            last_record = session.query(BalanceHistory).order_by(
                BalanceHistory.timestamp.desc()
            ).first()
            return last_record.balance if last_record else None
        finally:
            session.close()