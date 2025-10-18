"""
Conversor de AFN-ε a AFD usando el método del subconjunto (cerraduras-ε).
Implementa la conversión paso a paso con lógica formal.
"""

from typing import Set, Dict, List, Tuple, Optional
from .afn import AFN, EstadoAFN


class ConversorAFNAFDSubconjuntos:
    """
    Conversor de AFN-ε a AFD usando el método del subconjunto.
    """
    
    def __init__(self):
        """Inicializa el conversor."""
        self.afn = None
        self.afd_estados = {}  # {nombre_estado: conjunto_estados_afn}
        self.afd_transiciones = {}  # {estado: {simbolo: estado_destino}}
        self.afd_estado_inicial = None
        self.afd_estados_finales = set()
        self.contador_estados_afd = 0
    
    def convertir(self, afn: AFN) -> Dict:
        """
        Convierte un AFN-ε a AFD usando el método del subconjunto.
        
        Args:
            afn: AFN-ε a convertir
            
        Returns:
            Dict: AFD resultante con información detallada
        """
        self.afn = afn
        self.afd_estados = {}
        self.afd_transiciones = {}
        self.afd_estados_finales = set()
        self.contador_estados_afd = 0
        
        print("=" * 80)
        print("CONVERSION AFN-epsilon A AFD - METODO DEL SUBCONJUNTO")
        print("=" * 80)
        
        # Paso 1: Calcular ε-cerraduras
        print("\n1. CALCULANDO EPSILON-CERRADURAS")
        epsilon_cerraduras = self._calcular_epsilon_cerraduras()
        self._mostrar_epsilon_cerraduras(epsilon_cerraduras)
        
        # Paso 2: Determinar estado inicial del AFD
        print("\n2. DETERMINANDO ESTADO INICIAL DEL AFD")
        estado_inicial_afd = epsilon_cerraduras[afn.estado_inicial]
        print(f"Estado inicial del AFD = epsilon-cerradura(q{afn.estado_inicial})")
        print(f"-> A0 = {estado_inicial_afd}")
        
        # Paso 3: Aplicar método de subconjuntos
        print("\n3. APLICANDO METODO DE SUBCONJUNTOS")
        self._aplicar_metodo_subconjuntos(epsilon_cerraduras)
        
        # Paso 4: Generar tabla del AFD
        print("\n4. TABLA DE TRANSICIONES DEL AFD")
        self._mostrar_tabla_afd()
        
        return {
            'estados': self.afd_estados,
            'transiciones': self.afd_transiciones,
            'estado_inicial': self.afd_estado_inicial,
            'estados_finales': self.afd_estados_finales,
            'epsilon_cerraduras': epsilon_cerraduras
        }
    
    def _calcular_epsilon_cerraduras(self) -> Dict[int, Set[int]]:
        """
        Calcula las ε-cerraduras para todos los estados del AFN.
        
        Returns:
            Dict[int, Set[int]]: Mapeo de estado a su ε-cerradura
        """
        epsilon_cerraduras = {}
        
        for estado_id in self.afn.estados.keys():
            epsilon_cerraduras[estado_id] = self._epsilon_cerradura(estado_id)
        
        return epsilon_cerraduras
    
    def _epsilon_cerradura(self, estado: int) -> Set[int]:
        """
        Calcula la ε-cerradura de un estado específico.
        
        Args:
            estado: ID del estado
            
        Returns:
            Set[int]: Conjunto de estados en la ε-cerradura
        """
        cerradura = {estado}
        pila = [estado]
        
        while pila:
            estado_actual = pila.pop()
            if estado_actual in self.afn.estados:
                # Obtener transiciones epsilon
                transiciones_epsilon = self.afn.estados[estado_actual].transiciones.get('ε', set())
                for destino in transiciones_epsilon:
                    if destino not in cerradura:
                        cerradura.add(destino)
                        pila.append(destino)
        
        return cerradura
    
    def _mostrar_epsilon_cerraduras(self, epsilon_cerraduras: Dict[int, Set[int]]):
        """
        Muestra las ε-cerraduras calculadas.
        
        Args:
            epsilon_cerraduras: Mapeo de estado a ε-cerradura
        """
        print("Estado\tepsilon-cerradura")
        for estado, cerradura in sorted(epsilon_cerraduras.items()):
            cerradura_str = "{" + ",".join(f"q{q}" for q in sorted(cerradura)) + "}"
            print(f"q{estado}\t{cerradura_str}")
    
    def _aplicar_metodo_subconjuntos(self, epsilon_cerraduras: Dict[int, Set[int]]):
        """
        Aplica el método de subconjuntos para construir el AFD.
        
        Args:
            epsilon_cerraduras: Mapeo de estado a ε-cerradura
        """
        # Estado inicial del AFD
        estado_inicial_afn = self.afn.estado_inicial
        conjunto_inicial = epsilon_cerraduras[estado_inicial_afn]
        nombre_estado_inicial = self._crear_estado_afd(conjunto_inicial)
        self.afd_estado_inicial = nombre_estado_inicial
        
        # Cola de estados por procesar
        cola_estados = [conjunto_inicial]
        estados_procesados = set()
        
        while cola_estados:
            conjunto_actual = cola_estados.pop(0)
            nombre_estado_actual = self._obtener_nombre_estado(conjunto_actual)
            
            if nombre_estado_actual in estados_procesados:
                continue
            
            estados_procesados.add(nombre_estado_actual)
            
            # Verificar si es estado final
            if any(estado in self.afn.estados_finales for estado in conjunto_actual):
                self.afd_estados_finales.add(nombre_estado_actual)
            
            # Procesar cada símbolo del alfabeto
            for simbolo in self.afn.alfabeto:
                if simbolo == 'ε':
                    continue
                
                # Calcular move(conjunto_actual, simbolo)
                move_resultado = self._calcular_move(conjunto_actual, simbolo)
                
                if move_resultado:
                    # Aplicar ε-cerradura al resultado
                    epsilon_cerradura_resultado = set()
                    for estado in move_resultado:
                        epsilon_cerradura_resultado.update(epsilon_cerraduras[estado])
                    
                    # Crear o encontrar estado AFD
                    nombre_estado_destino = self._crear_estado_afd(epsilon_cerradura_resultado)
                    
                    # Agregar transición
                    if nombre_estado_actual not in self.afd_transiciones:
                        self.afd_transiciones[nombre_estado_actual] = {}
                    self.afd_transiciones[nombre_estado_actual][simbolo] = nombre_estado_destino
                    
                    # Agregar a la cola si es nuevo
                    if epsilon_cerradura_resultado not in [estado for estado in self.afd_estados.values()]:
                        cola_estados.append(epsilon_cerradura_resultado)
    
    def _calcular_move(self, conjunto_estados: Set[int], simbolo: str) -> Set[int]:
        """
        Calcula move(conjunto_estados, simbolo).
        
        Args:
            conjunto_estados: Conjunto de estados del AFN
            simbolo: Símbolo de entrada
            
        Returns:
            Set[int]: Conjunto de estados alcanzables
        """
        resultado = set()
        
        for estado in conjunto_estados:
            if estado in self.afn.estados:
                destinos = self.afn.estados[estado].transiciones.get(simbolo, set())
                resultado.update(destinos)
        
        return resultado
    
    def _crear_estado_afd(self, conjunto_estados: Set[int]) -> str:
        """
        Crea o encuentra un estado AFD para un conjunto de estados AFN.
        
        Args:
            conjunto_estados: Conjunto de estados del AFN
            
        Returns:
            str: Nombre del estado AFD
        """
        # Verificar si ya existe
        for nombre, conjunto_existente in self.afd_estados.items():
            if conjunto_existente == conjunto_estados:
                return nombre
        
        # Crear nuevo estado
        nombre_estado = f"A{self.contador_estados_afd}"
        self.afd_estados[nombre_estado] = conjunto_estados
        self.contador_estados_afd += 1
        
        return nombre_estado
    
    def _obtener_nombre_estado(self, conjunto_estados: Set[int]) -> str:
        """
        Obtiene el nombre del estado AFD para un conjunto de estados.
        
        Args:
            conjunto_estados: Conjunto de estados del AFN
            
        Returns:
            str: Nombre del estado AFD
        """
        for nombre, conjunto_existente in self.afd_estados.items():
            if conjunto_existente == conjunto_estados:
                return nombre
        
        return self._crear_estado_afd(conjunto_estados)
    
    def _mostrar_tabla_afd(self):
        """
        Muestra la tabla de transiciones del AFD resultante.
        """
        # Obtener todos los símbolos del alfabeto (sin ε)
        simbolos = sorted([s for s in self.afn.alfabeto if s != 'ε'])
        
        # Mostrar encabezados
        print(f"{'Estado AFD':<12} {'Conjunto AFN':<20}", end="")
        for simbolo in simbolos:
            print(f"{simbolo:<8}", end="")
        print(f"{'¿Final?':<8}")
        
        # Mostrar filas
        for nombre_estado, conjunto_estados in sorted(self.afd_estados.items()):
            conjunto_str = "{" + ",".join(f"q{q}" for q in sorted(conjunto_estados)) + "}"
            es_final = "Sí" if nombre_estado in self.afd_estados_finales else "No"
            
            print(f"{nombre_estado:<12} {conjunto_str:<20}", end="")
            
            for simbolo in simbolos:
                destino = self.afd_transiciones.get(nombre_estado, {}).get(simbolo, "")
                print(f"{destino:<8}", end="")
            
            print(f"{es_final:<8}")
        
        print(f"\nInicial: {self.afd_estado_inicial}")
        print(f"Aceptación: {', '.join(sorted(self.afd_estados_finales))}")
    
    def mostrar_diagrama_logico(self):
        """
        Muestra el diagrama lógico del AFD.
        """
        print(f"\n5. DIAGRAMA LOGICO (TEXTO)")
        
        # Construir diagrama
        diagrama = []
        for nombre_estado, transiciones in self.afd_transiciones.items():
            for simbolo, destino in transiciones.items():
                marca_final = " *" if destino in self.afd_estados_finales else ""
                diagrama.append(f"{nombre_estado} --{simbolo}--> {destino}{marca_final}")
        
        print(" ".join(diagrama))
        
        # Mostrar estados finales
        if self.afd_estados_finales:
            finales_str = ", ".join(sorted(self.afd_estados_finales))
            print(f"\n(* {finales_str} son de aceptación.)")