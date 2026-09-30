import { useState } from 'react';
import { reviewTransaction } from '../api/client';

export default function ReviewActions({ transaction, onReviewed }) {
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const isReviewed = transaction.status !== 'PENDING';

  const handleReview = async (status) => {
    setLoading(true);
    try {
      await reviewTransaction(transaction.id, { status, reviewer_notes: notes });
      onReviewed();
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white/5 border border-white/10 rounded-xl p-6 mt-6">
      <h3 className="text-sm font-medium text-white mb-4 uppercase tracking-wider">Manual Review</h3>
      {isReviewed ? (
        <div className="text-sm text-neutral-400">
          Transaction has been marked as <span className="font-medium text-white">{transaction.status}</span>.
        </div>
      ) : (
        <div className="space-y-4">
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            placeholder="Add reviewer notes..."
            className="w-full bg-white/5 border border-white/10 rounded-lg p-3 text-sm text-white placeholder:text-neutral-600 outline-none focus:border-white/20 resize-none h-24"
            disabled={loading}
          />
          <div className="flex gap-3">
            <button
              onClick={() => handleReview('CLEARED')}
              disabled={loading}
              className="flex-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Clear Transaction
            </button>
            <button
              onClick={() => handleReview('CONFIRMED_FRAUD')}
              disabled={loading}
              className="flex-1 bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
            >
              Confirm Fraud
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
