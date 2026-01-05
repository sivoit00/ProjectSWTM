type Props = {
  success: string | null;
  error: string | null;
};

export function FeedbackAlert({ success, error }: Props) {
  return (
    <>
      {success && (
        <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-2 rounded dark:bg-green-900/40 dark:border-green-500/60 dark:text-green-200">
          {success}
        </div>
      )}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-2 rounded dark:bg-red-900/40 dark:border-red-500/60 dark:text-red-200">
          {error}
        </div>
      )}
    </>
  );
}
