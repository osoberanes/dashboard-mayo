# Lorekeeper

Sistema de investigación y escritura de ensayos de política internacional asistido por Claude Code.

## Estructura

```
lorekeeper/
├── skills/
│   ├── document-analyzer/     ← Analiza PDFs y páginas web
│   ├── video-analyzer/        ← Analiza videos de YouTube
│   ├── research-harvester/    ← Búsqueda web temática
│   ├── research-agent/        ← Propone enfoques del ensayo
│   ├── essay-architect/       ← Diseña la estructura
│   ├── essay-writer/          ← Redacta el borrador
│   ├── style-humanizer/       ← Ajusta la voz del autor
│   └── quality-checker/       ← Verifica citas y calidad
└── vault/
    ├── referencias/           ← Base de conocimiento
    ├── ensayos/               ← Borradores y versiones
    └── recursos/              ← Notas propias
```

## Flujo completo

```
[research-harvester] ──→ [document-analyzer / video-analyzer]
                                      ↓
                              vault/referencias/
                                      ↓
                          [research-agent] → propone enfoques
                                      ↓
                          [essay-architect] → diseña estructura
                                      ↓
                          [essay-writer] → redacta borrador
                                      ↓
                          [style-humanizer] → ajusta voz
                                      ↓
                          [quality-checker] → revisión final
                                      ↓
                              vault/ensayos/
```

## Configuración inicial

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/lorekeeper.git
cd lorekeeper
```

### 2. Instalar dependencias para video-analyzer
```bash
pip install playwright
playwright install chromium
```

### 3. Abrir el vault en Obsidian
- Abre Obsidian → "Open folder as vault"
- Selecciona la carpeta `vault/` dentro de este repositorio

### 4. Instalar los skills en Claude Code
Coloca cada carpeta de `skills/` en el directorio de skills de Claude Code.

## Flujo de trabajo diario

```bash
# Al llegar a cualquier equipo
git pull

# Al terminar la sesión
git add .
git commit -m "sesión: [descripción breve]"
git push
```
