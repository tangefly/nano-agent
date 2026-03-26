"use client";

import { useState } from "react";
import ChatMessage from "@/components/ChatMessage";
import ChatInput from "@/components/ChatInput";
import { streamChat } from "@/lib/stream";
import Terminal from "@/components/Terminal";

export default function Page() {
  const [messages, setMessages] = useState<any[]>([]);
  const [input, setInput] = useState("");
  const [status, setStatus] = useState("");
  const [terminalOutput, setTerminalOutput] = useState("");
  const [loading, setLoading] = useState(false);
  const [currentCmd, setCurrentCmd] = useState("");
  const [currentCwd, setCurrentCwd] = useState("");


  const sendMessage = async () => {
    if (!input.trim()) return;

    const newMessages = [
      ...messages,
      { role: "user", content: input },
    ];

    setMessages(newMessages);
    setInput("");
    setLoading(true);

    let assistantMessage = "";

    // 每次发送前清空状态
    setStatus("");
    setTerminalOutput("");

    await streamChat(newMessages, (event) => {
      if (event.type === "chat") {
        assistantMessage += event.content;

        setMessages([
          ...newMessages,
          { role: "assistant", content: assistantMessage },
        ]);
      }

      if (event.type === "tool_start") {
        setCurrentCmd(event.cmd);
        setCurrentCwd(event.cwd);
        setTerminalOutput("");
      }

      if (event.type === "status") {
        setStatus(event.content);
      }

      if (event.type === "terminal") {
        setTerminalOutput((prev) => prev + event.content);
      }

      if (event.type === "tool_end") {
        // 可以标记完成（后面再优化）
      }
    });

    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-gray-100 flex flex-col">
      {/* 消息区 */}
      <div className="flex-1 overflow-y-auto p-4">
        {messages.map((m, i) => (
          <ChatMessage key={i} {...m} />
        ))}
        {loading && (
          <div className="w-full flex justify-center mb-6">
            <div className="w-full max-w-[900px]">
              <div className="flex justify-start">
                <div className="text-gray-500 dark:text-gray-400">
                  🤖 正在思考...
                </div>
              </div>
            </div>
          </div>
        )}
        {status && (
          <div className="w-full flex justify-center mb-2">
            <div className="w-full max-w-[900px] text-blue-500 text-sm">
              ⚙️ {status}
            </div>
          </div>
        )}

        {terminalOutput && (
          <div className="w-full flex justify-center mb-4">
            <div className="w-full max-w-[900px]">
              <Terminal
                output={terminalOutput}
                cmd={currentCmd}
                cwd={currentCwd}
              />
            </div>
          </div>
        )}
      </div>

      {/* 输入框固定在底部 */}
      <div className="p-4">
        <ChatInput
          input={input}
          setInput={setInput}
          onSend={sendMessage}
        />
      </div>
    </div>
  );
}
