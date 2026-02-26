'use client';

import { useState } from 'react';
import LabGrid from '@/components/lab/LabGrid';
import DailyIdea from '@/components/lab/DailyIdea';
import BacktestBuilder from '@/components/lab/BacktestBuilder';
import QuantBot from '@/components/lab/QuantBot';
import InfluencerSim from '@/components/lab/InfluencerSim';
import SwingLab from '@/components/lab/SwingLab';
import LongTermIdea from '@/components/lab/LongTermIdea';

type ActiveView = null | 'daily' | 'backtest' | 'quant' | 'influencer' | 'swing' | 'longterm';

export default function LabPage() {
  const [activeView, setActiveView] = useState<ActiveView>(null);

  const handleCardClick = (cardId: string) => {
    setActiveView(cardId as ActiveView);
  };

  const handleBack = () => {
    setActiveView(null);
  };

  // Render the appropriate view
  const renderActiveView = () => {
    switch (activeView) {
      case 'daily':
        return <DailyIdea onBack={handleBack} />;
      case 'backtest':
        return <BacktestBuilder onBack={handleBack} />;
      case 'quant':
        return <QuantBot onBack={handleBack} />;
      case 'influencer':
        return <InfluencerSim onBack={handleBack} />;
      case 'swing':
        return <SwingLab onBack={handleBack} />;
      case 'longterm':
        return <LongTermIdea onBack={handleBack} />;
      default:
        return <LabGrid onCardClick={handleCardClick} />;
    }
  };

  return (
    <div>
      {renderActiveView()}
    </div>
  );
}