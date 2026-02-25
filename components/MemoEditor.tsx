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
    tag: 'Îß§ÏàòÍ∑ºÍ±∞' | 'Îß§ÎèÑÍ∑ºÍ±∞' | 'Í¥ÄÏ∞? | 'AI?ºÏ?';
  }>({
    stock: '',
    title: '',
    content: '',
    tag: 'Îß§ÏàòÍ∑ºÍ±∞',
  });

  const stockOptions = [
    { value: '', label: 'Ï¢ÖÎ™© ?†ÌÉù (?†ÌÉù?¨Ìï≠)' },
    { value: '?êÏΩî?ÑÎ°ú', label: '?êÏΩî?ÑÎ°ú' },
    { value: '?ºÏÑ±?ÑÏûê', label: '?ºÏÑ±?ÑÏûê' },
    { value: 'SK?òÏù¥?âÏä§', label: 'SK?òÏù¥?âÏä§' },
    { value: '?ÑÏù¥ÎπîÌÖå?¨Î?Î°úÏ?', label: '?ÑÏù¥ÎπîÌÖå?¨Î?Î°úÏ?' },
    { value: 'HD?úÍµ≠Ï°∞ÏÑ†?¥Ïñë', label: 'HD?úÍµ≠Ï°∞ÏÑ†?¥Ïñë' },
    { value: 'Ïπ¥Ïπ¥??, label: 'Ïπ¥Ïπ¥?? },
  ];

  const tagOptions = [
    { id: 'Îß§ÏàòÍ∑ºÍ±∞', label: 'Îß§ÏàòÍ∑ºÍ±∞', icon: '?ìó' },
    { id: 'Îß§ÎèÑÍ∑ºÍ±∞', label: 'Îß§ÎèÑÍ∑ºÍ±∞', icon: '?ìï' },
    { id: 'Í¥ÄÏ∞?, label: 'Í¥ÄÏ∞?, icon: '?ìí' },
    { id: 'AI?ºÏ?', label: '?ÑÏù¥?îÏñ¥', icon: '?í°' }, // Changed from AI?ºÏ? to ?ÑÏù¥?îÏñ¥ as specified
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
        tag: 'Îß§ÏàòÍ∑ºÍ±∞',
      });
    }
  }, [memo, isOpen]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const tagIcon = tagOptions.find(t => t.id === formData.tag)?.icon || '?ìó';
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
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-bold text-[#191f28]">
              {memo ? 'Î©îÎ™® ?òÏ†ï' : '??Î©îÎ™® ?ëÏÑ±'}
            </h2>
            <button
              onClick={onClose}
              className="text-[#8b95a1] hover:text-gray-600 text-xl"
            >
              ??
            </button>
          </div>

          <form onSubmit={handleSubmit}>
            {/* Stock Selector */}
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Ï¢ÖÎ™©
              </label>
              <select
                value={formData.stock}
                onChange={(e) => setFormData({ ...formData, stock: e.target.value })}
                className="w-full border border-gray-300 rounded-2xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
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
                ?úÎ™© *
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full border border-gray-300 rounded-2xl px-3 py-2 focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
                placeholder="Î©îÎ™® ?úÎ™©???ÖÎ†•?òÏÑ∏??
              />
            </div>

            {/* Content */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ?¥Ïö© *
              </label>
              <textarea
                required
                value={formData.content}
                onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                className="w-full border border-gray-300 rounded-2xl px-3 py-2 min-h-[120px] resize-none focus:outline-none focus:ring-2 focus:ring-[#3182f6] focus:border-transparent"
                placeholder="Î©îÎ™® ?¥Ïö©???ÖÎ†•?òÏÑ∏??
              />
            </div>

            {/* Tag Selector */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">
                ?úÍ∑∏
              </label>
              <div className="flex gap-2">
                {tagOptions.map((tag) => (
                  <button
                    key={tag.id}
                    type="button"
                    onClick={() => setFormData({ ...formData, tag: tag.id as 'Îß§ÏàòÍ∑ºÍ±∞' | 'Îß§ÎèÑÍ∑ºÍ±∞' | 'Í¥ÄÏ∞? | 'AI?ºÏ?' })}
                    className={`px-4 py-2 rounded-2xl font-medium flex items-center gap-2 ${
                      formData.tag === tag.id
                        ? 'bg-[#3182f6] text-white'
                        : 'bg-[#f2f4f6] text-gray-700 hover:bg-gray-200'
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
                Ï≤®Î? ?êÎ£å
              </label>
              <div className="flex gap-2 flex-wrap">
                <button
                  type="button"
                  className="bg-blue-50 text-blue-600 px-4 py-2 rounded-2xl font-medium hover:bg-blue-100 transition-colors flex items-center gap-2"
                >
                  ?ìã Í≥µÏãú ?∞Í≤∞
                </button>
                <button
                  type="button"
                  className="bg-green-50 text-green-600 px-4 py-2 rounded-2xl font-medium hover:bg-green-100 transition-colors flex items-center gap-2"
                >
                  ?éØ Î¶¨Ìè¨???∞Í≤∞
                </button>
                <button
                  type="button"
                  className="bg-purple-50 text-purple-600 px-4 py-2 rounded-2xl font-medium hover:bg-purple-100 transition-colors flex items-center gap-2"
                >
                  ?ë§ ?∏ÌîåÏΩ??∞Í≤∞
                </button>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-3 justify-end">
              <button
                type="button"
                onClick={onClose}
                className="px-6 py-2 text-gray-600 bg-[#f2f4f6] rounded-2xl hover:bg-gray-200 transition-colors"
              >
                Ï∑®ÏÜå
              </button>
              <button
                type="submit"
                className="px-6 py-2 bg-[#3182f6] text-white rounded-2xl hover:bg-[#00c299] transition-colors"
              >
                ?Ä??
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}