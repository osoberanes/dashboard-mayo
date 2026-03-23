const bcrypt = require('bcryptjs');
const sqlite3 = require('sqlite3').verbose();
const path = require('path');

const dbPath = path.join(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath);

async function testLogin() {
  const email = 'admin@empresa.com';
  const password = 'admin123';
  
  console.log('Probando login con:', { email, password });
  
  // Buscar usuario
  db.get('SELECT * FROM usuarios WHERE email = ?', [email], async (err, user) => {
    if (err) {
      console.error('Error buscando usuario:', err);
      return;
    }
    
    if (!user) {
      console.log('Usuario no encontrado');
      return;
    }
    
    console.log('Usuario encontrado:', {
      id: user.id,
      email: user.email,
      nombre: user.nombre,
      rol: user.rol,
      activo: user.activo
    });
    
    // Verificar contraseña
    try {
      const passwordMatch = await bcrypt.compare(password, user.password_hash);
      console.log('Contraseña válida:', passwordMatch);
      
      if (passwordMatch) {
        console.log('✅ LOGIN EXITOSO');
      } else {
        console.log('❌ Contraseña incorrecta');
      }
    } catch (error) {
      console.error('Error verificando contraseña:', error);
    }
    
    db.close();
  });
}

testLogin();