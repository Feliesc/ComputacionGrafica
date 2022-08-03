
# Calculo de la componente K1 del método de RK4
def K1(f, t_n, z_n):
    k1 = f(t_n, z_n)
    return k1

# Calculo de la componente K2 del método de RK4
def K2(f, h, t_n, z_n):
    k2 = f(t_n + h/2, z_n + (h/2)*K1(f, t_n, z_n))
    return k2

# Calculo de la componente K3 del método de RK4
def K3(f, h, t_n, z_n):
    k3 = f(t_n + h/2, z_n + (h/2)*K2(f, h, t_n, z_n))
    return k3

# Calculo de la componente K4 del método de RK4
def K4(f, h, t_n, z_n):
    k4 = f(t_n + h, z_n + h*K3(f, h, t_n, z_n))
    return k4

# Calculo un paso de la aproximación con el método de RK4
def RK4_step(f, h, t_n, z_n):
    k1 = K1(f, t_n, z_n)
    k2 = K2(f, h, t_n, z_n)
    k3 = K3(f, h, t_n, z_n)
    k4 = K4(f, h, t_n, z_n)
    return z_n + (h/6)*(k1 + 2*k2 + 2*k3 + k4)

# Dada una función f, un h, un vector de tiempos y las condiciones iniciales, calcula la aproximación con RK4
def resolve_RK4(f, h, t, z_0):
    z = [z_0]

    for i in range(1, len(t)):
        rk4_step = RK4_step(f, h, t[i], z[-1])
        z.append(rk4_step)
    
    return z

# Calculo un paso de la aproximacion con el método de euler
def euler_step(f, h, t_n, z_n):
    next_z = z_n + h*f(t_n, z_n)
    return next_z

# Dada una función f, un h, un vector de tiempos y las condiciones iniciales, calcula la aproximación con euler
def resolve_euler(f, h, t, z_0):
    # Vector donde se dejarán los resultados
    z = [z_0]

    for i in range(1,len(t)):
        z_siguiente = euler_step(f, h, t[i], z[-1])
        z.append(z_siguiente)
    
    return z

