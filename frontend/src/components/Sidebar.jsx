import React, { useState } from "react";
import { Menu, MessageSquare, FileText, Sun, Moon, GraduationCap } from "lucide-react";
import { cn } from "../lib/utils";

export function Sidebar({ activeTab, onTabChange, isDark, onThemeToggle, documentCount = 0 }) {
  const [collapsed, setCollapsed] = useState(false);

  const navItems = [
    { id: "chat", label: "Assistant", icon: MessageSquare },
    { id: "documents", label: "Documents", icon: FileText, badge: documentCount },
  ];

  return (
    <aside
      className={cn(
        "relative z-20 h-screen shrink-0 flex flex-col glass border-r border-border/60 transition-all duration-300",
        collapsed ? "w-[68px]" : "w-64"
      )}
    >
      {/* Brand */}
      <div className="h-16 flex items-center gap-3 px-4 border-b border-border/60">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-lg brand-gradient shadow-soft">
          <GraduationCap className="h-5 w-5 text-white" strokeWidth={2} />
        </div>
        {!collapsed && (
          <div className="min-w-0">
            <p className="font-heading text-sm font-semibold leading-tight truncate">Smart Campus</p>
            <p className="text-[11px] text-muted-foreground leading-tight">AI Knowledge Bot</p>
          </div>
        )}
      </div>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed((c) => !c)}
        className="absolute -right-3 top-[68px] grid h-6 w-6 place-items-center rounded-full border border-border bg-card text-muted-foreground hover:text-foreground shadow-soft"
        aria-label="Toggle sidebar"
      >
        <Menu className="h-3.5 w-3.5" />
      </button>

      {/* Nav */}
      <nav className="flex-1 p-3 space-y-1">
        {navItems.map(({ id, label, icon: Icon, badge }) => {
          const active = activeTab === id;
          return (
            <button
              key={id}
              onClick={() => onTabChange(id)}
              title={collapsed ? label : undefined}
              className={cn(
                "group w-full flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all",
                active
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              )}
            >
              <Icon className="h-[18px] w-[18px] shrink-0" strokeWidth={2} />
              {!collapsed && <span className="flex-1 text-left">{label}</span>}
              {!collapsed && badge > 0 && (
                <span className="rounded-full bg-muted px-2 py-0.5 text-[11px] font-semibold text-muted-foreground">
                  {badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* Theme toggle */}
      <div className="p-3 border-t border-border/60">
        <button
          onClick={onThemeToggle}
          title={collapsed ? "Toggle theme" : undefined}
          className="w-full flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground transition-all"
        >
          {isDark ? <Sun className="h-[18px] w-[18px]" /> : <Moon className="h-[18px] w-[18px]" />}
          {!collapsed && <span>{isDark ? "Light mode" : "Dark mode"}</span>}
        </button>
      </div>
    </aside>
  );
}
