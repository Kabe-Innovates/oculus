from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from database import get_db
from models import Transaction
from schemas import TransactionCreate, TransactionResponse, ReviewRequest
import datetime

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.post("", response_model=TransactionResponse)
async def create_transaction(request: Request, tx_in: TransactionCreate, db: AsyncSession = Depends(get_db)):
    engine = request.app.state.fraud_engine_class(request.app.state.registry, db)
    tx_data = tx_in.model_dump()
    db_transaction = await engine.process_transaction(tx_data)
    
    ws_manager = request.app.state.ws_manager
    await ws_manager.broadcast(db_transaction)
    
    return db_transaction

@router.get("", response_model=List[TransactionResponse])
async def list_transactions(verdict: Optional[str] = None, status: Optional[str] = None, limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    stmt = select(Transaction).order_by(Transaction.timestamp.desc()).limit(limit).offset(offset)
    if verdict:
        stmt = stmt.where(Transaction.verdict == verdict)
    if status:
        stmt = stmt.where(Transaction.status == status)
        
    result = await db.execute(stmt)
    return result.scalars().all()

@router.get("/{id}", response_model=TransactionResponse)
async def get_transaction(id: str, db: AsyncSession = Depends(get_db)):
    stmt = select(Transaction).where(Transaction.id == id)
    result = await db.execute(stmt)
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx

@router.patch("/{id}/review", response_model=TransactionResponse)
async def review_transaction(id: str, review: ReviewRequest, db: AsyncSession = Depends(get_db)):
    stmt = select(Transaction).where(Transaction.id == id)
    result = await db.execute(stmt)
    tx = result.scalar_one_or_none()
    if not tx:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    tx.status = review.status
    tx.reviewer_notes = review.reviewer_notes
    tx.reviewed_at = datetime.datetime.now(datetime.timezone.utc)
    
    await db.commit()
    await db.refresh(tx)
    return tx
