# Módulo TNSRequest - Documentación

## Descripción General

El módulo `TNSRequest` es una clase de Python que proporciona una interfaz para interactuar con la API de TNS (Tributario Nacional Sistematizado). Esta clase maneja automáticamente la autenticación, peticiones HTTP y el manejo de errores para consultas relacionadas con prediales e impuestos de industria y comercio (ICA).

## Cambios Principales v2

La clase ha sido actualizada para trabajar con la nueva versión de la API de TNS (v2) que implementa un sistema de autenticación basado en tokens Bearer en lugar de parámetros de consulta.

### Principales Cambios:
- **URL Base**: Actualizada de `https://api-gov.tns.co/api/` a `https://api-gov.tns.co/v2/`
- **Autenticación**: Cambio de parámetros de consulta a autenticación Bearer con token
- **Persistencia de Token**: El token se almacena y reutiliza hasta que expire
- **Renovación Automática**: Renovación automática del token en caso de expiración (máximo 2 intentos)

## Estructura de la Clase

### Propiedades

- `url`: URL base de la API (v2)
- `endpoints`: Diccionario con los endpoints disponibles organizados por categoría
- `request`: Instancia de la librería requests
- `token`: Token de autenticación actual (se almacena automáticamente)

### Endpoints Disponibles

#### Prediales
- **Listar**: `Predial/ListarPrediosDocumento` - Lista predios por documento
- **PDF**: `Predial/GenRecTemporalFicha` - Genera recibo temporal por ficha

#### ICA (Industria y Comercio)
- **Establecimientos**: `Local/ListarEstablecimientosDocumento` - Lista establecimientos por documento
- **Historial**: `Local/GetAllDeclaracionesPlaca` - Obtiene historial de declaraciones por placa

## Métodos Principales

### Métodos Públicos

#### `getprediales(cc: str)`
Consulta la lista de predios asociados a un documento específico.

**Parámetros:**
- `cc` (str): Número de documento de identidad

**Retorna:**
- dict: Respuesta de la API con la lista de predios

**URL Final Generada:**
```
https://api-gov.tns.co/v2/Predial/ListarPrediosDocumento?documento={cc}
```

#### `getpaymethod(ficha: str)`
Obtiene el método de pago asociado a una ficha específica.

**Parámetros:**
- `ficha` (str): Número de ficha catastral

**Retorna:**
- dict: Respuesta de la API con el método de pago

**URL Final Generada:**
```
https://api-gov.tns.co/v2/Predial/GenRecTemporalFicha?ficha={ficha}
```

#### `getlocalesbycc(cc: str)`
Obtiene establecimientos comerciales asociados a un documento.

**Parámetros:**
- `cc` (str): Número de documento de identidad

**Retorna:**
- dict: Respuesta de la API con los establecimientos (OCODIGO, ONOMBRE, ODIRECCION)

**URL Final Generada:**
```
https://api-gov.tns.co/v2/Local/ListarEstablecimientosDocumento?documento={cc}
```

#### `gethistorybyplaca(placa: str)`
Obtiene el historial de declaraciones de un establecimiento por placa.

**Parámetros:**
- `placa` (str): Placa de identificación del establecimiento

**Retorna:**
- dict: Respuesta de la API con el historial (OTIPO, OPERIODO, OFECHA, OTOTALPAGO, OESTADO)

**URL Final Generada:**
```
https://api-gov.tns.co/v2/Local/GetAllDeclaracionesPlaca?placa={placa}
```

### Métodos Internos

#### `__env()`
Obtiene las variables de entorno necesarias para la autenticación.

**Variables de Entorno Requeridas:**
- `CODIGO_EMPRESA`: Código de la empresa
- `USUARIO`: Usuario para autenticación
- `PASSWD`: Contraseña del usuario
- `TNSTOKEN`: Token API (mantenido por compatibilidad, no usado en v2)

#### `__get_auth_token()`
Obtiene un nuevo token de autenticación desde la API.

**URL de Autenticación:**
```
https://api-gov.tns.co/v2/Acceso/SolicitarToken?empresa={empresa}&usuario={usuario}&password={password}
```

**Comportamiento:**
- Retorna el token como texto plano (content-type: text/plain)
- Almacena automáticamente el token en `self.token`
- Lanza `ValueError` si hay problemas en la autenticación

#### `__is_session_expired(response: Response)`
Verifica si la respuesta indica que la sesión ha caducado.

**Detecta el Error 401 con Estructura:**
```json
{
  "status": false,
  "message": "La sesión ha caducado.",
  "data": null
}
```

#### `geturlrequest(queryparams: dict)`
Construye la cadena de parámetros de consulta para las URLs.

**Cambio Principal:**
- Ya no incluye parámetros de autenticación
- Solo construye los parámetros específicos de cada endpoint

#### `make_request(endpoint, queryparams, method, api_err_message, custom_err_message)`
Método principal para realizar peticiones HTTP.

**Características Principales:**
- **Autenticación Automática**: Obtiene token si no existe
- **Headers Bearer**: Usa `Authorization: Bearer {token}`
- **Renovación Automática**: Máximo 2 intentos de renovación de token
- **Manejo de Errores**: Preserva la lógica de validación existente

**Flujo de Renovación:**
1. Si no hay token, obtiene uno nuevo
2. Realiza la petición con header de autorización
3. Si recibe error 401 de sesión caducada:
   - Limpia el token actual
   - Obtiene un nuevo token
   - Reintenta la petición (máximo 2 intentos)
4. Si falla después de 2 intentos, lanza error

#### `validate_response(response, api_err_message, custom_err_message)`
Valida las respuestas de la API (sin cambios - mantiene funcionalidad existente).

## Uso

```python
from hacienda.helpers.tnsrequest import TNSRequest

# Crear instancia
tns = TNSRequest()

# Consultar predios
predios = tns.getprediales("12345678")

# Obtener método de pago
pago = tns.getpaymethod("123456")

# Consultar establecimientos
establecimientos = tns.getlocalesbycc("12345678")

# Obtener historial por placa
historial = tns.gethistorybyplaca("ABC123")
```

## Manejo de Errores

La clase mantiene el comportamiento de errores existente:
- `ValueError`: Para errores específicos de la API o problemas de autenticación
- Mensajes personalizados para diferentes tipos de errores
- Preservación de la funcionalidad de `api_err_message` y `custom_err_message`

## Variables de Entorno

Asegúrese de que las siguientes variables estén configuradas:

```env
CODIGO_EMPRESA=tu_codigo_empresa
USUARIO=tu_usuario
PASSWD=tu_password
TNSTOKEN=tu_token_api  # Mantenido por compatibilidad
```

## Compatibilidad

La clase mantiene la misma interfaz pública que la versión anterior, asegurando que el código existente que usa esta clase continúe funcionando sin modificaciones.