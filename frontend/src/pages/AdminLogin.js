import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { adminLogin } from "../services/adminService";

export function AdminLogin() {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await adminLogin(username, password);
      navigate("/admin");
    } catch (err) {
      setError(err.message || "Giriş başarısız. Lütfen bilgilerinizi kontrol edin.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="adminLoginPage">
      <div className="adminLoginCard">
        <div className="adminLoginBrand">
          <div className="adminLoginLogo">🏥</div>
          <h1 className="adminLoginTitle">Klinik Yönetim Paneli</h1>
          <p className="adminLoginSub">İşletme hesabınızla giriş yapın</p>
        </div>

        <form className="adminLoginForm" onSubmit={handleSubmit}>
          <div className="field">
            <label className="label" htmlFor="adminUser">Kullanıcı Adı</label>
            <div className="inputWrap">
              <span className="inputIcon">👤</span>
              <input
                id="adminUser"
                className="input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="admin"
                autoComplete="username"
                required
              />
            </div>
          </div>

          <div className="field">
            <label className="label" htmlFor="adminPass">Şifre</label>
            <div className="inputWrap">
              <span className="inputIcon">🔒</span>
              <input
                id="adminPass"
                className="input"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                autoComplete="current-password"
                required
              />
            </div>
          </div>

          {error && <div className="alert alertError">{error}</div>}

          <button
            className="btn btnPrimary btnLarge"
            type="submit"
            disabled={loading}
            style={{ width: "100%", marginTop: "4px" }}
          >
            {loading ? (
              <>
                <span className="spinner" aria-hidden="true" />
                Giriş yapılıyor...
              </>
            ) : (
              "Giriş Yap"
            )}
          </button>
        </form>

        <p className="adminLoginFooter">
          Bu panel yalnızca yetkili klinik personeline açıktır.
        </p>
      </div>
    </div>
  );
}
