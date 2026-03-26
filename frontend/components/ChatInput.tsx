export default function ChatInput({
  input,
  setInput,
  onSend,
}: {
  input: string;
  setInput: (v: string) => void;
  onSend: () => void;
}) {
  return (
    /* ✅ 关键：和 ChatMessage 一样的容器 */
    <div className="w-full flex justify-center mt-4">
      <div className="w-full max-w-[900px]">
        
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onInput={(e) => {
              const el = e.currentTarget;

              el.style.height = "auto"; // 先重置
              const lineHeight = 24;    // 行高（px）
              const maxRows = 10;

              const maxHeight = lineHeight * maxRows;

              if (el.scrollHeight > maxHeight) {
                el.style.height = maxHeight + "px";
                el.style.overflowY = "auto"; // 超出出现滚动条
              } else {
                el.style.height = el.scrollHeight + "px";
                el.style.overflowY = "hidden";
              }
            }}
            onKeyDown={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                onSend();
              }
            }}
            placeholder="输入消息..."
            rows={1}
            className="
              flex-1 px-4 py-3 rounded-xl border resize-none
              bg-white border-gray-300 text-gray-900 placeholder-gray-400
              dark:bg-gray-800 dark:border-gray-600 dark:text-gray-100 dark:placeholder-gray-500
              focus:outline-none focus:ring-2 focus:ring-blue-500 dark:focus:ring-blue-400
            "
          />

          <button
            onClick={onSend}
            className="
              px-6 py-3 bg-blue-600 text-white rounded-xl
              hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-600
            "
          >
            发送
          </button>
        </div>

      </div>
    </div>
  );
}
