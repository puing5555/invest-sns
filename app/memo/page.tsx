'use client';

import { useState } from 'react';
import { MemoData, memoData } from '@/data/memoData';
import MemoFilter from '@/components/MemoFilter';
import AIJournalBanner from '@/components/AIJournalBanner';
import MemoCard from '@/components/MemoCard';
import MemoEditor from '@/components/MemoEditor';
import MemoDetail from '@/components/MemoDetail';

export default function MemoPage() {
  const [memos, setMemos] = useState<MemoData[]>(memoData);
  const [activeFilter, setActiveFilter] = useState('all');
  const [isEditorOpen, setIsEditorOpen] = useState(false);
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const [selectedMemo, setSelectedMemo] = useState<MemoData | null>(null);
  const [editingMemo, setEditingMemo] = useState<MemoData | undefined>(undefined);

  // Filter memos based on active filter
  const filteredMemos = memos.filter((memo) => {
    switch (activeFilter) {
      case 'all':
        return true;
      case 'by-stock':
        return memo.stock !== null;
      case '매수근거':
      case '매도근거':
      case 'AI일지':
        return memo.tag === activeFilter;
      default:
        return true;
    }
  });

  // Sort memos by date (newest first)
  const sortedMemos = filteredMemos.sort((a, b) => {
    const dateA = new Date(a.date.replace(/\./g, '-'));
    const dateB = new Date(b.date.replace(/\./g, '-'));
    return dateB.getTime() - dateA.getTime();
  });

  const handleNewMemo = () => {
    setEditingMemo(undefined);
    setIsEditorOpen(true);
  };

  const handleEditMemo = (memo: MemoData) => {
    setEditingMemo(memo);
    setIsEditorOpen(true);
    setIsDetailOpen(false);
  };

  const handleSaveMemo = (memoData: Omit<MemoData, 'id'>) => {
    if (editingMemo) {
      // Update existing memo
      setMemos(prev => prev.map(memo => 
        memo.id === editingMemo.id 
          ? { ...memoData, id: editingMemo.id }
          : memo
      ));
    } else {
      // Add new memo
      const newMemo: MemoData = {
        ...memoData,
        id: Math.max(...memos.map(m => m.id)) + 1,
      };
      setMemos(prev => [...prev, newMemo]);
    }
    setIsEditorOpen(false);
    setEditingMemo(undefined);
  };

  const handleDeleteMemo = (id: number) => {
    setMemos(prev => prev.filter(memo => memo.id !== id));
  };

  const handleCardClick = (memo: MemoData) => {
    setSelectedMemo(memo);
    setIsDetailOpen(true);
  };

  const handleCloseDetail = () => {
    setIsDetailOpen(false);
    setSelectedMemo(null);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-2">
                📝 투자 메모
              </h1>
              <p className="text-gray-600 mt-1">기록하는 투자자가 이긴다</p>
            </div>
            <button
              onClick={handleNewMemo}
              className="bg-[#3182f6] text-white px-6 py-3 rounded-lg font-medium hover:bg-[#00c299] transition-colors flex items-center gap-2"
            >
              + 새 메모
            </button>
          </div>
        </div>

        {/* AI Journal Banner */}
        <AIJournalBanner />

        {/* Filter */}
        <MemoFilter 
          activeFilter={activeFilter} 
          onFilterChange={setActiveFilter} 
        />

        {/* Memo List */}
        <div className="space-y-4">
          {sortedMemos.length > 0 ? (
            sortedMemos.map((memo) => (
              <MemoCard
                key={memo.id}
                memo={memo}
                onClick={handleCardClick}
              />
            ))
          ) : (
            <div className="text-center py-12">
              <p className="text-gray-500 text-lg mb-4">메모가 없습니다</p>
              <button
                onClick={handleNewMemo}
                className="text-[#3182f6] hover:text-[#00c299] font-medium"
              >
                첫 번째 메모를 작성해보세요
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Modals */}
      <MemoEditor
        isOpen={isEditorOpen}
        memo={editingMemo}
        onSave={handleSaveMemo}
        onClose={() => {
          setIsEditorOpen(false);
          setEditingMemo(undefined);
        }}
      />

      <MemoDetail
        memo={selectedMemo}
        isOpen={isDetailOpen}
        onClose={handleCloseDetail}
        onEdit={handleEditMemo}
        onDelete={handleDeleteMemo}
      />
    </div>
  );
}