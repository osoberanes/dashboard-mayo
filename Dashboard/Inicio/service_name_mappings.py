# -*- coding: utf-8 -*-
"""
Sistema de mapeo de nombres de servicios
Permite usar nombres cortos y precisos para visualizaciones
"""

import json
import os
from typing import Dict, Optional

class ServiceNameMapper:
    """Clase para gestionar el mapeo de nombres de servicios"""
    
    def __init__(self, config_file: str = "service_mappings.json"):
        self.config_file = config_file
        self.mappings: Dict[str, str] = {}
        self.reverse_mappings: Dict[str, str] = {}
        self.load_mappings()
    
    def load_mappings(self):
        """Carga los mapeos desde archivo de configuración"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.mappings = json.load(f)
                # Crear mapeo inverso
                self.reverse_mappings = {v: k for k, v in self.mappings.items()}
            else:
                # Crear mapeos por defecto
                self._create_default_mappings()
                self.save_mappings()
        except Exception as e:
            print(f"Error cargando mapeos: {e}")
            self._create_default_mappings()
    
    def _create_default_mappings(self):
        """Crear mapeos por defecto basados en servicios comunes"""
        self.mappings = {
            # Pasaportes
            "EXPEDICION DE PASAPORTE ORDINARIO": "Pasaporte Ordinario",
            "EXPEDICION DE PASAPORTE DIPLOMATICO": "Pasaporte Diplomático",
            "EXPEDICION DE PASAPORTE OFICIAL": "Pasaporte Oficial",
            "EXPEDICION DE PASAPORTE DE EMERGENCIA": "Pasaporte Emergencia",
            "RENOVACION DE PASAPORTE": "Renovación Pasaporte",
            
            # Matrículas Consulares
            "EXPEDICION DE MATRICULA CONSULAR": "Matrícula Consular",
            "RENOVACION DE MATRICULA CONSULAR": "Renovación Matrícula",
            "REPOSICION DE MATRICULA CONSULAR": "Reposición Matrícula",
            
            # Visas
            "VISA DE TURISTA": "Visa Turista",
            "VISA DE NEGOCIOS": "Visa Negocios",
            "VISA DE ESTUDIANTE": "Visa Estudiante",
            "VISA DE TRABAJO": "Visa Trabajo",
            "VISA DE TRANSITO": "Visa Tránsito",
            
            # Documentos
            "CONSTANCIA DE NACIONALIDAD MEXICANA": "Constancia Nacionalidad",
            "CARTA DE NATURALIZACION": "Carta Naturalización",
            "CERTIFICADO DE NACIMIENTO": "Cert. Nacimiento",
            "ACTA DE NACIMIENTO": "Acta Nacimiento",
            "ACTA DE MATRIMONIO": "Acta Matrimonio",
            "ACTA DE DEFUNCION": "Acta Defunción",
            
            # Servicios Notariales
            "FE DE HECHOS": "Fe de Hechos",
            "PROTOCOLIZACION": "Protocolización",
            "PODER NOTARIAL": "Poder Notarial",
            "TESTAMENTO": "Testamento",
            
            # Legalizaciones
            "LEGALIZACION DE DOCUMENTOS": "Legalización Docs",
            "APOSTILLE": "Apostilla",
            "CERTIFICACION DE FIRMAS": "Cert. Firmas",
            
            # Otros servicios
            "REGISTRO DE MEXICANOS": "Registro Mexicanos",
            "PROTECCION CONSULAR": "Protección Consular",
            "SERVICIOS MIGRATORIOS": "Servicios Migratorios",
            "ATENCION CIUDADANA": "Atención Ciudadana"
        }
        
        # Crear mapeo inverso
        self.reverse_mappings = {v: k for k, v in self.mappings.items()}
    
    def save_mappings(self):
        """Guarda los mapeos en archivo de configuración"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.mappings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error guardando mapeos: {e}")
    
    def get_short_name(self, original_name: str) -> str:
        """Obtiene nombre corto para un servicio"""
        if not original_name:
            return original_name
        
        # Buscar coincidencia exacta
        if original_name in self.mappings:
            return self.mappings[original_name]
        
        # Buscar coincidencia parcial (contiene)
        original_upper = original_name.upper()
        for long_name, short_name in self.mappings.items():
            if long_name.upper() in original_upper or original_upper in long_name.upper():
                return short_name
        
        # Si no encuentra mapeo, devolver nombre truncado
        return self._truncate_name(original_name)
    
    def get_original_name(self, short_name: str) -> str:
        """Obtiene nombre original desde nombre corto"""
        return self.reverse_mappings.get(short_name, short_name)
    
    def _truncate_name(self, name: str, max_length: int = 25) -> str:
        """Trunca un nombre si es muy largo"""
        if len(name) <= max_length:
            return name
        
        # Intentar cortar por palabras
        words = name.split()
        truncated = ""
        for word in words:
            if len(truncated + " " + word) <= max_length - 3:
                truncated += " " + word if truncated else word
            else:
                break
        
        if truncated:
            return truncated + "..."
        else:
            # Si no se puede cortar por palabras, cortar por caracteres
            return name[:max_length-3] + "..."
    
    def add_mapping(self, original_name: str, short_name: str):
        """Agrega un nuevo mapeo"""
        self.mappings[original_name] = short_name
        self.reverse_mappings[short_name] = original_name
        self.save_mappings()
    
    def remove_mapping(self, original_name: str):
        """Elimina un mapeo"""
        if original_name in self.mappings:
            short_name = self.mappings[original_name]
            del self.mappings[original_name]
            if short_name in self.reverse_mappings:
                del self.reverse_mappings[short_name]
            self.save_mappings()
    
    def get_all_mappings(self) -> Dict[str, str]:
        """Obtiene todos los mapeos"""
        return self.mappings.copy()
    
    def update_mappings(self, new_mappings: Dict[str, str]):
        """Actualiza múltiples mapeos"""
        self.mappings.update(new_mappings)
        self.reverse_mappings = {v: k for k, v in self.mappings.items()}
        self.save_mappings()

# Instancia global del mapper
service_mapper = ServiceNameMapper()

def get_short_service_name(original_name: str) -> str:
    """Función de conveniencia para obtener nombre corto"""
    return service_mapper.get_short_name(original_name)

def get_original_service_name(short_name: str) -> str:
    """Función de conveniencia para obtener nombre original"""
    return service_mapper.get_original_name(short_name)