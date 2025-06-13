```
# 🔥 SVP (Sistema Virtual de Puertos)

## 📌 Descripción  
SVP es una herramienta avanzada de **escaneo de puertos** desarrollada en **Python** con **Flask**,
enfocada en la detección de vulnerabilidades y el análisis de seguridad. Su sistema permite almacenar
datos en una **base de datos**, registrar **IP**, identificar amenazas, extraer **banners de seguridad**,
y generar reportes en **PDF** con información detallada sobre los escaneos realizados.

## 🌟 Características  
✔️ **Escaneo de puertos** para analizar la seguridad de una red  
✔️ 🛡️ **Detección de vulnerabilidades** y evaluación de amenazas  
✔️ 📋 **Obtención de banners de seguridad** para identificación de servicios  
✔️ 🗄️ **Base de datos integrada** para almacenar y consultar escaneos previos  
✔️ 📄 **Generación de informes en PDF** con detalles de cada análisis  
✔️ 📜 **Historial de escaneos** accesible desde la interfaz  

## 🚀 Instalación  
Para instalar y ejecutar SVP, sigue estos pasos:  

```sh
git clone https://github.com/usuario/svp.git
cd svp
pip install -r requirements.txt
```

## 🖥️ Uso  
Para iniciar la herramienta, usa el siguiente comando:  

```sh
python app.py
```

Luego, accede a la interfaz web en `http://localhost:5001` para comenzar el escaneo.

## 🔧 Dependencias  
SVP utiliza las siguientes dependencias:  
- 🐍 **Python** (>=3.x)  
- 🌐 **Flask**  
- 🗄️ **SQLite/MySQL** (según configuración)  
- 📝 **Bibliotecas para generación de PDF de los puertos escaneados**  

## 🤝 Contribución  
Si deseas mejorar SVP, envía un **pull request** o abre un **issue** en el repositorio para colaborar en su desarrollo.

## 📜 Licencia  
Este proyecto está bajo la licencia **MIT**, permitiendo su uso y modificación dentro de los términos establecidos.