# 📊 GYIE – Gestión de Ingresos y Egresos

Sistema de escritorio desarrollado en **Python** bajo el patrón **MVC**, diseñado para la gestión administrativa de droguerías y negocios comerciales. Permite el control de clientes, empleados, deudas, abonos, estadísticas y respaldos en Excel, con persistencia en MySQL.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat&logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-5.7+-4479A1?style=flat&logo=mysql&logoColor=white)
![Tkinter](https://img.shields.io/badge/Tkinter-GUI-informational?style=flat)
![Estado](https://img.shields.io/badge/Estado-Estable-brightgreen?style=flat)

---

## 📋 Tabla de Contenidos

- [Características](#-características-principales)
- [Arquitectura](#-arquitectura-mvc)
- [Stack Tecnológico](#-stack-tecnológico)
- [Instalación](#-instalación-y-configuración)
- [Autor](#-autor)

---

## ✨ Características Principales

### 👥 Gestión de Clientes y Empleados
- CRUD completo de clientes y empleados
- Búsqueda en tiempo real con autocompletado
- Historial detallado de transacciones por cliente
- Control de accesos por roles (administrador / empleado)

### 💰 Control de Deudas y Abonos
- Registro de deudas: **Fiado**, **Préstamo** y **Nequi Pendiente**
- Abonos en **efectivo** o **Nequi**
- Seguimiento de estados: `PENDIENTE`, `CANCELADA`, `PAGADA`
- Tachado de deudas con flujo de pago diferenciado por método

### 📊 Dashboard Interactivo
- Totales en tiempo real: deuda pendiente, caja y Nequi
- Filtros combinados por fecha, nombre, estado y monto
- Colores diferenciados por tipo de transacción (rojo / verde / morado)
- Detalle completo al hacer clic sobre cualquier transacción

### 📈 Estadísticas y Reportes
- **Resumen del día**: caja, Nequi, deudas nuevas y pagadas
- **Clientes con mayor deuda** pendiente
- **Clientes riesgosos**: sin pagar hace más de 30 días
- **Rendimiento por empleado**: total fiado y % recuperado
- **Flujo semanal**: ingresos vs deudas de los últimos 7 días
- **Movimientos por mes**: comparativo histórico
- Gráficos generados con Matplotlib integrados en la interfaz

### 💾 Sistema de Backups
- Exportación manual a Excel por rango de fechas
- Exportación del listado completo de clientes
- Envío automático por correo con archivos adjuntos
- Importación segura desde archivos generados por el sistema

### 🔐 Seguridad
- Autenticación de administrador con contraseña cifrada (SHA-256)
- Confirmación para operaciones críticas (tachado de deudas de empleados)
- Variables de entorno para credenciales sensibles

---

## 🏗️ Arquitectura MVC

```
GYIE/
├── controlador/
│   └── controlador.py          # Orquestador principal MVC
├── modelo/
│   ├── cliente.py              # CRUD de clientes y empleados
│   ├── conexion.py             # Conexión centralizada a MySQL
│   ├── datos_configuracion.py  # Contraseña admin y correo backup
│   ├── datos_graficas.py       # Consultas estadísticas agregadas
│   ├── enviador_mensajes.py    # Envío de correos SMTP con adjuntos
│   ├── filtros.py              # Consultas filtradas de transacciones
│   ├── gestion_archivos.py     # Exportación e importación de Excel
│   └── transaccion.py          # CRUD de transacciones
├── vista/
│   ├── ventana.py                          # Ventana raíz y gestor de paneles
│   ├── ventana_emergente.py                # Diálogos, formularios y alertas
│   ├── panel_inicio.py                     # Pantalla de login
│   ├── panel_dashboard.py                  # Vista principal de transacciones
│   ├── panel_administrador.py              # Menú de administración
│   ├── panel_administrador_empleado.py     # Gestión de empleados
│   ├── panel_administrador_backup.py       # Gestión de backups
│   └── panel_administrador_estadisticas.py # Estadísticas y gráficos
├── assets/
│   └── icono.ico
├── .env                  # Variables de entorno (no incluido en el repo)
├── .gitignore
├── db.sql                # Script de creación de la base de datos
├── main.py               # Punto de entrada
├── README.md
└── requirements.txt
```

### Flujo de navegación

```
Inicio
  ├── Login Administrador
  │     └── Panel Administrador
  │           ├── Gestión de Empleados
  │           ├── Backups (generar / importar)
  │           ├── Estadísticas
  │           └── Cambiar contraseña
  └── Login Empleado
        └── Dashboard
              ├── Ver / filtrar transacciones
              ├── Registrar deuda
              ├── Registrar abono
              └── Tachar deuda (marcar como pagada)
```

---

## 🛠️ Stack Tecnológico

| Tecnología | Versión | Uso |
|---|---|---|
| **Python** | 3.10+ | Lenguaje principal |
| **Tkinter** | stdlib | Interfaz gráfica de escritorio |
| **MySQL** | 5.7+ | Base de datos relacional |
| **mysql-connector-python** | latest | Conexión a MySQL desde Python |
| **Pandas** | latest | Procesamiento de datos y Excel |
| **openpyxl** | latest | Lectura/escritura de archivos `.xlsx` |
| **Matplotlib** | latest | Gráficos estadísticos integrados en GUI |
| **tkcalendar** | latest | Selector de fechas en la interfaz |
| **python-dotenv** | latest | Gestión de variables de entorno |
| **smtplib** | stdlib | Envío de correos con backups adjuntos |

---

## ⚙️ Instalación y Configuración

### 1. Requisitos previos

- Python 3.10 o superior
- MySQL 5.7 o superior
- En Linux, instalar Tkinter manualmente (no se incluye en pip):

```bash
sudo apt install python3-tk
```

### 2. Clonar el repositorio

```bash
git clone https://github.com/yeferchofas2005-dev/GYIE.git
cd GYIE
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar la base de datos

Ejecutar el script en MySQL Workbench o desde consola:

```bash
mysql -u root -p < db.sql
```

### 5. Crear el archivo `.env`

Crear un archivo `.env` en la raíz del proyecto con la siguiente estructura:

```env
# ===============================
# BASE DE DATOS
# ===============================
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=tu_contraseña
DB_NAME=ybook

# ===============================
# SMTP (correo de backups)
# ===============================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=tu_correo@gmail.com
SMTP_PASSWORD=tu_token_de_aplicacion
SMTP_USE_TLS=true

# ===============================
# BACKUPS
# ===============================
BACKUP_DIR=/ruta/donde/guardar/backups
```

> **⚠️ Importante:**
> - `SMTP_PASSWORD` debe ser un **token de aplicación** de Gmail, no tu contraseña normal. Puedes generarlo en [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords).
> - El archivo `.env` **nunca debe subirse al repositorio**. Ya está incluido en `.gitignore`.

### 6. Ejecutar la aplicación

```bash
python main.py
```

### 7. Credenciales por defecto

| Rol | Contraseña |
|---|---|
| Administrador | `admin` |

> Se recomienda cambiar la contraseña desde el panel de administración en el primer uso.

---

## 📸 Capturas de pantalla

> *Próximamente*

---

## 👨‍💻 Autor

**Yeferson Alejandro Acosta Millán**  
Desarrollador Full Stack  
📧 yeferchofas2005@gmail.com  
🔗 [github.com/yeferchofas2005-dev](https://github.com/yeferchofas2005-dev)