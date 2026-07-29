interface BadgeProps {
  variant: 'matcha' | 'dark-red' | 'orange' | 'okra' | 'brown';
  children: string;
}

const VARIANT_CLASSES = {
  matcha: 'badge-matcha',
  'dark-red': 'badge-dark-red',
  orange: 'badge-orange',
  okra: 'badge-okra',
  brown: 'badge-brown',
} as const;

export function Badge({ variant, children }: BadgeProps) {
  return (
    <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${VARIANT_CLASSES[variant]}`}>
      {children}
    </span>
  );
}
