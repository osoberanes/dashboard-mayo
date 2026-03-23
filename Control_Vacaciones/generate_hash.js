const bcrypt = require('bcryptjs');

async function generateHash() {
  const password = 'admin123';
  const saltRounds = 10;
  
  try {
    const hash = await bcrypt.hash(password, saltRounds);
    console.log('Contraseña:', password);
    console.log('Hash generado:', hash);
    
    // Verificar que funciona
    const isValid = await bcrypt.compare(password, hash);
    console.log('Verificación:', isValid);
  } catch (error) {
    console.error('Error:', error);
  }
}

generateHash();