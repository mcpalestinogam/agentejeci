"""
Skill de Gestión de Riesgo para Agente Local con Ollama + Qwen2.5
Diseñado para ser stateless, validado con Pydantic y ejecutable vía tool calling.
"""

import ollama
import json
import math
from pydantic import BaseModel, Field, ValidationError
from typing import Literal

# ──────────────────────────────────────────────────────────────
# 1. MODELOS DE DATO (Pydantic v2)
# ──────────────────────────────────────────────────────────────
class RiskInput(BaseModel):
    entry_price: float = Field(..., gt=0, description="Precio de entrada del activo")
    atr: float = Field(..., gt=0, description="Valor ATR del timeframe de operación")
    risk_percent: float = Field(..., gt=0, le=100, description="Riesgo máximo en % del capital (ej: 2.0)")
    capital: float = Field(..., gt=0, description="Capital total disponible")
    atr_multiplier: float = Field(default=2.0, ge=0.1, le=15.0, description="Multiplicador de ATR para el Stop Loss")
    direction: Literal["long", "short"] = Field(default="long", description="Dirección de la operación")
    lot_size: float = Field(default=1.0, gt=0, description="Unidad mínima negociable (ej: 0.001 en crypto)")

class RiskOutput(BaseModel):
    status: str
    stop_loss: float | None = None
    position_size: float | None = None
    risk_amount: float | None = None
    stop_distance: float | None = None
    message: str

# ──────────────────────────────────────────────────────────────
# 2. LÓGICA DE CÁLCULO (Determinista y segura)
# ──────────────────────────────────────────────────────────────
def calculate_risk(params: RiskInput) -> RiskOutput:
    try:
        stop_loss = params.entry_price - (params.atr * params.atr_multiplier) if params.direction == "long" \
                    else params.entry_price + (params.atr * params.atr_multiplier)
        
        if stop_loss <= 0 and params.direction == "long":
            return RiskOutput(status="error", message="Stop Loss inválido: cae por debajo de cero. Reduce el multiplicador ATR.")

        stop_distance = abs(params.entry_price - stop_loss)
        risk_amount = params.capital * (params.risk_percent / 100)
        position_size_raw = risk_amount / stop_distance

        # Redondeo seguro por lotes
        if params.lot_size < 1:
            decimals = abs(int(math.log10(params.lot_size)))
            position_size = round(math.floor(position_size_raw / params.lot_size) * params.lot_size, decimals)
        else:
            position_size = int(math.floor(position_size_raw / params.lot_size)) * params.lot_size

        return RiskOutput(
            status="success",
            stop_loss=round(stop_loss, 6),
            position_size=position_size,
            risk_amount=round(risk_amount, 2),
            stop_distance=round(stop_distance, 6),
            message="Cálculo exitoso. Posición ajustada por lotes."
        )
    except Exception as e:
        return RiskOutput(status="error", message=f"Error interno: {str(e)}")

# ──────────────────────────────────────────────────────────────
# 3. ADAPTADOR DE TOOL PARA OLLAMA
# ──────────────────────────────────────────────────────────────
def get_ollama_tool_schema() -> list[dict]:
    """Convierte el modelo Pydantic en el formato de tools que entiende Ollama."""
    schema = RiskInput.model_json_schema()
    return [{
        "type": "function",
        "function": {
            "name": "calculate_risk",
            "description": "Calcula stop loss y tamaño de posición usando ATR y gestión de riesgo. Devuelve JSON estructurado.",
            "parameters": {
                "type": "object",
                "properties": schema.get("properties", {}),
                "required": schema.get("required", [])
            }
        }
    }]

# ──────────────────────────────────────────────────────────────
# 4. AGENTE PRINCIPAL
# ──────────────────────────────────────────────────────────────
def run_risk_agent(user_prompt: str, model: str = "qwen2.5:14b-instruct-q4_K_M") -> str:
    """
    Ejecuta el flujo completo: LLM → Tool Call → Validación → Cálculo → Respuesta final.
    """
    tools = get_ollama_tool_schema()
    messages = [{"role": "user", "content": user_prompt}]

    # 1️⃣ Primera llamada: El LLM decide si usar la herramienta
    # Nota: Los parámetros de generación van dentro de 'options'
    response = ollama.chat(
        model=model,
        messages=messages,
        tools=tools,
        options={"temperature": 0.0}  # Crucial para tool calling determinista
    )

    message = response["message"]
    
    # 2️⃣ Detectar si hubo tool call
    if message.get("tool_calls"):
        tool_call = message["tool_calls"][0]
        func_name = tool_call["function"]["name"]
        args_str = tool_call["function"]["arguments"]

        print(f"🔧 Tool solicitado: {func_name}")
        print(f"📥 Args crudos: {args_str}\n")

        # 3️⃣ Validar y ejecutar con manejo robusto de errores
        try:
            # Intentar parsear directamente primero
            try:
                params = RiskInput.model_validate_json(args_str)
            except ValidationError:
                # Si falla, intentar normalizar los datos (el LLM puede usar variaciones)
                import re
                # Limpiar posibles caracteres extraños o formateo incorrecto
                clean_args = re.sub(r',\s*}', '}', args_str)
                clean_args = re.sub(r',\s*]', ']', clean_args)
                
                # Mapeo de alias comunes que el LLM podría usar
                alias_map = {
                    'entry': 'entry_price',
                    'price': 'entry_price',
                    'atr_value': 'atr',
                    'risk': 'risk_percent',
                    'risk_pct': 'risk_percent',
                    'balance': 'capital',
                    'account': 'capital',
                    'equity': 'capital',
                    'multiplier': 'atr_multiplier',
                    'atr_mult': 'atr_multiplier',
                    'dir': 'direction',
                    'side': 'direction',
                    'lot': 'lot_size',
                    'size': 'lot_size'
                }
                
                # Parsear como dict y normalizar claves
                import json as json_lib
                raw_dict = json_lib.loads(clean_args)
                normalized_dict = {}
                
                for key, value in raw_dict.items():
                    normalized_key = alias_map.get(key.lower(), key.lower())
                    # Normalizar dirección a minúsculas
                    if normalized_key == 'direction':
                        normalized_dict[normalized_key] = str(value).lower()
                    else:
                        normalized_dict[normalized_key] = value
                
                params = RiskInput(**normalized_dict)
            
            result = calculate_risk(params)
            result_json = result.model_dump_json()

            print(f"✅ Parámetros validados: {params}\n")
            print(f"📤 Resultado: {result.message}\n")

            # 4️⃣ Inyectar resultado al contexto y pedir respuesta final
            messages.append(message)
            messages.append({
                "role": "tool",
                "content": result_json,
                "tool_call_id": "risk_calc_001"  # Ollama ignora ID si no está, pero es buena práctica
            })

            final_response = ollama.chat(model=model, messages=messages, options={"temperature": 0.3})
            return final_response["message"]["content"]

        except ValidationError as e:
            return f"❌ Error de validación en los parámetros enviados por el modelo:\n{e.json(indent=2)}"
        except Exception as e:
            return f"❌ Error ejecutando la skill: {str(e)}"
    else:
        # El LLM no usó la herramienta (respuesta directa)
        return message["content"]