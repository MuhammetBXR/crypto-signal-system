"""
Database layer for signal storage and performance tracking
"""
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from contextlib import contextmanager
import config

Base = declarative_base()


class Signal(Base):
    """Signal table - stores all generated signals"""
    __tablename__ = "signals"
    
    id = Column(Integer, primary_key=True)
    symbol = Column(String(20), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    strategies = Column(JSON, nullable=False)  # List of strategy names
    direction = Column(String(4), nullable=False)  # BUY or SELL
    entry_price = Column(Float, nullable=False)
    target = Column(Float, nullable=False)
    stop_loss = Column(Float, nullable=False)
    confidence_score = Column(Integer, nullable=False)  # Number of strategies agreeing
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    status = Column(String(10), default="open", nullable=False)  # open, closed, expired
    
    # Relationship
    performance = relationship("Performance", back_populates="signal", uselist=False)


class Performance(Base):
    """Performance table - tracks signal outcomes"""
    __tablename__ = "performance"
    
    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey("signals.id"), nullable=False, unique=True)
    exit_price = Column(Float, nullable=True)
    pnl_percent = Column(Float, nullable=True)
    win = Column(Boolean, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationship
    signal = relationship("Signal", back_populates="performance")


class CoinMetadata(Base):
    """Metadata for each coin - prevent spam"""
    __tablename__ = "coin_metadata"
    
    symbol = Column(String(20), primary_key=True)
    last_signal_time = Column(DateTime, nullable=True)
    total_signals = Column(Integer, default=0)
    total_wins = Column(Integer, default=0)
    total_losses = Column(Integer, default=0)


class DatabaseManager:
    """Database operations manager"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.DATABASE_PATH
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def save_signal(self, signal_data: Dict) -> int:
        """Save a new signal to database"""
        with self.get_session() as session:
            signal = Signal(**signal_data)
            session.add(signal)
            session.flush()
            signal_id = signal.id
            
            # Update coin metadata
            metadata = session.query(CoinMetadata).filter_by(symbol=signal_data["symbol"]).first()
            if metadata:
                metadata.last_signal_time = datetime.utcnow()
                metadata.total_signals += 1
            else:
                metadata = CoinMetadata(
                    symbol=signal_data["symbol"],
                    last_signal_time=datetime.utcnow(),
                    total_signals=1
                )
                session.add(metadata)
            
            return signal_id
    
    def update_signal_performance(self, signal_id: int, exit_price: float, win: bool):
        """Update signal performance after close"""
        with self.get_session() as session:
            signal = session.query(Signal).filter_by(id=signal_id).first()
            if not signal:
                return
            
            # Calculate PnL
            if signal.direction == "BUY":
                pnl_percent = ((exit_price - signal.entry_price) / signal.entry_price) * 100
            else:
                pnl_percent = ((signal.entry_price - exit_price) / signal.entry_price) * 100
            
            # Create or update performance record
            perf = session.query(Performance).filter_by(signal_id=signal_id).first()
            if perf:
                perf.exit_price = exit_price
                perf.pnl_percent = pnl_percent
                perf.win = win
                perf.closed_at = datetime.utcnow()
            else:
                perf = Performance(
                    signal_id=signal_id,
                    exit_price=exit_price,
                    pnl_percent=pnl_percent,
                    win=win,
                    closed_at=datetime.utcnow()
                )
                session.add(perf)
            
            # Update signal status
            signal.status = "closed"
            
            # Update coin metadata
            metadata = session.query(CoinMetadata).filter_by(symbol=signal.symbol).first()
            if metadata:
                if win:
                    metadata.total_wins += 1
                else:
                    metadata.total_losses += 1
    
    def can_send_signal(self, symbol: str, cooldown_hours: int = None) -> bool:
        """Check if we can send a signal for this coin (cooldown check)"""
        cooldown_hours = cooldown_hours or config.SIGNAL_COOLDOWN_HOURS
        
        with self.get_session() as session:
            metadata = session.query(CoinMetadata).filter_by(symbol=symbol).first()
            
            if not metadata or not metadata.last_signal_time:
                return True
            
            time_since_last = datetime.utcnow() - metadata.last_signal_time
            return time_since_last >= timedelta(hours=cooldown_hours)
    
    def get_signal_history(self, symbol: str = None, days: int = 7) -> List[Dict]:
        """Get recent signal history"""
        with self.get_session() as session:
            query = session.query(Signal)
            
            if symbol:
                query = query.filter_by(symbol=symbol)
            
            since = datetime.utcnow() - timedelta(days=days)
            query = query.filter(Signal.created_at >= since)
            query = query.order_by(Signal.created_at.desc())
            
            signals = query.all()
            
            return [
                {
                    "id": s.id,
                    "symbol": s.symbol,
                    "timeframe": s.timeframe,
                    "strategies": s.strategies,
                    "direction": s.direction,
                    "entry_price": s.entry_price,
                    "target": s.target,
                    "stop_loss": s.stop_loss,
                    "confidence_score": s.confidence_score,
                    "created_at": s.created_at,
                    "status": s.status,
                }
                for s in signals
            ]
    
    def get_overall_stats(self) -> Dict:
        """Get overall performance statistics"""
        with self.get_session() as session:
            total_signals = session.query(Signal).count()
            closed_signals = session.query(Performance).filter(Performance.win.isnot(None)).count()
            total_wins = session.query(Performance).filter_by(win=True).count()
            total_losses = session.query(Performance).filter_by(win=False).count()
            
            win_rate = (total_wins / closed_signals * 100) if closed_signals > 0 else 0
            
            # Average PnL
            avg_profit_query = session.query(Performance).filter(Performance.win == True)
            avg_loss_query = session.query(Performance).filter(Performance.win == False)
            
            avg_profit = 0
            avg_loss = 0
            
            if total_wins > 0:
                profits = [p.pnl_percent for p in avg_profit_query.all() if p.pnl_percent]
                avg_profit = sum(profits) / len(profits) if profits else 0
            
            if total_losses > 0:
                losses = [p.pnl_percent for p in avg_loss_query.all() if p.pnl_percent]
                avg_loss = sum(losses) / len(losses) if losses else 0
            
            return {
                "total_signals": total_signals,
                "closed_signals": closed_signals,
                "open_signals": total_signals - closed_signals,
                "total_wins": total_wins,
                "total_losses": total_losses,
                "win_rate": round(win_rate, 2),
                "avg_profit": round(avg_profit, 2),
                "avg_loss": round(avg_loss, 2),
            }
    
    def get_open_signals(self) -> List[Dict]:
        """Get all open signals for performance tracking"""
        with self.get_session() as session:
            signals = session.query(Signal).filter_by(status="open").all()
            
            # Convert to dicts to avoid detached instance errors
            return [
                {
                    'id': s.id,
                    'symbol': s.symbol,
                    'direction': s.direction,
                    'entry_price': s.entry_price,
                    'target': s.target,
                    'stop_loss': s.stop_loss,
                    'created_at': s.created_at,
                }
                for s in signals
            ]
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics for bot commands"""
        stats = self.get_overall_stats()
        
        # Calculate risk/reward ratio
        if stats['avg_loss'] != 0:
            risk_reward = abs(stats['avg_profit'] / stats['avg_loss'])
        else:
            risk_reward = 0
        
        stats['risk_reward'] = round(risk_reward, 2)
        return stats
    
    def get_recent_signals(self, limit: int = 10) -> List[Dict]:
        """Get recent signals for bot command"""
        with self.get_session() as session:
            signals = session.query(Signal).order_by(Signal.created_at.desc()).limit(limit).all()
            
            result = []
            for s in signals:
                # Check if has performance
                perf = session.query(Performance).filter_by(signal_id=s.id).first()
                
                status = "open"
                if perf:
                    status = "win" if perf.win else "loss"
                
                result.append({
                    'id': s.id,
                    'symbol': s.symbol,
                    'direction': s.direction,
                    'entry_price': s.entry_price,
                    'confluence_score': s.confidence_score,
                    'created_at': s.created_at.strftime('%Y-%m-%d %H:%M'),
                    'status': status
                })
            
            return result

