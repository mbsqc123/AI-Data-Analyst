import { useRoutes, Navigate, Outlet } from "react-router-dom";
import Auth from "./pages/auth";
import Chat from "./pages/chat";
import Layout from "./components/Layout";
import ChatHistory from "./pages/chatHistory";
import DataSource from "./pages/dataSource";
import Settings from "./pages/settings";
import { getUser } from "./utils/localstorageUtils";

// AuthWrapper component to handle authentication logic
const AuthWrapper = () => {
  const isAuthenticated = getUser();

  if (!isAuthenticated?.access_token) {
    return <Navigate to="/" replace />;
  }

  return (
    <Layout>
      <Outlet />
    </Layout>
  );
};

// Define your routing logic
const AppRoutes = () => {
  const routes = useRoutes([
    { path: "/", element: <Auth /> },

    {
      element: <AuthWrapper />,
      children: [
        { path: "/chat/:data_source_id/:conversation_id", element: <Chat /> },
        { path: "/chat/:conversation_id", element: <Chat /> },
        { path: "/chat", element: <Chat /> },
        { path: "/chat-history", element: <ChatHistory /> },
        { path: "/data-sources", element: <DataSource /> },
        { path: "/settings", element: <Settings /> },
      ]
    },
  ]);

  return routes;
};

export default AppRoutes;
