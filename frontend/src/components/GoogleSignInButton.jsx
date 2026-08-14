import { useEffect, useRef, useState } from "react";

import { fetchGoogleConfig } from "../services/authService";

function waitForGoogleIdentity() {
  return new Promise((resolve, reject) => {
    const startedAt = Date.now();
    const timer = window.setInterval(() => {
      if (window.google?.accounts?.id) {
        window.clearInterval(timer);
        resolve(window.google.accounts.id);
        return;
      }

      if (Date.now() - startedAt > 5000) {
        window.clearInterval(timer);
        reject(new Error("Google sign-in script did not load."));
      }
    }, 100);
  });
}

export default function GoogleSignInButton({ onCredential, onError }) {
  const buttonRef = useRef(null);
  const [configured, setConfigured] = useState(true);
  const [message, setMessage] = useState("");

  useEffect(() => {
    let cancelled = false;

    const initialize = async () => {
      try {
        const config = await fetchGoogleConfig();
        if (cancelled) return;
        if (!config.configured || !config.client_id) {
          setConfigured(false);
          setMessage("Google client ID is missing on the backend.");
          onError?.("Google client ID is missing on the backend.");
          return;
        }

        const googleIdentity = await waitForGoogleIdentity();
        if (cancelled) return;

        googleIdentity.initialize({
          client_id: config.client_id,
          callback: (response) => {
            if (response?.credential) {
              onCredential(response.credential);
            } else {
              onError?.("Google did not return a sign-in credential.");
            }
          },
        });

        if (buttonRef.current) {
          googleIdentity.renderButton(buttonRef.current, {
            theme: "outline",
            size: "large",
            width: buttonRef.current.offsetWidth || 320,
          });
        }
      } catch (err) {
        if (!cancelled) {
          setConfigured(false);
          const status = err?.response?.status;
          const message =
            status === 404
              ? "Google sign-in backend route is not deployed yet."
              : err?.response?.data?.message || err?.message || "Google sign-in is not available yet.";
          setMessage(message);
          onError?.(message);
        }
      }
    };

    initialize();
    return () => {
      cancelled = true;
    };
  }, [onCredential, onError]);

  if (!configured) {
    return (
      <div className="rounded-lg border border-gray-200 bg-gray-50 px-4 py-3 text-center text-sm text-gray-500">
        {message || "Google sign-in is not configured."}
      </div>
    );
  }

  return <div ref={buttonRef} className="min-h-11 w-full" />;
}
