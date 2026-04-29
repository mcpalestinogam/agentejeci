# 📊 Skill de Gestión de Riesgo para Agente Inteligente

Skill profesional de cálculo de riesgo para trading, diseñada para ser utilizada por un agente inteligente local con **Ollama + Qwen2.5**.

## 🚀 Características

- ✅ **Modelos Pydantic v2** para validación estricta de datos
- ✅ **Cálculo determinista** de Stop Loss y tamaño de posición
- ✅ **Tool calling** nativo con Ollama
- ✅ **Soporte LONG/SHORT** con validación de SL inválido
- ✅ **Ajuste por lotes** para crypto y forex
- ✅ **Stateless** - sin estado compartido, seguro para producción
- ✅ **Tests unitarios** incluidos

## 📁 Estructura del Proyecto

```
/workspace/
├── risk_skill.py           # Skill principal con lógica y agente
├── examples_usage.py       # 5 ejemplos de uso completo
├── test_risk_skill.py      # Tests unitarios (7 tests)
└── README.md               # Este archivo
```

## 🔧 Requisitos

### Instalación con `uv` (recomendado)

```bash
# Crear entorno virtual y activarlo
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
uv pip install ollama pydantic
```

### Alternativa: Entorno automático con `uv run`

Si prefieres no gestionar el entorno manualmente, puedes usar `uv run`:

```bash
uv run python examples_usage.py
uv run python test_risk_skill.py
```

Esto creará un entorno temporal e instalará las dependencias automáticamente.

Necesitas tener **Ollama** corriendo con el modelo Qwen2.5:

```bash
# Descargar modelo (si no lo tienes)
ollama pull qwen2.5:14b-instruct-q4_K_M

# Iniciar servidor (en otra terminal)
ollama serve
```

## 💡 Uso Básico

### Desde Python

```python
from risk_skill import run_risk_agent

prompt = """
Calcula el riesgo para una operación LONG:
- Precio de entrada: 45000
- ATR: 150
- Riesgo: 2% del capital
- Capital total: 10000 USD
- Multiplicador ATR: 2.5
"""

respuesta = run_risk_agent(prompt)
print(respuesta)
```

### Ejecutar ejemplos completos

```bash
# Con entorno activado
python examples_usage.py

# O con uv run (sin activar entorno)
uv run python examples_usage.py
```

Esto ejecutará 5 escenarios:
1. ✅ Operación LONG básica
2. ✅ Operación SHORT
3. ✅ Crypto con lotes personalizados (0.001 BTC)
4. ✅ Error controlado (SL inválido)
5. ✅ Pregunta general sin tool call

### Ejecutar tests unitarios

```bash
# Con entorno activado
python test_risk_skill.py

# O con uv run (sin activar entorno)
uv run python test_risk_skill.py
```

## 📐 Fórmulas Utilizadas

| Concepto | Fórmula |
|----------|---------|
| **Stop Loss (LONG)** | `entry_price - (ATR × multiplicador)` |
| **Stop Loss (SHORT)** | `entry_price + (ATR × multiplicador)` |
| **Riesgo en USD** | `capital × (risk_percent / 100)` |
| **Tamaño de posición** | `riesgo_usd / distancia_sl` |
| **Ajuste por lotes** | `floor(tamaño_raw / lot_size) × lot_size` |

## 🛡️ Validaciones Incluidas

- ✅ `entry_price > 0`
- ✅ `atr > 0`
- ✅ `0 < risk_percent ≤ 100`
- ✅ `capital > 0`
- ✅ `0.1 ≤ atr_multiplier ≤ 15.0`
- ✅ `lot_size > 0`
- ✅ Stop Loss no negativo en LONG

## 🧠 Schema de la Tool (Ollama)

La skill expone automáticamente su schema para tool calling:

```python
from risk_skill import get_ollama_tool_schema

tools = get_ollama_tool_schema()
# tools[0]["function"] contiene el schema completo
```

Parámetros esperados:
- `entry_price` (float): Precio de entrada
- `atr` (float): Valor ATR del timeframe
- `risk_percent` (float): Riesgo máximo en % (ej: 2.0)
- `capital` (float): Capital total disponible
- `atr_multiplier` (float, opcional): Multiplicador para SL (default: 2.0)
- `direction` (str): "long" o "short" (default: "long")
- `lot_size` (float, opcional): Tamaño mínimo de lote (default: 1.0)

## 📤 Output Esperado

```json
{
  "status": "success",
  "stop_loss": 44625.0,
  "position_size": 0.53,
  "risk_amount": 200.0,
  "stop_distance": 375.0,
  "message": "Cálculo exitoso. Posición ajustada por lotes."
}
```

## ⚠️ Manejo de Errores

La skill devuelve errores estructurados:

```json
{
  "status": "error",
  "message": "Stop Loss inválido: cae por debajo de cero. Reduce el multiplicador ATR."
}
```

## 🎯 Casos de Uso

1. **Trading de Forex**: Calcula lotes estándar (1.0)
2. **Crypto**: Ajusta a satoshis o fracciones (0.001, 0.00001)
3. **Futuros**: Adapta a tamaño de contrato
4. **Backtesting**: Valida parámetros antes de ejecutar
5. **Educación**: Enseña gestión de riesgo con ejemplos reales

## 🔒 Seguridad

- No hay estado compartido entre llamadas
- Validación estricta con Pydantic
- Cálculos deterministas (sin aleatoriedad)
- Temperature=0.0 para tool calling consistente

---

**Autor**: Generado para agente inteligente con Ollama  
**Licencia**: MIT  
**Versión**: 1.0.0
