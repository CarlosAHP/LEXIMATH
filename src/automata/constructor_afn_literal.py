"""
Constructor de AFN-ε para cadenas literales usando el algoritmo de Thompson.
Implementa la construcción específica para cadenas exactas como (3a+b)^2.
"""

from typing import Set, Dict, List, Tuple, Optional
from .afn import AFN, EstadoAFN


class ConstructorAFNLiteral:
    """
    Constructor de AFN-ε para cadenas literales.
    Implementa el algoritmo de Thompson para cadenas exactas.
    """
    
    def __init__(self):
        """Inicializa el constructor de AFN literal."""
        self.contador_estados = 0
        self.alfabeto = set()
    
    def construir_afn_desde_cadena_literal(self, cadena: str) -> AFN:
        """
        Construye un AFN-ε para una cadena literal específica.
        
        Args:
            cadena: Cadena literal a convertir (ej: "(3a+b)^2")
            
        Returns:
            AFN: AFN-ε construido
        """
        # Limpiar y preparar
        self.contador_estados = 0
        self.alfabeto = set()
        
        # Crear AFN base
        afn = AFN()
        afn.estados = {}
        afn.alfabeto = set()
        
        # Procesar cada símbolo de la cadena
        if not cadena:
            return self._crear_afn_vacio(afn)
        
        # Crear AFN para el primer símbolo
        estado_inicial, estado_actual = self._crear_afn_simbolo(cadena[0], afn)
        afn.estado_inicial = estado_inicial
        
        # Procesar el resto de símbolos
        for i in range(1, len(cadena)):
            simbolo = cadena[i]
            nuevo_estado_inicial, nuevo_estado_final = self._crear_afn_simbolo(simbolo, afn)
            
            # Conectar con transición ε
            afn.agregar_transicion(estado_actual, 'ε', nuevo_estado_inicial)
            estado_actual = nuevo_estado_final
        
        # Marcar el último estado como final
        afn.estados_finales = {estado_actual}
        
        # Actualizar alfabeto
        afn.alfabeto = self.alfabeto.copy()
        
        return afn
    
    def _crear_afn_simbolo(self, simbolo: str, afn: AFN) -> Tuple[int, int]:
        """
        Crea un AFN para un símbolo literal.
        
        Args:
            simbolo: Símbolo literal
            afn: AFN base
            
        Returns:
            Tuple[int, int]: (estado_inicial, estado_final)
        """
        estado_inicial = self._nuevo_estado()
        estado_final = self._nuevo_estado()
        
        # Crear estados
        afn.agregar_estado(estado_inicial)
        afn.agregar_estado(estado_final)
        
        # Agregar transición
        afn.agregar_transicion(estado_inicial, simbolo, estado_final)
        
        # Actualizar alfabeto
        self.alfabeto.add(simbolo)
        
        return estado_inicial, estado_final
    
    def _crear_afn_vacio(self, afn: AFN) -> Tuple[int, int]:
        """
        Crea un AFN que acepta la cadena vacía.
        
        Args:
            afn: AFN base
            
        Returns:
            Tuple[int, int]: (estado_inicial, estado_final)
        """
        estado_inicial = self._nuevo_estado()
        estado_final = self._nuevo_estado()
        
        # Crear estados
        afn.agregar_estado(estado_inicial)
        afn.agregar_estado(estado_final)
        
        # Agregar transición ε
        afn.agregar_transicion(estado_inicial, 'ε', estado_final)
        
        return estado_inicial, estado_final
    
    def _nuevo_estado(self) -> int:
        """
        Genera un nuevo estado único.
        
        Returns:
            int: ID del nuevo estado
        """
        estado = self.contador_estados
        self.contador_estados += 1
        return estado
    
    def obtener_tabla_transiciones(self, afn: AFN) -> Dict:
        """
        Obtiene la tabla de transiciones del AFN en formato tabular.
        
        Args:
            afn: AFN construido
            
        Returns:
            Dict: Tabla de transiciones
        """
        # Obtener todos los símbolos del alfabeto (incluyendo ε)
        simbolos = sorted(list(afn.alfabeto))
        simbolos.append('ε')
        
        # Crear tabla
        tabla = {}
        
        for estado_id in sorted(afn.estados.keys()):
            estado = afn.estados[estado_id]
            fila = {}
            
            for simbolo in simbolos:
                destinos = estado.transiciones.get(simbolo, set())
                if destinos:
                    fila[simbolo] = sorted(list(destinos))
                else:
                    fila[simbolo] = []
            
            tabla[f"q{estado_id}"] = fila
        
        return tabla
    
    def mostrar_afn_detallado(self, afn: AFN, cadena: str):
        """
        Muestra información detallada del AFN construido.
        
        Args:
            afn: AFN construido
            cadena: Cadena original
        """
        print("=" * 80)
        print(f"AFN-ε PARA CADENA LITERAL: {cadena}")
        print("=" * 80)
        
        print(f"Estados: q0, ..., q{len(afn.estados)-1}")
        print(f"Estado inicial: q{afn.estado_inicial}")
        print(f"Estado(s) de aceptación: q{list(afn.estados_finales)[0]}")
        print(f"Alfabeto: {sorted(list(afn.alfabeto))}")
        
        print(f"\nEstructura (esquema):")
        self._mostrar_esquema_transiciones(afn, cadena)
        
        print(f"\nTabla de transiciones (AFN-ε):")
        self._mostrar_tabla_transiciones(afn)
    
    def _mostrar_esquema_transiciones(self, afn: AFN, cadena: str):
        """
        Muestra el esquema de transiciones del AFN.
        
        Args:
            afn: AFN construido
            cadena: Cadena original
        """
        esquema = []
        estado_actual = afn.estado_inicial
        
        for i, simbolo in enumerate(cadena):
            if i == 0:
                esquema.append(f"q_{estado_actual} \\xrightarrow{{{simbolo}}} q_{estado_actual + 1}")
            else:
                esquema.append(f"\\xrightarrow{{\\varepsilon}} q_{estado_actual} \\xrightarrow{{{simbolo}}} q_{estado_actual + 1}")
            estado_actual += 1
        
        print(" ".join(esquema))
    
    def _mostrar_tabla_transiciones(self, afn: AFN):
        """
        Muestra la tabla de transiciones del AFN.
        
        Args:
            afn: AFN construido
        """
        tabla = self.obtener_tabla_transiciones(afn)
        
        # Obtener todos los símbolos
        simbolos = set()
        for fila in tabla.values():
            simbolos.update(fila.keys())
        simbolos = sorted(list(simbolos))
        
        # Mostrar encabezados
        print(f"{'Estado':<8}", end="")
        for simbolo in simbolos:
            print(f"{simbolo:<8}", end="")
        print()
        
        # Mostrar filas
        for estado, transiciones in tabla.items():
            print(f"{estado:<8}", end="")
            for simbolo in simbolos:
                destinos = transiciones.get(simbolo, [])
                if destinos:
                    destinos_str = ','.join(map(str, destinos))
                    print(f"{{{destinos_str}}}<8", end="")
                else:
                    print(f"∅{'':<7}", end="")
            print()
    
    def probar_cadena(self, afn: AFN, cadena_prueba: str) -> bool:
        """
        Prueba si el AFN acepta una cadena específica.
        
        Args:
            afn: AFN construido
            cadena_prueba: Cadena a probar
            
        Returns:
            bool: True si la cadena es aceptada
        """
        # Simular el procesamiento de la cadena
        estados_actuales = {afn.estado_inicial}
        
        # Aplicar ε-cerradura inicial
        estados_actuales = self._aplicar_epsilon_cerradura(afn, estados_actuales)
        
        for simbolo in cadena_prueba:
            # Mover con el símbolo
            nuevos_estados = set()
            for estado in estados_actuales:
                if estado in afn.estados:
                    destinos = afn.estados[estado].transiciones.get(simbolo, set())
                    nuevos_estados.update(destinos)
            
            if not nuevos_estados:
                return False
            
            # Aplicar ε-cerradura
            estados_actuales = self._aplicar_epsilon_cerradura(afn, nuevos_estados)
        
        # Verificar si algún estado actual es final
        return any(estado in afn.estados_finales for estado in estados_actuales)
    
    def _aplicar_epsilon_cerradura(self, afn: AFN, estados: Set[int]) -> Set[int]:
        """
        Aplica ε-cerradura a un conjunto de estados.
        
        Args:
            afn: AFN
            estados: Conjunto de estados
            
        Returns:
            Set[int]: Conjunto de estados con ε-cerradura aplicada
        """
        cerradura = set(estados)
        pila = list(estados)
        
        while pila:
            estado = pila.pop()
            if estado in afn.estados:
                destinos_epsilon = afn.estados[estado].transiciones.get('ε', set())
                for destino in destinos_epsilon:
                    if destino not in cerradura:
                        cerradura.add(destino)
                        pila.append(destino)
        
        return cerradura
