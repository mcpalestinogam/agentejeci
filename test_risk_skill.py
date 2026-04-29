"""
Script de prueba unitaria para la Skill de Riesgo
==================================================
Prueba la lógica de cálculo sin depender de Ollama/LLM.
"""

import unittest
from risk_skill import RiskInput, RiskOutput, calculate_risk

class TestRiskCalculation(unittest.TestCase):
    
    def test_long_position_basic(self):
        """Prueba operación LONG básica"""
        params = RiskInput(
            entry_price=100.0,
            atr=5.0,
            risk_percent=2.0,
            capital=10000.0,
            atr_multiplier=2.0,
            direction="long"
        )
        result = calculate_risk(params)
        
        self.assertEqual(result.status, "success")
        # SL = 100 - (5 * 2) = 90
        self.assertEqual(result.stop_loss, 90.0)
        # Distancia = 10
        self.assertEqual(result.stop_distance, 10.0)
        # Riesgo = 10000 * 0.02 = 200
        self.assertEqual(result.risk_amount, 200.0)
        # Tamaño = 200 / 10 = 20
        self.assertEqual(result.position_size, 20.0)
    
    def test_short_position_basic(self):
        """Prueba operación SHORT básica"""
        params = RiskInput(
            entry_price=100.0,
            atr=5.0,
            risk_percent=2.0,
            capital=10000.0,
            atr_multiplier=2.0,
            direction="short"
        )
        result = calculate_risk(params)
        
        self.assertEqual(result.status, "success")
        # SL = 100 + (5 * 2) = 110
        self.assertEqual(result.stop_loss, 110.0)
        # Distancia = 10
        self.assertEqual(result.stop_distance, 10.0)
    
    def test_invalid_stop_loss_long(self):
        """Prueba cuando el SL cae por debajo de cero en LONG"""
        params = RiskInput(
            entry_price=50.0,
            atr=30.0,
            risk_percent=5.0,
            capital=5000.0,
            atr_multiplier=3.0,  # SL = 50 - 90 = -40 (inválido)
            direction="long"
        )
        result = calculate_risk(params)
        
        self.assertEqual(result.status, "error")
        self.assertIn("Stop Loss inválido", result.message)
    
    def test_crypto_lot_sizing(self):
        """Prueba redondeo por lotes en crypto"""
        params = RiskInput(
            entry_price=50000.0,
            atr=500.0,
            risk_percent=1.0,
            capital=10000.0,
            atr_multiplier=2.0,
            direction="long",
            lot_size=0.001  # Lote mínimo: 0.001
        )
        result = calculate_risk(params)
        
        self.assertEqual(result.status, "success")
        # SL = 50000 - 1000 = 49000
        self.assertEqual(result.stop_loss, 49000.0)
        # Distancia = 1000
        # Riesgo = 10000 * 0.01 = 100
        # Tamaño raw = 100 / 1000 = 0.1
        # Tamaño ajustado a lotes de 0.001 = 0.100
        self.assertEqual(result.position_size, 0.1)
    
    def test_validation_entry_price_zero(self):
        """Prueba validación: precio de entrada no puede ser cero"""
        with self.assertRaises(Exception):
            RiskInput(
                entry_price=0,
                atr=5.0,
                risk_percent=2.0,
                capital=10000.0
            )
    
    def test_validation_risk_percent_max(self):
        """Prueba validación: riesgo máximo 100%"""
        with self.assertRaises(Exception):
            RiskInput(
                entry_price=100.0,
                atr=5.0,
                risk_percent=150.0,  # > 100
                capital=10000.0
            )
    
    def test_custom_atr_multiplier(self):
        """Prueba con multiplicador ATR personalizado"""
        params = RiskInput(
            entry_price=200.0,
            atr=8.0,
            risk_percent=3.0,
            capital=15000.0,
            atr_multiplier=3.5,
            direction="long"
        )
        result = calculate_risk(params)
        
        self.assertEqual(result.status, "success")
        # SL = 200 - (8 * 3.5) = 200 - 28 = 172
        self.assertEqual(result.stop_loss, 172.0)
        # Distancia = 28
        # Riesgo = 15000 * 0.03 = 450
        # Tamaño = 450 / 28 = 16.0714... → floor = 16.0
        self.assertEqual(result.position_size, 16.0)

if __name__ == "__main__":
    print("\n🧪 EJECUTANDO PRUEBAS UNITARIAS DE RISK_SKILL\n")
    unittest.main(verbosity=2)
