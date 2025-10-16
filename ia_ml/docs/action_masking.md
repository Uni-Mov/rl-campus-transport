# Action Masking

## El problema

Imagínate que estás entrenando un agente para navegar por un grafo. En cada nodo, el agente puede elegir entre 10 acciones (0, 1, 2, 3, 4, 5, 6, 7, 8, 9), pero en realidad solo 2 o 3 de esas acciones van a nodos que realmente existen.

Sin masking, el agente puede elegir la acción 7, que no lleva a ningún lado. El entorno le da una penalización de -10 y le dice "esa acción no existe". El agente aprende que la acción 7 es mala, pero sigue perdiendo tiempo probándola una y otra vez.

## La solución 
Con action masking, el agente simplemente no ve las acciones inválidas. Si solo hay 3 vecinos reales, el agente solo puede elegir entre 3 acciones válidas. No puede elegir la acción 7 porque no existe en su universo.

## Por qué funciona tan bien

El agente aprende mucho más rápido porque:
- No desperdicia tiempo en acciones que no sirven
- Solo ve experiencias útiles
- No se confunde con opciones que no existen
- Puede enfocarse en aprender la estrategia real

## En la práctica

### Sin masking:
```python
# El agente ve todas las acciones
action_space = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
# Elige acción 7 (que no existe)
action = 7
# Recibe penalización
reward = -10
# Sigue perdiendo tiempo con esta acción
```

### Con masking
```python
# El agente solo ve acciones válidas
valid_actions = [0, 1, 2]  # Solo las que van a vecinos reales
# No puede elegir acción 7 porque no la ve
# Solo puede elegir entre acciones útiles
```


## Resultados que se obtienen

- **Mejor calidad del modelo final**
- **Convergencia más estable**
- **Menos episodios para aprender**


## El espacio dinámico

Además del masking, el sistema también ajusta automáticamente el número de acciones disponibles según el grafo. Si tu grafo tiene un grado máximo de 4, el agente solo ve las acciones valida para cada nodo

Es más limpio y eficiente. El agente no ve acciones que nunca va a usar.

## Flujo del ActionMaskingWrapper

```
         Agente 
       Elige acción 5
            .
            .  
            .

         Wrapper                      
     1. Recibe acción 5              
     2. Mira vecinos disponibles     
        neighbors = [2, 7, 9]        
     3. Crea máscara                 
        [F,F,T,F,F,F,F,T,F,T]        
     4. ¿Acción 5 válida? NO         
     5. Cambia a acción 7            
            .
            .
            .

        Entorno base 
     1. Ejecuta acción 7 (válida)  
     2.  Mueve al nodo 7        
     3.  Calcula recompensa    
            .
            .
            .
      se repite, nuevamente va al agente, wrapper, ...
```

### ¿Qué hace cada paso?

1. **Agente elige acción** → Puede ser inválida
2. **Wrapper verifica** → Mira si la acción va a un vecino real
3. **Wrapper corrige** → Cambia acción inválida por válida
4. **Entorno ejecuta** → Solo ve acciones válidas
5. **Wrapper procesa** → Agrega penalizaciones por ciclos
6. **Agente recibe** → Resultado como si eligió acción válida

**Resultado**: El agente nunca ve acciones inválidas, solo experiencias útiles.