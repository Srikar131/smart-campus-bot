import React, { useState } from 'react';
import { Menu, X, MessageSquare, FileText, Sun, Moon, GraduationCap } from 'lucide-react';
import { Button } from './ui/button';

export function Sidebar({ activeTab, onTabChange, isDark, onThemeToggle }) {
  const [isCollapsed, setIsCollapsed] = useState(false);

  const navItems = [
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'documents', label: 'Documents', icon: FileText },
  ];

  return (
    <aside
      className={`
        h-screen flex flex-col border-r border-border transition-all duration-300
        ${isCollapsed ? 'w-16' : 'w-64'}
        glass
      `}
    >
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-border">
        {!isCollapsed && (
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded bg-academic-teal flex items-center justify-center">
              <GraduationCap className="w-5 h-5 text-white" strokeWidth={1.5} />
            </div>
            <span className="font-heading font-semibold text-lg">E1</span>
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setIsCollapsed(!isCollapsed)}
          data-testid="sidebar-toggle"
        >
          {isCollapsed ? <Menu className="w-4 h-4" /> : <X className="w-4 h-4" />}
        </Button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`
                w-full flex items-center gap-3 px-3 py-2.5 text-sm font-medium transition-all
                ${activeTab === item.id
                  ? 'bg-academic-teal text-white'
                  : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                }
              `}
              data-testid={`nav-${item.id}`}
            >
              <Icon className="w-5 h-5" strokeWidth={1.5} />
              {!isCollapsed && <span className="uppercase tracking-widest text-xs">{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Theme Toggle */}
      <div className="p-3 border-t border-border">
        <Button
          variant="ghost"
          size={isCollapsed ? "icon" : "default"}
          onClick={onThemeToggle}
          className="w-full justify-start"
          data-testid="theme-toggle"
        >
          {isDark ? (
            <>
              <Sun className="w-4 h-4" />
              {!isCollapsed && <span className="ml-3 uppercase tracking-widest text-xs">Light Mode</span>}
            </>
          ) : (
            <>
              <Moon className="w-4 h-4" />
              {!isCollapsed && <span className="ml-3 uppercase tracking-widest text-xs">Dark Mode</span>}
            </>
          )}
        </Button>
      </div>
    </aside>
  );
}
