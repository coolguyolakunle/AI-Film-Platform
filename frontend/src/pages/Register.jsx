import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../hooks/useAuth";
import { extractErrorMessage } from "../services/authService";
import Button from "../components/Button.jsx";
import GoogleSignInButton from "../components/GoogleSignInButton.jsx";

export default function Register() {
  const { register, loginWithGoogle } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register({ name, email, password });
      navigate("/profile/setup");
    } catch (err) {
      setError(extractErrorMessage(err, "Could not create your account."));
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleCredential = async (credential) => {
    setError("");
    try {
      const loggedInUser = await loginWithGoogle(credential);
      navigate(loggedInUser.profile_completed ? "/dashboard" : "/profile/setup");
    } catch (err) {
      setError(extractErrorMessage(err, "Google sign-in failed."));
    }
  };

  return (
    <div className="mx-auto flex max-w-sm flex-col gap-6 px-4 py-10 sm:px-6 sm:py-16">
      <h1 className="text-2xl font-semibold text-gray-900">Create your account</h1>

      {error && (
        <div className="rounded-lg bg-red-50 px-4 py-3 text-sm text-red-700">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Name</label>
          <input
            type="text"
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Email</label>
          <input
            type="email"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Password</label>
          <input
            type="password"
            required
            minLength={8}
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
          />
          <p className="mt-1 text-xs text-gray-400">At least 8 characters, with a letter and a number.</p>
        </div>
        <Button type="submit" loading={loading} className="w-full">
          Sign up
        </Button>
      </form>

      <div className="flex items-center gap-3 text-xs text-gray-400">
        <div className="h-px flex-1 bg-gray-200" />
        OR
        <div className="h-px flex-1 bg-gray-200" />
      </div>

      <GoogleSignInButton onCredential={handleGoogleCredential} onError={setError} />

      <p className="text-center text-sm text-gray-500">
        Already have an account?{" "}
        <Link to="/login" className="font-medium text-brand-600 hover:underline">
          Log in
        </Link>
      </p>
    </div>
  );
}
