import { FileText, Settings } from "lucide-react";

function Navbar() {
  return (
    <nav className="flex items-center justify-between border-b bg-white px-8 py-4">
      
      <div className="flex items-center gap-3">
        <div className="rounded-lg bg-blue-600 p-2">
          <FileText className="h-6 w-6 text-white" />
        </div>

        <div>
          <h1 className="text-xl font-bold text-gray-900">
            ContextIQ
          </h1>

          <p className="text-xs text-gray-500">
            Private Semantic Search
          </p>
        </div>
      </div>

      <div className="flex items-center gap-6">
        <button className="text-sm font-medium text-gray-600 hover:text-blue-600">
          Documents
        </button>

        <button className="text-gray-600 hover:text-blue-600">
          <Settings className="h-5 w-5" />
        </button>
      </div>

    </nav>
  );
}

export default Navbar;