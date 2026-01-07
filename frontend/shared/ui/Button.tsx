// frontend/shared/ui/Button.tsx
import React from 'react';
import {Loader2} from 'lucide-react';
import {cn} from '@/shared/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'danger' | 'success' | 'ghost';
    size?: 'sm' | 'md' | 'lg';
    loading?: boolean;
    icon?: React.ComponentType<{ size?: number }>;
}

export const Button = ({
                           variant = 'primary',
                           size = 'md',
                           loading = false,
                           icon: Icon,
                           children,
                           className,
                           disabled,
                           ...props
                       }: ButtonProps) => {
    const baseClasses = 'inline-flex items-center justify-center gap-2 font-semibold rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950';

    const variants = {
        primary: 'bg-blue-600 text-white hover:bg-blue-500 active:bg-blue-700 focus:ring-blue-500 shadow-lg shadow-blue-900/20',
        secondary: 'bg-slate-800 text-white hover:bg-slate-700 active:bg-slate-900 focus:ring-slate-500',
        danger: 'bg-red-600 text-white hover:bg-red-500 active:bg-red-700 focus:ring-red-500 shadow-lg shadow-red-900/20',
        success: 'bg-green-600 text-white hover:bg-green-500 active:bg-green-700 focus:ring-green-500 shadow-lg shadow-green-900/20',
        ghost: 'text-slate-300 hover:bg-slate-800 active:bg-slate-900 focus:ring-slate-500'
    };

    const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2.5 text-sm',
        lg: 'px-6 py-3 text-base'
    };

    return (
        <button
            className={cn(baseClasses, variants[variant], sizes[size], className)}
            disabled={loading || disabled}
            {...props}
        >
            {loading ? (
                <Loader2 size={18} className="animate-spin"/>
            ) : Icon ? (
                <Icon size={18}/>
            ) : null}
            {children}
        </button>
    );
};