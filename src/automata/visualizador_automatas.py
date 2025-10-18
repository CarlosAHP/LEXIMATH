"""
Visualizador de autómatas usando Graphviz.
Genera gráficos profesionales para AFN-epsilon, AFD y AFD reducido.
"""

from graphviz import Digraph
from typing import Dict, List, Set, Optional


class VisualizadorAutomatas:
    """
    Visualizador de autómatas finitos usando Graphviz.
    """
    
    def __init__(self):
        """Inicializa el visualizador."""
        self.formato = 'png'
        self.directorio_salida = 'graficos'
    
    def graficar_automata(self, automata: Dict, nombre: str = "AFD", eps: bool = False) -> str:
        """
        Dibuja un autómata (AFD o AFN-epsilon).
        
        Args:
            automata: Diccionario con 'estados', 'transiciones', 'inicial', 'finales'
            nombre: Nombre del archivo de salida
            eps: True si deseas mostrar transiciones epsilon
            
        Returns:
            str: Ruta del archivo generado
        """
        g = Digraph(nombre, format=self.formato)
        g.attr(rankdir='LR', size='12,8')
        
        # Configurar estilos
        g.attr('node', fontname='Arial', fontsize='12')
        g.attr('edge', fontname='Arial', fontsize='10')
        
        # Nodo invisible para la flecha de inicio
        g.attr('node', shape='none', width='0', height='0')
        g.node('inicio')
        
        # Estados
        for estado in automata["estados"]:
            if estado in automata["finales"]:
                g.attr('node', shape='doublecircle', color='green', fillcolor='lightgreen', style='filled')
            else:
                g.attr('node', shape='circle', color='black', fillcolor='lightblue', style='filled')
            g.node(estado)
        
        # Flecha de inicio
        g.edge('inicio', automata["inicial"], style='bold', color='red')
        
        # Transiciones
        for origen, destinos in automata["transiciones"].items():
            for simbolo, lista_destinos in destinos.items():
                if simbolo == "ε" and not eps:
                    continue
                for destino in lista_destinos:
                    if simbolo == "ε":
                        g.edge(origen, destino, label='ε', style='dashed', color='gray')
                    else:
                        g.edge(origen, destino, label=simbolo, color='blue')
        
        # Exportar
        try:
            ruta_archivo = g.render(filename=nombre, cleanup=True)
            print(f"Grafico generado: {nombre}.{self.formato}")
            return ruta_archivo
        except Exception as e:
            print(f"Error al generar grafico: {e}")
            return ""
    
    def crear_afn_epsilon_binomio(self) -> Dict:
        """
        Crea la estructura de datos para el AFN-epsilon de (3a+b)^2.
        
        Returns:
            Dict: Estructura del AFN-epsilon
        """
        return {
            "estados": [f"q{i}" for i in range(16)],
            "alfabeto": ["(", "3", "a", "+", "b", ")", "^", "2"],
            "transiciones": {
                "q0": {"(": ["q1"]},
                "q1": {"ε": ["q2"]},
                "q2": {"3": ["q3"]},
                "q3": {"ε": ["q4"]},
                "q4": {"a": ["q5"]},
                "q5": {"ε": ["q6"]},
                "q6": {"+": ["q7"]},
                "q7": {"ε": ["q8"]},
                "q8": {"b": ["q9"]},
                "q9": {"ε": ["q10"]},
                "q10": {")": ["q11"]},
                "q11": {"ε": ["q12"]},
                "q12": {"^": ["q13"]},
                "q13": {"ε": ["q14"]},
                "q14": {"2": ["q15"]}
            },
            "inicial": "q0",
            "finales": ["q15"]
        }
    
    def crear_afd_subconjuntos_binomio(self) -> Dict:
        """
        Crea la estructura de datos para el AFD de (3a+b)^2.
        
        Returns:
            Dict: Estructura del AFD
        """
        return {
            "estados": [f"A{i}" for i in range(9)],
            "alfabeto": ["(", "3", "a", "+", "b", ")", "^", "2"],
            "transiciones": {
                "A0": {"(": ["A1"]},
                "A1": {"3": ["A2"]},
                "A2": {"a": ["A3"]},
                "A3": {"+": ["A4"]},
                "A4": {"b": ["A5"]},
                "A5": {")": ["A6"]},
                "A6": {"^": ["A7"]},
                "A7": {"2": ["A8"]}
            },
            "inicial": "A0",
            "finales": ["A8"]
        }
    
    def crear_afd_reducido_binomio(self) -> Dict:
        """
        Crea la estructura de datos para el AFD reducido de (3a+b)^2.
        En este caso es igual al AFD original porque no hay estados equivalentes.
        
        Returns:
            Dict: Estructura del AFD reducido
        """
        return self.crear_afd_subconjuntos_binomio()
    
    def graficar_proceso_completo(self) -> List[str]:
        """
        Grafica el proceso completo: AFN-epsilon → AFD → AFD reducido.
        
        Returns:
            List[str]: Lista de rutas de archivos generados
        """
        print("=" * 80)
        print("GENERANDO GRAFICOS DEL PROCESO COMPLETO")
        print("=" * 80)
        
        archivos_generados = []
        
        # 1. AFN-epsilon
        print("\n1. Generando AFN-epsilon (Thompson)...")
        afn_e = self.crear_afn_epsilon_binomio()
        archivo_afn = self.graficar_automata(afn_e, "AFN_epsilon_binomio", eps=True)
        if archivo_afn:
            archivos_generados.append(archivo_afn)
        
        # 2. AFD (subconjuntos)
        print("\n2. Generando AFD (metodo de subconjuntos)...")
        afd = self.crear_afd_subconjuntos_binomio()
        archivo_afd = self.graficar_automata(afd, "AFD_subconjuntos_binomio")
        if archivo_afd:
            archivos_generados.append(archivo_afd)
        
        # 3. AFD reducido
        print("\n3. Generando AFD reducido (metodo de particiones)...")
        afd_reducido = self.crear_afd_reducido_binomio()
        archivo_reducido = self.graficar_automata(afd_reducido, "AFD_reducido_binomio")
        if archivo_reducido:
            archivos_generados.append(archivo_reducido)
        
        return archivos_generados
    
    def mostrar_informacion_automatas(self):
        """
        Muestra información detallada de cada autómata.
        """
        print("\n" + "=" * 80)
        print("INFORMACION DE LOS AUTOMATAS")
        print("=" * 80)
        
        # AFN-epsilon
        afn_e = self.crear_afn_epsilon_binomio()
        print(f"\nAFN-epsilon (Thompson):")
        print(f"  Estados: {len(afn_e['estados'])}")
        print(f"  Alfabeto: {afn_e['alfabeto']}")
        print(f"  Estado inicial: {afn_e['inicial']}")
        print(f"  Estados finales: {afn_e['finales']}")
        print(f"  Transiciones epsilon: SI")
        
        # AFD
        afd = self.crear_afd_subconjuntos_binomio()
        print(f"\nAFD (metodo de subconjuntos):")
        print(f"  Estados: {len(afd['estados'])}")
        print(f"  Alfabeto: {afd['alfabeto']}")
        print(f"  Estado inicial: {afd['inicial']}")
        print(f"  Estados finales: {afd['finales']}")
        print(f"  Transiciones epsilon: NO")
        
        # AFD reducido
        afd_reducido = self.crear_afd_reducido_binomio()
        print(f"\nAFD reducido (metodo de particiones):")
        print(f"  Estados: {len(afd_reducido['estados'])}")
        print(f"  Alfabeto: {afd_reducido['alfabeto']}")
        print(f"  Estado inicial: {afd_reducido['inicial']}")
        print(f"  Estados finales: {afd_reducido['finales']}")
        print(f"  Transiciones epsilon: NO")
        print(f"  Reduccion: 0 estados (ya es minimo)")
    
    def crear_comparacion_visual(self):
        """
        Crea un gráfico comparativo de los tres autómatas.
        """
        print("\n" + "=" * 80)
        print("CREANDO COMPARACION VISUAL")
        print("=" * 80)
        
        # Crear gráfico comparativo
        g = Digraph('Comparacion_Automatas', format=self.formato)
        g.attr(rankdir='TB', size='16,12')
        g.attr('node', fontname='Arial', fontsize='14', fontweight='bold')
        g.attr('edge', fontname='Arial', fontsize='12')
        
        # Título
        g.attr('node', shape='plaintext', fontsize='20')
        g.node('titulo', 'Proceso Completo: (3a+b)^2')
        
        # Subgrafos para cada autómata
        with g.subgraph(name='cluster_afn') as c:
            c.attr(style='filled', color='lightblue', label='AFN-epsilon (Thompson)')
            c.attr('node', shape='circle', fillcolor='lightblue', style='filled')
            c.node('q0_afn', 'q0')
            c.node('q15_afn', 'q15')
            c.attr('node', shape='doublecircle', fillcolor='lightgreen', style='filled')
            c.node('q15_final', 'q15')
            c.edge('q0_afn', 'q15_afn', label='(3a+b)^2', style='dashed')
        
        with g.subgraph(name='cluster_afd') as c:
            c.attr(style='filled', color='lightyellow', label='AFD (Subconjuntos)')
            c.attr('node', shape='circle', fillcolor='lightyellow', style='filled')
            c.node('A0_afd', 'A0')
            c.node('A8_afd', 'A8')
            c.attr('node', shape='doublecircle', fillcolor='lightgreen', style='filled')
            c.node('A8_final', 'A8')
            c.edge('A0_afd', 'A8_afd', label='(3a+b)^2', style='solid')
        
        with g.subgraph(name='cluster_reducido') as c:
            c.attr(style='filled', color='lightcoral', label='AFD Reducido (Particiones)')
            c.attr('node', shape='circle', fillcolor='lightcoral', style='filled')
            c.node('A0_red', 'A0')
            c.node('A8_red', 'A8')
            c.attr('node', shape='doublecircle', fillcolor='lightgreen', style='filled')
            c.node('A8_red_final', 'A8')
            c.edge('A0_red', 'A8_red', label='(3a+b)^2', style='solid')
        
        # Flechas de proceso
        g.edge('cluster_afn', 'cluster_afd', label='Metodo de Subconjuntos', style='bold', color='blue')
        g.edge('cluster_afd', 'cluster_reducido', label='Metodo de Particiones', style='bold', color='red')
        
        # Exportar
        try:
            ruta_archivo = g.render(filename='Comparacion_Automatas', cleanup=True)
            print(f"Comparacion visual generada: Comparacion_Automatas.{self.formato}")
            return ruta_archivo
        except Exception as e:
            print(f"Error al generar comparacion: {e}")
            return ""
