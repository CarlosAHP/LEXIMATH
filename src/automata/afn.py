"""
Implementación del Autómata Finito No Determinista (AFN) con ε-transiciones.
"""

from typing import Dict, Set, List, Optional, Tuple
from ..lexer.tokens import Token

class EstadoAFN:
    """Representa un estado del AFN."""
    
    def __init__(self, nombre: str, es_final: bool = False):
        self.nombre = nombre
        self.es_final = es_final
        self.transiciones: Dict[str, Set['EstadoAFN']] = {}
    
    def agregar_transicion(self, simbolo: str, estado_destino: 'EstadoAFN'):
        """Agrega una transición desde este estado."""
        if simbolo not in self.transiciones:
            self.transiciones[simbolo] = set()
        self.transiciones[simbolo].add(estado_destino)
    
    def obtener_estados_destino(self, simbolo: str) -> Set['EstadoAFN']:
        """Obtiene los estados destino para un símbolo dado."""
        return self.transiciones.get(simbolo, set())

class AFN:
    """Autómata Finito No Determinista con ε-transiciones para expresiones algebraicas."""
    
    def __init__(self):
        self.estados: Dict[str, EstadoAFN] = {}
        self.estado_inicial: Optional[EstadoAFN] = None
        self.alfabeto: Set[str] = set()
        self._construir_afn()
    
    def _construir_afn(self):
        """Construye el AFN para reconocer expresiones algebraicas."""
        # Crear estados
        q0 = EstadoAFN("q0")  # Estado inicial
        q1 = EstadoAFN("q1")  # Después de dígito
        q2 = EstadoAFN("q2")  # Después de variable
        q3 = EstadoAFN("q3")  # Después de operador
        q4 = EstadoAFN("q4")  # Después de paréntesis izquierdo
        q5 = EstadoAFN("q5")  # Después de paréntesis derecho
        q6 = EstadoAFN("q6")  # Después de exponente
        q7 = EstadoAFN("q7", es_final=True)  # Estado final
        
        # Agregar estados al AFN
        self.estados = {
            "q0": q0, "q1": q1, "q2": q2, "q3": q3,
            "q4": q4, "q5": q5, "q6": q6, "q7": q7
        }
        
        self.estado_inicial = q0
        
        # Definir alfabeto (incluyendo ε)
        self.alfabeto = {'DIGITO', 'VARIABLE', 'OPERADOR', 'PARENTESIS_IZQ', 
                        'PARENTESIS_DER', 'EXPONENTE', 'ε'}
        
        # Definir transiciones con ε-transiciones
        # Desde q0 (estado inicial)
        q0.agregar_transicion('DIGITO', q1)
        q0.agregar_transicion('VARIABLE', q2)
        q0.agregar_transicion('PARENTESIS_IZQ', q4)
        
        # Desde q1 (después de dígito)
        q1.agregar_transicion('VARIABLE', q2)  # Coeficiente
        q1.agregar_transicion('OPERADOR', q3)
        q1.agregar_transicion('PARENTESIS_DER', q5)
        q1.agregar_transicion('EXPONENTE', q6)
        q1.agregar_transicion('ε', q7)  # ε-transición al estado final
        
        # Desde q2 (después de variable)
        q2.agregar_transicion('OPERADOR', q3)
        q2.agregar_transicion('PARENTESIS_DER', q5)
        q2.agregar_transicion('EXPONENTE', q6)
        q2.agregar_transicion('ε', q7)  # ε-transición al estado final
        
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
        q5.agregar_transicion('ε', q7)  # ε-transición al estado final
        
        # Desde q6 (después de exponente)
        q6.agregar_transicion('DIGITO', q1)
        q6.agregar_transicion('VARIABLE', q2)
        q6.agregar_transicion('PARENTESIS_IZQ', q4)
    
    def cerrar_epsilon(self, estados: Set[EstadoAFN]) -> Set[EstadoAFN]:
        """
        Calcula la clausura ε de un conjunto de estados.
        
        Args:
            estados: Conjunto de estados iniciales
            
        Returns:
            Set[EstadoAFN]: Conjunto de estados incluyendo clausura ε
        """
        clausura = set(estados)
        pila = list(estados)
        
        while pila:
            estado = pila.pop()
            estados_epsilon = estado.obtener_estados_destino('ε')
            
            for estado_epsilon in estados_epsilon:
                if estado_epsilon not in clausura:
                    clausura.add(estado_epsilon)
                    pila.append(estado_epsilon)
        
        return clausura
    
    def mover(self, estados: Set[EstadoAFN], simbolo: str) -> Set[EstadoAFN]:
        """
        Calcula el conjunto de estados alcanzables desde un conjunto de estados
        con un símbolo dado.
        
        Args:
            estados: Conjunto de estados origen
            simbolo: Símbolo de entrada
            
        Returns:
            Set[EstadoAFN]: Conjunto de estados destino
        """
        resultado = set()
        
        for estado in estados:
            estados_destino = estado.obtener_estados_destino(simbolo)
            resultado.update(estados_destino)
        
        return resultado
    
    def procesar_tokens(self, tokens) -> Tuple[bool, List[str]]:
        """
        Procesa una lista de tokens usando el AFN.
        
        Args:
            tokens: Lista de tokens (objetos Token o strings) a procesar
            
        Returns:
            Tuple[bool, List[str]]: (es_valida, lista_de_errores)
        """
        if not tokens:
            return False, ["No hay tokens para procesar"]
        
        # Determinar si son objetos Token o strings
        if isinstance(tokens[0], str):
            # Son strings (valores reales)
            tokens_validos = tokens
        else:
            # Son objetos Token
            tokens_validos = [token.valor for token in tokens if token.tipo != 'ESPACIO']
        
        # Estado inicial con clausura ε
        estados_actuales = self.cerrar_epsilon({self.estado_inicial})
        errores = []
        historial = [f"{{{', '.join(sorted(s.nombre for s in estados_actuales))}}}"]
        
        for i, token in enumerate(tokens_validos):
            # Mover con el símbolo
            estados_destino = self.mover(estados_actuales, token)
            
            if not estados_destino:
                errores.append(f"No hay transición desde {historial[-1]} con token '{token}' en posición {i}")
                return False, errores
            
            # Aplicar clausura ε
            estados_actuales = self.cerrar_epsilon(estados_destino)
            historial.append(f"{{{', '.join(sorted(s.nombre for s in estados_actuales))}}}")
        
        # Verificar si algún estado actual es final
        tiene_estado_final = any(estado.es_final for estado in estados_actuales)
        
        if not tiene_estado_final:
            errores.append(f"Ningún estado final alcanzado. Estados actuales: {historial[-1]}")
            return False, errores
        
        return True, []
    
    def obtener_historial_estados(self, tokens) -> List[str]:
        """
        Obtiene el historial de estados durante el procesamiento.
        
        Args:
            tokens: Lista de tokens (objetos Token o strings) a procesar
            
        Returns:
            List[str]: Lista de conjuntos de estados visitados
        """
        if not tokens:
            return []
        
        # Determinar si son objetos Token o strings
        if isinstance(tokens[0], str):
            # Son strings (valores reales)
            tokens_validos = tokens
        else:
            # Son objetos Token
            tokens_validos = [token.valor for token in tokens if token.tipo != 'ESPACIO']
        
        # Estado inicial con clausura ε
        estados_actuales = self.cerrar_epsilon({self.estado_inicial})
        historial = [f"{{{', '.join(sorted(s.nombre for s in estados_actuales))}}}"]
        
        for token in tokens_validos:
            # Mover con el símbolo
            estados_destino = self.mover(estados_actuales, token)
            
            if not estados_destino:
                break
            
            # Aplicar clausura ε
            estados_actuales = self.cerrar_epsilon(estados_destino)
            historial.append(f"{{{', '.join(sorted(s.nombre for s in estados_actuales))}}}")
        
        return historial
    
    def obtener_estados(self) -> Dict[str, EstadoAFN]:
        """Retorna todos los estados del AFN."""
        return self.estados
    
    def obtener_estado_inicial(self) -> EstadoAFN:
        """Retorna el estado inicial del AFN."""
        return self.estado_inicial
    
    def obtener_alfabeto(self) -> Set[str]:
        """Retorna el alfabeto del AFN."""
        return self.alfabeto
