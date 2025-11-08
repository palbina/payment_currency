# Instrucciones para Publicación en GitHub

## 🚀 Pasos para Subir el Repositorio

### 1. Crear el Repositorio en GitHub

1. Inicia sesión en [GitHub](https://github.com)
2. Haz clic en **"New repository"** (o en "+" > "New repository")
3. Configura el repositorio:
   - **Repository name**: `payment_currency`
   - **Description**: `Odoo 16 module for currency configuration in payment providers`
   - **Visibility**: Public (recomendado para módulos open source)
   - **NO marcar** "Add a README file" (ya tenemos uno profesional)
   - **NO marcar** "Add .gitignore" (ya tenemos uno profesional)
   - **NO marcar** "Choose a license" (ya está definida en el README)

4. Haz clic en **"Create repository"**

### 2. Conectar y Subir el Repositorio Local

Ejecuta los siguientes comandos en tu terminal:

```bash
# Agregar el remote de GitHub (reemplaza TU_USUARIO)
git remote add origin https://github.com/TU_USUARIO/payment_currency.git

# Verificar el remote
git remote -v

# Subir la rama main a GitHub
git push -u origin main

# Subir los tags
git push origin --tags
```

### 3. Configurar el Repositorio en GitHub

#### A. Configurar Descripción y Topics

1. Ve a la página principal de tu repositorio
2. Haz clic en **"About"** > **"Edit"**
3. Agrega una descripción corta: `Odoo 16 module for currency configuration in payment providers`
4. Agrega el website: `https://globalresponse.cl`
5. Agrega **Topics** (etiquetas):
   - `odoo`
   - `odoo16`
   - `payment`
   - `currency`
   - `odoo-module`
   - `python`

#### B. Configurar Branch Protection (Opcional pero recomendado)

1. Ve a **Settings** > **Branches**
2. Haz clic en **"Add rule"**
3. Configura:
   - **Branch name pattern**: `main`
   - **Require pull request reviews before merging**: ✅
   - **Require status checks to pass before merging**: ✅
   - **Require branches to be up to date before merging**: ✅

#### C. Configurar GitHub Pages (Opcional)

1. Ve a **Settings** > **Pages**
2. **Source**: Deploy from a branch
3. **Branch**: `main` / `/root`
4. **Theme**: Choose a theme (recomendado)

### 4. Crear un Release Profesional

1. Ve a **Releases** > **"Create a new release"**
2. **Tag**: `v16.0.0` (ya existe localmente)
3. **Target**: `main`
4. **Release title**: `v16.0.0 - Payment Currency for Odoo 16`
5. **Description**:
```markdown
## 🎉 Payment Currency v16.0.0 for Odoo 16

### ✨ Features
- Currency configuration per payment provider
- Forced currency conversion support
- Complete migration from Odoo 15 to 16
- Professional documentation and README
- Production-ready implementation

### 📦 Installation
```bash
# Clone the repository
git clone https://github.com/TU_USUARIO/payment_currency.git

# Copy to Odoo addons directory
cp -r payment_currency /path/to/odoo/addons/

# Install via Odoo Apps interface
```

### 🔧 Configuration
1. Go to Settings > Payments > Payment Providers
2. Configure allowed currencies per provider
3. Enable forced currency conversion if needed

### 🐛 Bug Fixes
- Fixed payment.acquirer to payment.provider migration
- Resolved currency validation issues
- Improved error handling

### 📚 Documentation
- Complete README with installation guide
- API documentation included
- Troubleshooting section added

### 🏆 Contributors
- @kilocode - Migration and Odoo 16 adaptation
- Daniel Santibáñez Polanco - Original development

---

**Download**: [payment_currency.zip](https://github.com/TU_USUARIO/payment_currency/archive/v16.0.0.zip)
```

6. Marca **"This is a pre-release"**: ❌ (es una versión estable)
7. Haz clic en **"Publish release"**

### 5. Configurar Badges para el README

Agrega estos badges al principio del README.md:

```markdown
[![License: LGPL-3](https://img.shields.io/badge/License-LGPL--3-blue.svg)](https://www.gnu.org/licenses/lgpl-3.0)
[![Odoo Version](https://img.shields.io/badge/Odoo-16.0-green.svg)](https://www.odoo.com/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Release](https://img.shields.io/github/release/TU_USUARIO/payment_currency.svg)](https://github.com/TU_USUARIO/payment_currency/releases/latest)
[![Downloads](https://img.shields.io/github/downloads/TU_USUARIO/payment_currency/total.svg)](https://github.com/TU_USUARIO/payment_currency/releases)
```

### 6. Configurar Issues y Pull Requests

#### Templates para Issues

Crea el archivo `.github/ISSUE_TEMPLATE/bug_report.md`:

```markdown
---
name: Bug Report
about: Create a report to help us improve
title: '[BUG] '
labels: bug
assignees: ''
---

**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

**Expected behavior**
A clear and concise description of what you expected to happen.

**Screenshots**
If applicable, add screenshots to help explain your problem.

**Environment:**
- Odoo Version: [e.g. 16.0]
- Payment Currency Version: [e.g. 16.0.0]
- Browser: [e.g. chrome, safari]
- OS: [e.g. Windows, macOS]

**Additional context**
Add any other context about the problem here.
```

### 7. Promoción del Módulo

#### A. Odoo Apps Store (Opcional)

Si quieres publicar en la Odoo Apps Store:

1. Crea una cuenta en [Odoo Apps](https://apps.odoo.com)
2. Prepara un archivo ZIP del módulo
3. Sigue las guías de publicación de Odoo
4. Agrega screenshots y descripción detallada

#### B. Compartir en Comunidades

- **Reddit**: r/odoo
- **Foro de Odoo**: https://www.odoo.com/forum/help-1
- **LinkedIn**: Comparte en grupos de Odoo
- **Twitter**: Menciona a @odoo

### 8. Mantenimiento Futuro

#### Flujo de Trabajo para Nuevas Versiones

```bash
# Crear rama de desarrollo
git checkout -b develop

# Hacer cambios y commits
git add .
git commit -m "feat: Add new feature"

# Fusionar con main
git checkout main
git merge develop

# Crear nuevo tag
git tag -a v16.0.1 -m "Release v16.0.1: Bug fixes and improvements"

# Subir cambios
git push origin main
git push origin --tags
```

#### Versionado Semánttico

- **MAJOR**: Cambios incompatibles (16.0.0 → 17.0.0)
- **MINOR**: Nuevas funcionalidades compatibles (16.0.0 → 16.1.0)
- **PATCH**: Bug fixes (16.0.0 → 16.0.1)

---

## 🎯 Checklist Final

- [ ] Repositorio creado en GitHub
- [ ] Código subido correctamente
- [ ] Tags subidos
- [ ] Release creado
- [ ] README actualizado con badges
- [ ] Issues templates configurados
- [ ] Branch protection configurado
- [ ] Topics agregados
- [ ] Documentación completa
- [ ] Licencia especificada

¡Felicidades! Tu módulo `payment_currency` está ahora profesionalmente publicado en GitHub. 🚀