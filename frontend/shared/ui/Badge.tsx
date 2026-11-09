// frontend/shared/ui/Badge.tsx
import {cn} from '@/shared/lib/utils';

interface BadgeProps {
    variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
    children: React.ReactNode;
    className?: string;
}

export const Badge = ({variant = 'default', children, className}: BadgeProps) => {
    const variants = {
        default: 'bg-slate-800 text-slate-300 border-slate-700',
        primary: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        success: 'bg-green-500/10 text-green-400 border-green-500/20',
        warning: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
        danger: 'bg-red-500/10 text-red-400 border-red-500/20'
    };

    return (
        <span className={cn(
            'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold border',
            variants[variant],
            className
        )}>
      {children}
    </span>
    );
};