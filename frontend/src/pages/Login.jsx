import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { loginUser } from "../services/authService";

function Login() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });

  const [errorMessage, setErrorMessage] = useState("");

  const handleChange = (e) => {
    setErrorMessage(""); // Clear error while typing

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
      localStorage.setItem("access_token", response.access_token);
      navigate("/dashboard");

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
    <div style={{ padding: "40px" }}>
      <h1>Login</h1>

      <form onSubmit={handleLogin}>
        <input
          type="email"
          name="email"
          placeholder="Enter Email"
          value={formData.email}
          onChange={handleChange}
        />

        <br /><br />

        <input
          type="password"
          name="password"
          placeholder="Enter Password"
          value={formData.password}
          onChange={handleChange}
        />

        <br /><br />

        {errorMessage && (
          <p style={{ color: "red", marginBottom: "15px" }}>
            {errorMessage}
          </p>
        )}

        <button type="submit">
          Login
        </button>
      </form>

      <br />

      <button onClick={() => navigate("/register")}>
        Create Account
      </button>
    </div>
  );
}

export default Login;