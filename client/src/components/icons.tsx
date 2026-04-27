import type { PropsWithChildren } from 'react';

type IconProps = {
  size?: number;
};

function Icon({ children, size = 12 }: PropsWithChildren<IconProps>) {
  return (
    <svg width={size} height={size} viewBox="0 0 16 16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      {children}
    </svg>
  );
}

export function CheckIcon(props: IconProps) {
  return <Icon {...props}><path d="M3 8.5l3 3L13 5" /></Icon>;
}

export function DeleteIcon(props: IconProps) {
  return <Icon {...props}><path d="M3 3l10 10M13 3L3 13" /></Icon>;
}

export function ContinueIcon(props: IconProps) {
  return <Icon {...props}><path d="M4 4l4 4-4 4" /><path d="M9 4l4 4-4 4" /></Icon>;
}

export function ChevronLeftIcon(props: IconProps) {
  return <Icon {...props}><path d="M10 12L6 8l4-4" /></Icon>;
}

export function ChevronRightIcon(props: IconProps) {
  return <Icon {...props}><path d="M6 4l4 4-4 4" /></Icon>;
}

export function PlusIcon(props: IconProps) {
  return <Icon {...props}><path d="M8 3v10M3 8h10" /></Icon>;
}

export function EditIcon(props: IconProps) {
  return <Icon {...props}><path d="M12 2l2 2-9 9-3 1 1-3 9-9z" /></Icon>;
}

export function MoveIcon(props: IconProps) {
  return <Icon {...props}><path d="M3 8h10M9 4l4 4-4 4" /></Icon>;
}
