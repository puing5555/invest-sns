import { useState, useEffect } from 'react';
import { MemoData } from '@/data/memoData';

interface MemoEditorProps {
  isOpen: boolean;
  memo?: MemoData;
  onSave: (memo: Omit<MemoData, 'id'>) => void;
  onClose: () => void;
}

export default function MemoEditor({ isOpen, memo, onSave, onClose }: MemoEditorProps) {
  const [formData, setFormData] = useState<{
    stock: string;
    title: string;
    content: string;
    tag: '매수근거' | '매도근거' | '관찰' | 'AI일지';
  }>({
    stock: '',
    title: '',
    content: '',
    tag: '매수근거',
  });

  const stockOptions = [
    { value: '', label: '종목 선택 (선택사항)' },
    { value: '에코프로', label: '에코프로' },
    { value: '삼성전자', label: '삼성전자' },
    { value: 'SK하이닉스', label: 'SK하이닉스' },
    { value: '아이빔테크놀로지', label: '아이빔테크놀로지' },
    { value: 'HD한국조선해양', label: 'HD한국조선해양' },
    { value: '카카오', label: '카카오' },
  ];

  const tagOptions = [
    { id: '매수근거', label: '매수근거', icon: '📗' },
    { id: '매도근거', label: '매도근거', icon: '📕' },
    { id: '관찰', label: '관찰', icon: '📒' },
    { id: 'AI일지', label: '아이디어', icon: '💡' }, // Changed from AI일지 to 아이디어 as specified
  ];

  useEffect(() => {
    if (memo) {
      setFormData({
        stock: memo.stock || '',
        title: memo.title,
        content: memo.content,
        tag: memo.tag,
      });
    } else {
      setFormData({
        stock: '',
        title: '',
        content: '',
        tag: '매수근거',
      });
    }
  }, [memo, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const tagIcon = tagOptions.find(t => t.id === formData.tag)?.icon || '📗';
    const currentDate = new Date().toLocaleDateString('ko-KR').replace(/\. /g, '.').replace(/\.$/, '');
    
    onSave({
      stock: formData.stock || null,
      title: formData.title,
      content: formData.content,
      tag: formData.tag,
      tagIcon,
      date: currentDate,
      attachments: [], // Empty for now since attachments are non-functional
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-gray-900">
              {memo ? '메모 수정' : '새 메모 작성'}
            </h2>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-xl"
            >
              ✕
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Stock Selector */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                종목
              </label>
              <select
                value={formData.stock}
                onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
              >
                {stockOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Title */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                제목 *
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
                placeholder="메모 제목을 입력하세요"
              />
            </div>

            {/* Content */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                내용 *
              </label>
              <textarea
                required
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                className="w-full border border-gray-300 rounded-lg px-3 py-2 min-h-[120px] resize-none focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
                placeholder="메모 내용을 입력하세요"
              />
            </div>

            {/* Tag Selector */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                태그
              </label>
              <div className="flex gap-2">
                {tagOptions.map((tag) => (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, tag: tag.id as '매수근거' | '매도근거' | '관찰' | 'AI일지' })}
                    className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 ${
                      formData.tag === tag.id
                        ? 'bg-[#3182f6] text-white'
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    {tag.icon} {tag.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Attachment Buttons */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                첨부 자료
              </label>
              <div className="flex gap-2 flex-wrap">
                <button
                  type="button"
                  className="bg-blue-50 text-blue-600 px-4 py-2 rounded-lg font-medium hover:bg-blue-100 transition-colors flex items-center gap-2"
                >
                  📋 공시 연결
                </button>
                <button
                  type="button"
                  className="bg-green-50 text-green-600 px-4 py-2 rounded-lg font-medium hover:bg-green-100 transition-colors flex items-center gap-2"
                >
                  🎯 리포트 연결
                </button>
                <button
                  type="button"
                  className="bg-purple-50 text-purple-600 px-4 py-2 rounded-lg font-medium hover:bg-purple-100 transition-colors flex items-center gap-2"
                >
                  👤 인플콜 연결
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2 text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
              >
                취소
              </button>
              <button
                type="submit"
                className="px-6 py-2 bg-[#3182f6] text-white rounded-lg hover:bg-[#00c299] transition-colors"
              >
                저장
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}