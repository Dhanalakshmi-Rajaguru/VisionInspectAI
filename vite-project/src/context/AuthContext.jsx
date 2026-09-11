import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

const AuthContext = createContext(null);

const API_URL = "http://127.0.0.1:8000";


export function AuthProvider({ children }) {

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);


  // =====================================================
  // CHECK EXISTING LOGIN
  // =====================================================

  useEffect(() => {

    const token =
      localStorage.getItem("access_token");


    if (!token) {

      setLoading(false);

      return;
    }


    const checkUser = async () => {

      try {

        const response = await fetch(
          `${API_URL}/auth/me`,
          {
            method: "GET",

            headers: {
              Authorization: `Bearer ${token}`,
              Accept: "application/json",
            },
          }
        );


        if (!response.ok) {

          throw new Error(
            "Session expired. Please login again."
          );
        }


        const data =
          await response.json();


        setUser(data);

      } catch (error) {

        console.error(
          "Authentication check failed:",
          error
        );


        localStorage.removeItem(
          "access_token"
        );

        setUser(null);

      } finally {

        setLoading(false);
      }
    };


    checkUser();

  }, []);


  // =====================================================
  // LOGIN
  // =====================================================

  const login = async (
    email,
    password
  ) => {

    try {

      const response = await fetch(
        `${API_URL}/auth/login`,
        {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
          },

          body: JSON.stringify({
            email: email,
            password: password,
          }),
        }
      );


      // -------------------------------------------------
      // Handle HTTP error
      // -------------------------------------------------

      if (!response.ok) {

        let errorMessage =
          "Login failed.";

        try {

          const errorData =
            await response.json();

          errorMessage =
            errorData.detail ||
            errorMessage;

        } catch {
          // Response was not JSON
        }


        throw new Error(
          errorMessage
        );
      }


      // -------------------------------------------------
      // Read successful response
      // -------------------------------------------------

      const data =
        await response.json();


      console.log(
        "Login successful:",
        data
      );


      // -------------------------------------------------
      // Make sure token exists
      // -------------------------------------------------

      if (!data.access_token) {

        throw new Error(
          "Login succeeded but no access token was returned."
        );
      }


      // -------------------------------------------------
      // Save JWT
      // -------------------------------------------------

      localStorage.setItem(
        "access_token",
        data.access_token
      );


      // -------------------------------------------------
      // Login response already contains user
      // -------------------------------------------------

      if (data.user) {

        setUser(data.user);

        return data.user;
      }


      // -------------------------------------------------
      // Fallback: fetch /auth/me
      // -------------------------------------------------

      const userResponse =
        await fetch(
          `${API_URL}/auth/me`,
          {
            method: "GET",

            headers: {
              Authorization:
                `Bearer ${data.access_token}`,

              Accept: "application/json",
            },
          }
        );


      if (!userResponse.ok) {

        throw new Error(
          "Unable to fetch user information."
        );
      }


      const userData =
        await userResponse.json();


      setUser(userData);

      return userData;

    } catch (error) {

      console.error(
        "Login error:",
        error
      );


      // -------------------------------------------------
      // Browser/network error
      // -------------------------------------------------

      if (
        error instanceof TypeError &&
        error.message === "Failed to fetch"
      ) {

        throw new Error(
          "Cannot connect to VisionInspect AI server. Make sure FastAPI is running on http://127.0.0.1:8000."
        );
      }


      throw error;
    }
  };


  // =====================================================
  // LOGOUT
  // =====================================================

  const logout = () => {

    localStorage.removeItem(
      "access_token"
    );

    setUser(null);
  };


  // =====================================================
  // CONTEXT
  // =====================================================

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}


// =======================================================
// useAuth
// =======================================================

export function useAuth() {

  const context =
    useContext(AuthContext);


  if (!context) {

    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }


  return context;
}