import { MemoData } from '@/data/memoData';

interface MemoDetailProps {
  memo: MemoData | null;
  isOpen: boolean;
  onClose: () => void;
  onEdit: (memo: MemoData) => void;
  onDelete: (id: number) => void;
}

export default function MemoDetail({ memo, isOpen, onClose, onEdit, onDelete }: MemoDetailProps) {
  if (!memo || !isOpen) return null;

  const getAttachmentIcon = (type: string) => {
    switch (type) {
      case 'Í≥µÏãú': return '?ìã';
      case '?†ÎÑêÎ¶¨Ìè¨??: return '?éØ';
      case '?∏ÌîåÎ£®Ïñ∏?úÏΩú': return '?ë§';
      default: return '?ìÑ';
    }
  };

  const handleShare = () => {
    // Non-functional for now
    alert('Í≥µÏú† Í∏∞Îä•?Ä Í∞úÎ∞ú Ï§ëÏûÖ?àÎã§.');
  };

  const handleDelete = () => {
    if (confirm('??Î©îÎ™®Î•???†ú?òÏãúÍ≤†Ïäµ?àÍπå?')) {
      onDelete(memo.id);
      onClose();
    }
  };

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-20 z-40 transition-opacity"
        onClick={onClose}
      />
      
      {/* Slide-in Panel */}
      <div className={`fixed right-0 top-0 h-full w-[400px] bg-white shadow-xl z-50 transform transition-transform duration-300 ease-in-out ${
        isOpen ? 'translate-x-0' : 'translate-x-full'
      }`}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-200">
            <h2 className="text-lg font-bold text-[#191f28]">Î©îÎ™® ?ÅÏÑ∏</h2>
            <button
              onClick={onClose}
              className="text-[#8b95a1] hover:text-gray-600 text-xl"
            >
              ??
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-6">
            {/* Stock and Date */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                {memo.stock && (
                  <span className="bg-[#f2f4f6] text-gray-700 px-3 py-1 rounded-full text-sm font-medium">
                    {memo.stock}
                  </span>
                )}
                {memo.isAI && (
                  <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded text-xs font-medium">
                    ?êÎèô ?ùÏÑ±
                  </span>
                )}
              </div>
              <span className="text-[#8b95a1] text-sm">{memo.date}</span>
            </div>

            {/* Tag */}
            <div className="mb-4">
              <span className="bg-[#f2f4f6] text-gray-700 px-3 py-2 rounded-full text-sm font-medium flex items-center gap-2 inline-flex">
                {memo.tagIcon} {memo.tag}
              </span>
            </div>

            {/* Title */}
            <h3 className="text-xl font-bold text-[#191f28] mb-4">{memo.title}</h3>

            {/* Content */}
            <div className="text-gray-700 mb-6 whitespace-pre-wrap">
              {memo.content}
            </div>

            {/* Attachments */}
            {memo.attachments.length > 0 && (
              <div className="mb-6">
                <h4 className="text-sm font-medium text-gray-700 mb-3">Ï≤®Î? ?êÎ£å</h4>
                <div className="space-y-2">
                  {memo.attachments.map((attachment, index) => (
                    <div
                      key={index}
                      className="bg-[#f2f4f6] border border-gray-200 rounded-2xl p-3 flex items-center gap-3"
                    >
                      <span className="text-lg">
                        {getAttachmentIcon(attachment.type)}
                      </span>
                      <div>
                        <p className="font-medium text-[#191f28] text-sm">{attachment.label}</p>
                        <p className="text-[#8b95a1] text-xs">{attachment.type}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Footer Actions */}
          <div className="border-t border-gray-200 p-6">
            <div className="flex gap-2">
              <button
                onClick={() => onEdit(memo)}
                className="flex-1 bg-[#3182f6] text-white py-2 px-4 rounded-2xl font-medium hover:bg-[#00c299] transition-colors"
              >
                ?òÏ†ï
              </button>
              <button
                onClick={handleDelete}
                className="flex-1 bg-red-500 text-white py-2 px-4 rounded-2xl font-medium hover:bg-red-600 transition-colors"
              >
                ??†ú
              </button>
              <button
                onClick={handleShare}
                className="flex-1 bg-[#f2f4f6] text-gray-700 py-2 px-4 rounded-2xl font-medium hover:bg-gray-200 transition-colors"
              >
                Í≥µÏú†
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}