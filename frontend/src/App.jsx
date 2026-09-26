import { useState } from "react";

import {
  Search,
  FileText,
  Upload,
  Database,
  Zap,
  ShieldCheck,
  ArrowUpRight,
  MoreHorizontal,
  Sparkles,
  Clock3,
  MessageCircle,
  Send,
  Loader2,
  Radar,
  CheckCircle2,
  AlertCircle,
} from "lucide-react";

import ThemePanel from "./components/ThemePanel";

function App() {
  // =========================
  // FILE UPLOAD
  // =========================
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadLoading, setUploadLoading] = useState(false);
  const [uploadMessage, setUploadMessage] = useState("");
  const [uploadError, setUploadError] = useState("");

  // =========================
  // SEARCH
  // =========================
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchError, setSearchError] = useState("");

  // =========================
  // CHAT
  // =========================
  const [chatInput, setChatInput] = useState("");
  const [chatMessages, setChatMessages] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [chatError, setChatError] = useState("");

  // =========================
  // MEANING RADAR
  // =========================
  const [radarData, setRadarData] = useState(null);
  const [radarLoading, setRadarLoading] = useState(false);
  const [radarError, setRadarError] = useState("");

  // =========================
  // DOCUMENTS
  // =========================
  const [documents, setDocuments] = useState([
    {
      name: "Company Security Policy.pdf",
      type: "PDF",
      chunks: 124,
      updated: "2 hours ago",
    },
    {
      name: "Employee Handbook.pdf",
      type: "PDF",
      chunks: 86,
      updated: "Yesterday",
    },
    {
      name: "IT Support Guide.docx",
      type: "DOCX",
      chunks: 54,
      updated: "2 days ago",
    },
  ]);

  // =========================
  // FILE SELECT
  // =========================
  const handleFileChange = (event) => {
    const file = event.target.files[0];

    if (file) {
      setSelectedFile(file);
      setUploadMessage("");
      setUploadError("");
    }
  };

  // =========================
  // UPLOAD API
  // =========================
  const handleUpload = async () => {
    if (!selectedFile) {
      setUploadError("Please choose a document first.");
      return;
    }

    setUploadLoading(true);
    setUploadMessage("");
    setUploadError("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      const chunkCount =
        data.chunks ??
        data.chunk_count ??
        data.num_chunks ??
        data.total_chunks ??
        0;

      setUploadMessage(
        chunkCount
          ? `${selectedFile.name} uploaded successfully • ${chunkCount} chunks`
          : `${selectedFile.name} uploaded successfully`
      );

      setDocuments((prev) => [
        {
          name: selectedFile.name,
          type: selectedFile.name.split(".").pop().toUpperCase(),
          chunks: chunkCount || "-",
          updated: "Just now",
        },
        ...prev,
      ]);

      setSelectedFile(null);

      const fileInput = document.getElementById("file-upload");
      if (fileInput) {
        fileInput.value = "";
      }
    } catch (error) {
      console.error("Upload error:", error);
      setUploadError(
        "Unable to upload document. Please make sure the backend is running."
      );
    } finally {
      setUploadLoading(false);
    }
  };

  // =========================
  // SEARCH API
  // =========================
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;

    setSearchLoading(true);
    setSearchError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: searchQuery,
          top_k: 5,
        }),
      });

      if (!response.ok) {
        throw new Error("Search failed");
      }

      const data = await response.json();

      console.log("Search results:", data);

      setSearchResults(
        Array.isArray(data)
          ? data
          : data.results || data.matches || data.documents || []
      );
    } catch (error) {
      console.error("Search error:", error);
      setSearchError(
        "Unable to connect to search service. Please make sure the backend is running."
      );
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  // =========================
  // SEARCH ENTER KEY
  // =========================
  const handleSearchKeyDown = (event) => {
    if (event.key === "Enter") {
      handleSearch();
    }
  };

  // =========================
  // CHAT API
  // =========================
  const handleChat = async () => {
    if (!chatInput.trim() || chatLoading) return;

    const userMessage = chatInput.trim();

    const newUserMessage = {
      role: "user",
      content: userMessage,
    };

    const updatedMessages = [...chatMessages, newUserMessage];

    setChatMessages(updatedMessages);
    setChatInput("");
    setChatLoading(true);
    setChatError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          message: userMessage,
          mode: "auto",
          top_k: 5,
          history: chatMessages,
        }),
      });

      if (!response.ok) {
        throw new Error("Chat failed");
      }

      const data = await response.json();

      console.log("Chat response:", data);

      const assistantAnswer =
        data.answer ||
        data.response ||
        data.message ||
        data.content ||
        "I couldn't find an answer.";

      const sources = data.sources || [];

      setChatMessages([
        ...updatedMessages,
        {
          role: "assistant",
          content: assistantAnswer,
          sources,
        },
      ]);
    } catch (error) {
      console.error("Chat error:", error);

      setChatError(
        "Unable to connect to AI chat. Please make sure the backend is running."
      );
    } finally {
      setChatLoading(false);
    }
  };

  const handleChatKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      handleChat();
    }
  };

  // =========================
  // MEANING RADAR API
  // =========================
  const loadMeaningRadar = async () => {
    setRadarLoading(true);
    setRadarError("");

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/meaning-radar"
      );

      if (!response.ok) {
        throw new Error("Meaning Radar failed");
      }

      const data = await response.json();

      console.log("Meaning Radar:", data);

      setRadarData(data);
    } catch (error) {
      console.error("Meaning Radar error:", error);
      setRadarError(
        "Meaning Radar data is not available right now."
      );
    } finally {
      setRadarLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      {/* =========================
          TOP NAVBAR
      ========================= */}
      <header className="sticky top-0 z-50 border-b border-slate-200 bg-white/90 backdrop-blur">
        <div className="mx-auto flex h-20 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-blue-600 text-white shadow-lg shadow-blue-200">
              <Sparkles size={22} />
            </div>

            <div>
              <h1 className="text-lg font-bold tracking-tight">
                ContextIQ
              </h1>

              <p className="text-xs text-slate-500">
                Private Semantic Search
              </p>
            </div>
          </div>

          <div className="hidden items-center gap-8 md:flex">
            <button className="text-sm font-semibold text-blue-600">
              Dashboard
            </button>

            <button className="text-sm font-medium text-slate-500 hover:text-slate-900">
              Documents
            </button>

            <button className="text-sm font-medium text-slate-500 hover:text-slate-900">
              Search History
            </button>

            <div className="h-9 w-9 rounded-full bg-slate-900 text-center text-sm font-bold leading-9 text-white">
              H
            </div>
          </div>
        </div>
      </header>

      {/* =========================
          MAIN
      ========================= */}
      <main className="mx-auto max-w-7xl px-6 py-10">
        {/* =========================
            HERO + SEARCH
        ========================= */}
        <section className="relative overflow-hidden rounded-3xl bg-slate-950 px-8 py-12 text-white shadow-xl md:px-12">
          <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-blue-500/20 blur-3xl" />

          <div className="absolute -bottom-20 left-1/3 h-64 w-64 rounded-full bg-purple-500/20 blur-3xl" />

          <div className="relative max-w-3xl">
            <div className="mb-5 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/10 px-4 py-2 text-xs font-medium text-slate-200">
              <ShieldCheck size={15} />
              Privacy-focused document intelligence
            </div>

            <h2 className="text-4xl font-bold leading-tight tracking-tight md:text-5xl">
              Search your knowledge.
              <span className="block text-blue-400">
                Understand your data.
              </span>
            </h2>

            <p className="mt-5 max-w-2xl text-base leading-7 text-slate-300">
              Find information by meaning, not just keywords. ContextIQ
              understands your documents and helps you discover the exact
              information you need.
            </p>

            {/* SEARCH */}
            <div className="mt-8 flex max-w-3xl items-center gap-3 rounded-2xl bg-white p-2 shadow-2xl">
              <Search className="ml-3 text-slate-400" size={22} />

              <input
                type="text"
                placeholder="Ask anything about your documents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={handleSearchKeyDown}
                className="min-w-0 flex-1 bg-transparent px-2 py-3 text-sm text-slate-900 outline-none"
              />

              <button
                onClick={handleSearch}
                disabled={searchLoading}
                className="flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
              >
                {searchLoading ? (
                  <>
                    <Loader2 size={17} className="animate-spin" />
                    Searching
                  </>
                ) : (
                  "Search"
                )}
              </button>
            </div>

            <div className="mt-4 flex items-center gap-2 text-xs text-slate-400">
              <Zap size={14} />
              Semantic + keyword hybrid search
            </div>
          </div>
        </section>

        {/* =========================
            SEARCH RESULTS
        ========================= */}
        {(searchResults.length > 0 || searchError) && (
          <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold">
                  Search Results
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Top relevant passages from your documents
                </p>
              </div>

              {searchResults.length > 0 && (
                <span className="rounded-full bg-blue-50 px-3 py-1 text-xs font-semibold text-blue-600">
                  {searchResults.length} results
                </span>
              )}
            </div>

            {searchError && (
              <div className="mt-5 flex items-center gap-3 rounded-2xl bg-red-50 p-4 text-sm text-red-600">
                <AlertCircle size={18} />
                {searchError}
              </div>
            )}

            <div className="mt-6 space-y-4">
              {searchResults.map((result, index) => {
                const source =
                  result.source ||
                  result.filename ||
                  result.file_name ||
                  result.metadata?.source ||
                  result.metadata?.filename ||
                  "Document";

                const passage =
                  result.passage ||
                  result.text ||
                  result.content ||
                  result.chunk ||
                  "No passage available";

                const page =
                  result.page ??
                  result.page_number ??
                  result.metadata?.page ??
                  "-";

                const finalScore =
                  result.score ??
                  result.final_score ??
                  result.relevance_score ??
                  "-";

                const semanticScore =
                  result.semantic_score ??
                  result.semantic ??
                  result.metadata?.semantic_score ??
                  "-";

                const keywordScore =
                  result.keyword_score ??
                  result.keyword ??
                  result.metadata?.keyword_score ??
                  "-";

                return (
                  <div
                    key={index}
                    className="rounded-2xl border border-slate-200 bg-slate-50 p-5 transition hover:border-blue-200 hover:shadow-sm"
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
                      <div>
                        <div className="flex items-center gap-2">
                          <FileText
                            size={17}
                            className="text-blue-600"
                          />

                          <p className="font-semibold text-slate-900">
                            {source}
                          </p>
                        </div>

                        <p className="mt-1 text-xs text-slate-400">
                          Page: {page}
                        </p>
                      </div>

                      <div className="flex flex-wrap gap-2 text-xs">
                        <span className="rounded-full bg-blue-100 px-3 py-1 font-semibold text-blue-700">
                          Relevance: {finalScore}
                        </span>

                        <span className="rounded-full bg-purple-100 px-3 py-1 font-semibold text-purple-700">
                          Semantic: {semanticScore}
                        </span>

                        <span className="rounded-full bg-emerald-100 px-3 py-1 font-semibold text-emerald-700">
                          Keyword: {keywordScore}
                        </span>
                      </div>
                    </div>

                    <p className="mt-4 text-sm leading-7 text-slate-600">
                      {passage}
                    </p>
                  </div>
                );
              })}
            </div>
          </section>
        )}

        {/* =========================
            STATS
        ========================= */}
        <section className="mt-8 grid gap-4 md:grid-cols-3">
          <StatCard
            icon={<FileText size={21} />}
            title="Documents Indexed"
            value={documents.length}
            subtitle="Current workspace"
          />

          <StatCard
            icon={<Database size={21} />}
            title="Text Chunks"
            value="1,284"
            subtitle="Across all documents"
          />

          <StatCard
            icon={<Zap size={21} />}
            title="Average Search"
            value="42 ms"
            subtitle="Fast semantic retrieval"
          />
        </section>

        {/* =========================
            CONTENT GRID
        ========================= */}
        <section className="mt-8 grid gap-8 lg:grid-cols-3">
          {/* DOCUMENTS */}
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm lg:col-span-2">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold">
                  Recent documents
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Your latest indexed knowledge
                </p>
              </div>

              <button className="flex items-center gap-1 text-sm font-semibold text-blue-600">
                View all
                <ArrowUpRight size={16} />
              </button>
            </div>

            <div className="mt-6 space-y-3">
              {documents.map((doc) => (
                <div
                  key={`${doc.name}-${doc.updated}`}
                  className="group flex items-center justify-between rounded-2xl border border-slate-100 p-4 transition hover:border-blue-200 hover:bg-blue-50/40"
                >
                  <div className="flex items-center gap-4">
                    <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                      <FileText size={20} />
                    </div>

                    <div>
                      <h4 className="text-sm font-semibold text-slate-800">
                        {doc.name}
                      </h4>

                      <div className="mt-1 flex items-center gap-3 text-xs text-slate-400">
                        <span>{doc.type}</span>
                        <span>•</span>
                        <span>{doc.chunks} chunks</span>
                        <span>•</span>
                        <span>{doc.updated}</span>
                      </div>
                    </div>
                  </div>

                  <button className="text-slate-400 transition group-hover:text-slate-700">
                    <MoreHorizontal size={20} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* UPLOAD */}
          <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-bold">
              Add knowledge
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Upload a document to your search engine.
            </p>

            <div className="mt-6 flex min-h-52 flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 p-6 text-center transition hover:border-blue-300 hover:bg-blue-50/40">
              <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-blue-100 text-blue-600">
                <Upload size={24} />
              </div>

              <h4 className="mt-4 text-sm font-semibold">
                Drop your document here
              </h4>

              <p className="mt-2 text-xs text-slate-400">
                PDF, DOCX or TXT
              </p>

              <label
                htmlFor="file-upload"
                className="relative z-10 mt-5 inline-flex cursor-pointer items-center justify-center rounded-xl bg-slate-900 px-6 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
              >
                Choose file
              </label>

              <input
                id="file-upload"
                type="file"
                accept=".pdf,.docx,.txt"
                className="hidden"
                onChange={handleFileChange}
              />

              {selectedFile && (
                <div className="mt-4 w-full rounded-xl bg-blue-50 px-4 py-3">
                  <p className="text-sm font-semibold text-blue-700">
                    Selected file:
                  </p>

                  <p className="selected-file-name mt-1 max-w-full break-all text-sm font-medium">
                    {selectedFile.name}
                  </p>

                  <button
                    type="button"
                    onClick={handleUpload}
                    disabled={uploadLoading}
                    className="mt-3 flex w-full items-center justify-center gap-2 rounded-xl bg-blue-600 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-70"
                  >
                    {uploadLoading ? (
                      <>
                        <Loader2
                          size={17}
                          className="animate-spin"
                        />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload size={17} />
                        Upload Document
                      </>
                    )}
                  </button>
                </div>
              )}

              {uploadMessage && (
                <div className="mt-4 flex w-full items-start gap-2 rounded-xl bg-emerald-50 px-4 py-3 text-left text-sm text-emerald-700">
                  <CheckCircle2 size={18} className="mt-0.5 shrink-0" />
                  <span>{uploadMessage}</span>
                </div>
              )}

              {uploadError && (
                <div className="mt-4 flex w-full items-start gap-2 rounded-xl bg-red-50 px-4 py-3 text-left text-sm text-red-600">
                  <AlertCircle size={18} className="mt-0.5 shrink-0" />
                  <span>{uploadError}</span>
                </div>
              )}
            </div>
          </div>
        </section>

        {/* =========================
            AI CHAT
        ========================= */}
        <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-purple-100 text-purple-600">
              <MessageCircle size={22} />
            </div>

            <div>
              <h3 className="text-lg font-bold">
                AI Chat
              </h3>

              <p className="text-sm text-slate-500">
                Ask questions about your documents or have a general conversation.
              </p>
            </div>
          </div>

          <div className="mt-6 min-h-48 max-h-[420px] space-y-4 overflow-y-auto rounded-2xl bg-slate-50 p-5">
            {chatMessages.length === 0 ? (
              <div className="flex min-h-36 flex-col items-center justify-center text-center">
                <Sparkles className="text-purple-400" size={28} />

                <p className="mt-3 text-sm font-semibold text-slate-700">
                  Start a conversation
                </p>

                <p className="mt-1 text-xs text-slate-400">
                  Try asking something about your uploaded documents.
                </p>
              </div>
            ) : (
              chatMessages.map((message, index) => (
                <div
                  key={index}
                  className={`flex ${
                    message.role === "user"
                      ? "justify-end"
                      : "justify-start"
                  }`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 ${
                      message.role === "user"
                        ? "bg-blue-600 text-white"
                        : "border border-slate-200 bg-white text-slate-700"
                    }`}
                  >
                    <p className="whitespace-pre-wrap text-sm leading-6">
                      {message.content}
                    </p>

                    {message.sources &&
                      message.sources.length > 0 && (
                        <div className="mt-3 border-t border-slate-200 pt-3">
                          <p className="mb-2 text-xs font-semibold text-slate-500">
                            Sources
                          </p>

                          <div className="space-y-1">
                            {message.sources.map(
                              (source, sourceIndex) => (
                                <p
                                  key={sourceIndex}
                                  className="text-xs text-slate-400"
                                >
                                  •{" "}
                                  {typeof source === "string"
                                    ? source
                                    : source.filename ||
                                      source.source ||
                                      source.name ||
                                      "Document source"}
                                </p>
                              )
                            )}
                          </div>
                        </div>
                      )}
                  </div>
                </div>
              ))
            )}

            {chatLoading && (
              <div className="flex justify-start">
                <div className="flex items-center gap-2 rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-500">
                  <Loader2
                    size={17}
                    className="animate-spin"
                  />
                  AI is thinking...
                </div>
              </div>
            )}
          </div>

          {chatError && (
            <div className="mt-4 flex items-center gap-2 rounded-xl bg-red-50 p-3 text-sm text-red-600">
              <AlertCircle size={17} />
              {chatError}
            </div>
          )}

          <div className="mt-4 flex items-end gap-3 rounded-2xl border border-slate-200 bg-white p-2">
            <textarea
              value={chatInput}
              onChange={(e) => setChatInput(e.target.value)}
              onKeyDown={handleChatKeyDown}
              rows={2}
              placeholder="Ask ContextIQ anything..."
              className="min-h-12 flex-1 resize-none bg-transparent px-3 py-2 text-sm text-slate-900 outline-none"
            />

            <button
              onClick={handleChat}
              disabled={chatLoading || !chatInput.trim()}
              className="flex h-11 items-center gap-2 rounded-xl bg-blue-600 px-5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Send size={17} />
              Send
            </button>
          </div>
        </section>

        {/* =========================
            MEANING RADAR
        ========================= */}
        <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-100 text-cyan-600">
                <Radar size={22} />
              </div>

              <div>
                <h3 className="text-lg font-bold">
                  Meaning Radar
                </h3>

                <p className="text-sm text-slate-500">
                  Explore semantic meaning signals from your knowledge base.
                </p>
              </div>
            </div>

            <button
              onClick={loadMeaningRadar}
              disabled={radarLoading}
              className="flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-5 py-3 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:opacity-60"
            >
              {radarLoading ? (
                <>
                  <Loader2
                    size={17}
                    className="animate-spin"
                  />
                  Loading...
                </>
              ) : (
                <>
                  <Radar size={17} />
                  Load Radar
                </>
              )}
            </button>
          </div>

          {radarError && (
            <div className="mt-5 flex items-center gap-2 rounded-xl bg-slate-50 p-4 text-sm text-slate-500">
              <AlertCircle size={17} />
              {radarError}
            </div>
          )}

          {!radarData && !radarError && (
            <div className="mt-6 flex min-h-40 flex-col items-center justify-center rounded-2xl border border-dashed border-slate-200 bg-slate-50 text-center">
              <Radar size={30} className="text-slate-300" />

              <p className="mt-3 text-sm font-semibold text-slate-600">
                Meaning Radar is ready
              </p>

              <p className="mt-1 text-xs text-slate-400">
                Click “Load Radar” to fetch the latest backend data.
              </p>
            </div>
          )}

          {radarData && (
            <div className="mt-6 rounded-2xl border border-slate-200 bg-slate-50 p-5">
              <p className="mb-3 text-sm font-semibold text-slate-700">
                Radar data received
              </p>

              <pre className="max-h-72 overflow-auto rounded-xl bg-slate-950 p-4 text-xs leading-6 text-slate-200">
                {JSON.stringify(radarData, null, 2)}
              </pre>
            </div>
          )}
        </section>

        {/* =========================
            HOW IT WORKS
        ========================= */}
        <section className="mt-8 rounded-3xl border border-slate-200 bg-white p-8">
          <div className="text-center">
            <p className="text-sm font-semibold text-blue-600">
              HOW CONTEXTIQ WORKS
            </p>

            <h3 className="mt-2 text-2xl font-bold">
              From documents to understanding
            </h3>

            <p className="mx-auto mt-3 max-w-2xl text-sm text-slate-500">
              ContextIQ converts your documents into searchable knowledge
              and finds relevant information based on meaning.
            </p>
          </div>

          <div className="mt-8 grid gap-6 md:grid-cols-3">
            <ProcessCard
              number="01"
              icon={<Upload size={22} />}
              title="Upload"
              text="Add your PDF, DOCX or TXT documents."
            />

            <ProcessCard
              number="02"
              icon={<Database size={22} />}
              title="Understand"
              text="Documents are split into meaningful searchable chunks."
            />

            <ProcessCard
              number="03"
              icon={<Search size={22} />}
              title="Search"
              text="Ask naturally and discover relevant information instantly."
            />
          </div>
        </section>

        {/* =========================
            FOOTER
        ========================= */}
        <footer className="py-10 text-center text-xs text-slate-400">
          ContextIQ • Private Semantic Search Engine
        </footer>
      </main>

      <ThemePanel />
    </div>
  );
}

// =========================
// STAT CARD
// =========================
function StatCard({ icon, title, value, subtitle }) {
  return (
    <div className="rounded-3xl border border-slate-200 bg-white p-6 shadow-sm transition hover:-translate-y-1 hover:shadow-md">
      <div className="flex items-center justify-between">
        <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
          {icon}
        </div>

        <Clock3 size={17} className="text-slate-300" />
      </div>

      <p className="mt-5 text-sm font-medium text-slate-500">
        {title}
      </p>

      <div className="mt-1 flex items-end gap-2">
        <span className="text-3xl font-bold tracking-tight">
          {value}
        </span>
      </div>

      <p className="mt-1 text-xs text-slate-400">
        {subtitle}
      </p>
    </div>
  );
}

// =========================
// PROCESS CARD
// =========================
function ProcessCard({ number, icon, title, text }) {
  return (
    <div className="rounded-2xl border border-slate-100 bg-slate-50 p-6">
      <div className="flex items-center justify-between">
        <span className="text-xs font-bold text-slate-300">
          {number}
        </span>

        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-white text-blue-600 shadow-sm">
          {icon}
        </div>
      </div>

      <h4 className="mt-5 font-bold">
        {title}
      </h4>

      <p className="mt-2 text-sm leading-6 text-slate-500">
        {text}
      </p>
    </div>
  );
}

export default App;