import { useNavigate } from "react-router-dom";
import { MessageSquare, Clock, Shield } from "lucide-react";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="flex flex-col items-center justify-center h-screen p-8 text-white overflow-y-auto">
      <div className="max-w-4xl w-full space-y-12">
        {/* Hero Section */}
        <div className="text-center space-y-4">
          <h1 className="text-5xl font-bold">
            Welcome to <span className="text-blue-400">MyClone</span>
          </h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto">
            Your intelligent assistant for vehicle maintenance and service management. Let our AI handle everything for you with simple conversations.
          </p>
          <button
            onClick={() => navigate("/chat")}
            className="mt-6 inline-flex items-center gap-2 px-8 py-4 bg-blue-600 hover:bg-blue-700 rounded-lg text-lg font-semibold shadow-lg transition transform hover:scale-105"
          >
            <MessageSquare size={24} />
            Start Chat Now
          </button>
        </div>

        {/* Features */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 hover:border-blue-500/40 transition">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
              <MessageSquare className="text-white" size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-2">AI-Powered</h3>
            <p className="text-gray-300">
              Chat with our intelligent AI assistant that understands your vehicle service needs and handles everything automatically.
            </p>
          </div>

          <div className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 hover:border-blue-500/40 transition">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
              <Clock className="text-white" size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Save Time</h3>
            <p className="text-gray-300">
              No complex forms or navigation. Simply describe what you need, and our AI takes care of the rest instantly.
            </p>
          </div>

          <div className="bg-blue-900/30 backdrop-blur-sm border border-blue-500/20 rounded-xl p-6 hover:border-blue-500/40 transition">
            <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center mb-4">
              <Shield className="text-white" size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-2">Simple & Secure</h3>
            <p className="text-gray-300">
              Easy-to-use interface designed for everyone. Your data is protected with enterprise-grade security.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to get started?</h2>
          <p className="text-lg text-blue-100 mb-6">
            Experience the future of vehicle service management. Chat with our AI and let it handle your requests in seconds.
          </p>
          <button
            onClick={() => navigate("/chat")}
            className="inline-flex items-center gap-2 px-8 py-3 bg-white text-blue-600 hover:bg-gray-100 rounded-lg font-semibold shadow-lg transition"
          >
            <MessageSquare size={20} />
            Open Chat Assistant
          </button>
        </div>
      </div>
    </div>
  );
}
