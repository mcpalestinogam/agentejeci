"""
Ejemplos de uso de la Skill de Riesgo con Agente Inteligente
=============================================================
Este archivo muestra diferentes escenarios de uso del agente de riesgo.
"""

from risk_skill import run_risk_agent

# ──────────────────────────────────────────────────────────────
# EJEMPLO 1: Cálculo básico Long
# ──────────────────────────────────────────────────────────────
def ejemplo_basico_long():
    prompt = """
    Calcula el riesgo para una operación LONG con estos datos:
    - Precio de entrada: 45000
    - ATR: 150
    - Riesgo: 2% del capital
    - Capital total: 10000 USD
    - Multiplicador ATR: 2.5
    """
    print("=" * 60)
    print("EJEMPLO 1: Operación LONG básica")
    print("=" * 60)
    respuesta = run_risk_agent(prompt)
    print(respuesta)
    print()

# ──────────────────────────────────────────────────────────────
# EJEMPLO 2: Operación SHORT
# ──────────────────────────────────────────────────────────────
def ejemplo_short():
    prompt = """
    Necesito calcular stop loss y tamaño de posición para SHORT:
    Entry: 1850.50
    ATR: 25.3
    Riesgo máximo: 1.5%
    Capital: 25000 USD
    Dirección: short
    """
    print("=" * 60)
    print("EJEMPLO 2: Operación SHORT")
    print("=" * 60)
    respuesta = run_risk_agent(prompt)
    print(respuesta)
    print()

# ──────────────────────────────────────────────────────────────
# EJEMPLO 3: Con lotes personalizados (Crypto)
# ──────────────────────────────────────────────────────────────
def ejemplo_crypto_lotes():
    prompt = """
    Operación en Bitcoin con lotes mínimos:
    - Entrada: 67500
    - ATR: 800
    - Riesgo: 3%
    - Capital: 50000 USD
    - Tamaño de lote mínimo: 0.001 BTC
    - Dirección: long
    - Multiplicador ATR: 2.0
    """
    print("=" * 60)
    print("EJEMPLO 3: Crypto con lotes personalizados")
    print("=" * 60)
    respuesta = run_risk_agent(prompt)
    print(respuesta)
    print()

# ──────────────────────────────────────────────────────────────
# EJEMPLO 4: Escenario con error (Stop Loss inválido)
# ──────────────────────────────────────────────────────────────
def ejemplo_error_stop():
    prompt = """
    Calcula riesgo para LONG:
    - Entrada: 50 USD
    - ATR: 30
    - Riesgo: 5%
    - Capital: 5000 USD
    - Multiplicador ATR: 3.0 (muy alto para este caso)
    """
    print("=" * 60)
    print("EJEMPLO 4: Error - Stop Loss inválido")
    print("=" * 60)
    respuesta = run_risk_agent(prompt)
    print(respuesta)
    print()

# ──────────────────────────────────────────────────────────────
# EJEMPLO 5: Pregunta directa sin tool call
# ──────────────────────────────────────────────────────────────
def ejemplo_pregunta_general():
    prompt = "¿Qué es la gestión de riesgo en trading y por qué es importante?"
    print("=" * 60)
    print("EJEMPLO 5: Pregunta general (sin tool call)")
    print("=" * 60)
    respuesta = run_risk_agent(prompt)
    print(respuesta)
    print()

# ──────────────────────────────────────────────────────────────
# MAIN: Ejecutar todos los ejemplos
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n🚀 INICIANDO DEMOSTRACIÓN DE SKILL DE RIESGO\n")
    
    try:
        ejemplo_basico_long()
        ejemplo_short()
        ejemplo_crypto_lotes()
        ejemplo_error_stop()
        ejemplo_pregunta_general()
        
        print("\n✅ Demostración completada exitosamente")
    except Exception as e:
        print(f"\n❌ Error durante la ejecución: {e}")
        print("\nNota: Asegúrate de tener Ollama corriendo con el modelo qwen2.5:")
        print("   ollama pull qwen2.5:14b-instruct-q4_K_M")
        print("   ollama serve")
