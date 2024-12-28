"use client";

import { useState, useRef, useEffect } from "react";
import Draggable from "react-draggable";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { 
  MessageCircle, 
  Send, 
  Trash2, 
  History, 
  FileText,
  Minimize2,
  Maximize2,
  X,
  LogOut
} from "lucide-react";
import { LoginForm } from "./LoginForm";
import { useSession } from "@/hooks/useSession";
import { chatService, type ChatMessage } from "@/lib/services/chatService";

export const ChatWindow = () => {
  const { isAuthenticated, employee, login, logout } = useSession();
  const [message, setMessage] = useState("");
  const [isMinimized, setIsMinimized] = useState(false);
  const [isMaximized, setIsMaximized] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [showHistory, setShowHistory] = useState(false);

  // Load chat history when user logs in
  useEffect(() => {
    if (isAuthenticated && employee) {
      loadChatHistory();
    }
  }, [isAuthenticated, employee]);

  const loadChatHistory = async () => {
    if (!employee) return;
    const history = await chatService.getHistory(employee.employee_id);
    if (history.length > 0) {
      setMessages(history);
    }
  };

  const handleSend = () => {
    if (!message.trim() || !isAuthenticated) return;

    const newMessage: ChatMessage = {
      id: Date.now().toString(),
      text: message,
      sender: "user",
      timestamp: new Date(),
    };

    setMessages([...messages, newMessage]);
    setMessage("");

    // TODO: Send message to backend/API
    // TODO: Handle assistant response
  };

  const handleClear = () => {
    setMessage("");
    setMessages([]);
    if (employee) {
      chatService.saveHistory({
        employee_id: employee.employee_id,
        messages: [],
        timestamp: new Date(),
      });
    }
  };

  const handleHistory = async () => {
    setShowHistory(!showHistory);
    if (!showHistory && employee) {
      await loadChatHistory();
    }
  };

  const handlePolicy = () => {
    // TODO: Implement policy functionality
  };

  const toggleMinimize = () => {
    setIsMinimized(!isMinimized);
    if (isMaximized) setIsMaximized(false);
  };

  const toggleMaximize = () => {
    setIsMaximized(!isMaximized);
    if (isMinimized) setIsMinimized(false);
  };

  const handleClose = async () => {
    // Save chat history before closing
    if (isAuthenticated && employee && messages.length > 0) {
      await chatService.saveHistory({
        employee_id: employee.employee_id,
        messages,
        timestamp: new Date(),
      });
    }
    logout();
    setMessages([]);
  };

  if (!isAuthenticated) {
    return (
      <div className="fixed bottom-4 right-4 bg-white rounded-lg shadow-xl border border-gray-200 w-96">
        <div className="p-4 border-b bg-primary text-primary-foreground rounded-t-lg">
          <h2 className="text-lg font-semibold">Login Required</h2>
        </div>
        <LoginForm onLogin={login} />
      </div>
    );
  }

  return (
    <Draggable handle=".drag-handle" disabled={isMaximized}>
      <div
        className={`fixed bottom-4 right-4 bg-white rounded-lg shadow-xl border border-gray-200 transition-all duration-300 ${
          isMaximized
            ? "w-full h-full top-0 left-0 m-0"
            : isMinimized
            ? "w-72 h-12"
            : "w-96 h-[600px]"
        }`}
      >
        {/* Header */}
        <div className="drag-handle flex items-center justify-between p-4 border-b cursor-move bg-primary text-primary-foreground rounded-t-lg">
          <div className="flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            <div className="flex flex-col">
              <span className="font-semibold">HSA/FSA/COBRA Assistant</span>
              {!isMinimized && (
                <span className="text-xs opacity-80">
                  Logged in as: {employee?.name}
                </span>
              )}
            </div>
          </div>
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={toggleMinimize}
            >
              <Minimize2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6"
              onClick={toggleMaximize}
            >
              <Maximize2 className="h-4 w-4" />
            </Button>
            <Button
              variant="ghost"
              size="icon"
              className="h-6 w-6 hover:bg-red-500 hover:text-white"
              onClick={handleClose}
            >
              <X className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Chat Content */}
        {!isMinimized && (
          <>
            <div className="flex-1 p-4 overflow-y-auto h-[calc(100%-8rem)]">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`mb-4 ${
                    msg.sender === "user" ? "text-right" : "text-left"
                  }`}
                >
                  <div
                    className={`inline-block p-3 rounded-lg ${
                      msg.sender === "user"
                        ? "bg-primary text-primary-foreground"
                        : "bg-muted"
                    }`}
                  >
                    {msg.text}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {new Date(msg.timestamp).toLocaleTimeString()}
                  </div>
                </div>
              ))}
            </div>

            {/* Input Area */}
            <div className="absolute bottom-0 left-0 right-0 p-4 border-t bg-background">
              <div className="flex gap-2">
                <Input
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Type your message..."
                  className="flex-1"
                  onKeyPress={(e) => e.key === "Enter" && handleSend()}
                />
                <Button onClick={handleSend} size="icon">
                  <Send className="h-4 w-4" />
                </Button>
              </div>
              <div className="flex justify-between mt-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleClear}
                  className="flex items-center gap-1"
                >
                  <Trash2 className="h-4 w-4" />
                  Clear
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleHistory}
                  className="flex items-center gap-1"
                >
                  <History className="h-4 w-4" />
                  History
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handlePolicy}
                  className="flex items-center gap-1"
                >
                  <FileText className="h-4 w-4" />
                  Policy
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={logout}
                  className="flex items-center gap-1"
                >
                  <LogOut className="h-4 w-4" />
                  Logout
                </Button>
              </div>
            </div>
          </>
        )}
      </div>
    </Draggable>
  );
}; 