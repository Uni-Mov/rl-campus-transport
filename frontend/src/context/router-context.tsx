import { createContext, useContext, useState, type ReactNode } from "react";

type RouterContextType = {
  useCustomRouter: boolean;
  setUseCustomRouter: (value: boolean) => void;
};

const RouterContext = createContext<RouterContextType | undefined>(undefined);

export function RouterProvider({ children }: { children: ReactNode }) {
  const [useCustomRouter, setUseCustomRouter] = useState(false);

  return (
    <RouterContext.Provider value={{ useCustomRouter, setUseCustomRouter }}>
      {children}
    </RouterContext.Provider>
  );
}

export function useRouter() {
  const context = useContext(RouterContext);
  if (context === undefined) {
    throw new Error("useRouter must be used within a RouterProvider");
  }
  return context;
}
