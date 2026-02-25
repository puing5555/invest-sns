interface SignalBadgeProps {
  icon: string;
  label: string;
}

export default function SignalBadge({ icon, label }: SignalBadgeProps) {
  return (
    <span className="inline-flex items-center gap-1 px-2 py-1 bg-[#f2f4f6] rounded-full text-xs font-medium">
      <span>{icon}</span>
      <span>{label}</span>
    </span>
  );
}