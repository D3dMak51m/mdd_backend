// frontend/shared/ui/Skeleton.tsx
export const Skeleton = ({className}: { className?: string }) => (
    <div className={`bg-slate-800 animate-pulse rounded ${className}`}/>
);