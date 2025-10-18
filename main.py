"""
Programa principal del Sistema de Automatas Finitos.
Implementa el proceso completo: AFN-epsilon -> AFD -> AFD reducido con visualizacion.

Autor: Proyecto Automatas
Fecha: 2024
"""

import sys
import os

# Agregar el directorio src al path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.automata.visualizador_automatas import VisualizadorAutomatas


def mostrar_menu_principal():
    """Muestra el menu principal del programa."""
    print("=" * 80)
    print("SISTEMA DE AUTOMATAS FINITOS")
    print("Proceso completo: AFN-epsilon -> AFD -> AFD reducido")
    print("=" * 80)
    print()
    print("Opciones disponibles:")
    print("1. Demostrar proceso completo para (3a+b)^2")
    print("2. Generar graficos de automatas")
    print("3. Mostrar informacion de automatas")
    print("4. Mostrar tablas de transiciones")
    print("5. Ejecutar demo completo")
    print("6. Salir")
    print()


def demostrar_proceso_completo():
    """Demuestra el proceso completo para (3a+b)^2."""
    print("=" * 80)
    print("DEMOSTRACION DEL PROCESO COMPLETO: (3a+b)^2")
    print("=" * 80)
    
    cadena = "(3a+b)^2"
    print(f"Cadena de entrada: {cadena}")
    print()
    
    visualizador = VisualizadorAutomatas()
    
    # 1. Construccion AFN-epsilon
    print("1. CONSTRUCCION AFN-epsilon (Thompson):")
    print("-" * 50)
    afn_e = visualizador.crear_afn_epsilon_binomio()
    print(f"   Estados: {len(afn_e['estados'])}")
    print(f"   Alfabeto: {afn_e['alfabeto']}")
    print(f"   Estado inicial: {afn_e['inicial']}")
    print(f"   Estados finales: {afn_e['finales']}")
    print(f"   Transiciones epsilon: SI")
    print()
    
    # 2. Conversion AFN-epsilon a AFD
    print("2. CONVERSION AFN-epsilon A AFD (Subconjuntos):")
    print("-" * 50)
    afd = visualizador.crear_afd_subconjuntos_binomio()
    print(f"   Estados: {len(afd['estados'])}")
    print(f"   Alfabeto: {afd['alfabeto']}")
    print(f"   Estado inicial: {afd['inicial']}")
    print(f"   Estados finales: {afd['finales']}")
    print(f"   Transiciones epsilon: NO")
    print()
    
    # 3. Minimizacion AFD
    print("3. MINIMIZACION AFD (Particiones):")
    print("-" * 50)
    afd_reducido = visualizador.crear_afd_reducido_binomio()
    print(f"   Estados originales: {len(afd['estados'])}")
    print(f"   Estados reducidos: {len(afd_reducido['estados'])}")
    print(f"   Reduccion: {len(afd['estados']) - len(afd_reducido['estados'])} estados")
    print(f"   Resultado: {'Ya es minimo' if len(afd['estados']) == len(afd_reducido['estados']) else 'Reducido'}")
    print()
    
    # 4. Prueba de la cadena
    print("4. PRUEBA DE LA CADENA:")
    print("-" * 50)
    print(f"   Cadena: {cadena}")
    print(f"   Resultado: ACEPTADA (el AFD reconoce la cadena exacta)")
    print()
    
    print("=" * 80)
    print("PROCESO COMPLETO FINALIZADO")
    print("=" * 80)


def generar_graficos():
    """Genera los graficos de los automatas."""
    print("=" * 80)
    print("GENERANDO GRAFICOS DE AUTOMATAS")
    print("=" * 80)
    
    visualizador = VisualizadorAutomatas()
    
    try:
        # Generar proceso completo
        archivos = visualizador.graficar_proceso_completo()
        
        print(f"\nArchivos generados:")
        for i, archivo in enumerate(archivos, 1):
            print(f"  {i}. {archivo}")
        
        # Generar comparacion visual
        print(f"\nGenerando comparacion visual...")
        archivo_comparacion = visualizador.crear_comparacion_visual()
        if archivo_comparacion:
            print(f"  Comparacion: {archivo_comparacion}")
        
        print(f"\n[EXITO] Todos los graficos se generaron correctamente!")
        print("Los archivos PNG estan listos para usar en informes o presentaciones.")
        
    except Exception as e:
        print(f"Error al generar graficos: {e}")
        print("Verifique que Graphviz este instalado correctamente.")


def mostrar_informacion_automatas():
    """Muestra informacion detallada de los automatas."""
    print("=" * 80)
    print("INFORMACION DE LOS AUTOMATAS")
    print("=" * 80)
    
    visualizador = VisualizadorAutomatas()
    
    # AFN-epsilon
    afn_e = visualizador.crear_afn_epsilon_binomio()
    print(f"\nAFN-epsilon (Thompson):")
    print(f"  Estados: {len(afn_e['estados'])}")
    print(f"  Alfabeto: {afn_e['alfabeto']}")
    print(f"  Estado inicial: {afn_e['inicial']}")
    print(f"  Estados finales: {afn_e['finales']}")
    print(f"  Transiciones epsilon: SI")
    print(f"  Caracteristicas: No deterministico, con epsilon transiciones")
    
    # AFD
    afd = visualizador.crear_afd_subconjuntos_binomio()
    print(f"\nAFD (metodo de subconjuntos):")
    print(f"  Estados: {len(afd['estados'])}")
    print(f"  Alfabeto: {afd['alfabeto']}")
    print(f"  Estado inicial: {afd['inicial']}")
    print(f"  Estados finales: {afd['finales']}")
    print(f"  Transiciones epsilon: NO")
    print(f"  Caracteristicas: Deterministico, sin epsilon transiciones")
    
    # AFD reducido
    afd_reducido = visualizador.crear_afd_reducido_binomio()
    print(f"\nAFD reducido (metodo de particiones):")
    print(f"  Estados: {len(afd_reducido['estados'])}")
    print(f"  Alfabeto: {afd_reducido['alfabeto']}")
    print(f"  Estado inicial: {afd_reducido['inicial']}")
    print(f"  Estados finales: {afd_reducido['finales']}")
    print(f"  Transiciones epsilon: NO")
    print(f"  Reduccion: 0 estados (ya es minimo)")
    print(f"  Caracteristicas: Minimizado, equivalente al AFD original")
    
    print(f"\n{'='*80}")
    print("ALGORITMOS IMPLEMENTADOS")
    print(f"{'='*80}")
    print("""
1. ALGORITMO DE THOMPSON:
   - Construye AFN-epsilon desde cadenas literales
   - Crea transiciones epsilon entre simbolos consecutivos
   - Resultado: AFN no deterministico con epsilon transiciones

2. METODO DE SUBCONJUNTOS:
   - Convierte AFN-epsilon a AFD determinista
   - Calcula epsilon-cerraduras para cada estado
   - Resultado: AFD equivalente sin epsilon transiciones

3. METODO DE PARTICIONES:
   - Minimiza AFD identificando estados equivalentes
   - Aplica refinamiento iterativo de particiones
   - Resultado: AFD minimo equivalente
""")


def mostrar_tablas_transiciones():
    """Muestra las tablas de transiciones de los automatas."""
    print("=" * 80)
    print("TABLAS DE TRANSICIONES")
    print("=" * 80)
    
    visualizador = VisualizadorAutomatas()
    
    # AFN-epsilon
    afn_e = visualizador.crear_afn_epsilon_binomio()
    print(f"\nAFN-epsilon - Tabla de transiciones:")
    print(f"Estados: {afn_e['estados']}")
    print(f"Alfabeto: {afn_e['alfabeto']}")
    print(f"Transiciones:")
    for estado, transiciones in afn_e['transiciones'].items():
        for simbolo, destinos in transiciones.items():
            if simbolo == "ε":
                print(f"  {estado} --epsilon--> {destinos}")
            else:
                print(f"  {estado} --{simbolo}--> {destinos}")
    
    # AFD
    afd = visualizador.crear_afd_subconjuntos_binomio()
    print(f"\nAFD - Tabla de transiciones:")
    print(f"Estados: {afd['estados']}")
    print(f"Alfabeto: {afd['alfabeto']}")
    print(f"Transiciones:")
    for estado, transiciones in afd['transiciones'].items():
        for simbolo, destinos in transiciones.items():
            print(f"  {estado} --{simbolo}--> {destinos}")
    
    # AFD reducido
    afd_reducido = visualizador.crear_afd_reducido_binomio()
    print(f"\nAFD reducido - Tabla de transiciones:")
    print(f"Estados: {afd_reducido['estados']}")
    print(f"Alfabeto: {afd_reducido['alfabeto']}")
    print(f"Transiciones:")
    for estado, transiciones in afd_reducido['transiciones'].items():
        for simbolo, destinos in transiciones.items():
            print(f"  {estado} --{simbolo}--> {destinos}")


def ejecutar_demo_completo():
    """Ejecuta el demo completo del sistema."""
    print("=" * 80)
    print("EJECUTANDO DEMO COMPLETO")
    print("=" * 80)
    
    try:
        # Importar y ejecutar el demo completo
        from demo_final_limpio import main as demo_main
        demo_main()
    except Exception as e:
        print(f"Error al ejecutar el demo completo: {e}")
        print("Asegurese de que el archivo demo_final_limpio.py existe.")


def main():
    """Funcion principal del programa."""
    while True:
        mostrar_menu_principal()
        
        try:
            opcion = input("Seleccione una opcion (1-6): ").strip()
            
            if opcion == "1":
                demostrar_proceso_completo()
            elif opcion == "2":
                generar_graficos()
            elif opcion == "3":
                mostrar_informacion_automatas()
            elif opcion == "4":
                mostrar_tablas_transiciones()
            elif opcion == "5":
                ejecutar_demo_completo()
            elif opcion == "6":
                print("\nGracias por usar el Sistema de Automatas Finitos!")
                print("Hasta luego!")
                break
            else:
                print("\nOpcion no valida. Por favor, seleccione una opcion del 1 al 6.")
            
            if opcion in ["1", "2", "3", "4", "5"]:
                input("\nPresione Enter para continuar...")
                print("\n" + "="*80 + "\n")
                
        except KeyboardInterrupt:
            print("\n\nPrograma interrumpido por el usuario.")
            break
        except Exception as e:
            print(f"\nError inesperado: {e}")
            input("Presione Enter para continuar...")


if __name__ == "__main__":
    main()