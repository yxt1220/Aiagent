import React, { useEffect, useMemo, useRef, useState } from "react";

const API_BASE = "http://localhost:8000";
const CHAT_URL = `${API_BASE}/chat/`;
const UPLOAD_URL = `${API_BASE}/upload/`;

export default function ChatWindow() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [isBooting, setIsBooting] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [hintLevel, setHintLevel] = useState(null);
  const [phase, setPhase] = useState(null);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [dragActive, setDragActive] = useState(false);

  const bottomRef = useRef(null);
  const fileRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isSending, isBooting]);

  useEffect(() => { boot(); }, []);

  const canSend = useMemo(
    () => input.trim().length > 0 && !isSending && !isBooting,
    [input, isSending, isBooting]
  );

  const ts = () =>
    new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

  // ── 从后端返回中提取状态 ──
  const syncState = (data) => {
    setHintLevel(data.pedagogical_control?.hint_level || null);
    setPhase(data.episode_state?.phase || null);
  };

  // ── 初始化：发空消息，后端会 reset + 返回欢迎语 ──
  const boot = async () => {
    setIsBooting(true);
    try {
      const res = await fetch(CHAT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: "" }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      syncState(data);
      setMessages([
        { id: crypto.randomUUID(), role: "assistant", content: data.response, timestamp: ts() },
      ]);
    } catch {
      setMessages([
        { id: crypto.randomUUID(), role: "assistant", content: "无法连接后端，请确认后端已启动。", timestamp: ts() },
      ]);
    } finally {
      setIsBooting(false);
    }
  };

  // ── 发消息 ──
  const send = async () => {
    if (!canSend) return;
    const text = input.trim();
    setMessages((p) => [...p, { id: crypto.randomUUID(), role: "user", content: text, timestamp: ts() }]);
    setInput("");
    setIsSending(true);
    try {
      const res = await fetch(CHAT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: text }),
      });
      if (!res.ok) throw new Error();
      const data = await res.json();
      syncState(data);
      setMessages((p) => [...p, { id: crypto.randomUUID(), role: "assistant", content: data.response, timestamp: ts() }]);
    } catch {
      setMessages((p) => [...p, { id: crypto.randomUUID(), role: "assistant", content: "请求失败，请检查后端。", timestamp: ts() }]);
    } finally {
      setIsSending(false);
    }
  };

  // ── New Session：清前端 + 发空消息让后端 reset ──
  const newSession = async () => {
    setMessages([]);
    setUploadedFiles([]);
    setHintLevel(null);
    setPhase(null);
    await boot();
  };

  // ── 文件上传 ──
  const upload = async (files) => {
    if (!files || files.length === 0) return;
    for (const file of Array.from(files)) {
      setMessages((p) => [...p, { id: crypto.randomUUID(), role: "assistant", content: `正在上传 ${file.name}...`, timestamp: ts() }]);
      const fd = new FormData();
      fd.append("file", file);
      try {
        const res = await fetch(UPLOAD_URL, { method: "POST", body: fd });
        if (!res.ok) {
          const err = await res.json().catch(() => ({}));
          throw new Error(err.detail || "上传失败");
        }
        const data = await res.json();
        setUploadedFiles((p) => [...p, { id: data.file_id || crypto.randomUUID(), name: file.name }]);
        setMessages((p) => [...p, { id: crypto.randomUUID(), role: "assistant", content: `${file.name} 上传成功！`, timestamp: ts() }]);
      } catch (e) {
        setMessages((p) => [...p, { id: crypto.randomUUID(), role: "assistant", content: `${file.name} 上传失败：${e.message}`, timestamp: ts() }]);
      }
    }
  };

  const onFileSelect = async (e) => { await upload(e.target.files); e.target.value = ""; };
  const onDragOver = (e) => { e.preventDefault(); setDragActive(true); };
  const onDragLeave = (e) => { e.preventDefault(); setDragActive(false); };
  const onDrop = async (e) => { e.preventDefault(); setDragActive(false); await upload(e.dataTransfer.files); };
  const onKey = (e) => { if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); send(); } };

  const phaseLabel = { diagnose: "诊断中", scaffold: "引导中", verify: "确认理解", close: "已完成" };
  const phaseColor = {
    diagnose: "bg-blue-100 text-blue-700",
    scaffold: "bg-zinc-100 text-zinc-600",
    verify: "bg-amber-100 text-amber-700",
    close: "bg-green-100 text-green-700",
  };

  return (
    <div className="flex h-screen w-full bg-zinc-50 text-zinc-900">
      {/* ── 侧边栏 ── */}
      {sidebarOpen && (
        <aside className="w-72 border-r border-zinc-200 bg-white">
          <div className="flex h-full flex-col">
            <div className="border-b border-zinc-200 p-4">
              <div className="text-sm font-semibold">Scaffolding Tutor</div>
              <div className="mt-1 text-xs text-zinc-400">AI 引导式教学助手</div>
              <button onClick={newSession} className="mt-4 w-full rounded-2xl bg-zinc-900 px-4 py-3 text-sm font-medium text-white hover:bg-zinc-800">
                New Session
              </button>
            </div>

            <div className="flex-1 space-y-3 overflow-y-auto p-3">
              <div className="rounded-2xl border border-zinc-200 p-3 text-sm">
                <div className="font-medium">Hint Level</div>
                <div className="mt-1 text-xs text-zinc-500">{hintLevel || "—"}</div>
              </div>
              <div className="rounded-2xl border border-zinc-200 p-3 text-sm">
                <div className="font-medium">Phase</div>
                <div className="mt-1 text-xs text-zinc-500">{phase ? (phaseLabel[phase] || phase) : "—"}</div>
              </div>
              <div className="rounded-2xl border border-zinc-200 p-3 text-sm">
                <div className="font-medium">已上传文件</div>
                <div className="mt-2 space-y-1 text-xs text-zinc-500">
                  {uploadedFiles.length === 0 ? <div>暂无</div> : uploadedFiles.map((f) => <div key={f.id} className="truncate">📄 {f.name}</div>)}
                </div>
              </div>
            </div>
          </div>
        </aside>
      )}

      {/* ── 主区 ── */}
      <main className="flex min-w-0 flex-1 flex-col">
        {/* 顶栏 */}
        <header className="flex items-center justify-between border-b border-zinc-200 bg-white px-4 py-3">
          <div className="flex items-center gap-2">
            <button onClick={() => setSidebarOpen((v) => !v)} className="rounded-lg p-2 hover:bg-zinc-100">
              <span className="text-base">☰</span>
            </button>
            <div className="text-sm font-semibold">Scaffolding Tutor</div>
          </div>
          <div className="flex items-center gap-2">
            {phase && (
              <span className={`rounded-full px-3 py-1 text-xs font-medium ${phaseColor[phase] || "bg-zinc-100 text-zinc-600"}`}>
                {phaseLabel[phase] || phase}
              </span>
            )}
            {hintLevel && (
              <span className="rounded-full bg-zinc-900 px-3 py-1 text-xs font-medium text-white">{hintLevel}</span>
            )}
          </div>
        </header>

        {/* 消息 */}
        <div className={`relative flex-1 overflow-y-auto ${dragActive ? "bg-zinc-100" : ""}`} onDragOver={onDragOver} onDragLeave={onDragLeave} onDrop={onDrop}>
          {dragActive && (
            <div className="pointer-events-none absolute inset-0 z-10 flex items-center justify-center bg-black/10">
              <div className="rounded-2xl border-2 border-dashed border-zinc-500 bg-white px-8 py-6 text-sm font-medium text-zinc-700 shadow">
                把文件拖到这里上传
              </div>
            </div>
          )}

          <div className="mx-auto flex w-full max-w-4xl flex-col gap-6 px-4 py-6 md:px-6">
            {messages.map((m) => {
              const isUser = m.role === "user";
              return (
                <div key={m.id} className={`flex w-full gap-3 ${isUser ? "justify-end" : "justify-start"}`}>
                  {!isUser && (
                    <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-900 text-xs font-medium text-white">T</div>
                  )}
                  <div className="max-w-[88%] md:max-w-[75%]">
                    <div className={`whitespace-pre-wrap rounded-3xl px-4 py-3 text-sm leading-6 shadow-sm ${isUser ? "bg-zinc-900 text-white" : "border border-zinc-200 bg-white text-zinc-900"}`}>
                      {m.content}
                    </div>
                    <div className={`mt-1 px-2 text-xs text-zinc-400 ${isUser ? "text-right" : "text-left"}`}>{m.timestamp}</div>
                  </div>
                  {isUser && (
                    <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-200 text-xs font-medium text-zinc-700">我</div>
                  )}
                </div>
              );
            })}

            {(isSending || isBooting) && (
              <div className="flex gap-3">
                <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-zinc-900 text-xs font-medium text-white">T</div>
                <div className="rounded-3xl border border-zinc-200 bg-white px-4 py-3 text-sm shadow-sm">
                  <div className="flex items-center gap-1">
                    <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.3s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400 [animation-delay:-0.15s]" />
                    <span className="h-2 w-2 animate-bounce rounded-full bg-zinc-400" />
                  </div>
                </div>
              </div>
            )}
            <div ref={bottomRef} />
          </div>
        </div>

        {/* 输入 */}
        <div className="border-t border-zinc-200 bg-white px-4 py-4">
          <div className="mx-auto max-w-4xl">
            <div className="mb-3 flex items-center gap-2">
              <button type="button" onClick={() => fileRef.current?.click()} className="rounded-full border border-zinc-200 px-3 py-2 text-sm hover:bg-zinc-100">
                📎 上传文件
              </button>
              <input ref={fileRef} type="file" multiple className="hidden" onChange={onFileSelect} />
              <div className="text-xs text-zinc-400">支持 CSV、PDF、DOCX、PPTX</div>
            </div>
            <div className="rounded-3xl border border-zinc-200 bg-white p-2 shadow-sm">
              <div className="flex items-end gap-2">
                <input value={input} onChange={(e) => setInput(e.target.value)} onKeyDown={onKey} placeholder="输入你的问题..." className="flex-1 rounded-2xl px-3 py-2 outline-none" disabled={isBooting} />
                <button onClick={send} disabled={!canSend} className="rounded-full bg-zinc-900 px-4 py-2 text-sm text-white disabled:opacity-50 hover:bg-zinc-800">
                  发送
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
