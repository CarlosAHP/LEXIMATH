"""
Minimizador de AFD usando el método de particiones.
Implementa el algoritmo de minimización paso a paso.
"""

from typing import Set, Dict, List, Tuple, Optional
from collections import defaultdict


class MinimizadorAFDParticiones:
    """
    Minimizador de AFD usando el método de particiones.
    """
    
    def __init__(self):
        """Inicializa el minimizador."""
        self.afd_original = None
        self.alfabeto = set()
        self.estados = set()
        self.estado_inicial = None
        self.estados_finales = set()
        self.transiciones = {}
        self.particiones = []
        self.afd_minimizado = {}
    
    def minimizar(self, afd_info: Dict) -> Dict:
        """
        Minimiza un AFD usando el método de particiones.
        
        Args:
            afd_info: Información del AFD a minimizar
            
        Returns:
            Dict: AFD minimizado
        """
        self._inicializar_datos(afd_info)
        
        print("=" * 80)
        print("MINIMIZACION DE AFD - METODO DE PARTICIONES")
        print("=" * 80)
        
        # Paso 1: Partición inicial
        print("\n1. PARTICION INICIAL P0")
        particion_inicial = self._crear_particion_inicial()
        self.particiones = [particion_inicial]
        self._mostrar_particion(0, particion_inicial)
        
        # Paso 2: Refinar particiones
        print("\n2. REFINAR PARTICIONES")
        iteracion = 1
        while True:
            nueva_particion = self._refinar_particion(self.particiones[-1])
            if nueva_particion == self.particiones[-1]:
                break
            
            self.particiones.append(nueva_particion)
            self._mostrar_particion(iteracion, nueva_particion)
            iteracion += 1
        
        # Paso 3: Generar AFD minimizado
        print(f"\n3. AFD MINIMIZADO")
        afd_minimizado = self._generar_afd_minimizado()
        self._mostrar_afd_minimizado(afd_minimizado)
        
        return afd_minimizado
    
    def _inicializar_datos(self, afd_info: Dict):
        """
        Inicializa los datos del AFD a minimizar.
        
        Args:
            afd_info: Información del AFD
        """
        self.afd_original = afd_info
        self.estados = set(afd_info['estados'].keys())
        self.estado_inicial = afd_info['estado_inicial']
        self.estados_finales = set(afd_info['estados_finales'])
        self.transiciones = afd_info['transiciones']
        
        # Obtener alfabeto de las transiciones
        self.alfabeto = set()
        for estado, trans_estado in self.transiciones.items():
            self.alfabeto.update(trans_estado.keys())
        self.alfabeto.discard('ε')  # Remover epsilon si existe
    
    def _crear_particion_inicial(self) -> List[Set[str]]:
        """
        Crea la partición inicial separando estados finales y no finales.
        
        Returns:
            List[Set[str]]: Partición inicial
        """
        estados_finales = set()
        estados_no_finales = set()
        
        for estado in self.estados:
            if estado in self.estados_finales:
                estados_finales.add(estado)
            else:
                estados_no_finales.add(estado)
        
        particion = []
        if estados_finales:
            particion.append(estados_finales)
        if estados_no_finales:
            particion.append(estados_no_finales)
        
        return particion
    
    def _mostrar_particion(self, iteracion: int, particion: List[Set[str]]):
        """
        Muestra una partición de manera legible.
        
        Args:
            iteracion: Número de iteración
            particion: Partición a mostrar
        """
        print(f"P{iteracion} = {{")
        for i, grupo in enumerate(particion):
            grupo_str = "{" + ",".join(sorted(grupo)) + "}"
            if i < len(particion) - 1:
                print(f"  {grupo_str},")
            else:
                print(f"  {grupo_str}")
        print("}")
    
    def _refinar_particion(self, particion_actual: List[Set[str]]) -> List[Set[str]]:
        """
        Refina una partición separando estados que no son equivalentes.
        
        Args:
            particion_actual: Partición actual
            
        Returns:
            List[Set[str]]: Nueva partición refinada
        """
        nueva_particion = []
        
        for grupo in particion_actual:
            if len(grupo) == 1:
                # Grupo con un solo estado, no se puede refinar
                nueva_particion.append(grupo)
                continue
            
            # Agrupar estados por comportamiento
            grupos_comportamiento = defaultdict(list)
            
            for estado in grupo:
                comportamiento = self._obtener_comportamiento(estado, particion_actual)
                grupos_comportamiento[comportamiento].append(estado)
            
            # Agregar grupos resultantes
            for grupo_comportamiento in grupos_comportamiento.values():
                nueva_particion.append(set(grupo_comportamiento))
        
        return nueva_particion
    
    def _obtener_comportamiento(self, estado: str, particion: List[Set[str]]) -> Tuple:
        """
        Obtiene el comportamiento de un estado respecto a una partición.
        
        Args:
            estado: Estado a analizar
            particion: Partición actual
            
        Returns:
            Tuple: Comportamiento del estado
        """
        comportamiento = []
        
        for simbolo in sorted(self.alfabeto):
            destino = self.transiciones.get(estado, {}).get(simbolo, None)
            if destino is None:
                comportamiento.append(None)
            else:
                # Encontrar a qué grupo pertenece el destino
                for i, grupo in enumerate(particion):
                    if destino in grupo:
                        comportamiento.append(i)
                        break
                else:
                    comportamiento.append(-1)  # No encontrado
        
        return tuple(comportamiento)
    
    def _generar_afd_minimizado(self) -> Dict:
        """
        Genera el AFD minimizado a partir de las particiones finales.
        
        Returns:
            Dict: AFD minimizado
        """
        particion_final = self.particiones[-1]
        
        # Crear mapeo de estados originales a nuevos estados
        mapeo_estados = {}
        nuevos_estados = {}
        nuevos_estados_finales = set()
        nuevo_estado_inicial = None
        
        for i, grupo in enumerate(particion_final):
            nombre_nuevo_estado = f"G{i}"
            nuevos_estados[nombre_nuevo_estado] = grupo
            
            # Mapear cada estado del grupo al nuevo estado
            for estado_original in grupo:
                mapeo_estados[estado_original] = nombre_nuevo_estado
            
            # Verificar si es estado final
            if any(estado in self.estados_finales for estado in grupo):
                nuevos_estados_finales.add(nombre_nuevo_estado)
            
            # Verificar si contiene el estado inicial
            if self.estado_inicial in grupo:
                nuevo_estado_inicial = nombre_nuevo_estado
        
        # Crear transiciones del AFD minimizado
        nuevas_transiciones = {}
        for nombre_nuevo, grupo_estados in nuevos_estados.items():
            nuevas_transiciones[nombre_nuevo] = {}
            
            # Tomar un representante del grupo para las transiciones
            estado_representante = next(iter(grupo_estados))
            transiciones_representante = self.transiciones.get(estado_representante, {})
            
            for simbolo, destino in transiciones_representante.items():
                if destino and destino in mapeo_estados:
                    nuevas_transiciones[nombre_nuevo][simbolo] = mapeo_estados[destino]
        
        return {
            'estados': nuevos_estados,
            'transiciones': nuevas_transiciones,
            'estado_inicial': nuevo_estado_inicial,
            'estados_finales': nuevos_estados_finales,
            'alfabeto': self.alfabeto,
            'mapeo_estados': mapeo_estados
        }
    
    def _mostrar_afd_minimizado(self, afd_minimizado: Dict):
        """
        Muestra el AFD minimizado.
        
        Args:
            afd_minimizado: AFD minimizado
        """
        print(f"Estados: {', '.join(sorted(afd_minimizado['estados'].keys()))}")
        print(f"Estado inicial: {afd_minimizado['estado_inicial']}")
        print(f"Estados finales: {', '.join(sorted(afd_minimizado['estados_finales']))}")
        print(f"Alfabeto: {sorted(afd_minimizado['alfabeto'])}")
        
        # Mostrar tabla de transiciones
        print(f"\nTabla de transiciones del AFD minimizado:")
        simbolos = sorted(afd_minimizado['alfabeto'])
        
        # Encabezados
        print(f"{'Estado':<8}", end="")
        for simbolo in simbolos:
            print(f"{simbolo:<8}", end="")
        print(f"{'Final':<8}")
        
        # Filas
        for estado in sorted(afd_minimizado['estados'].keys()):
            es_final = "SI" if estado in afd_minimizado['estados_finales'] else "No"
            print(f"{estado:<8}", end="")
            
            for simbolo in simbolos:
                destino = afd_minimizado['transiciones'].get(estado, {}).get(simbolo, "")
                print(f"{destino:<8}", end="")
            
            print(f"{es_final:<8}")
        
        # Mostrar mapeo de estados
        print(f"\nMapeo de estados:")
        for estado_original, estado_nuevo in sorted(afd_minimizado['mapeo_estados'].items()):
            print(f"  {estado_original} -> {estado_nuevo}")
    
    def mostrar_proceso_detallado(self):
        """
        Muestra el proceso de minimización paso a paso.
        """
        print(f"\n4. PROCESO DETALLADO DE MINIMIZACION")
        print("=" * 50)
        
        for i, particion in enumerate(self.particiones):
            print(f"\nIteracion {i}:")
            self._mostrar_particion(i, particion)
            
            if i < len(self.particiones) - 1:
                print("  -> Refinando...")
            else:
                print("  -> No se puede refinar mas (convergencia)")
        
        print(f"\nResultado: {len(self.particiones[-1])} grupos finales")
        
        # Verificar si hay reducción
        estados_originales = len(self.estados)
        estados_minimizados = len(self.particiones[-1])
        reduccion = estados_originales - estados_minimizados
        
        if reduccion > 0:
            print(f"Reduccion: {reduccion} estados eliminados")
        else:
            print("No hay reduccion posible - AFD ya es minimo")
