import { useEffect, useState } from 'react';

type Theme = 'light' | 'dark';

function currentTheme(): Theme {
  return (localStorage.getItem('theme') as Theme | null) || 'light';
}

export function ThemeToggle() {
  const [theme, setTheme] = useState<Theme>(currentTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  return (
    <button
      id="theme-toggle"
      className="theme-toggle"
      title="Toggle light/dark mode"
      onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
    >
      {theme === 'dark' ? '☀' : '☾'}
    </button>
  );
}
