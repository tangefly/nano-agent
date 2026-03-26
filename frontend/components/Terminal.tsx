"use client";

import { useEffect, useRef } from "react";

export default function Terminal({ output, cmd, cwd }: { output: string, cmd: string, cwd: string }) {
  const ref = useRef<HTMLDivElement>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (ref.current) {
      ref.current.scrollTop = ref.current.scrollHeight;
    }
  }, [output]);

  return (
    <div className="w-full bg-black rounded-xl border border-gray-800 overflow-hidden shadow-sm">
        {/* 顶部栏 */}
        <div className="flex items-center justify-between px-3 py-2 bg-gray-900 border-b border-gray-800">
        <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-red-500" />
            <div className="w-3 h-3 rounded-full bg-yellow-500" />
            <div className="w-3 h-3 rounded-full bg-green-500" />
        </div>
        <div className="text-xs text-gray-500">Terminal</div>
        </div>

        {/* 命令行（核心） */}
        <div className="px-4 py-2 text-sm font-mono bg-black border-b border-gray-800">
        <span className="text-gray-500">{cwd}</span>
        <br />
        <span className="text-green-400">$ {cmd}</span>
        </div>

        {/* 输出 */}
        <div
        ref={ref}
        className="p-4 h-64 overflow-y-auto text-sm font-mono text-green-400 whitespace-pre-wrap leading-relaxed"
        >
        {output || (
            <span className="text-gray-500">（等待输出...）</span>
        )}
        </div>
    </div>
  );
}
