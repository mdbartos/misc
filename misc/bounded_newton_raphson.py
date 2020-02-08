def newton_raphson(f, df, x0, x_lb, x_ub, args, max_iter=1000, eps=1e-8):
    # 1. Initial steps
    # 1a.
    x = x0
    f_lx = f(x_lb, *args)
    f_ux = f(x_ub, *args)
    if (f_lx > f_ux):
        x_lb, x_ub = x_ub, x_lb
    # 1b.
    if (x < x_lb) or (x > x_ub):
        x = (x_lb + x_ub) / 2
    # 1c.
    dx = np.abs(x_ub - x_lb)
    # 1d.
    fx = f(x, *args)
    dfx = df(x, *args)
    # 2.
    for _ in range(max_iter):
        cond_0 = (((x - x_ub) * dfx - fx) * ((x - x_lb) * dfx - fx)) >= 0.
        cond_1 = (np.abs(2 * fx) > np.abs(dx * dfx))
        if (cond_0 or cond_1):
            dx = 0.5 * (x_ub - x_lb)
            x = x_lb + dx
        # 3.
        else:
            dx = fx / dfx
            x = x - dx
        # 4.
        if np.abs(dx) < eps:
            return x
        # 5.
        fx = f(x, *args)
        dfx = df(x, *args)
        if fx < 0:
            x_lb = x
        else:
            x_ub = x
