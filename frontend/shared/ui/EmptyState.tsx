// frontend/shared/ui/EmptyState.tsx
export const EmptyState = ({icon: Icon, title, description, action}: any) => (
    <div className="flex flex-col items-center justify-center py-12 text-center">
        <div className="h-16 w-16 rounded-full bg-slate-800 flex items-center justify-center mb-4">
            <Icon size={32} className="text-slate-600"/>
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">{title}</h3>
        <p className="text-sm text-slate-400 mb-6">{description}</p>
        {action}
    </div>
);