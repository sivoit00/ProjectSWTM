interface ErrorMessageProps {
  message: string;
}

export default function ErrorMessage({ message }: ErrorMessageProps) {
  return (
    <div className="bg-red-900/20 border border-red-500 text-red-200 px-6 py-4 rounded-lg">
      <p className="font-medium">❌ Fehler</p>
      <p className="text-sm mt-1">{message}</p>
    </div>
  );
}
