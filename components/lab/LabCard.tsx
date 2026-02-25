interface LabCardProps {
  icon: string;
  iconBgColor: string;
  title: string;
  description: string;
  badge: string;
  badgeColor: string;
  onClick: () => void;
}

export default function LabCard({
  icon,
  iconBgColor,
  title,
  description,
  badge,
  badgeColor,
  onClick
}: LabCardProps) {
  return (
    <div
      className="bg-[#25253e] p-6 rounded-xl cursor-pointer transition-all hover:border hover:border-[#00d4aa] hover:shadow-lg hover:shadow-[#00d4aa]/20"
      onClick={onClick}
    >
      {/* Icon */}
      <div className={`w-12 h-12 ${iconBgColor} rounded-full flex items-center justify-center mb-4`}>
        <span className="text-2xl">{icon}</span>
      </div>

      {/* Content */}
      <div className="space-y-3">
        <h3 className="text-lg font-bold text-white">{title}</h3>
        <p className="text-sm text-gray-400 leading-relaxed">{description}</p>
        
        {/* Badge */}
        <div className="flex">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${badgeColor}`}>
            {badge}
          </span>
        </div>
      </div>
    </div>
  );
}