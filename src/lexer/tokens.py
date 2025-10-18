"""
Definición de tokens para el analizador léxico de expresiones algebraicas.
"""

import re

class Token:
    """Clase que representa un token con su tipo y valor."""
    
    def __init__(self, tipo, valor, posicion=None):
        self.tipo = tipo
        self.valor = valor
        self.posicion = posicion
    
    def __repr__(self):
        return f"Token({self.tipo}, {self.valor})"

# Definición de tipos de tokens
TIPOS_TOKEN = {
    'DIGITO': r'\d+',
    'VARIABLE': r'[a-zA-Z]',
    'OPERADOR': r'[+\-*/]',
    'EXPONENTE': r'\^',
    'PARENTESIS_IZQ': r'\(',
    'PARENTESIS_DER': r'\)',
    'COEFICIENTE': r'\d+[a-zA-Z]',
    'ESPACIO': r'\s+',
    'DESCONOCIDO': r'.'
}

# Expresiones regulares para cada tipo de token
EXPRESIONES_REGULARES = {
    'DIGITO': re.compile(r'\d+'),
    'VARIABLE': re.compile(r'[a-zA-Z]'),
    'OPERADOR': re.compile(r'[+\-*/]'),
    'EXPONENTE': re.compile(r'\^'),
    'PARENTESIS_IZQ': re.compile(r'\('),
    'PARENTESIS_DER': re.compile(r'\)'),
    'COEFICIENTE': re.compile(r'\d+[a-zA-Z]'),
    'ESPACIO': re.compile(r'\s+'),
    'DESCONOCIDO': re.compile(r'.')
}

def es_token_valido(token):
    """Verifica si un token es válido según los tipos definidos."""
    return token.tipo in TIPOS_TOKEN and token.tipo != 'DESCONOCIDO'

def obtener_tipo_token(texto):
    """Determina el tipo de token basado en el texto."""
    for tipo, patron in EXPRESIONES_REGULARES.items():
        if patron.match(texto):
            return tipo
    return 'DESCONOCIDO'
