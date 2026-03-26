import React, { useState, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import remarkBreaks from "remark-breaks";
import rehypeHighlight from "rehype-highlight";
import rehypeKatex from "rehype-katex";
import "highlight.js/styles/github-dark.css";
import "katex/dist/katex.min.css";

type ChatMessageProps = {
  role: "user" | "assistant";
  content: string;
};


export default function ChatMessage({ role, content }: ChatMessageProps) {
  const isUser = role === "user";
  let safeContent = String(content ?? " ").trim();
  // safeContent = safeContent.replace(/<think\b[^>]*>[\s\S]*?<\/think>/gi, "");

  return (
    <div className="w-full flex justify-center mb-6">
      <div className="w-full max-w-[900px]">
        {isUser ? (
          <div className="flex justify-end">
            <div className="max-w-[75%] px-4 py-3 rounded-2xl bg-blue-500 text-white whitespace-pre-wrap break-words">
              {content}
            </div>
          </div>
        ) : (
          <div className="flex justify-start">
            <div
              className="
                text-left 
                leading-relaxed 
                break-words 
                markdown-body
                prose prose-sm
                dark:prose-invert
                max-w-full
              "
            >
              <ReactMarkdown
                remarkPlugins={[remarkGfm, remarkMath, remarkBreaks]}
                rehypePlugins={[rehypeHighlight, rehypeKatex]}
                components={{
                  // 自定义分割线样式
                  hr: ({ node, ...props }) => (
                    <hr
                      {...props}
                      className="
                        my-8           // 上下边距
                        border-t-2     // 顶部边框，粗细为2
                        border-gray-300 // 灰色边框
                        dark:border-gray-700 // 暗黑模式下的颜色
                      "
                    />
                  ),
                  // 其他自定义组件...
                  pre: PreWithCopyButton,
                  a: ({ node, ...props }) => (
                    <a target="_blank" rel="noopener noreferrer" {...props} />
                  ),
                }}
              >
                {safeContent || " "}
              </ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

/* 其他组件 (PreWithCopyButton) 保持不变 */
function PreWithCopyButton({ children, ...props }: any) {
  const preRef = useRef<HTMLPreElement>(null);
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    if (preRef.current) {
      const text = preRef.current.textContent || "";
      navigator.clipboard.writeText(text).then(() => {
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
      });
    }
  };

  return (
    <div className="relative group my-4">
      <button
        onClick={handleCopy}
        className="
          absolute top-2 right-2 
          px-2 py-1 rounded 
          bg-gray-600 text-xs text-white
          opacity-0 group-hover:opacity-100 
          transition-opacity duration-200
          hover:bg-gray-500
        "
      >
        {copied ? "已复制!" : "复制代码"}
      </button>
      <pre ref={preRef} {...props}>
        {children}
      </pre>
    </div>
  );
}