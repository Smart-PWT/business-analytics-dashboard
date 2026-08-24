import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { account } from "../config/appwrite";

function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async(e) => {
    e.preventDefault();
    setError("");

    if (!email || !password) {
      setError("Please fill in all fields.");
      return;
    }

    try {
      // Delete any active session first to avoid session conflicts
      try {
        await account.deleteSession("current");
      } catch {
        // Ignore if there is no active session
      }
      await account.createEmailPasswordSession({ email: email.trim(), password });
      navigate("/dashboard");
    } catch (err) {
      alert(err.message || "Failed to find the user's Account");
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Header banner */}
        <div className="auth-banner">
          <span>HISAABI</span>
        </div>

        {/* Toggle buttons */}
        <div className="auth-tabs">
          <button className="auth-tab auth-tab--active">LOG IN</button>
          <Link to="/signup" className="auth-tab">SIGN UP</Link>
        </div>

        <h2 className="auth-title">ACCOUNT LOGIN</h2>

        <form className="auth-form" onSubmit={handleSubmit}>
          {/* Email */}
          <div className="auth-field">
            <label className="auth-label">EMAIL ADDRESS</label>
            <input
              type="email"
              className="auth-input"
              placeholder="name@firm.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          {/* Password */}
          <div className="auth-field">
            <div className="auth-label-row">
              <label className="auth-label">PASSWORD</label>
              <Link to="/forgot-password" className="auth-forgot">
                Forgot?
              </Link>
            </div>
            <input
              type="password"
              className="auth-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {/* Error */}
          {error && <p className="auth-error">{error}</p>}

          {/* Submit */}
          <button type="submit" className="auth-btn">
            LOG IN
          </button>
        </form>

        <div className="auth-divider" />

        <p className="auth-note">
          Your data is verified. User permission to your account.
        </p>
      </div>
    </div>
  );
}

export default Login;
