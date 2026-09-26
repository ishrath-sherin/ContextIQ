import {useEffect , useState } from "react";

function ThemePanel() {
  const [darkMode, setDarkMode] = useState(
  localStorage.getItem("contextiq-theme") === "dark"
);

const [accent, setAccent] = useState(
  localStorage.getItem("contextiq-accent") || "#6366f1"
);
useEffect(() => {
  document.documentElement.classList.toggle("dark", darkMode);
  document.documentElement.style.setProperty("--accent-color", accent);

  localStorage.setItem(
    "contextiq-theme",
    darkMode ? "dark" : "light"
  );

  localStorage.setItem("contextiq-accent", accent);
}, [darkMode, accent]);
  

  const toggleTheme = () => {
    setDarkMode(!darkMode);

    document.documentElement.classList.toggle("dark");

    document.documentElement.style.setProperty(
      "--accent-color",
      !darkMode ? accent : "#6366f1"
    );
  };

  const changeAccent = (color) => {
    setAccent(color);
    document.documentElement.style.setProperty("--accent-color", color);
  };

  return (
    <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-lg">
      <h3 className="mb-4 text-lg font-semibold text-slate-900">
        Customize Theme
      </h3>

      <button
        onClick={toggleTheme}
        className="mb-5 w-full rounded-xl bg-slate-900 px-4 py-3 text-sm font-medium text-white hover:bg-slate-700"
      >
        {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
      </button>

      <p className="mb-3 text-sm font-medium text-slate-700">
        Accent Color
      </p>

      <div className="flex flex-wrap gap-3">
        {[
          "#6366f1",
          "#8b5cf6",
          "#06b6d4",
          "#10b981",
          "#f59e0b",
          "#ef4444",
          "#ec4899",
          "#14b8a6",
        ].map((color) => (
          <button
            key={color}
            onClick={() => changeAccent(color)}
            className="h-9 w-9 rounded-full border-2 border-white shadow"
            style={{ backgroundColor: color }}
          />
        ))}
      </div>
    </div>
  );
  <label
  className="flex h-9 w-9 cursor-pointer items-center justify-center rounded-full border-2 border-white bg-slate-100 shadow"
  title="Custom color"
>
  🎨
  <input
    type="color"
    value={accent}
    onChange={(e) => changeAccent(e.target.value)}
    className="hidden"
  />
</label>
}

export default ThemePanel;