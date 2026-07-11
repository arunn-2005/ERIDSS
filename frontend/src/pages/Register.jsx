import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { registerUser } from "../services/authService";
import "../styles/Register.css";

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
    confirm_password: "",
  });

  const [error, setError] = useState("");

  const handleChange = (e) => {
    setError("");

    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleRegister = async (e) => {
    e.preventDefault();

    setError("");

    if (formData.password !== formData.confirm_password) {
      setError("Passwords do not match");
      return;
    }

    try {
      await registerUser({
        username: formData.username,
        email: formData.email,
        password: formData.password,
      });

      navigate("/login");
    } catch (err) {
      if (err.response && err.response.data) {
        setError(err.response.data.detail);
      } else {
        setError("Registration failed. Please try again.");
      }
    }
  };

  return (
    <div className="register-page">

      <div className="register-left">

        <div className="brand">
          <h1>ERIDSS</h1>

          <h2>
            Enterprise Risk Intelligence Decision
            <br />
           Support System
          </h2>

          <p>
              Transform enterprise documents into actionable insights using
            AI-powered entity extraction, Knowledge Graphs and intelligent
            risk analysis.
          </p>
        </div>

      </div>

      <div className="register-right">

        <div className="register-card">

          <h2>Create Account</h2>

          <p className="subtitle">
            Register to access the ERIDSS platform.
          </p>

          <form onSubmit={handleRegister}>

            <div className="input-group">
              <label>Username</label>

              <input
                type="text"
                name="username"
                placeholder="Enter username"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>

            <div className="input-group">
              <label>Email</label>

              <input
                type="email"
                name="email"
                placeholder="Enter email"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="input-group">
              <label>Password</label>

              <input
                type="password"
                name="password"
                placeholder="Enter password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            <div className="input-group">
              <label>Confirm Password</label>

              <input
                type="password"
                name="confirm_password"
                placeholder="Confirm password"
                value={formData.confirm_password}
                onChange={handleChange}
                required
              />
            </div>

            {error && (
              <div className="error-box">
                {error}
              </div>
            )}

            <button
              type="submit"
              className="register-btn"
            >
              Create Account
            </button>

          </form>

          <div className="divider"></div>

          <button
            className="login-btn"
            onClick={() => navigate("/login")}
          >
            Back to Login
          </button>

        </div>

      </div>

    </div>
  );
}

export default Register;