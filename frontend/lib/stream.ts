type Message = {
  role: "user" | "assistant";
  content: string;
};

// export async function streamChat(
//   messages: Message[],
//   onUpdate: (text: string) => void
// ): Promise<void> {
//   const res = await fetch("http://localhost:8031/chat", {
//     method: "POST",  
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({ messages }),
//   });

//   if (!res.body) {
//     throw new Error("No response body");
//   }

//   const reader = res.body.getReader();
//   const decoder = new TextDecoder();

//   let buffer = "";
//   let content = "";

//   while (true) {
//     const { done, value } = await reader.read();
//     if (done) break;

//     buffer += decoder.decode(value, { stream: true });

//     // const parts = buffer.split("\n\n");
//     // buffer = parts.pop() || "";

//     // for (const part of parts) {
//     //   if (part.startsWith("data: ")) {
//     //     const jsonStr = part.replace("data: ", "");
//     //     const data = JSON.parse(jsonStr);
        
//     //     if (data.type == "chat"){
//     //       content += data.content;
//     //     }

//     //     onUpdate(content);
//     //   }
//     // }
//     onUpdate(buffer);
//   }
// }


export async function streamChat(
  messages: Message[],
  onEvent: (event: any) => void
): Promise<void> {
  const res = await fetch("http://localhost:8031/chat", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ messages }),
  });

  if (!res.body) {
    throw new Error("No response body");
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();

  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // 按行切割
    const lines = buffer.split("\n");

    // 最后一行可能不完整，留到下次
    buffer = lines.pop() || "";

    for (let line of lines) {
      line = line.trim();

      // 只处理 data: 开头
      if (!line.startsWith("data:")) continue;

      const jsonStr = line.replace(/^data:\s*/, "");

      if (!jsonStr) continue;

      try {
        const event = JSON.parse(jsonStr);
        onEvent(event);
      } catch (err) {
        console.error("JSON parse error:", err, jsonStr);
      }
    }
  }
}
