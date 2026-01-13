# 📊 Sistema GYIE – Gestión Integral para Droguerías

Sistema de escritorio desarrollado en **Python** bajo el patrón **MVC**, diseñado específicamente para la gestión administrativa de droguerías. Permite el control de clientes, empleados, deudas, abonos, estadísticas y respaldos en Excel, con persistencia en MySQL.

**🔹 Estado:** ✅ **Funcional y estable** – Listo para uso en entornos reales  
**🔹 Arquitectura:** 🏗️ **Modular y escalable** (MVC)  
**🔹 Destino:** 🏪 **Administración de droguerías / negocios comerciales**

---

## 🧩 Características Principales

### 👥 **Gestión de Clientes y Empleados**
- CRUD completo de clientes y empleados
- Historial detallado de transacciones por cliente
- Control de accesos por roles (administrador / empleado)

### 💰 **Control de Deudas y Abonos**
- Registro detallado de deudas con descripción y monto
- Sistema de abonos parciales o totales
- Seguimiento de saldos pendientes

### 📊 **Dashboard Interactivo**
- Métricas en tiempo real (deudas activas, total abonado, clientes registrados)
- Indicadores visuales de estados
- Filtros avanzados por fecha, cliente, estado y monto

### 📈 **Estadísticas y Reportes**
- Gráficos generados con Matplotlib (integrados en Tkinter)
- Clientes con mayor deuda
- Comparativo deudas vs. abonos
- Transacciones por mes/rango de fechas

### 💾 **Sistema de Backups**
- **Exportación manual/automática a Excel** (clientes, transacciones)
- **Importación** de datos desde archivos generados por el sistema
- **Envío automático por correo** con archivos adjuntos
- Rutas personalizables de guardado

### 🔐 **Seguridad y Configuración**
- Autenticación segura con cifrado
- Variables de entorno para configuración sensible (.env)
- Confirmaciones para operaciones críticas
- Interfaz intuitiva con validaciones visuales

---

## 🏗️ Arquitectura MVC
GIYE
├── controlador
│   └── controlador.py
├── modelo
│   ├── cliente.py
│   ├── conexion.py
│   ├── datos_configuracion.py
│   ├── datos_graficas.py
│   ├── enviador_mensajes.py
│   ├── filtros.py
│   ├── gestion_archivos.py
│   └── transaccion.py
├── vista
│   ├── panel_administrador_backup.py
│   ├── panel_administrador_empleado.py
│   ├── panel_administrador_estadisticas.py
│   ├── panel_administrador.py
│   ├── panel_dashboard.py
│   ├── panel_inicio.py
│   ├── ventana_emergente.py
│   └── ventana.py
├── db.sql
├── main.py
├── readme.md
└── requirements.txt


### 🔹 **Módulo Modelo**
- Conexión centralizada a MySQL
- CRUD de entidades
- Consultas avanzadas con filtros
- Generación/importación de Excel
- Envío de correos con adjuntos

### 🔹 **Módulo Vista**
- Interfaz con Tkinter
- Dashboard con métricas visuales
- Paneles modulares (clientes, empleados, backups, estadísticas)
- Calendarios integrados (tkcalendar)

### 🔹 **Módulo Controlador**
- Gestión de sesiones y permisos
- Validación de datos
- Orquestación de operaciones
- Navegación entre paneles

---

## 🛠️ Stack Tecnológico

| Tecnología | Uso |
|------------|-----|
| **Python 3.10+** | Lenguaje principal |
| **Tkinter** | Interfaz gráfica de escritorio |
| **MySQL** | Base de datos relacional |
| **Pandas** | Procesamiento de datos y Excel |
| **Matplotlib** | Generación de gráficos estadísticos |
| **tkcalendar** | Selectores de fecha en GUI |
| **python-dotenv** | Gestión de variables de entorno |
| **SMTP** | Envío de correos con backups |

---

## ⚙️ Instalación y Configuración

### 1. Requisitos del Sistema
```bash
# En Linux (Tkinter no se instala vía pip)
sudo apt install python3-tk
```

### 2. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configuración de Base de Datos y .env

Crear archivo .env en la raíz del proyecto con la siguiente estructura:

```bash
# ===============================
# CONFIGURACIÓN SMTP
# ===============================
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=notificaciones.yalejo@gmail.com
SMTP_PASSWORD=secreto
SMTP_USE_TLS=true

# ===============================
# BACKUPS
# ===============================
BACKUP_DIR=/home/yefer-computador-v0/Escritorio/Python/backups

# ===============================
# BASE DE DATOS 
# ===============================
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=contraseña
DB_NAME=ybook
DB_PORT=3306
```

📝 Notas importantes sobre el archivo .env:

SMTP_PASSWORD: Usar token de aplicación de Gmail (no la contraseña normal)

BACKUP_DIR: Ruta donde se guardarán los archivos Excel de backup

DB_PASSWORD: Contraseña de tu usuario de MySQL

DB_NAME: Nombre de la base de datos creada en MySQLv

### 4. Crear Base de Datos en MySQL
```bash
python main.py
```
### 5. Ejecución
```bash
python main.py
```

---
👨‍💻 Autor
Yeferson Alejandro Acosta Millan
Desarrollador Full Stack
📧 Contacto: yeferchofas2005@gmail.com
🔗 GitHub: @yeferchofas2005-dev