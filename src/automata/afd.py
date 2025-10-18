"""
Implementación del Autómata Finito Determinista (AFD) para expresiones algebraicas.
"""

from typing import Dict, Set, List, Optional, Tuple
from ..lexer.tokens import Token

class EstadoAFD:
    """Representa un estado del AFD."""
    
    def __init__(self, nombre: str, es_final: bool = False):
        self.nombre = nombre
        self.es_final = es_final
        self.transiciones: Dict[str, 'EstadoAFD'] = {}
    
    def agregar_transicion(self, simbolo: str, estado_destino: 'EstadoAFD'):
        """Agrega una transición desde este estado."""
        self.transiciones[simbolo] = estado_destino
    
    def obtener_siguiente_estado(self, simbolo: str) -> Optional['EstadoAFD']:
        """Obtiene el siguiente estado basado en el símbolo de entrada."""
        return self.transiciones.get(simbolo)

class AFD:
    """Autómata Finito Determinista para expresiones algebraicas."""
    
    def __init__(self):
        self.estados: Dict[str, EstadoAFD] = {}
        self.estado_inicial: Optional[EstadoAFD] = None
        self.alfabeto: Set[str] = set()
        self._construir_afd()
    
    def _construir_afd(self):
        """Construye el AFD para reconocer expresiones algebraicas."""
        # Crear estados
        q0 = EstadoAFD("q0")  # Estado inicial
        q1 = EstadoAFD("q1")  # Después de dígito
        q2 = EstadoAFD("q2")  # Después de variable
        q3 = EstadoAFD("q3")  # Después de operador
        q4 = EstadoAFD("q4")  # Después de paréntesis izquierdo
        q5 = EstadoAFD("q5")  # Después de paréntesis derecho
        q6 = EstadoAFD("q6")  # Después de exponente
        q7 = EstadoAFD("q7", es_final=True)  # Estado final
        
        # Agregar estados al AFD
        self.estados = {
            "q0": q0, "q1": q1, "q2": q2, "q3": q3,
            "q4": q4, "q5": q5, "q6": q6, "q7": q7
        }
        
        self.estado_inicial = q0
        
        # Definir alfabeto
        self.alfabeto = {'DIGITO', 'VARIABLE', 'OPERADOR', 'PARENTESIS_IZQ', 
                        'PARENTESIS_DER', 'EXPONENTE'}
        
        # Definir transiciones
        # Desde q0 (estado inicial)
        q0.agregar_transicion('DIGITO', q1)
        q0.agregar_transicion('VARIABLE', q2)
        q0.agregar_transicion('PARENTESIS_IZQ', q4)
        
        # Desde q1 (después de dígito)
        q1.agregar_transicion('VARIABLE', q2)  # Coeficiente
        q1.agregar_transicion('OPERADOR', q3)
        q1.agregar_transicion('PARENTESIS_DER', q5)
        q1.agregar_transicion('EXPONENTE', q6)
        
        # Desde q2 (después de variable)
        q2.agregar_transicion('OPERADOR', q3)
        q2.agregar_transicion('PARENTESIS_DER', q5)
        q2.agregar_transicion('EXPONENTE', q6)
        
        # Desde q3 (después de operador)
        q3.agregar_transicion('DIGITO', q1)
        q3.agregar_transicion('VARIABLE', q2)
        q3.agregar_transicion('PARENTESIS_IZQ', q4)
        
        # Desde q4 (después de paréntesis izquierdo)
        q4.agregar_transicion('DIGITO', q1)
        q4.agregar_transicion('VARIABLE', q2)
        q4.agregar_transicion('PARENTESIS_IZQ', q4)
        
        # Desde q5 (después de paréntesis derecho)
        q5.agregar_transicion('OPERADOR', q3)
        q5.agregar_transicion('PARENTESIS_DER', q5)
        q5.agregar_transicion('EXPONENTE', q6)
        
        # Desde q6 (después de exponente)
        q6.agregar_transicion('DIGITO', q1)
        q6.agregar_transicion('VARIABLE', q2)
        q6.agregar_transicion('PARENTESIS_IZQ', q4)
        
        # Transiciones a estado final
        q1.agregar_transicion('EOF', q7)
        q2.agregar_transicion('EOF', q7)
        q5.agregar_transicion('EOF', q7)
    
    def _validar_tokens_entrada(self, tokens) -> List[str]:
        """
        Valida que los tokens de entrada sean válidos para expresiones algebraicas.
        
        Args:
            tokens: Lista de tokens a validar
            
        Returns:
            List[str]: Lista de errores encontrados (vacía si no hay errores)
        """
        errores = []
        
        if not tokens:
            return ["No hay tokens para procesar"]
        
        # Tipos de tokens permitidos para expresiones algebraicas
        tipos_permitidos = {'DIGITO', 'VARIABLE', 'OPERADOR', 'EXPONENTE', 
                           'PARENTESIS_IZQ', 'PARENTESIS_DER', 'COEFICIENTE'}
        
        # Si son objetos Token, validar tipos
        if hasattr(tokens[0], 'tipo'):
            for token in tokens:
                if token.tipo == 'DESCONOCIDO':
                    errores.append(f"Carácter no permitido: '{token.valor}' en posición {token.posicion}")
                elif token.tipo not in tipos_permitidos and token.tipo != 'ESPACIO':
                    errores.append(f"Token no permitido: '{token.tipo}' con valor '{token.valor}' en posición {token.posicion}")
        
        return errores
    
    def _validar_estructura_algebraica(self, tokens) -> List[str]:
        """
        Valida que la estructura sea una expresión algebraica válida.
        
        Args:
            tokens: Lista de tokens a validar (pueden ser objetos Token o strings)
            
        Returns:
            List[str]: Lista de errores encontrados (vacía si no hay errores)
        """
        errores = []
        
        if not tokens:
            return ["No hay tokens para procesar"]
        
        # Determinar si son objetos Token o strings
        if isinstance(tokens[0], str):
            # Son strings (símbolos), no podemos validar estructura aquí
            # La validación de estructura se hace en el analizador léxico
            return []
        
        # Filtrar solo tokens no espaciales
        tokens_validos = [token for token in tokens if token.tipo != 'ESPACIO']
        
        if not tokens_validos:
            return ["No hay tokens válidos para procesar"]
        
        # Verificar que no sea solo una secuencia de variables (como "carlos")
        solo_variables = all(token.tipo == 'VARIABLE' for token in tokens_validos)
        if solo_variables and len(tokens_validos) > 1:
            errores.append("Secuencia de solo variables no es una expresión algebraica válida")
            return errores
        
        # Verificar que no sea solo una secuencia de dígitos
        solo_digitos = all(token.tipo == 'DIGITO' for token in tokens_validos)
        # También verificar si es un solo token de dígitos con múltiples caracteres
        if solo_digitos and len(tokens_validos) == 1 and len(tokens_validos[0].valor) > 1:
            errores.append("Secuencia de solo dígitos no es una expresión algebraica válida")
            return errores
        
        # Verificar que tenga al menos un operador o paréntesis (estructura algebraica)
        tiene_operador = any(token.tipo == 'OPERADOR' for token in tokens_validos)
        tiene_parentesis = any(token.tipo in ['PARENTESIS_IZQ', 'PARENTESIS_DER'] for token in tokens_validos)
        tiene_exponente = any(token.tipo == 'EXPONENTE' for token in tokens_validos)
        
        # Si es una sola variable o un solo dígito, es válido
        if len(tokens_validos) == 1:
            return []
        
        # Si es una secuencia de solo dígitos (más de uno), no es algebraica
        if solo_digitos and len(tokens_validos) > 1:
            errores.append("Secuencia de solo dígitos no es una expresión algebraica válida")
            return errores
        
        # Si no tiene operadores, paréntesis o exponentes, no es algebraica
        if not (tiene_operador or tiene_parentesis or tiene_exponente):
            errores.append("La expresión debe contener operadores, paréntesis o exponentes para ser algebraica")
        
        return errores
    
    def _mapear_token_a_simbolo(self, token) -> str:
        """
        Mapea un token a su símbolo correspondiente en el AFD.
        
        Args:
            token: Token a mapear
            
        Returns:
            str: Símbolo correspondiente
        """
        if token.tipo == 'DIGITO':
            return 'DIGITO'
        elif token.tipo == 'VARIABLE':
            return 'VARIABLE'
        elif token.tipo == 'OPERADOR':
            return 'OPERADOR'
        elif token.tipo == 'EXPONENTE':
            return 'EXPONENTE'
        elif token.tipo == 'PARENTESIS_IZQ':
            return 'PARENTESIS_IZQ'
        elif token.tipo == 'PARENTESIS_DER':
            return 'PARENTESIS_DER'
        elif token.tipo == 'COEFICIENTE':
            return 'COEFICIENTE'
        else:
            return token.tipo
    
    def procesar_tokens(self, tokens) -> Tuple[bool, List[str]]:
        """
        Procesa una lista de tokens usando el AFD.
        
        Args:
            tokens: Lista de tokens (objetos Token o strings) a procesar
            
        Returns:
            Tuple[bool, List[str]]: (es_valida, lista_de_errores)
        """
        if not tokens:
            return False, ["No hay tokens para procesar"]
        
        # Validar que todos los tokens sean válidos para expresiones algebraicas
        errores_validacion = self._validar_tokens_entrada(tokens)
        if errores_validacion:
            return False, errores_validacion
        
        # Validar estructura algebraica
        errores_estructura = self._validar_estructura_algebraica(tokens)
        if errores_estructura:
            return False, errores_estructura
        
        estado_actual = self.estado_inicial
        errores = []
        historial = [estado_actual.nombre]
        
        # Determinar si son objetos Token o strings
        if isinstance(tokens[0], str):
            # Son strings (valores reales)
            tokens_validos = tokens
        else:
            # Son objetos Token - filtrar espacios y verificar que no sean desconocidos
            tokens_validos = []
            for token in tokens:
                if token.tipo == 'ESPACIO':
                    continue
                elif token.tipo == 'DESCONOCIDO':
                    errores.append(f"Token inválido '{token.valor}' en posición {token.posicion}")
                    return False, errores
                else:
                    # Convertir el tipo de token al símbolo que espera el AFD
                    simbolo = self._mapear_token_a_simbolo(token)
                    tokens_validos.append(simbolo)
        
        for i, token in enumerate(tokens_validos):
            siguiente_estado = estado_actual.obtener_siguiente_estado(token)
            
            if siguiente_estado is None:
                errores.append(f"Transición inválida desde {estado_actual.nombre} con token '{token}' en posición {i}")
                return False, errores
            
            estado_actual = siguiente_estado
            historial.append(estado_actual.nombre)
        
        # Agregar token EOF para terminar la expresión
        siguiente_estado = estado_actual.obtener_siguiente_estado('EOF')
        if siguiente_estado is not None:
            estado_actual = siguiente_estado
            historial.append(estado_actual.nombre)
        
        # Verificar si terminamos en un estado final
        if estado_actual.es_final:
            return True, []
        else:
            errores.append(f"La expresión no termina en un estado final. Estado actual: {estado_actual.nombre}")
            return False, errores
    
    def obtener_historial_estados(self, tokens) -> List[str]:
        """
        Obtiene el historial de estados durante el procesamiento.
        
        Args:
            tokens: Lista de tokens (objetos Token o strings) a procesar
            
        Returns:
            List[str]: Lista de nombres de estados visitados
        """
        if not tokens:
            return []
        
        estado_actual = self.estado_inicial
        historial = [estado_actual.nombre]
        
        # Determinar si son objetos Token o strings
        if isinstance(tokens[0], str):
            # Son strings (valores reales)
            tokens_validos = tokens
        else:
            # Son objetos Token - mapear a símbolos del AFD
            tokens_validos = []
            for token in tokens:
                if token.tipo != 'ESPACIO':
                    simbolo = self._mapear_token_a_simbolo(token)
                    tokens_validos.append(simbolo)
        
        for token in tokens_validos:
            siguiente_estado = estado_actual.obtener_siguiente_estado(token)
            if siguiente_estado is None:
                break
                
            estado_actual = siguiente_estado
            historial.append(estado_actual.nombre)
        
        return historial
    
    def obtener_estados(self) -> Dict[str, EstadoAFD]:
        """Retorna todos los estados del AFD."""
        return self.estados
    
    def obtener_estado_inicial(self) -> EstadoAFD:
        """Retorna el estado inicial del AFD."""
        return self.estado_inicial
    
    def obtener_alfabeto(self) -> Set[str]:
        """Retorna el alfabeto del AFD."""
        return self.alfabeto
