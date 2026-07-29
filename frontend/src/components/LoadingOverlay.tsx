export function LoadingOverlay({ message = 'Generating model…' }: { message?: string }) {
  return (
    <div className="loading-overlay" role="status" aria-live="polite">
      {message}
    </div>
  )
}
