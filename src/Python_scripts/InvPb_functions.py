
# ---------------------------------------------------------------------------

def make_history():
    return {"iteration": [],
            "g": [],
            "cost": [], }


def make_callback(history, iter_count):
    """
        Callback for L-BFGS-B.

        Important:
        The argument name must be exactly 'intermediate_result'
        so that scipy.optimize.minimize passes an OptimizeResult
        containing x and fun.
    """
    def callback(intermediate_result):
        iter_count[0] += 1

        g    = intermediate_result.x
        cost = intermediate_result.fun

        history["iteration"].append(iter_count[0])
        history["g"].append(float(g[0]))
        history["cost"].append(float(cost))

        print(
            f"Iteration {iter_count[0]}: "
            f"g = {g[0]:.12f}, "
            f"f(g) = {cost:.12e}"
        )

    return callback

# ---------------------------------------------------------------------------

def parse_g0_list(raw: str) -> list[float]:
    """
        Converts a user-entered string into a list of floating-point values.
        
        Accepted formats (separators: comma, space, or semicolon):
            "0.5 1.0 1.5"
            "0.5, 1.0, 1.5"
            "0.5;1.0;1.5"
    """
    tokens = raw.replace(",", " ").replace(";", " ").split()
    values = [float(t) for t in tokens]
    if not values:
        raise ValueError("Aucune valeur g0 fournie.")
    return values