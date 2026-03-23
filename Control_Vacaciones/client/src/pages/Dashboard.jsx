import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import './Dashboard.css';

const Dashboard = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [recentSolicitudes, setRecentSolicitudes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, solicitudesRes] = await Promise.all([
        axios.get('/api/reportes/estadisticas').catch(() => ({ data: null })),
        axios.get('/api/solicitudes?limit=5')
      ]);

      setStats(statsRes.data);
      setRecentSolicitudes(solicitudesRes.data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (estado) => {
    switch (estado) {
      case 'aprobada': return '#27ae60';
      case 'rechazada': return '#e74c3c';
      case 'cancelada': return '#95a5a6';
      default: return '#f39c12';
    }
  };

  const getStatusText = (estado) => {
    switch (estado) {
      case 'aprobada': return 'Aprobada';
      case 'rechazada': return 'Rechazada';
      case 'cancelada': return 'Cancelada';
      default: return 'Pendiente';
    }
  };

  if (loading) {
    return <div className="loading">Cargando dashboard...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Bienvenido, {user?.nombre} {user?.apellidos}</p>
      </div>

      <div className="dashboard-grid">
        {/* Tarjeta de información personal */}
        <div className="dashboard-card user-info-card">
          <h3>Tu Información</h3>
          <div className="user-stats">
            <div className="stat-item">
              <span className="stat-label">Días Acumulados:</span>
              <span className="stat-value">{user?.dias_acumulados || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Departamento:</span>
              <span className="stat-value">{user?.departamento_nombre || 'N/A'}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Rol:</span>
              <span className="stat-value">
                {user?.rol === 'A' ? 'Administrador' : 
                 user?.rol === 'B' ? 'Manager' : 'Empleado'}
              </span>
            </div>
          </div>
        </div>

        {/* Estadísticas generales (solo para admin/manager) */}
        {stats && (user?.rol === 'A' || user?.rol === 'B') && (
          <div className="dashboard-card stats-card">
            <h3>Estadísticas Generales</h3>
            <div className="stats-grid">
              <div className="stat-box">
                <div className="stat-number">{stats.total_usuarios}</div>
                <div className="stat-label">Total Usuarios</div>
              </div>
              <div className="stat-box">
                <div className="stat-number">{stats.solicitudes_pendientes}</div>
                <div className="stat-label">Solicitudes Pendientes</div>
              </div>
              <div className="stat-box">
                <div className="stat-number">{stats.solicitudes_aprobadas_mes}</div>
                <div className="stat-label">Aprobadas este Mes</div>
              </div>
              <div className="stat-box">
                <div className="stat-number">{Math.round(stats.promedio_dias_acumulados * 10) / 10}</div>
                <div className="stat-label">Promedio Días</div>
              </div>
            </div>
          </div>
        )}

        {/* Solicitudes recientes */}
        <div className="dashboard-card recent-solicitudes">
          <h3>
            {user?.rol === 'C' ? 'Mis Solicitudes Recientes' : 'Solicitudes Recientes'}
          </h3>
          {recentSolicitudes.length === 0 ? (
            <p className="no-data">No hay solicitudes recientes</p>
          ) : (
            <div className="solicitudes-list">
              {recentSolicitudes.map((solicitud) => (
                <div key={solicitud.id} className="solicitud-item">
                  <div className="solicitud-header">
                    <span className="solicitud-user">
                      {user?.rol === 'C' ? 'Tu solicitud' : solicitud.usuario_nombre}
                    </span>
                    <span 
                      className="solicitud-status"
                      style={{ backgroundColor: getStatusColor(solicitud.estado) }}
                    >
                      {getStatusText(solicitud.estado)}
                    </span>
                  </div>
                  <div className="solicitud-details">
                    <span>{solicitud.fecha_inicio} - {solicitud.fecha_fin}</span>
                    <span>{solicitud.dias_solicitados} días</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Acciones rápidas */}
        <div className="dashboard-card quick-actions">
          <h3>Acciones Rápidas</h3>
          <div className="actions-grid">
            <button 
              className="action-btn primary"
              onClick={() => window.location.href = '/solicitudes'}
            >
              📝 Nueva Solicitud
            </button>
            <button 
              className="action-btn secondary"
              onClick={() => window.location.href = '/solicitudes'}
            >
              📋 Ver Solicitudes
            </button>
            {(user?.rol === 'A' || user?.rol === 'B') && (
              <>
                <button 
                  className="action-btn secondary"
                  onClick={() => window.location.href = '/usuarios'}
                >
                  👥 Gestionar Usuarios
                </button>
                <button 
                  className="action-btn secondary"
                  onClick={() => window.location.href = '/reportes'}
                >
                  📊 Ver Reportes
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;