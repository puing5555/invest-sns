'use client';

import { Sector } from '../data/guruData';

interface SectorPieChartProps {
  sectors: Sector[];
}

export default function SectorPieChart({ sectors }: SectorPieChartProps) {
  const size = 160;
  const radius = 60;
  const centerX = size / 2;
  const centerY = size / 2;
  const strokeWidth = 20;

  let cumulativePercentage = 0;
  
  const createArcPath = (startAngle: number, endAngle: number, radius: number) => {
    const start = polarToCartesian(centerX, centerY, radius, endAngle);
    const end = polarToCartesian(centerX, centerY, radius, startAngle);
    const largeArcFlag = endAngle - startAngle <= 180 ? "0" : "1";
    
    return [
      "M", start.x, start.y, 
      "A", radius, radius, 0, largeArcFlag, 0, end.x, end.y
    ].join(" ");
  };

  const polarToCartesian = (centerX: number, centerY: number, radius: number, angleInDegrees: number) => {
    const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0;
    return {
      x: centerX + (radius * Math.cos(angleInRadians)),
      y: centerY + (radius * Math.sin(angleInRadians))
    };
  };

  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size} className="mb-4">
        <circle 
          cx={centerX} 
          cy={centerY} 
          r={radius} 
          fill="none" 
          stroke="#e5e7eb" 
          strokeWidth={strokeWidth}
        />
        
        {sectors.map((sector) => {
          const startAngle = cumulativePercentage * 3.6; // Convert to degrees
          const endAngle = (cumulativePercentage + sector.pct) * 3.6;
          cumulativePercentage += sector.pct;

          const arcPath = createArcPath(startAngle, endAngle, radius);
          
          return (
            <path
              key={sector.name}
              d={arcPath}
              fill="none"
              stroke={sector.color}
              strokeWidth={strokeWidth}
              strokeLinecap="round"
            />
          );
        })}
      </svg>
      
      <div className="grid grid-cols-1 gap-2 w-full">
        {sectors.map((sector) => (
          <div key={sector.name} className="flex items-center justify-between text-sm">
            <div className="flex items-center gap-2">
              <div 
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: sector.color }}
              />
              <span className="text-gray-700">{sector.name}</span>
            </div>
            <span className="font-medium text-[#191f28]">{sector.pct}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}