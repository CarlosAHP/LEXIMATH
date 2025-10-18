"""
Interfaz gráfica para el Sistema de Automatas Finitos.
Implementa el proceso completo: AFN-epsilon -> AFD -> AFD reducido con visualización.
Incluye analizador léxico, validador de expresiones algebraicas y tablas de transiciones.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sys
import os
import re
import subprocess
from datetime import datetime

# Agregar el directorio padre al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.automata.constructor_afn_literal import ConstructorAFNLiteral
from src.automata.conversor_afn_afd_subconjuntos import ConversorAFNAFDSubconjuntos
from src.automata.minimizador_afd_particiones import MinimizadorAFDParticiones
from src.automata.visualizador_automatas import VisualizadorAutomatas


class ValidadorExpresionesAlgebraicas:
    """Validador completo de expresiones algebraicas."""
    
    def __init__(self):
        # Definir tokens con expresiones regulares
        self.TOKENS = [
            ("NUM",   r"[0-9]+"),
            ("VAR",   r"[a-zA-Z]"),
            ("PLUS",  r"\+"),
            ("MINUS", r"-"),
            ("MUL",   r"\*"),
            ("DIV",   r"/"),
            ("POW",   r"\^"),
            ("LPAR",  r"\("),
            ("RPAR",  r"\)"),
            ("SPACE", r"\s+"),
        ]
    
    def lexer(self, expr):
        """Analizador léxico - convierte cadena en tokens."""
        tokens = []
        i = 0
        while i < len(expr):
            match = None
            for token_type, pattern in self.TOKENS:
                regex = re.compile(pattern)
                match = regex.match(expr, i)
                if match:
                    text = match.group(0)
                    if token_type != "SPACE":  # ignorar espacios
                        tokens.append((token_type, text, i))
                    i = match.end(0)
                    break
            if not match:
                raise ValueError(f"Error léxico en posición {i}: '{expr[i]}' no es válido")
        return tokens
    
    def parser(self, tokens):
        """Analizador sintáctico - valida orden correcto de tokens."""
        stack = []
        last_type = None
        
        for tok_type, tok_val, pos in tokens:
            if tok_type == "LPAR":
                stack.append(tok_type)
            elif tok_type == "RPAR":
                if not stack:
                    raise ValueError("Paréntesis de cierre sin apertura")
                stack.pop()
            elif tok_type in ("PLUS", "MINUS", "MUL", "DIV", "POW"):
                if last_type in (None, "PLUS", "MINUS", "MUL", "DIV", "POW", "LPAR"):
                    raise ValueError("Operador mal ubicado")
            elif tok_type in ("NUM", "VAR"):
                # Permitir NUM seguido de VAR (multiplicación implícita como 3a)
                # Permitir VAR seguido de NUM (multiplicación implícita como a3)
                # Permitir NUM seguido de NUM (números consecutivos como 12)
                if last_type in ("NUM", "VAR", "RPAR"):
                    # Solo dar error si es realmente inválido (dos variables consecutivas sin operador)
                    if last_type == "VAR" and tok_type == "VAR":
                        raise ValueError("Falta operador entre variables")
                    # Permitir multiplicación implícita: 3a, a3, etc.
                    pass
            last_type = tok_type
        
        if stack:
            raise ValueError("Paréntesis sin cerrar")
        return True
    
    def validar_expresion(self, expr):
        """Valida una expresión algebraica completa."""
        try:
            # Análisis léxico
            tokens = self.lexer(expr)
            
            # Análisis sintáctico
            self.parser(tokens)
            
            return True, tokens, "Expresión válida"
            
        except ValueError as e:
            return False, [], str(e)


class AnalizadorLexico:
    """Analizador léxico para expresiones algebraicas."""
    
    def __init__(self):
        self.tokens = []
        self.errores = []
    
    def analizar(self, expresion):
        """Analiza una expresión algebraica y extrae tokens."""
        self.tokens = []
        self.errores = []
        
        # Patrones de regex para diferentes tipos de tokens
        patrones = [
            (r'\d+', 'NUMERO'),
            (r'[a-zA-Z]', 'VARIABLE'),
            (r'\+', 'SUMA'),
            (r'-', 'RESTA'),
            (r'\*', 'MULTIPLICACION'),
            (r'/', 'DIVISION'),
            (r'\^', 'EXPONENTE'),
            (r'\(', 'PARENTESIS_IZQ'),
            (r'\)', 'PARENTESIS_DER'),
            (r'\s+', 'ESPACIO')
        ]
        
        posicion = 0
        while posicion < len(expresion):
            encontrado = False
            
            for patron, tipo in patrones:
                match = re.match(patron, expresion[posicion:])
                if match:
                    valor = match.group()
                    if tipo != 'ESPACIO':  # Ignorar espacios
                        self.tokens.append({
                            'tipo': tipo,
                            'valor': valor,
                            'posicion': posicion
                        })
                    posicion += len(valor)
                    encontrado = True
                    break
            
            if not encontrado:
                self.errores.append(f"Caracter no reconocido: '{expresion[posicion]}' en posicion {posicion}")
                posicion += 1
        
        return self.tokens
    
    def generar_regex(self):
        """Genera una expresión regular a partir de los tokens."""
        regex_parts = []
        
        for token in self.tokens:
            if token['tipo'] == 'NUMERO':
                regex_parts.append(r'\d+')
            elif token['tipo'] == 'VARIABLE':
                regex_parts.append(r'[a-zA-Z]')
            elif token['tipo'] == 'SUMA':
                regex_parts.append(r'\+')
            elif token['tipo'] == 'RESTA':
                regex_parts.append(r'-')
            elif token['tipo'] == 'MULTIPLICACION':
                regex_parts.append(r'\*')
            elif token['tipo'] == 'DIVISION':
                regex_parts.append(r'/')
            elif token['tipo'] == 'EXPONENTE':
                regex_parts.append(r'\^')
            elif token['tipo'] == 'PARENTESIS_IZQ':
                regex_parts.append(r'\(')
            elif token['tipo'] == 'PARENTESIS_DER':
                regex_parts.append(r'\)')
        
        return ''.join(regex_parts)
    
    def obtener_errores(self):
        """Retorna la lista de errores."""
        return self.errores


class ProcesadorCompleto:
    """Procesador completo que maneja todo el pipeline de autómatas."""
    
    def __init__(self):
        self.constructor_afn = ConstructorAFNLiteral()
        self.conversor_afn_afd = ConversorAFNAFDSubconjuntos()
        self.minimizador_afd = MinimizadorAFDParticiones()
        self.visualizador = VisualizadorAutomatas()
    
    def procesar_expresion(self, expresion):
        """Procesa una expresión completa: AFN-epsilon -> AFD -> AFD reducido."""
        try:
            # 1. Crear AFN-epsilon usando Thompson para la cadena literal
            afn_e = self._crear_afn_epsilon_thompson(expresion)
            
            # 2. Convertir AFN-epsilon a AFD usando subconjuntos
            afd = self._convertir_afn_a_afd(afn_e)
            
            # 3. Minimizar AFD
            afd_reducido = self._minimizar_afd(afd)
            
            return {
                'afn_e': afn_e,
                'afd': afd,
                'afd_reducido': afd_reducido,
                'expresion': expresion
            }
            
        except Exception as e:
            raise Exception(f"Error en el procesamiento: {str(e)}")
    
    def _crear_afn_epsilon_thompson(self, expresion):
        """Crea AFN-epsilon usando el algoritmo de Thompson para cadena literal."""
        estados = []
        transiciones = {}
        alfabeto = []
        
        # Crear estados: q0, q1, q2, ..., q(2n) para n símbolos
        # Patrón: n símbolos = 2n estados
        num_estados = 2 * len(expresion)
        for i in range(num_estados):
            estados.append(f"q{i}")
        
        # Estado inicial y final
        estado_inicial = "q0"
        estados_finales = [f"q{num_estados - 1}"]
        
        # Crear transiciones según Thompson
        for i, simbolo in enumerate(expresion):
            # Para cada símbolo: q(2i) --simbolo--> q(2i+1) --epsilon--> q(2i+2)
            estado_actual = f"q{2*i}"
            estado_intermedio = f"q{2*i + 1}"
            estado_siguiente = f"q{2*i + 2}"
            
            # Transición por símbolo
            if estado_actual not in transiciones:
                transiciones[estado_actual] = {}
            transiciones[estado_actual][simbolo] = [estado_intermedio]
            
            # Transición epsilon
            if estado_intermedio not in transiciones:
                transiciones[estado_intermedio] = {}
            transiciones[estado_intermedio]['ε'] = [estado_siguiente]
            
            # Agregar al alfabeto en orden
            if simbolo not in alfabeto:
                alfabeto.append(simbolo)
        
        return {
            'estados': estados,
            'inicial': estado_inicial,
            'finales': estados_finales,
            'transiciones': transiciones,
            'alfabeto': alfabeto
        }
    
    def _convertir_afn_a_afd(self, afn_e):
        """Convierte AFN-epsilon a AFD usando el método de subconjuntos."""
        # Calcular ε-cerraduras
        epsilon_cerraduras = self._calcular_epsilon_cerraduras(afn_e)
        
        # Estado inicial del AFD = ε-cerradura(q0)
        estado_inicial_afn = afn_e['inicial']
        estado_inicial_afd = epsilon_cerraduras[estado_inicial_afn]
        
        # Crear estados AFD usando el método de subconjuntos
        estados_afd = []
        transiciones_afd = {}
        alfabeto = afn_e['alfabeto'].copy()
        
        # Mapeo de conjuntos de estados AFN a estados AFD
        conjunto_a_estado = {}
        estado_a_conjunto = {}
        
        # Estado inicial
        conjunto_inicial = tuple(sorted(estado_inicial_afd))
        conjunto_a_estado[conjunto_inicial] = "A0"
        estado_a_conjunto["A0"] = conjunto_inicial
        estados_afd.append("A0")
        
        # Procesar estados pendientes
        pendientes = [conjunto_inicial]
        contador_estados = 1
        
        while pendientes:
            conjunto_actual = pendientes.pop(0)
            estado_afd_actual = conjunto_a_estado[conjunto_actual]
            
            if estado_afd_actual not in transiciones_afd:
                transiciones_afd[estado_afd_actual] = {}
            
            # Para cada símbolo del alfabeto
            for simbolo in alfabeto:
                # Calcular move(conjunto_actual, simbolo)
                estados_destino = set()
                for estado_afn in conjunto_actual:
                    if estado_afn in afn_e['transiciones'] and simbolo in afn_e['transiciones'][estado_afn]:
                        estados_destino.update(afn_e['transiciones'][estado_afn][simbolo])
                
                if estados_destino:
                    # Aplicar ε-cerradura al resultado
                    conjunto_destino = set()
                    for estado in estados_destino:
                        conjunto_destino.update(epsilon_cerraduras[estado])
                    
                    conjunto_destino_tuple = tuple(sorted(conjunto_destino))
                    
                    # Si es un nuevo conjunto, crear nuevo estado AFD
                    if conjunto_destino_tuple not in conjunto_a_estado:
                        nuevo_estado = f"A{contador_estados}"
                        conjunto_a_estado[conjunto_destino_tuple] = nuevo_estado
                        estado_a_conjunto[nuevo_estado] = conjunto_destino_tuple
                        estados_afd.append(nuevo_estado)
                        pendientes.append(conjunto_destino_tuple)
                        contador_estados += 1
                    
                    # Agregar transición
                    estado_destino = conjunto_a_estado[conjunto_destino_tuple]
                    transiciones_afd[estado_afd_actual][simbolo] = [estado_destino]
        
        # Determinar estados finales
        estados_finales_afd = []
        for estado_afd in estados_afd:
            conjunto_estados = estado_a_conjunto[estado_afd]
            # Si el conjunto contiene algún estado final del AFN-ε
            if any(estado in afn_e['finales'] for estado in conjunto_estados):
                estados_finales_afd.append(estado_afd)
        
        return {
            'estados': estados_afd,
            'inicial': "A0",
            'finales': estados_finales_afd,
            'transiciones': transiciones_afd,
            'alfabeto': alfabeto
        }
    
    def _calcular_epsilon_cerraduras(self, afn_e):
        """Calcula las ε-cerraduras para todos los estados del AFN-ε."""
        epsilon_cerraduras = {}
        
        for estado in afn_e['estados']:
            cerradura = {estado}
            pendientes = [estado]
            
            while pendientes:
                estado_actual = pendientes.pop(0)
                if estado_actual in afn_e['transiciones'] and 'ε' in afn_e['transiciones'][estado_actual]:
                    for estado_destino in afn_e['transiciones'][estado_actual]['ε']:
                        if estado_destino not in cerradura:
                            cerradura.add(estado_destino)
                            pendientes.append(estado_destino)
            
            epsilon_cerraduras[estado] = cerradura
        
        return epsilon_cerraduras
    
    def _minimizar_afd(self, afd):
        """Minimiza el AFD usando el método de particiones."""
        # Algoritmo de minimización por particiones
        
        # Paso 1: Partición inicial - separar finales de no finales
        estados_finales = set(afd['finales'])
        estados_no_finales = set(afd['estados']) - estados_finales
        
        # Partición inicial
        particion_actual = [list(estados_no_finales), list(estados_finales)]
        particion_actual = [grupo for grupo in particion_actual if grupo]  # Eliminar grupos vacíos
        
        # Paso 2: Refinamiento iterativo
        cambio = True
        while cambio:
            cambio = False
            nueva_particion = []
            
            for grupo in particion_actual:
                if len(grupo) <= 1:
                    # Grupo con un solo estado no se puede dividir
                    nueva_particion.append(grupo)
                    continue
                
                # Dividir el grupo según las transiciones
                subgrupos = {}
                for estado in grupo:
                    # Crear clave basada en las transiciones del estado
                    clave = []
                    for simbolo in afd['alfabeto']:
                        if estado in afd['transiciones'] and simbolo in afd['transiciones'][estado]:
                            destino = afd['transiciones'][estado][simbolo][0]
                            # Encontrar a qué grupo pertenece el destino
                            grupo_destino = None
                            for i, g in enumerate(particion_actual):
                                if destino in g:
                                    grupo_destino = i
                                    break
                            clave.append(grupo_destino)
                        else:
                            clave.append(None)  # Sin transición
                    
                    clave_tuple = tuple(clave)
                    if clave_tuple not in subgrupos:
                        subgrupos[clave_tuple] = []
                    subgrupos[clave_tuple].append(estado)
                
                # Agregar subgrupos a la nueva partición
                for subgrupo in subgrupos.values():
                    nueva_particion.append(subgrupo)
                    if len(subgrupo) < len(grupo):
                        cambio = True
            
            particion_actual = nueva_particion
        
        # Paso 3: Crear AFD reducido
        if len(particion_actual) == len(afd['estados']):
            # No hay reducción posible
            return afd.copy()
        
        # Crear mapeo de estados originales a estados reducidos
        estado_a_grupo = {}
        for i, grupo in enumerate(particion_actual):
            for estado in grupo:
                estado_a_grupo[estado] = f"A{i}"
        
        # Crear AFD reducido
        estados_reducidos = [f"A{i}" for i in range(len(particion_actual))]
        transiciones_reducidas = {}
        
        for i, grupo in enumerate(particion_actual):
            estado_reducido = f"A{i}"
            transiciones_reducidas[estado_reducido] = {}
            
            # Usar el primer estado del grupo como representante
            estado_representante = grupo[0]
            
            for simbolo in afd['alfabeto']:
                if estado_representante in afd['transiciones'] and simbolo in afd['transiciones'][estado_representante]:
                    destino_original = afd['transiciones'][estado_representante][simbolo][0]
                    destino_reducido = estado_a_grupo[destino_original]
                    transiciones_reducidas[estado_reducido][simbolo] = [destino_reducido]
        
        # Determinar estados finales reducidos
        finales_reducidos = []
        for i, grupo in enumerate(particion_actual):
            if any(estado in afd['finales'] for estado in grupo):
                finales_reducidos.append(f"A{i}")
        
        # Estado inicial reducido
        inicial_reducido = estado_a_grupo[afd['inicial']]
        
        return {
            'estados': estados_reducidos,
            'inicial': inicial_reducido,
            'finales': finales_reducidos,
            'transiciones': transiciones_reducidas,
            'alfabeto': afd['alfabeto']
        }


class InterfazAutomatas:
    """Interfaz gráfica principal del sistema de autómatas finitos."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Sistema de Automatas Finitos - AFN-epsilon -> AFD -> AFD reducido")
        self.root.geometry("1800x1000")
        self.root.configure(bg='#f0f0f0')
        
        # Configurar PATH de Graphviz
        os.environ['PATH'] += os.pathsep + r'C:\Program Files\Graphviz\bin'
        
        # Inicializar componentes
        self.analizador = AnalizadorLexico()
        self.validador = ValidadorExpresionesAlgebraicas()
        self.procesador = ProcesadorCompleto()
        
        # Variables
        self.cadena_actual = ""
        self.tokens_actuales = []
        self.regex_generado = ""
        self.resultados_completos = None
        self.carpeta_resultados = ""
        
        self._crear_interfaz()
    
    def _crear_interfaz(self):
        """Crea la interfaz gráfica."""
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=2)  # Panel central más ancho
        main_frame.columnconfigure(2, weight=1)  # Panel derecho
        main_frame.rowconfigure(3, weight=1)
        
        # Título
        titulo = ttk.Label(main_frame, text="Sistema de Automatas Finitos", 
                          font=('Arial', 18, 'bold'))
        titulo.grid(row=0, column=0, columnspan=3, pady=(0, 10))
        
        subtitulo = ttk.Label(main_frame, text="Proceso completo: Validación -> Analizador Léxico -> AFN-epsilon -> AFD -> AFD reducido", 
                             font=('Arial', 12))
        subtitulo.grid(row=1, column=0, columnspan=3, pady=(0, 20))
        
        # Frame de entrada
        self._crear_frame_entrada(main_frame)
        
        # Frame de analizador léxico (más angosto)
        self._crear_frame_lexico(main_frame)
        
        # Frame de resultados con tablas
        self._crear_frame_resultados(main_frame)
        
        # Frame de visualización
        self._crear_frame_visualizacion(main_frame)
        
        # Frame de botones
        self._crear_frame_botones(main_frame)
    
    def _crear_frame_entrada(self, parent):
        """Crea el frame de entrada de datos."""
        frame_entrada = ttk.LabelFrame(parent, text="Entrada de Expresión Algebraica", padding="10")
        frame_entrada.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        frame_entrada.columnconfigure(1, weight=1)
        
        # Etiqueta y campo de entrada
        ttk.Label(frame_entrada, text="Expresión:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.entrada_cadena = tk.StringVar()
        self.campo_entrada = ttk.Entry(frame_entrada, textvariable=self.entrada_cadena, 
                                      font=('Arial', 12), width=50)
        self.campo_entrada.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        self.campo_entrada.bind('<Return>', lambda e: self.procesar_cadena())
        
        # Botón de procesamiento
        ttk.Button(frame_entrada, text="Procesar", 
                  command=self.procesar_cadena).grid(row=0, column=2)
        
        # Ejemplos
        ttk.Label(frame_entrada, text="Ejemplos:", font=('Arial', 10, 'bold')).grid(row=1, column=0, 
                                                                                    sticky=tk.W, pady=(10, 5))
        
        ejemplos = [
            "2a+3b",
            "(3a+b)^2",
            "x^2+y^2",
            "a*b+c"
        ]
        
        for i, ejemplo in enumerate(ejemplos):
            btn_ejemplo = ttk.Button(frame_entrada, text=ejemplo, 
                                   command=lambda e=ejemplo: self.cargar_ejemplo(e))
            btn_ejemplo.grid(row=2, column=i, padx=5, pady=5)
    
    def _crear_frame_lexico(self, parent):
        """Crea el frame del analizador léxico (más angosto)."""
        frame_lexico = ttk.LabelFrame(parent, text="Analizador Léxico", padding="10")
        frame_lexico.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), 
                         padx=(0, 10))
        frame_lexico.columnconfigure(0, weight=1)
        frame_lexico.rowconfigure(1, weight=1)
        
        # Información del análisis léxico
        self.label_lexico = ttk.Label(frame_lexico, text="Ingrese una expresión para analizar", 
                                     font=('Arial', 10))
        self.label_lexico.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Área de texto para tokens y regex (más angosta)
        self.texto_lexico = scrolledtext.ScrolledText(frame_lexico, height=20, width=40,
                                                      font=('Courier', 9))
        self.texto_lexico.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
    
    def _crear_frame_resultados(self, parent):
        """Crea el frame de resultados con tablas."""
        frame_resultados = ttk.LabelFrame(parent, text="Resultados y Tablas de Transiciones", padding="10")
        frame_resultados.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        frame_resultados.columnconfigure(0, weight=1)
        frame_resultados.rowconfigure(1, weight=1)
        
        # Información del procesamiento
        self.label_info = ttk.Label(frame_resultados, text="Resultados del procesamiento", 
                                   font=('Arial', 10))
        self.label_info.grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        # Área de texto para resultados y tablas
        self.texto_resultados = scrolledtext.ScrolledText(frame_resultados, height=20, width=80,
                                                         font=('Courier', 9))
        self.texto_resultados.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(5, 0))
    
    def _crear_frame_visualizacion(self, parent):
        """Crea el frame de visualización."""
        frame_viz = ttk.LabelFrame(parent, text="Visualización de Automatas", padding="10")
        frame_viz.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        frame_viz.columnconfigure(0, weight=1)
        
        # Botones para mostrar diagramas
        ttk.Button(frame_viz, text="Generar Graficos PNG", 
                  command=self.generar_graficos).grid(row=0, column=0, pady=5)
        
        ttk.Button(frame_viz, text="Mostrar AFN-epsilon", 
                  command=lambda: self.mostrar_diagrama('afn')).grid(row=0, column=1, pady=5, padx=5)
        
        ttk.Button(frame_viz, text="Mostrar AFD", 
                  command=lambda: self.mostrar_diagrama('afd')).grid(row=0, column=2, pady=5, padx=5)
        
        ttk.Button(frame_viz, text="Mostrar AFD Reducido", 
                  command=lambda: self.mostrar_diagrama('afd_reducido')).grid(row=0, column=3, pady=5, padx=5)
        
        # Canvas para matplotlib
        self.canvas_frame = ttk.Frame(frame_viz)
        self.canvas_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        self.canvas_frame.columnconfigure(0, weight=1)
        self.canvas_frame.rowconfigure(0, weight=1)
    
    def _crear_frame_botones(self, parent):
        """Crea el frame de botones de control."""
        frame_botones = ttk.Frame(parent)
        frame_botones.grid(row=5, column=0, columnspan=3, pady=(20, 0))
        
        ttk.Button(frame_botones, text="Limpiar", 
                  command=self.limpiar_resultados).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(frame_botones, text="Guardar Resultados", 
                  command=self.guardar_resultados).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(frame_botones, text="Abrir Carpeta Resultados", 
                  command=self.abrir_carpeta).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(frame_botones, text="Demo Completo", 
                  command=self.ejecutar_demo).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(frame_botones, text="Salir", 
                  command=self.root.quit).pack(side=tk.RIGHT)
    
    def cargar_ejemplo(self, ejemplo):
        """Carga un ejemplo en el campo de entrada."""
        self.entrada_cadena.set(ejemplo)
        self.procesar_cadena()
    
    def procesar_cadena(self):
        """Procesa la cadena ingresada."""
        cadena = self.entrada_cadena.get().strip()
        
        if not cadena:
            messagebox.showwarning("Advertencia", "Por favor ingrese una expresión.")
            return
        
        try:
            # 1. Validación de expresión algebraica
            es_valida, tokens_validacion, mensaje_validacion = self.validador.validar_expresion(cadena)
            
            if not es_valida:
                messagebox.showerror("Error de Validación", f"Expresión inválida: {mensaje_validacion}")
                return
            
            self.cadena_actual = cadena
            
            # 2. Análisis léxico
            self.tokens_actuales = self.analizador.analizar(cadena)
            self.regex_generado = self.analizador.generar_regex()
            
            # 3. Procesamiento completo de autómatas
            self.resultados_completos = self.procesador.procesar_expresion(cadena)
            
            # 4. Crear carpeta de resultados
            self._crear_carpeta_resultados()
            
            # 5. Mostrar resultados
            self._mostrar_resultados_completos(cadena)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante el procesamiento: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _crear_carpeta_resultados(self):
        """Crea una carpeta con el nombre de la expresión."""
        # Limpiar nombre de la expresión para usar como nombre de carpeta
        nombre_carpeta = re.sub(r'[^\w\-_\.]', '_', self.cadena_actual)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.carpeta_resultados = f"resultados_{nombre_carpeta}_{timestamp}"
        
        if not os.path.exists(self.carpeta_resultados):
            os.makedirs(self.carpeta_resultados)
    
    def _mostrar_resultados_completos(self, cadena):
        """Muestra los resultados del procesamiento completo."""
        # Limpiar áreas de texto
        self.texto_lexico.delete(1.0, tk.END)
        self.texto_resultados.delete(1.0, tk.END)
        
        # 1. Mostrar análisis léxico
        self._mostrar_analisis_lexico(cadena)
        
        # 2. Mostrar resultados de autómatas con tablas
        self._mostrar_resultados_automatas_con_tablas(cadena)
        
        # 3. Actualizar información general
        afn_e = self.resultados_completos['afn_e']
        afd = self.resultados_completos['afd']
        afd_reducido = self.resultados_completos['afd_reducido']
        
        info_texto = f"Expresión: {cadena} (VÁLIDA)\n"
        info_texto += f"Carpeta: {self.carpeta_resultados}\n"
        info_texto += f"Tokens: {len(self.tokens_actuales)}\n"
        info_texto += f"Estados AFN: {len(afn_e['estados'])} | AFD: {len(afd['estados'])} | AFD_min: {len(afd_reducido['estados'])}\n"
        
        self.label_info.config(text=info_texto, foreground="green")
    
    def _mostrar_analisis_lexico(self, cadena):
        """Muestra el análisis léxico."""
        self.texto_lexico.insert(tk.END, "ANALISIS LEXICO\n")
        self.texto_lexico.insert(tk.END, "=" * 30 + "\n\n")
        
        # Mostrar tokens
        self.texto_lexico.insert(tk.END, "TOKENS:\n")
        self.texto_lexico.insert(tk.END, "-" * 20 + "\n")
        self.texto_lexico.insert(tk.END, f"{'No.':<3} {'Tipo':<12} {'Valor':<8}\n")
        self.texto_lexico.insert(tk.END, "-" * 20 + "\n")
        
        for i, token in enumerate(self.tokens_actuales, 1):
            self.texto_lexico.insert(tk.END, 
                                   f"{i:<3} {token['tipo']:<12} {token['valor']:<8}\n")
        
        # Mostrar regex generado
        self.texto_lexico.insert(tk.END, "\n" + "=" * 30 + "\n")
        self.texto_lexico.insert(tk.END, "REGEX GENERADO:\n")
        self.texto_lexico.insert(tk.END, "=" * 30 + "\n")
        self.texto_lexico.insert(tk.END, f"{self.regex_generado}\n")
        self.texto_lexico.insert(tk.END, f"Longitud: {len(self.regex_generado)}\n")
        
        # Mostrar errores si los hay
        errores = self.analizador.obtener_errores()
        if errores:
            self.texto_lexico.insert(tk.END, "\nERRORES:\n")
            self.texto_lexico.insert(tk.END, "-" * 20 + "\n")
            for error in errores:
                self.texto_lexico.insert(tk.END, f"• {error}\n")
    
    def _mostrar_resultados_automatas_con_tablas(self, cadena):
        """Muestra los resultados de los autómatas con sus tablas de transiciones."""
        afn_e = self.resultados_completos['afn_e']
        afd = self.resultados_completos['afd']
        afd_reducido = self.resultados_completos['afd_reducido']
        
        self.texto_resultados.insert(tk.END, "PROCESAMIENTO DE AUTOMATAS FINITOS\n")
        self.texto_resultados.insert(tk.END, "=" * 80 + "\n\n")
        
        # 1. AFN-epsilon con tabla
        self.texto_resultados.insert(tk.END, "1. AFN-epsilon (Thompson):\n")
        self.texto_resultados.insert(tk.END, "-" * 50 + "\n")
        self.texto_resultados.insert(tk.END, f"Estados: {len(afn_e['estados'])}\n")
        self.texto_resultados.insert(tk.END, f"Alfabeto: {afn_e['alfabeto']}\n")
        self.texto_resultados.insert(tk.END, f"Estado inicial: {afn_e['inicial']}\n")
        self.texto_resultados.insert(tk.END, f"Estados finales: {afn_e['finales']}\n")
        self.texto_resultados.insert(tk.END, f"Transiciones epsilon: SI\n\n")
        
        # Tabla de transiciones AFN-epsilon
        self.texto_resultados.insert(tk.END, "TABLA DE TRANSICIONES AFN-epsilon:\n")
        self._mostrar_tabla_transiciones(afn_e, "AFN-epsilon")
        
        # 2. AFD con tabla
        self.texto_resultados.insert(tk.END, "\n2. AFD (Subconjuntos):\n")
        self.texto_resultados.insert(tk.END, "-" * 50 + "\n")
        self.texto_resultados.insert(tk.END, f"Estados: {len(afd['estados'])}\n")
        self.texto_resultados.insert(tk.END, f"Alfabeto: {afd['alfabeto']}\n")
        self.texto_resultados.insert(tk.END, f"Estado inicial: {afd['inicial']}\n")
        self.texto_resultados.insert(tk.END, f"Estados finales: {afd['finales']}\n")
        self.texto_resultados.insert(tk.END, f"Transiciones epsilon: NO\n\n")
        
        # Tabla de transiciones AFD
        self.texto_resultados.insert(tk.END, "TABLA DE TRANSICIONES AFD:\n")
        self._mostrar_tabla_transiciones(afd, "AFD")
        
        # 3. AFD reducido con tabla
        self.texto_resultados.insert(tk.END, "\n3. AFD Reducido (Particiones):\n")
        self.texto_resultados.insert(tk.END, "-" * 50 + "\n")
        self.texto_resultados.insert(tk.END, f"Estados: {len(afd_reducido['estados'])}\n")
        self.texto_resultados.insert(tk.END, f"Alfabeto: {afd_reducido['alfabeto']}\n")
        self.texto_resultados.insert(tk.END, f"Estado inicial: {afd_reducido['inicial']}\n")
        self.texto_resultados.insert(tk.END, f"Estados finales: {afd_reducido['finales']}\n")
        self.texto_resultados.insert(tk.END, f"Transiciones epsilon: NO\n")
        self.texto_resultados.insert(tk.END, f"Reducción: {len(afd['estados']) - len(afd_reducido['estados'])} estados\n\n")
        
        # Tabla de transiciones AFD reducido
        self.texto_resultados.insert(tk.END, "TABLA DE TRANSICIONES AFD REDUCIDO:\n")
        self._mostrar_tabla_transiciones(afd_reducido, "AFD-Reducido")
        
        # 4. Resumen
        self.texto_resultados.insert(tk.END, "\n4. RESUMEN:\n")
        self.texto_resultados.insert(tk.END, "-" * 50 + "\n")
        self.texto_resultados.insert(tk.END, f"Proceso completado exitosamente\n")
        self.texto_resultados.insert(tk.END, f"Expresión procesada: {cadena}\n")
        self.texto_resultados.insert(tk.END, f"Regex generado: {self.regex_generado}\n")
        self.texto_resultados.insert(tk.END, f"Resultado: ACEPTADA (el AFD reconoce la expresión exacta)\n")
    
    def _mostrar_tabla_transiciones(self, automata, nombre):
        """Muestra la tabla de transiciones de un autómata."""
        # Obtener alfabeto
        alfabeto = automata['alfabeto']
        estados = automata['estados']
        
        # Crear encabezado
        header = f"{'Estado':<8}"
        for simbolo in alfabeto:
            header += f"{simbolo:<8}"
        if nombre == "AFN-epsilon":
            header += "ε"
        
        self.texto_resultados.insert(tk.END, header + "\n")
        self.texto_resultados.insert(tk.END, "-" * len(header) + "\n")
        
        # Mostrar filas
        for estado in estados:
            fila = f"{estado:<8}"
            for simbolo in alfabeto:
                if estado in automata['transiciones'] and simbolo in automata['transiciones'][estado]:
                    destinos = automata['transiciones'][estado][simbolo]
                    fila += f"{str(destinos):<8}"
                else:
                    fila += "∅      "
            
            # Mostrar transiciones epsilon para AFN-epsilon
            if nombre == "AFN-epsilon" and estado in automata['transiciones'] and 'ε' in automata['transiciones'][estado]:
                fila += str(automata['transiciones'][estado]['ε'])
            
            self.texto_resultados.insert(tk.END, fila + "\n")
    
    def generar_graficos(self):
        """Genera los gráficos PNG de los autómatas."""
        if not self.cadena_actual or not self.resultados_completos:
            messagebox.showwarning("Advertencia", "No hay expresión procesada para generar gráficos.")
            return
        
        try:
            # Cambiar al directorio de resultados
            directorio_original = os.getcwd()
            os.chdir(self.carpeta_resultados)
            
            # Generar gráficos usando el visualizador
            afn_e = self.resultados_completos['afn_e']
            afd = self.resultados_completos['afd']
            afd_reducido = self.resultados_completos['afd_reducido']
            
            # Generar gráficos individuales
            archivos = []
            
            # AFN-epsilon
            archivo_afn = self.procesador.visualizador.graficar_automata(afn_e, "AFN_epsilon", eps=True)
            if archivo_afn:
                archivos.append(archivo_afn)
            
            # AFD
            archivo_afd = self.procesador.visualizador.graficar_automata(afd, "AFD_subconjuntos")
            if archivo_afd:
                archivos.append(archivo_afd)
            
            # AFD reducido
            archivo_afd_red = self.procesador.visualizador.graficar_automata(afd_reducido, "AFD_reducido")
            if archivo_afd_red:
                archivos.append(archivo_afd_red)
            
            # Volver al directorio original
            os.chdir(directorio_original)
            
            mensaje = f"Gráficos generados en carpeta: {self.carpeta_resultados}\n\n"
            mensaje += "Archivos generados:\n"
            for i, archivo in enumerate(archivos, 1):
                mensaje += f"{i}. {archivo}\n"
            
            messagebox.showinfo("Éxito", mensaje)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al generar gráficos: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def mostrar_diagrama(self, tipo):
        """Muestra un diagrama específico."""
        if not self.cadena_actual or not self.resultados_completos:
            messagebox.showwarning("Advertencia", "No hay expresión procesada para mostrar diagrama.")
            return
        
        try:
            # Limpiar canvas anterior
            for widget in self.canvas_frame.winfo_children():
                widget.destroy()
            
            # Obtener autómata según el tipo
            if tipo == 'afn':
                automata = self.resultados_completos['afn_e']
                titulo = "AFN-epsilon (Thompson)"
            elif tipo == 'afd':
                automata = self.resultados_completos['afd']
                titulo = "AFD (Subconjuntos)"
            elif tipo == 'afd_reducido':
                automata = self.resultados_completos['afd_reducido']
                titulo = "AFD Reducido (Particiones)"
            else:
                raise ValueError(f"Tipo de diagrama desconocido: {tipo}")
            
            # Crear figura simple con matplotlib
            fig, ax = plt.subplots(figsize=(12, 8))
            ax.set_title(titulo, fontsize=14, fontweight='bold')
            
            # Información del autómata
            info_text = f"Estados: {len(automata['estados'])}\n"
            info_text += f"Alfabeto: {automata['alfabeto']}\n"
            info_text += f"Estado inicial: {automata['inicial']}\n"
            info_text += f"Estados finales: {automata['finales']}\n"
            info_text += f"Transiciones epsilon: {'SI' if tipo == 'afn' else 'NO'}"
            
            ax.text(0.5, 0.5, info_text, ha='center', va='center', fontsize=12, 
                   bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue"))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Crear canvas de matplotlib
            canvas = FigureCanvasTkAgg(fig, self.canvas_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al mostrar diagrama {tipo}: {str(e)}")
    
    def abrir_carpeta(self):
        """Abre la carpeta de resultados."""
        if self.carpeta_resultados and os.path.exists(self.carpeta_resultados):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(self.carpeta_resultados)
                else:  # Linux/Mac
                    subprocess.run(['xdg-open', self.carpeta_resultados])
            except Exception as e:
                messagebox.showerror("Error", f"Error al abrir carpeta: {str(e)}")
        else:
            messagebox.showwarning("Advertencia", "No hay carpeta de resultados para abrir.")
    
    def ejecutar_demo(self):
        """Ejecuta el demo completo."""
        try:
            import subprocess
            subprocess.run(["python", "demo_final_limpio.py"], check=True)
        except Exception as e:
            messagebox.showerror("Error", f"Error al ejecutar demo: {str(e)}")
    
    def limpiar_resultados(self):
        """Limpia todos los resultados."""
        self.entrada_cadena.set("")
        self.texto_lexico.delete(1.0, tk.END)
        self.texto_resultados.delete(1.0, tk.END)
        self.label_info.config(text="Resultados del procesamiento", foreground="black")
        self.label_lexico.config(text="Ingrese una expresión para analizar", foreground="black")
        
        # Limpiar canvas
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
        
        self.cadena_actual = ""
        self.tokens_actuales = []
        self.regex_generado = ""
        self.resultados_completos = None
        self.carpeta_resultados = ""
    
    def guardar_resultados(self):
        """Guarda los resultados en un archivo."""
        if not self.cadena_actual:
            messagebox.showwarning("Advertencia", "No hay resultados para guardar.")
            return
        
        archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        
        if archivo:
            try:
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write("ANALISIS COMPLETO DE AUTOMATAS FINITOS\n")
                    f.write("=" * 50 + "\n\n")
                    f.write(f"Expresión: {self.cadena_actual}\n")
                    f.write(f"Regex: {self.regex_generado}\n")
                    f.write(f"Carpeta: {self.carpeta_resultados}\n")
                    f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    f.write("ANALISIS LEXICO:\n")
                    f.write("-" * 30 + "\n")
                    f.write(self.texto_lexico.get(1.0, tk.END))
                    
                    f.write("\n\nRESULTADOS DE AUTOMATAS:\n")
                    f.write("-" * 30 + "\n")
                    f.write(self.texto_resultados.get(1.0, tk.END))
                
                messagebox.showinfo("Éxito", f"Resultados guardados en: {archivo}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")
    
    def ejecutar(self):
        """Ejecuta la interfaz gráfica."""
        self.root.mainloop()

def main():
    """Función principal para ejecutar la interfaz."""
    app = InterfazAutomatas()
    app.ejecutar()

if __name__ == "__main__":
    main()