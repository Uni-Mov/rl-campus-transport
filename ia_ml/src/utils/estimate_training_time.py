"""
Script para estimar el tiempo de entrenamiento del PPO
basado en parámetros y configuración del entrenamiento.
"""
import argparse
from typing import Dict, Tuple


def estimate_step_time(grid_size: int, max_steps: int) -> float:
    """
    Estima el tiempo por step en segundos basado en la complejidad del entorno.
    
    Args:
        grid_size: Tamaño de la grilla (NxN)
        max_steps: Máximo de pasos por episodio
        
    Returns:
        Tiempo estimado por step en segundos
    """
    n_nodes = grid_size * grid_size
    
    # Tiempo base por step (en segundos)
    # Este valor se ajusta según la complejidad del grafo
    base_time = 0.001  # 1ms base
    
    # Factor de complejidad basado en el tamaño del grafo
    complexity_factor = 1 + (n_nodes / 100) * 0.5
    
    # Factor por max_steps (más steps = episodios más largos)
    episode_factor = 1 + (max_steps / 100) * 0.2
    
    step_time = base_time * complexity_factor * episode_factor
    
    return step_time


def estimate_eval_time(
    n_eval_episodes: int,
    max_steps: int,
    grid_size: int,
    eval_overhead: float = 1.5
) -> float:
    """
    Estima el tiempo de una evaluación completa.
    
    Args:
        n_eval_episodes: Número de episodios de evaluación
        max_steps: Máximo de pasos por episodio
        grid_size: Tamaño de la grilla
        eval_overhead: Factor de overhead por evaluación (logging, guardado, etc.)
        
    Returns:
        Tiempo estimado de evaluación en segundos
    """
    step_time = estimate_step_time(grid_size, max_steps)
    
    # Tiempo total = episodios * steps promedio * tiempo por step
    avg_steps_per_episode = max_steps * 0.6  # Asumimos que en promedio usa 60% de max_steps
    eval_time = n_eval_episodes * avg_steps_per_episode * step_time * eval_overhead
    
    return eval_time


def estimate_early_stopping(
    total_timesteps: int,
    eval_freq: int,
    max_no_improvement_evals: int,
    min_evals: int,
    grid_size: int,
    convergence_difficulty: str = "medium"
) -> Tuple[float, int, str]:
    """
    Estima si el early stopping se activará y en qué momento.
    
    Args:
        total_timesteps: Total de timesteps configurados
        eval_freq: Frecuencia de evaluación
        max_no_improvement_evals: Máximo de evaluaciones sin mejora antes de parar
        min_evals: Mínimo de evaluaciones antes de poder parar
        grid_size: Tamaño de la grilla (afecta dificultad)
        convergence_difficulty: Dificultad del problema (easy/medium/hard)
        
    Returns:
        Tupla de (probabilidad_early_stop, timesteps_estimados, descripcion)
    """
    n_nodes = grid_size * grid_size
    total_evals = total_timesteps // eval_freq
    
    # Factores de dificultad (qué % de las evaluaciones se usan para converger)
    difficulty_factors = {
        "easy": 0.5,      # Problemas simples convergen rápido (50% de evals)
        "medium": 0.65,   # Problemas medianos (65% de evals)
        "hard": 0.85      # Problemas difíciles (85% de evals)
    }
    
    # Ajustar dificultad según tamaño del grafo
    if n_nodes < 25:
        convergence_difficulty = "easy"
    elif n_nodes < 100:
        convergence_difficulty = "medium"
    else:
        convergence_difficulty = "hard"
    
    difficulty_factor = difficulty_factors.get(convergence_difficulty, 0.65)
    
    # Estimar en qué evaluación convergerá (desde min_evals)
    # Converge después de min_evals más un porcentaje de las evaluaciones restantes
    remaining_evals = max(0, total_evals - min_evals)
    expected_convergence_eval = min_evals + int(remaining_evals * difficulty_factor)
    
    # Early stopping se activa después de max_no_improvement_evals evaluaciones sin mejora
    early_stop_eval = expected_convergence_eval + max_no_improvement_evals
    
    if early_stop_eval < total_evals:
        # Early stopping se activará
        probability = 0.7 + (0.2 if n_nodes < 100 else 0)  # 70-90% de probabilidad
        estimated_timesteps = early_stop_eval * eval_freq
        saved_evals = total_evals - early_stop_eval
        description = f"Probable (converge ~eval {expected_convergence_eval}/{total_evals}, para en eval {early_stop_eval}, ahorra {saved_evals} evals)"
    else:
        # Probablemente use todos los timesteps
        probability = 0.3  # 30% de probabilidad de early stop
        estimated_timesteps = total_timesteps
        shortage = early_stop_eval - total_evals
        description = f"Poco probable (necesitaría {shortage} evals más, usará todos los timesteps)"
    
    return probability, estimated_timesteps, description


def estimate_total_time(
    total_timesteps: int,
    grid_size: int,
    max_steps: int = 30,
    eval_freq: int = 5000,
    n_eval_episodes: int = 5,
    learning_rate: float = 3e-4,
    batch_size: int = 64,
    n_epochs: int = 10,
    max_no_improvement_evals: int = 10,
    min_evals: int = 5,
    enable_early_stopping: bool = True
) -> Dict[str, float]:
    """
    Estima el tiempo total de entrenamiento.
    
    Args:
        total_timesteps: Total de timesteps para entrenar
        grid_size: Tamaño de la grilla (NxN)
        max_steps: Máximo de pasos por episodio
        eval_freq: Frecuencia de evaluación (cada cuántos steps)
        n_eval_episodes: Número de episodios por evaluación
        learning_rate: Tasa de aprendizaje (afecta convergencia)
        batch_size: Tamaño del batch para PPO
        n_epochs: Número de épocas de actualización PPO
        max_no_improvement_evals: Máximo de evaluaciones sin mejora (early stopping)
        min_evals: Mínimo de evaluaciones antes de poder parar
        enable_early_stopping: Si considerar early stopping en la estimación
        
    Returns:
        Diccionario con estimaciones de tiempo
    """
    # Estimar early stopping
    early_stop_info = None
    effective_timesteps = total_timesteps
    
    if enable_early_stopping:
        probability, estimated_timesteps, description = estimate_early_stopping(
            total_timesteps, eval_freq, max_no_improvement_evals, 
            min_evals, grid_size
        )
        early_stop_info = {
            'probability': probability,
            'estimated_timesteps': estimated_timesteps,
            'description': description
        }
        # Usar timesteps estimados si la probabilidad es alta
        if probability > 0.5:
            effective_timesteps = estimated_timesteps
    
    # Tiempo de steps de entrenamiento
    step_time = estimate_step_time(grid_size, max_steps)
    training_time = effective_timesteps * step_time
    training_time_max = total_timesteps * step_time  # Tiempo máximo sin early stop
    
    # Tiempo de evaluaciones
    n_evaluations = effective_timesteps // eval_freq
    n_evaluations_max = total_timesteps // eval_freq
    eval_time_per_eval = estimate_eval_time(n_eval_episodes, max_steps, grid_size)
    total_eval_time = n_evaluations * eval_time_per_eval
    total_eval_time_max = n_evaluations_max * eval_time_per_eval
    
    # Tiempo de actualización del modelo (PPO updates)
    # PPO hace actualizaciones cada cierto número de steps
    update_frequency = 2048  # steps por actualización (valor típico de PPO)
    n_updates = effective_timesteps // update_frequency
    n_updates_max = total_timesteps // update_frequency
    
    # Tiempo por actualización depende del batch_size y n_epochs
    time_per_update = (batch_size / 1000) * n_epochs * 0.1  # segundos
    total_update_time = n_updates * time_per_update
    total_update_time_max = n_updates_max * time_per_update
    
    # Factor de learning rate (menor LR puede requerir más tiempo para converger)
    lr_factor = 1.0
    if learning_rate < 1e-4:
        lr_factor = 1.3
    elif learning_rate > 1e-3:
        lr_factor = 0.9
    
    # Tiempo total con overhead del sistema (~20%)
    overhead = 1.2
    total_time = (training_time + total_eval_time + total_update_time) * overhead * lr_factor
    total_time_max = (training_time_max + total_eval_time_max + total_update_time_max) * overhead * lr_factor
    
    # Calcular tiempos en diferentes unidades
    result = {
        'total_seconds': total_time,
        'total_minutes': total_time / 60,
        'total_hours': total_time / 3600,
        'training_seconds': training_time,
        'eval_seconds': total_eval_time,
        'update_seconds': total_update_time,
        'n_evaluations': n_evaluations,
        'n_updates': n_updates,
        'step_time_ms': step_time * 1000,
        'effective_timesteps': effective_timesteps,
        'early_stop_info': early_stop_info
    }
    
    # Si hay early stopping, agregar tiempos máximos
    if enable_early_stopping and early_stop_info and early_stop_info['probability'] > 0.5:
        result['total_seconds_max'] = total_time_max
        result['total_minutes_max'] = total_time_max / 60
        result['total_hours_max'] = total_time_max / 3600
        result['n_evaluations_max'] = n_evaluations_max
        result['n_updates_max'] = n_updates_max
    
    return result


def format_time(seconds: float) -> str:
    """Formatea el tiempo en un string legible."""
    if seconds < 60:
        return f"{seconds:.1f} segundos"
    elif seconds < 3600:
        return f"{seconds/60:.1f} minutos ({seconds:.0f}s)"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours}h {minutes}m ({seconds/60:.1f} minutos)"


def main():
    parser = argparse.ArgumentParser(
        description='Estimar tiempo de entrenamiento PPO'
    )
    
    # Parámetros principales
    parser.add_argument('--timesteps', type=int, default=20000,
                       help='Total de timesteps para entrenar')
    parser.add_argument('--grid-size', type=int, default=5,
                       help='Tamaño de la grilla (NxN)')
    
    # Parámetros del entorno
    parser.add_argument('--max-steps', type=int, default=30,
                       help='Máximo de pasos por episodio')
    
    # Parámetros de evaluación
    parser.add_argument('--eval-freq', type=int, default=5000,
                       help='Frecuencia de evaluación')
    parser.add_argument('--n-eval-episodes', type=int, default=5,
                       help='Episodios por evaluación')
    
    # Parámetros PPO
    parser.add_argument('--learning-rate', type=float, default=3e-4,
                       help='Tasa de aprendizaje')
    parser.add_argument('--batch-size', type=int, default=64,
                       help='Tamaño del batch')
    parser.add_argument('--n-epochs', type=int, default=10,
                       help='Número de épocas de actualización')
    
    # Parámetros de Early Stopping
    parser.add_argument('--max-no-improvement', type=int, default=10,
                       help='Máximo de evaluaciones sin mejora (early stopping)')
    parser.add_argument('--min-evals', type=int, default=5,
                       help='Mínimo de evaluaciones antes de poder parar')
    parser.add_argument('--no-early-stopping', action='store_true',
                       help='Desactivar estimación de early stopping')
    
    args = parser.parse_args()
    
    # Calcular estimación
    estimates = estimate_total_time(
        total_timesteps=args.timesteps,
        grid_size=args.grid_size,
        max_steps=args.max_steps,
        eval_freq=args.eval_freq,
        n_eval_episodes=args.n_eval_episodes,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        n_epochs=args.n_epochs,
        max_no_improvement_evals=args.max_no_improvement,
        min_evals=args.min_evals,
        enable_early_stopping=not args.no_early_stopping
    )
    
    # Mostrar resultados
    n_nodes = args.grid_size * args.grid_size
    
    print("=" * 70)
    print("ESTIMACIÓN DE TIEMPO DE ENTRENAMIENTO PPO")
    print("=" * 70)
    print("\nCONFIGURACIÓN:")
    print(f"  • Total timesteps:      {args.timesteps:,}")
    print(f"  • Tamaño de grilla:     {args.grid_size}x{args.grid_size} ({n_nodes} nodos)")
    print(f"  • Max steps/episodio:   {args.max_steps}")
    print(f"  • Evaluación cada:      {args.eval_freq:,} steps")
    print(f"  • Episodios/eval:       {args.n_eval_episodes}")
    print(f"  • Learning rate:        {args.learning_rate}")
    print(f"  • Batch size:           {args.batch_size}")
    print(f"  • Épocas de update:     {args.n_epochs}")
    
    # Mostrar configuración de early stopping
    if not args.no_early_stopping:
        print(f"\nEARLY STOPPING:")
        print(f"  • Max sin mejora:       {args.max_no_improvement} evaluaciones")
        print(f"  • Min evaluaciones:     {args.min_evals}")
    
    print("\nMÉTRICAS:")
    print(f"  • Tiempo por step:      {estimates['step_time_ms']:.3f} ms")
    
    # Mostrar información de early stopping
    early_stop_info = estimates.get('early_stop_info')
    if early_stop_info:
        print(f"\nEARLY STOPPING ESTIMADO:")
        print(f"  • Estado:               {early_stop_info['description']}")
        print(f"  • Probabilidad:         {early_stop_info['probability']*100:.0f}%")
        print(f"  • Timesteps esperados:  {early_stop_info['estimated_timesteps']:,}")
        
        if early_stop_info['probability'] > 0.5:
            print(f"\n  >> Con early stopping:")
            print(f"    - Evaluaciones:       {int(estimates['n_evaluations'])}")
            print(f"    - Updates del modelo: {int(estimates['n_updates'])}")
            print(f"\n  >> Sin early stopping (máximo):")
            print(f"    - Evaluaciones:       {int(estimates['n_evaluations_max'])}")
            print(f"    - Updates del modelo: {int(estimates['n_updates_max'])}")
        else:
            print(f"  • Evaluaciones totales: {int(estimates['n_evaluations'])}")
            print(f"  • Updates del modelo:   {int(estimates['n_updates'])}")
    else:
        print(f"  • Evaluaciones totales: {int(estimates['n_evaluations'])}")
        print(f"  • Updates del modelo:   {int(estimates['n_updates'])}")
    
    print("\nDESGLOSE DE TIEMPO:")
    print(f"  • Entrenamiento:        {format_time(estimates['training_seconds'])}")
    print(f"  • Evaluaciones:         {format_time(estimates['eval_seconds'])}")
    print(f"  • Updates PPO:          {format_time(estimates['update_seconds'])}")
    
    print("\n" + "=" * 70)
    
    # Mostrar tiempo con early stopping si aplica
    if early_stop_info and early_stop_info['probability'] > 0.5:
        print(f"TIEMPO ESTIMADO (con early stopping):  {format_time(estimates['total_seconds'])}")
        print("=" * 70)
        print(f"\nTiempo máximo (sin early stopping):    {format_time(estimates['total_seconds_max'])}")
        
        # Ahorro estimado
        time_saved = estimates['total_seconds_max'] - estimates['total_seconds']
        percent_saved = (time_saved / estimates['total_seconds_max']) * 100
        print(f"Ahorro estimado:                       {format_time(time_saved)} ({percent_saved:.0f}%)")
    else:
        print(f"TIEMPO TOTAL ESTIMADO:  {format_time(estimates['total_seconds'])}")
        print("=" * 70)
    
    # Rangos de estimación
    min_time = estimates['total_seconds'] * 0.7
    max_time_range = estimates.get('total_seconds_max', estimates['total_seconds'] * 1.5)
    
    print(f"\nRango estimado: {format_time(min_time)} - {format_time(max_time_range)}")
    print("\nNOTA: Esta es una estimación aproximada. El tiempo real puede variar")
    print("      según el hardware, carga del sistema y velocidad de convergencia.")
    if early_stop_info and early_stop_info['probability'] > 0.5:
        print("      El early stopping puede activarse antes o después de lo estimado.")
    print()


if __name__ == "__main__":
    main()

