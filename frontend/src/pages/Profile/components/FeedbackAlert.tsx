type Props = {
  success: string | null;
  error: string | null;
};

export function FeedbackAlert({ success, error }: Props) {
  return (
    <>
      {success && (
        <div className="bg-green-900/40 border border-green-500/60 text-green-200 px-4 py-2 rounded">
          {success}
        </div>
      )}
      {error && (
        <div className="bg-red-900/40 border border-red-500/60 text-red-200 px-4 py-2 rounded">
          {error}
        </div>
      )}
    </>
  );
}
