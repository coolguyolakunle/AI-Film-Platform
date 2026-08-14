export default function LoadingSpinner({ label = "Loading...", size = "md" }) {
  const sizeClasses = { sm: "h-4 w-4", md: "h-8 w-8", lg: "h-12 w-12" };

  return (
    <div className="flex flex-col items-center justify-center gap-3 py-10 text-gray-500">
      <span
        className={`animate-spin rounded-full border-4 border-brand-200 border-t-brand-600 ${sizeClasses[size]}`}
      />
      {label && <span className="text-sm">{label}</span>}
    </div>
  );
}
