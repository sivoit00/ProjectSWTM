export default function LoadingIndicator() {
  return (
    <div className="flex gap-1 h-5 items-center">
      <div 
        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" 
        style={{ animationDelay: '0ms' }} 
      />
      <div 
        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" 
        style={{ animationDelay: '150ms' }} 
      />
      <div 
        className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" 
        style={{ animationDelay: '300ms' }} 
      />
    </div>
  );
}