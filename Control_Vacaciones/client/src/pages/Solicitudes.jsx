import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import './Solicitudes.css';

const Solicitudes = () => {
  const { user } = useAuth();
  const [solicitudes, setSolicitudes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    fecha_inicio: '',
    fecha_fin: '',
    motivo: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchSolicitudes();
  }, []);

  const fetchSolicitudes = async () => {
    try {
      const response = await axios.get('/api/solicitudes');
      setSolicitudes(response.data);
    } catch (error) {
      console.error('Error fetching solicitudes:', error);
      setError('Error cargando solicitudes');
    } finally {
      setLoading(false);
    }
  };

  const calculateDays = (start, end) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    const diffTime = Math.abs(endDate - startDate);
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (name === 'fecha_inicio' || name === 'fecha_fin') {
      if (formData.fecha_inicio && (name === 'fecha_fin' ? value : formData.fecha_fin)) {
        const start = name === 'fecha_inicio' ? value : formData.fecha_inicio;
        const end = name === 'fecha_fin' ? value : formData.fecha_fin;
        if (start && end) {
          const days = calculateDays(start, end);
          setFormData(prev => ({ ...prev, dias_solicitados: days }));
        }
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!formData.fecha_inicio || !formData.fecha_fin) {
      setError('Las fechas de inicio y fin son requeridas');
      return;
    }

    const dias_solicitados = calculateDays(formData.fecha_inicio, formData.fecha_fin);

    try {
      await axios.post('/api/solicitudes', {
        ...formData,
        dias_solicitados
      });
      
      setSuccess('Solicitud creada exitosamente');
      setFormData({ fecha_inicio: '', fecha_fin: '', motivo: '' });
      setShowForm(false);
      fetchSolicitudes();
    } catch (error) {
      setError(error.response?.data?.error || 'Error creando solicitud');
    }
  };

  const handleApprove = async (id) => {
    try {
      await axios.put(`/api/solicitudes/${id}/aprobar`, {
        comentarios: 'Aprobada'
      });
      setSuccess('Solicitud aprobada exitosamente');
      fetchSolicitudes();
    } catch (error) {
      setError(error.response?.data?.error || 'Error aprobando solicitud');
    }
  };

  const handleReject = async (id) => {
    const comentarios = prompt('Comentarios de rechazo (opcional):');
    try {
      await axios.put(`/api/solicitudes/${id}/rechazar`, {
        comentarios
      });
      setSuccess('Solicitud rechazada');
      fetchSolicitudes();
    } catch (error) {
      setError(error.response?.data?.error || 'Error rechazando solicitud');
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
    return <div className="loading">Cargando solicitudes...</div>;
  }

  return (
    <div className="solicitudes">
      <div className="solicitudes-header">
        <h1>Gestión de Solicitudes</h1>
        <button 
          className="btn-primary" 
          onClick={() => setShowForm(true)}
        >
          + Nueva Solicitud
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}
      {success && <div className="success-message">{success}</div>}

      {/* Formulario de nueva solicitud */}
      {showForm && (
        <div className="modal-overlay">
          <div className="modal">
            <div className="modal-header">
              <h2>Nueva Solicitud de Vacaciones</h2>
              <button 
                className="btn-close" 
                onClick={() => setShowForm(false)}
              >
                ×
              </button>
            </div>
            
            <form onSubmit={handleSubmit} className="solicitud-form">
              <div className="form-row">
                <div className="form-group">
                  <label>Fecha de Inicio</label>
                  <input
                    type="date"
                    name="fecha_inicio"
                    value={formData.fecha_inicio}
                    onChange={handleInputChange}
                    required
                    min={new Date().toISOString().split('T')[0]}
                  />
                </div>
                
                <div className="form-group">
                  <label>Fecha de Fin</label>
                  <input
                    type="date"
                    name="fecha_fin"
                    value={formData.fecha_fin}
                    onChange={handleInputChange}
                    required
                    min={formData.fecha_inicio || new Date().toISOString().split('T')[0]}
                  />
                </div>
              </div>

              {formData.fecha_inicio && formData.fecha_fin && (
                <div className="days-info">
                  <strong>Días solicitados: {calculateDays(formData.fecha_inicio, formData.fecha_fin)}</strong>
                </div>
              )}

              <div className="form-group">
                <label>Motivo (opcional)</label>
                <textarea
                  name="motivo"
                  value={formData.motivo}
                  onChange={handleInputChange}
                  placeholder="Describe el motivo de tu solicitud..."
                  rows={3}
                />
              </div>

              <div className="form-actions">
                <button type="button" onClick={() => setShowForm(false)} className="btn-secondary">
                  Cancelar
                </button>
                <button type="submit" className="btn-primary">
                  Crear Solicitud
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lista de solicitudes */}
      <div className="solicitudes-list">
        {solicitudes.length === 0 ? (
          <div className="no-solicitudes">
            <p>No hay solicitudes registradas</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="solicitudes-table">
              <thead>
                <tr>
                  <th>ID</th>
                  {user?.rol !== 'C' && <th>Usuario</th>}
                  <th>Fecha Inicio</th>
                  <th>Fecha Fin</th>
                  <th>Días</th>
                  <th>Estado</th>
                  <th>Motivo</th>
                  <th>Fecha Creación</th>
                  {user?.rol !== 'C' && <th>Acciones</th>}
                </tr>
              </thead>
              <tbody>
                {solicitudes.map((solicitud) => (
                  <tr key={solicitud.id}>
                    <td>{solicitud.id}</td>
                    {user?.rol !== 'C' && <td>{solicitud.usuario_nombre}</td>}
                    <td>{new Date(solicitud.fecha_inicio).toLocaleDateString()}</td>
                    <td>{new Date(solicitud.fecha_fin).toLocaleDateString()}</td>
                    <td>{solicitud.dias_solicitados}</td>
                    <td>
                      <span 
                        className="status-badge"
                        style={{ backgroundColor: getStatusColor(solicitud.estado) }}
                      >
                        {getStatusText(solicitud.estado)}
                      </span>
                    </td>
                    <td>{solicitud.motivo || '-'}</td>
                    <td>{new Date(solicitud.fecha_creacion).toLocaleDateString()}</td>
                    {user?.rol !== 'C' && (
                      <td>
                        {solicitud.estado === 'pendiente' && (
                          <div className="action-buttons">
                            <button 
                              className="btn-approve"
                              onClick={() => handleApprove(solicitud.id)}
                            >
                              ✓ Aprobar
                            </button>
                            <button 
                              className="btn-reject"
                              onClick={() => handleReject(solicitud.id)}
                            >
                              ✗ Rechazar
                            </button>
                          </div>
                        )}
                        {solicitud.estado !== 'pendiente' && (
                          <span className="approved-by">
                            {solicitud.estado === 'aprobada' ? 'Aprobada' : 'Rechazada'} por {solicitud.aprobado_por_nombre}
                          </span>
                        )}
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Solicitudes;