import { useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './Layout.css';

const Layout = ({ children }) => {
  const { user, logout, isAdmin, isManagerOrAdmin } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    {
      path: '/dashboard',
      label: 'Dashboard',
      icon: '📊',
      roles: ['A', 'B', 'C']
    },
    {
      path: '/solicitudes',
      label: 'Solicitudes',
      icon: '📝',
      roles: ['A', 'B', 'C']
    },
    {
      path: '/usuarios',
      label: 'Usuarios',
      icon: '👥',
      roles: ['A', 'B']
    },
    {
      path: '/reportes',
      label: 'Reportes',
      icon: '📈',
      roles: ['A', 'B']
    },
    {
      path: '/configuracion',
      label: 'Configuración',
      icon: '⚙️',
      roles: ['A']
    }
  ];

  const filteredMenuItems = menuItems.filter(item => 
    item.roles.includes(user?.rol)
  );

  const getRoleDisplayName = (rol) => {
    switch (rol) {
      case 'A': return 'Administrador';
      case 'B': return 'Manager';
      case 'C': return 'Empleado';
      default: return 'Usuario';
    }
  };

  return (
    <div className="layout">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <button 
            className="sidebar-toggle"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
          >
            ☰
          </button>
          <h1 className="app-title">Control de Vacaciones</h1>
        </div>
        
        <div className="header-right">
          <div className="user-info">
            <span className="user-name">{user?.nombre} {user?.apellidos}</span>
            <span className="user-role">({getRoleDisplayName(user?.rol)})</span>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            🚪 Salir
          </button>
        </div>
      </header>

      <div className="layout-body">
        {/* Sidebar */}
        <aside className={`sidebar ${isSidebarOpen ? 'open' : 'closed'}`}>
          <nav className="sidebar-nav">
            {filteredMenuItems.map((item) => (
              <Link
                key={item.path}
                to={item.path}
                className={`nav-item ${location.pathname === item.path ? 'active' : ''}`}
              >
                <span className="nav-icon">{item.icon}</span>
                {isSidebarOpen && <span className="nav-label">{item.label}</span>}
              </Link>
            ))}
          </nav>

          {isSidebarOpen && (
            <div className="sidebar-footer">
              <div className="user-details">
                <p><strong>Email:</strong> {user?.email}</p>
                <p><strong>Departamento:</strong> {user?.departamento_nombre || 'N/A'}</p>
                {user?.dias_acumulados !== undefined && (
                  <p><strong>Días disponibles:</strong> {user.dias_acumulados}</p>
                )}
              </div>
            </div>
          )}
        </aside>

        {/* Main Content */}
        <main className="main-content">
          {children}
        </main>
      </div>
    </div>
  );
};

export default Layout;