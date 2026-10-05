import { useState } from "react";
import { useAuth } from "../context/AuthContext";

function Login() {
  const { login } = useAuth();

  const [isSignup, setIsSignup] = useState(false);

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [name, setName] = useState("");
  const [role, setRole] = useState("quality_engineer");
  const [confirmPassword, setConfirmPassword] = useState("");

  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const resetMessages = () => {
    setError("");
    setSuccess("");
  };

  const switchToSignup = () => {
    resetMessages();
    setIsSignup(true);
    setPassword("");
    setConfirmPassword("");
  };

  const switchToLogin = () => {
    resetMessages();
    setIsSignup(false);
    setPassword("");
    setConfirmPassword("");
  };

  

  const handleLogin = async (e) => {
    e.preventDefault();

    resetMessages();

    if (!email || !password) {
      setError("Please enter email and password.");
      return;
    }

    try {
      setLoading(true);

      await login(email, password);
    } catch (err) {
      setError(err.message || "Login failed.");
    } finally {
      setLoading(false);
    }
  };


  const handleSignup = async (e) => {
    e.preventDefault();

    resetMessages();

    if (!name || !email || !password || !confirmPassword) {
      setError("Please fill in all fields.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 6) {
      setError("Password must contain at least 6 characters.");
      return;
    }

    try {
      setLoading(true);

      const response = await fetch(
        "http://127.0.0.1:8000/auth/register",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            name,
            email,
            password,
            role,
          }),
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Registration failed. Please try again."
        );
      }

      setSuccess("Account created successfully. Please sign in.");

      setName("");
      setEmail("");
      setPassword("");
      setConfirmPassword("");

      setTimeout(() => {
        setIsSignup(false);
        setSuccess("");
      }, 1200);
    } catch (err) {
      setError(err.message || "Registration failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center overflow-hidden bg-gradient-to-br from-slate-950 via-blue-950 to-cyan-950 px-4 py-10">

      {/* Background glow */}

      <div className="absolute -left-32 -top-32 h-96 w-96 rounded-full bg-cyan-500/15 blur-3xl" />

      <div className="absolute -bottom-32 -right-32 h-96 w-96 rounded-full bg-blue-500/20 blur-3xl" />

      <div className="absolute left-1/2 top-0 h-64 w-64 -translate-x-1/2 rounded-full bg-indigo-500/10 blur-3xl" />

      {/* Main container */}

      <div className="relative z-10 w-full max-w-md">

        <div className="overflow-hidden rounded-3xl border border-white/15 bg-slate-900/90 shadow-2xl shadow-black/40 backdrop-blur-xl">

          {/* Header */}

          <div className="relative border-b border-white/10 bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900 px-8 py-9 text-center">

            <div className="absolute left-0 top-0 h-px w-full bg-gradient-to-r from-transparent via-cyan-400/60 to-transparent" />

            <div className="relative">

              <h1 className="text-3xl font-bold tracking-tight text-white">
                VisionInspect{" "}
                <span className="text-cyan-400">
                  AI
                </span>
              </h1>

              <div className="mx-auto mt-3 h-1 w-12 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500" />

              <p className="mt-4 text-sm text-slate-400">
                AI-powered manufacturing quality inspection
              </p>

            </div>

          </div>

          {/* Form area */}

          <div className="px-8 py-8">

            {/* Heading */}

            <div className="mb-7 text-center">

              <h2 className="text-2xl font-semibold text-white">
                {isSignup ? "Create your account" : "Welcome back"}
              </h2>

              <p className="mt-2 text-sm text-slate-400">
                {isSignup
                  ? "Create an account to start inspecting products"
                  : "Sign in to continue to your dashboard"}
              </p>

            </div>

            {/* Error */}

            {error && (
              <div className="mb-5 rounded-xl border border-red-400/20 bg-red-500/10 px-4 py-3 text-sm font-medium text-red-300">
                {error}
              </div>
            )}

            {/* Success */}

            {success && (
              <div className="mb-5 rounded-xl border border-emerald-400/20 bg-emerald-500/10 px-4 py-3 text-sm font-medium text-emerald-300">
                {success}
              </div>
            )}

            {/* LOGIN */}

            {!isSignup ? (
              <form
                onSubmit={handleLogin}
                className="space-y-5"
              >

                {/* Email */}

                <div>

                  <label
                    htmlFor="login-email"
                    className="mb-2 block text-sm font-medium text-slate-300"
                  >
                    Email
                  </label>

                  <input
                    id="login-email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/10"
                  />

                </div>

                {/* Password */}

                <div>

                  <label
                    htmlFor="login-password"
                    className="mb-2 block text-sm font-medium text-slate-300"
                  >
                    Password
                  </label>

                  <div className="relative">

                    <input
                      id="login-password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Enter your password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-3 pr-20 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/10"
                    />

                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-semibold text-cyan-400 transition hover:text-cyan-300"
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>

                  </div>

                </div>

                {/* Login button */}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-3.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/20 transition-all hover:-translate-y-0.5 hover:from-cyan-400 hover:to-blue-500 hover:shadow-cyan-500/30 focus:outline-none focus:ring-4 focus:ring-cyan-400/20 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">

                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />

                      Signing in...

                    </span>
                  ) : (
                    "Sign In"
                  )}
                </button>

              </form>

            ) : (

              /* SIGN UP */

              <form
                onSubmit={handleSignup}
                className="space-y-4"
              >

                {/* Name */}

                <div>

                  <label
                    htmlFor="signup-name"
                    className="mb-2 block text-sm font-medium text-slate-300"
                  >
                    Full Name
                  </label>

                  <input
                    id="signup-name"
                    type="text"
                    placeholder="Enter your name"
                    value={name}
                    onChange={(e) => setName(e.target.value)}
                    required
                    className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/10"
                  />

                </div>

                {/* Email */}

                <div>

                  <label
                    htmlFor="signup-email"
                    className="mb-2 block text-sm font-medium text-slate-300"
                  >
                    Email
                  </label>

                  <input
                    id="signup-email"
                    type="email"
                    placeholder="Enter your email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-3 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/10"
                  />

                </div>

                {/* Role */}

                <div>

                  <label
                    htmlFor="signup-role"
                    className="mb-2 block text-sm font-medium text-slate-300"
                  >
                    Role
                  </label>

                  <select
                    id="signup-role"
                    value={role}
                    onChange={(e) => setRole(e.target.value)}
                    className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-3 text-sm text-white outline-none transition focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/10"
                  >

                    <option value="quality_engineer">
                      Quality Engineer
                    </option>

                    <option value="factory_supervisor">
                      Factory Supervisor
                    </option>

                  </select>

                </div>

                {/* Password */}

                <div>

                  <label
                    htmlFor="signup-password"
                    className="mb-2 block text-sm font-medium text-slate-300"
                  >
                    Password
                  </label>

                  <div className="relative">

                    <input
                      id="signup-password"
                      type={showPassword ? "text" : "password"}
                      placeholder="Create a password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      required
                      className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-3 pr-20 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/10"
                    />

                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-semibold text-cyan-400 transition hover:text-cyan-300"
                    >
                      {showPassword ? "Hide" : "Show"}
                    </button>

                  </div>

                </div>

                {/* Confirm password */}

                <div>

                  <label
                    htmlFor="confirm-password"
                    className="mb-2 block text-sm font-medium text-slate-300"
                  >
                    Confirm Password
                  </label>

                  <div className="relative">

                    <input
                      id="confirm-password"
                      type={
                        showConfirmPassword
                          ? "text"
                          : "password"
                      }
                      placeholder="Confirm your password"
                      value={confirmPassword}
                      onChange={(e) =>
                        setConfirmPassword(e.target.value)
                      }
                      required
                      className="w-full rounded-xl border border-slate-700 bg-slate-800/80 px-4 py-3 pr-20 text-sm text-white outline-none transition placeholder:text-slate-500 focus:border-cyan-400 focus:ring-4 focus:ring-cyan-400/10"
                    />

                    <button
                      type="button"
                      onClick={() =>
                        setShowConfirmPassword(
                          !showConfirmPassword
                        )
                      }
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-xs font-semibold text-cyan-400 transition hover:text-cyan-300"
                    >
                      {showConfirmPassword ? "Hide" : "Show"}
                    </button>

                  </div>

                </div>

                {/* Signup button */}

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-3.5 text-sm font-bold text-white shadow-lg shadow-cyan-500/20 transition-all hover:-translate-y-0.5 hover:from-cyan-400 hover:to-blue-500 hover:shadow-cyan-500/30 focus:outline-none focus:ring-4 focus:ring-cyan-400/20 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading
                    ? "Creating account..."
                    : "Create Account"}
                </button>

              </form>
            )}

            {/* Login / signup switch */}

            <div className="mt-7 border-t border-slate-700/70 pt-6 text-center">

              {isSignup ? (

                <p className="text-sm text-slate-400">

                  Already have an account?{" "}

                  <button
                    type="button"
                    onClick={switchToLogin}
                    className="font-semibold text-cyan-400 transition hover:text-cyan-300"
                  >
                    Sign in
                  </button>

                </p>

              ) : (

                <p className="text-sm text-slate-400">

                  Don't have an account?{" "}

                  <button
                    type="button"
                    onClick={switchToSignup}
                    className="font-semibold text-cyan-400 transition hover:text-cyan-300"
                  >
                    Sign up
                  </button>

                </p>

              )}

            </div>

            {/* Footer */}

            <p className="mt-5 text-center text-xs text-slate-500">
              Secure AI-powered quality control platform
            </p>

          </div>

        </div>

      </div>

    </div>
  );
}

export default Login;

