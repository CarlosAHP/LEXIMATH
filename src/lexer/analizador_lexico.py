"""
Analizador léxico para expresiones algebraicas.
"""

import re
from .tokens import Token, TIPOS_TOKEN, EXPRESIONES_REGULARES

class AnalizadorLexico:
    """Analizador léxico para expresiones algebraicas."""
    
    def __init__(self):
        self.tokens = []
        self.posicion_actual = 0
        self.texto_entrada = ""
    
    def analizar(self, texto):
        """
        Analiza el texto de entrada y genera una lista de tokens.
        
        Args:
            texto (str): Texto a analizar
            
        Returns:
            list: Lista de tokens identificados
        """
        self.texto_entrada = texto.strip()
        self.tokens = []
        self.posicion_actual = 0
        
        # Validar que la entrada no esté vacía
        if not self.texto_entrada:
            return self.tokens
        
        while self.posicion_actual < len(self.texto_entrada):
            # Saltar espacios en blanco
            if self._es_espacio():
                self._saltar_espacios()
                continue
            
            # Intentar identificar el token
            token = self._siguiente_token()
            if token:
                self.tokens.append(token)
            else:
                # Token desconocido - esto indica un carácter inválido
                token_desconocido = Token(
                    'DESCONOCIDO',
                    self.texto_entrada[self.posicion_actual],
                    self.posicion_actual
                )
                self.tokens.append(token_desconocido)
                self.posicion_actual += 1
        
        return self.tokens
    
    def _es_espacio(self):
        """Verifica si el carácter actual es un espacio en blanco."""
        if self.posicion_actual >= len(self.texto_entrada):
            return False
        return self.texto_entrada[self.posicion_actual].isspace()
    
    def _saltar_espacios(self):
        """Avanza la posición saltando espacios en blanco."""
        while (self.posicion_actual < len(self.texto_entrada) and 
               self.texto_entrada[self.posicion_actual].isspace()):
            self.posicion_actual += 1
    
    def _siguiente_token(self):
        """
        Identifica el siguiente token en el texto.
        
        Returns:
            Token: El token identificado o None si no se puede identificar
        """
        texto_restante = self.texto_entrada[self.posicion_actual:]
        
        # Verificar cada tipo de token en orden de prioridad
        for tipo, patron in EXPRESIONES_REGULARES.items():
            if tipo == 'ESPACIO':
                continue
                
            coincidencia = patron.match(texto_restante)
            if coincidencia:
                valor = coincidencia.group()
                token = Token(tipo, valor, self.posicion_actual)
                self.posicion_actual += len(valor)
                return token
        
        return None
    
    def obtener_tokens(self):
        """Retorna la lista de tokens identificados."""
        return self.tokens
    
    def imprimir_tokens(self):
        """Imprime la lista de tokens de forma legible."""
        print("Tokens identificados:")
        print("-" * 40)
        for i, token in enumerate(self.tokens, 1):
            print(f"{i:2d}. {token.tipo:15s} | {token.valor:10s} | Pos: {token.posicion}")
        print("-" * 40)
    
    def validar_expresion(self):
        """
        Valida si la expresión contiene solo tokens válidos para expresiones algebraicas.
        
        Returns:
            bool: True si la expresión es válida, False en caso contrario
        """
        # Verificar que no haya tokens desconocidos
        for token in self.tokens:
            if token.tipo == 'DESCONOCIDO':
                return False
        
        # Verificar que haya al menos un token válido
        if not self.tokens:
            return False
            
        # Verificar que solo contenga tokens permitidos para expresiones algebraicas
        tipos_permitidos = {'DIGITO', 'VARIABLE', 'OPERADOR', 'EXPONENTE', 
                           'PARENTESIS_IZQ', 'PARENTESIS_DER', 'COEFICIENTE'}
        
        for token in self.tokens:
            if token.tipo not in tipos_permitidos:
                return False
        
        # Validar estructura algebraica
        if not self._validar_estructura_algebraica():
            return False
                
        return True
    
    def obtener_errores(self):
        """
        Retorna una lista de errores encontrados en el análisis.
        
        Returns:
            list: Lista de errores
        """
        errores = []
        for token in self.tokens:
            if token.tipo == 'DESCONOCIDO':
                errores.append(f"Carácter inválido '{token.valor}' en posición {token.posicion}. Solo se permiten números, variables (letras), operadores (+, -, *, /), exponentes (^) y paréntesis.")
        return errores
    
    def _validar_estructura_algebraica(self) -> bool:
        """
        Valida que la estructura sea una expresión algebraica válida.
        
        Returns:
            bool: True si la estructura es válida, False en caso contrario
        """
        # Filtrar solo tokens no espaciales
        tokens_validos = [token for token in self.tokens if token.tipo != 'ESPACIO']
        
        if not tokens_validos:
            return False
        
        # Verificar que no sea solo una secuencia de variables (como "carlos")
        solo_variables = all(token.tipo == 'VARIABLE' for token in tokens_validos)
        if solo_variables and len(tokens_validos) > 1:
            return False
        
        # Verificar que no sea solo una secuencia de dígitos
        solo_digitos = all(token.tipo == 'DIGITO' for token in tokens_validos)
        if solo_digitos and len(tokens_validos) == 1 and len(tokens_validos[0].valor) > 1:
            return False
        
        # Si es una sola variable o un solo dígito, es válido
        if len(tokens_validos) == 1:
            return True
        
        # Verificar que tenga al menos un operador o paréntesis (estructura algebraica)
        tiene_operador = any(token.tipo == 'OPERADOR' for token in tokens_validos)
        tiene_parentesis = any(token.tipo in ['PARENTESIS_IZQ', 'PARENTESIS_DER'] for token in tokens_validos)
        tiene_exponente = any(token.tipo == 'EXPONENTE' for token in tokens_validos)
        
        # Si no tiene operadores, paréntesis o exponentes, no es algebraica
        if not (tiene_operador or tiene_parentesis or tiene_exponente):
            return False
        
        return True
    
    def obtener_errores_validacion(self):
        """
        Retorna errores específicos de validación para expresiones algebraicas.
        
        Returns:
            list: Lista de errores de validación
        """
        errores = []
        
        # Verificar tokens desconocidos
        for token in self.tokens:
            if token.tipo == 'DESCONOCIDO':
                errores.append(f"Carácter no permitido: '{token.valor}' en posición {token.posicion}")
        
        # Verificar que la expresión no esté vacía
        if not self.tokens:
            errores.append("La expresión no puede estar vacía")
            return errores
        
        # Verificar tipos de tokens no permitidos
        tipos_permitidos = {'DIGITO', 'VARIABLE', 'OPERADOR', 'EXPONENTE', 
                           'PARENTESIS_IZQ', 'PARENTESIS_DER', 'COEFICIENTE'}
        
        for token in self.tokens:
            if token.tipo not in tipos_permitidos:
                errores.append(f"Token no permitido: '{token.tipo}' con valor '{token.valor}' en posición {token.posicion}")
        
        # Verificar estructura algebraica
        if not self._validar_estructura_algebraica():
            tokens_validos = [token for token in self.tokens if token.tipo != 'ESPACIO']
            
            # Verificar si es solo variables
            solo_variables = all(token.tipo == 'VARIABLE' for token in tokens_validos)
            if solo_variables and len(tokens_validos) > 1:
                errores.append("Secuencia de solo variables no es una expresión algebraica válida")
            
            # Verificar si es solo dígitos
            solo_digitos = all(token.tipo == 'DIGITO' for token in tokens_validos)
            if solo_digitos and len(tokens_validos) == 1 and len(tokens_validos[0].valor) > 1:
                errores.append("Secuencia de solo dígitos no es una expresión algebraica válida")
            
            # Verificar si no tiene estructura algebraica
            if len(tokens_validos) > 1:
                tiene_operador = any(token.tipo == 'OPERADOR' for token in tokens_validos)
                tiene_parentesis = any(token.tipo in ['PARENTESIS_IZQ', 'PARENTESIS_DER'] for token in tokens_validos)
                tiene_exponente = any(token.tipo == 'EXPONENTE' for token in tokens_validos)
                
                if not (tiene_operador or tiene_parentesis or tiene_exponente):
                    errores.append("La expresión debe contener operadores, paréntesis o exponentes para ser algebraica")
        
        return errores
