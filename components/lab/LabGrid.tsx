import { labCards } from '@/data/labData';
import LabCard from './LabCard';

interface LabGridProps {
  onCardClick: (cardId: string) => void;
}

export default function LabGrid({ onCardClick }: LabGridProps) {
  return (
    <div className="min-h-screen bg-white p-6">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-[#191f28] mb-2">?„ëµ?°êµ¬??/h1>
          <p className="text-[#6b7280]">AI?€ ì»¤ë??ˆí‹°ê°€ ?¨ê»˜ ë§Œë“œ???¬ì ?„ì´?”ì–´</p>
        </div>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {labCards.map((card) => (
            <LabCard
              key={card.id}
              icon={card.icon}
              iconBgColor={card.iconBgColor}
              title={card.title}
              description={card.description}
              badge={card.badge}
              badgeColor={card.badgeColor}
              onClick={() => onCardClick(card.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}