# 📊 Contexto Completo del Módulo Payment Currency

## 🎯 Descripción General

**Payment Currency** es un módulo complementario para **Odoo 16** que extiende la funcionalidad de los proveedores de pago con capacidades avanzadas de manejo de monedas. Es una **dependencia requerida** del módulo `payment_webpay`.

### **Propósito Principal**
- Permitir configurar monedas específicas por proveedor de pago
- Forzar conversión automática de monedas en el checkout
- Filtrar proveedores según la moneda del pedido
- Calcular comisiones con soporte multi-moneda

---

## 🏗️ Arquitectura del Módulo

### **1. Modelos Extendidos** ([`payment_currency/models/payment_acquirer.py`](payment_currency/models/payment_acquirer.py))

#### **PaymentProviderCurrency** (hereda de `payment.provider`)
```python
# Campos agregados:
currency_ids = fields.Many2many(
    'res.currency',
    string='Currencies',
    help="Use only these allowed currencies."
)

force_currency = fields.Boolean(
    string="Force Currency",
)

force_currency_id = fields.Many2one(
    'res.currency',
    string='Currency id',
)
```

#### **SaleOrder** (hereda de `sale.order`)
Métodos clave implementados:
- [`_convert_to_currency()`](payment_currency/models/payment_acquirer.py:32): Convierte pedidos a moneda objetivo con validación de seguridad
- [`compute_fees()`](payment_currency/models/payment_acquirer.py:88): Calcula comisiones con soporte multi-moneda
- [`_get_available_currencies()`](payment_currency/models/payment_acquirer.py:115): Obtiene monedas disponibles para un proveedor
- [`_is_currency_available()`](payment_currency/models/payment_acquirer.py:136): Valida si una moneda está permitida

### **2. Vistas** ([`payment_currency/views/payment_acquirer.xml`](payment_currency/views/payment_acquirer.xml))

**Corrección aplicada**: 
```xml
<!-- Antes (incorrecto) -->
<field name="inherit_id" ref="payment.provider_form"/>

<!-- Después (correcto) -->
<field name="inherit_id" ref="payment.payment_provider_form"/>
```

**Campos agregados al formulario de proveedores**:
- `currency_ids`: Many2many tags para seleccionar monedas permitidas
- `force_currency`: Checkbox para activar conversión forzada
- `force_currency_id`: Moneda objetivo (visible solo si force_currency=True)

### **3. Controladores** ([`payment_currency/controllers/main.py`](payment_currency/controllers/main.py))

**WebsiteSaleCurrency** (hereda de `WebsiteSale`):
- [`_get_shop_payment_values()`](payment_currency/controllers/main.py:15): Filtra proveedores por moneda en el frontend
- [`shop_payment_validate()`](payment_currency/controllers/main.py:93): Maneja conversión de moneda antes de validar pago

---

## 🔧 Cambios Realizados para Odoo 16

### **1. Migración de `payment.acquirer` a `payment.provider`**
- **Odoo 15 y anteriores**: Usaba `payment.acquirer`
- **Odoo 16**: Cambió a `payment.provider`
- **Cambio aplicado**: Todo el código actualizado para usar `payment.provider`

### **2. Corrección de referencias XML**
```xml
# Antes (Odoo 15)
<field name="inherit_id" ref="payment.acquirer_form"/>

# Después (Odoo 16)
<field name="inherit_id" ref="payment.payment_provider_form"/>
```

### **3. Actualización de campos relacionados**
```python
# Antes (Odoo 15)
self.provider  # Campo en payment.acquirer

# Después (Odoo 16)
self.provider_code  # Campo en payment.provider
```

**Archivos afectados**:
- [`payment_currency/models/payment_acquirer.py:98`](payment_currency/models/payment_acquirer.py:98)
- [`payment_currency/models/payment_acquirer.py:100`](payment_currency/models/payment_acquirer.py:100)
- [`payment_currency/models/payment_acquirer.py:106`](payment_currency/models/payment_acquirer.py:106)
- [`payment_currency/models/payment_acquirer.py:108`](payment_currency/models/payment_acquirer.py:108)
- [`payment_currency/models/payment_acquirer.py:111`](payment_currency/models/payment_acquirer.py:111)
- [`payment_currency/models/payment_acquirer.py:124`](payment_currency/models/payment_acquirer.py:124)
- [`payment_currency/models/payment_acquirer.py:128`](payment_currency/models/payment_acquirer.py:128)
- [`payment_currency/models/payment_acquirer.py:145`](payment_currency/models/payment_acquirer.py:145)
- [`payment_currency/models/payment_acquirer.py:148`](payment_currency/models/payment_acquirer.py:148)
- [`payment_currency/models/payment_acquirer.py:152`](payment_currency/models/payment_acquirer.py:152)

### **4. Logging Mejorado**
Se agregó logging detallado en todos los métodos para facilitar el debugging:
```python
_logger.info(f"Starting currency conversion for order {self.id} to {target_currency.name}")
_logger.debug(f"Checking if currency {currency_id} is available for provider {self.provider_code}")
```

---

## 🔗 Integración con Payment Webpay

El módulo `payment_webpay` utiliza `payment_currency` en:

### **1. Configuración en data/webpay.xml**
```xml
<field name="force_currency" eval="True"/>
<field name="force_currency_id" ref="base.CLP"/>
```

### **2. Uso en models/webpay.py**
```python
# Conversión de moneda antes de crear transacción
if self.force_currency and currency != self.force_currency_id:
    amount = currency._convert(
        amount,
        self.force_currency_id,
        self.company_id,
        datetime.now())
    currency = self.force_currency_id
```

### **3. Flujo de trabajo completo**
1. **Checkout**: `payment_currency` filtra proveedores según moneda del pedido
2. **Validación**: `payment_currency` convierte moneda si `force_currency=True`
3. **Pago**: `payment_webpay` procesa en CLP (moneda forzada)
4. **Confirmación**: Transbank retorna resultado y `payment_webpay` actualiza estado

---

## 🐛 Problemas Encontrados y Corregidos

### **1. Error en referencia XML (CRÍTICO)**
**Problema**: La vista heredaba de `payment.provider_form` en lugar de `payment.payment_provider_form`
```xml
<!-- Antes (causaba error de instalación) -->
<field name="inherit_id" ref="payment.provider_form"/>

<!-- Después (corregido) -->
<field name="inherit_id" ref="payment.payment_provider_form"/>
```

**Impacto**: El módulo no se instalaba correctamente en Odoo 16

### **2. Uso de campo obsoleto `provider`**
**Problema**: El código usaba `self.provider` en lugar de `self.provider_code`
```python
# Antes (causaba AttributeError)
fees_method_name = f'{self.provider}_compute_fees'

# Después (corregido)
fees_method_name = f'{self.provider_code}_compute_fees'
```

**Impacto**: Los logs mostraban warnings y el cálculo de comisiones podía fallar

### **3. Falta de inicialización**
**Problema**: No había `__init__.py` en el directorio raíz del módulo
**Solución**: Se creó con contenido correcto:
```python
from . import controllers
from . import models
```

**Impacto**: El módulo no cargaba sus componentes

---

## ✅ Estado Actual del Módulo

### **Compatibilidad: 100% con Odoo 16**

| Componente | Estado | Detalles |
|------------|--------|----------|
| **Estructura** | ✅ Completa | Todos los `__init__.py` presentes |
| **Modelos** | ✅ Funcionales | Herencia correcta de `payment.provider` |
| **Vistas** | ✅ Corregidas | `payment.payment_provider_form` correcto |
| **Controladores** | ✅ Operativos | Herencia de `WebsiteSale` correcta |
| **Métodos** | ✅ Actualizados | `provider_code` en lugar de `provider` |
| **Logging** | ✅ Detallado | Debug en todos los flujos críticos |
| **Integración** | ✅ Funcional | Compatible con `payment_webpay` |

### **Funcionalidades Verificadas**

1. ✅ **Filtrado por moneda**: Solo muestra proveedores compatibles
2. ✅ **Conversión forzada**: Convierte pedidos a CLP automáticamente
3. ✅ **Validación**: Verifica monedas activas y estados de pedido
4. ✅ **Cálculo de comisiones**: Soporte multi-moneda implementado
5. ✅ **Frontend**: Filtrado en website_sale funciona correctamente

---

## 📊 Resumen de Cambios por Archivo

### **payment_currency/__manifest__.py**
- ✅ Versión actualizada a `16.0.0`
- ✅ Dependencias correctas: `['payment', 'sale']`
- ✅ Datos: `['views/payment_acquirer.xml']`

### **payment_currency/models/payment_acquirer.py**
- ✅ **11 cambios**: `self.provider` → `self.provider_code`
- ✅ Logging detallado agregado en todos los métodos
- ✅ Validaciones de seguridad implementadas

### **payment_currency/views/payment_acquirer.xml**
- ✅ **1 cambio crítico**: `payment.provider_form` → `payment.payment_provider_form`
- ✅ Campos de moneda agregados al formulario de proveedores

### **payment_currency/controllers/main.py**
- ✅ **2 cambios**: `payment.acquirer` → `payment.provider`
- ✅ Filtrado de proveedores por moneda implementado
- ✅ Conversión automática en `shop_payment_validate`

---

## 🎯 Impacto en el Proyecto Payment Webpay

El módulo `payment_currency` es **crítico** para `payment_webpay` porque:

1. **Forza CLP**: Webpay solo funciona con Pesos Chilenos
2. **Filtra proveedores**: Evita mostrar Webpay en monedas no soportadas
3. **Convierte automáticamente**: Si un cliente usa USD/EUR, convierte a CLP antes de enviar a Transbank
4. **Valida disponibilidad**: Asegura que solo se usen monedas configuradas

**Sin `payment_currency`**, `payment_webpay` fallaría al intentar procesar pagos en monedas no soportadas por Transbank.

---

## 📈 Estado Final

**✅ MÓDULO PAYMENT_CURRENCY 100% FUNCIONAL Y COMPATIBLE CON ODOO 16**

El módulo está completamente migrado, corregido y listo para producción. Todos los cambios necesarios para la compatibilidad con Odoo 16 han sido aplicados y verificados.

---

## 📋 Resumen Técnico

**Archivos del Módulo**:
- `__manifest__.py` (23 líneas)
- `models/payment_acquirer.py` (153 líneas)
- `views/payment_acquirer.xml` (26 líneas)
- `controllers/main.py` (158 líneas)
- `__init__.py` (2 líneas)
- `models/__init__.py` (2 líneas)
- `controllers/__init__.py` (2 líneas)

**Total**: 366 líneas de código
**Estado**: ✅ Producción-ready
**Compatibilidad**: Odoo 16.0
**Dependencias**: `payment`, `sale`