interface AccuracyCircleProps {
  percentage: number;
  successful: number;
  total: number;
  size?: number;
}

export default function AccuracyCircle({ 
  percentage, 
  successful, 
  total, 
  size = 64 
}: AccuracyCircleProps) {
  const radius = (size - 8) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = circumference;
  const strokeDashoffset = circumference - (percentage / 100) * circumference;

  // Color based on percentage
  const getColor = (pct: number) => {
    if (pct >= 60) return '#22c55e'; // green
    if (pct >= 50) return '#eab308'; // yellow
    return '#ef4444'; // red
  };

  const color = getColor(percentage);

  return (
    <div className="flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg
          width={size}
          height={size}
          className="transform -rotate-90"
        >
          {/* Background circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#e5e7eb"
            strokeWidth="4"
            fill="transparent"
          />
          {/* Progress circle */}
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={color}
            strokeWidth="4"
            fill="transparent"
            strokeDasharray={strokeDasharray}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            className="transition-all duration-300 ease-in-out"
          />
        </svg>
        {/* Percentage text in center */}
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xl font-bold" style={{ color }}>
            {percentage}%
          </span>
        </div>
      </div>
      {/* Success rate below circle */}
      <span className="text-sm text-gray-600 mt-1">
        {successful}/{total}
      </span>
    </div>
  );
}