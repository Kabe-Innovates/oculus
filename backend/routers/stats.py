from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from database import get_db
from models import Transaction
from schemas import StatsResponse
from collections import defaultdict

router = APIRouter(prefix="/api/stats", tags=["stats"])

@router.get("", response_model=StatsResponse)
async def get_stats(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Transaction))
    transactions = result.scalars().all()
    
    total = len(transactions)
    flagged = sum(1 for tx in transactions if tx.verdict == 'REVIEW')
    blocked = sum(1 for tx in transactions if tx.verdict == 'BLOCK')
    cleared = sum(1 for tx in transactions if tx.status == 'CLEARED')
    
    avg_score = sum(tx.risk_score for tx in transactions if tx.risk_score is not None) / total if total > 0 else 0.0
    
    distribution = defaultdict(int)
    for tx in transactions:
        if tx.risk_score is not None:
            bucket = f"{int(tx.risk_score // 10) * 10}-{int(tx.risk_score // 10) * 10 + 9}"
            distribution[bucket] += 1
            
    return StatsResponse(
        total_transactions=total,
        flagged_count=flagged,
        blocked_count=blocked,
        cleared_count=cleared,
        avg_risk_score=avg_score,
        risk_distribution=dict(distribution)
    )
