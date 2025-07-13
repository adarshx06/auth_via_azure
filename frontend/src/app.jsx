// React + MSAL basic UI to test FastAPI SSO

import React, { useEffect, useState } from "react";
import { PublicClientApplication } from "@azure/msal-browser";
import { MsalProvider, useMsal, useIsAuthenticated } from "@azure/msal-react";

const msalConfig = {
  auth: {
    clientId: "<YOUR-FRONTEND-CLIENT-ID>",
    authority: "https://login.microsoftonline.com/<YOUR-TENANT-ID>",
    redirectUri: "http://localhost:3000"
  }
};

const pca = new PublicClientApplication(msalConfig);

function AppContent() {
  const { instance, accounts } = useMsal();
  const isAuthenticated = useIsAuthenticated();
  const [apiData, setApiData] = useState(null);

  const login = () => {
    instance.loginPopup({ scopes: ["api://<YOUR-BACKEND-CLIENT-ID>/.default"] });
  };

  const callApi = async () => {
    try {
      const response = await instance.acquireTokenSilent({
        scopes: ["api://<YOUR-BACKEND-CLIENT-ID>/.default"],
        account: accounts[0]
      });

      const apiRes = await fetch("http://localhost:8000/employees", {
        headers: {
          Authorization: `Bearer ${response.accessToken}`
        }
      });

      const data = await apiRes.json();
      setApiData(data);
    } catch (err) {
      console.error("API call failed:", err);
    }
  };

  return (
    <div className="p-6 space-y-4">
      {!isAuthenticated ? (
        <button onClick={login} className="bg-blue-500 text-white px-4 py-2 rounded">
          Sign In with Azure AD
        </button>
      ) : (
        <>
          <div>Welcome, {accounts[0]?.username}</div>
          <button onClick={callApi} className="bg-green-500 text-white px-4 py-2 rounded">
            Call FastAPI Backend
          </button>
          {apiData && (
            <pre className="mt-4 bg-gray-100 p-4 rounded">{JSON.stringify(apiData, null, 2)}</pre>
          )}
        </>
      )}
    </div>
  );
}

export default function App() {
  return (
    <MsalProvider instance={pca}>
      <AppContent />
    </MsalProvider>
  );
}
