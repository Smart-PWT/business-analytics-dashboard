import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { ID } from "appwrite";
import { account } from "../config/appwrite";

function Signup() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [confirm, setConfirm] = useState("");

  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();
    setError("");

    if (!name || !email || !password || !confirm) {
      setError("Please fill in all fields.");
      return;
    }
    if (password !== confirm) {
      setError("Passwords do not match.");
      return;
    }

    const signupPromise = account.create(ID.unique(), email.trim(), password, name.trim());

    signupPromise.then(
      function (res) {
        navigate("/login");
      },
      function (error) {
        alert(error);
      },
    );
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        {/* Header banner */}
        <div className="auth-banner">
          <span>HISAABI</span>
        </div>

        <div className="auth-tabs">
          <Link to="/login" className="auth-tab">
            LOG IN
          </Link>
          <button className="auth-tab auth-tab--active">SIGN UP</button>
        </div>

        <h2 className="auth-title">CREATE ACCOUNT</h2>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="auth-field">
            <label className="auth-label">FULL NAME</label>
            <input
              type="text"
              className="auth-input"
              placeholder="Your full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          </div>

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

          <div className="auth-field">
            <label className="auth-label">PASSWORD</label>
            <input
              type="password"
              className="auth-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <div className="auth-field">
            <label className="auth-label">CONFIRM PASSWORD</label>
            <input
              type="password"
              className="auth-input"
              placeholder="••••••••"
              value={confirm}
              onChange={(e) => setConfirm(e.target.value)}
            />
          </div>

          {error && <p className="auth-error">{error}</p>}

          <button type="submit" className="auth-btn">
            CREATE ACCOUNT
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

export default Signup;
