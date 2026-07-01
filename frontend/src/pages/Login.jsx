import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/authService";
import "../styles/Login.css";

function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [errorMessage, setErrorMessage] = useState("");

  const handleChange = (e) => {
    setErrorMessage("");

    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleLogin = async (e) => {
    e.preventDefault();

    setErrorMessage("");

    try {
      const response = await loginUser(formData);

      // Store authentication token
      localStorage.setItem("access_token", response.access_token);

      // Store login session
      localStorage.setItem("isLoggedIn", "true");

      // Redirect to dashboard
      navigate("/dashboard", { replace: true });

    } catch (error) {
      if (error.response) {
        setErrorMessage("Invalid Email or Password");
      } else {
        setErrorMessage("Something went wrong. Please try again.");
      }

      console.error(error);
    }
  };

  return (
    <div className="login-page">
      <div className="login-left">
        <div className="brand">
          <h1>ERIDSS</h1>

          <h2>
            Enterprise Risk Intelligence Decision Support System
          </h2>

          <p>
            Transform enterprise documents into actionable insights using
            AI-powered entity extraction, Knowledge Graphs and intelligent
            risk analysis.
          </p>
        </div>
      </div>

      <div className="login-right">
        <div className="login-card">

          <h2>Welcome Back</h2>

          <p className="subtitle">
            Sign in to continue to ERIDSS
          </p>

          <form onSubmit={handleLogin}>

            <div className="input-group">
              <label>Email Address</label>

              <input
                type="email"
                name="email"
                placeholder="Enter your email"
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
                placeholder="Enter your password"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            {errorMessage && (
              <div className="error-box">
                {errorMessage}
              </div>
            )}

            <button className="login-btn" type="submit">
              Login
            </button>

          </form>

          <div className="divider"></div>

          <button
            className="register-btn"
            onClick={() => navigate("/register")}
          >
            Create Account
          </button>

        </div>
      </div>
    </div>
  );
}

export default Login;