import asyncio
from minizinc import Instance, Model, Solver

class BaseOperations:
    def __add__(self, b):
        return Operation(self, "+", b)
    
    def __sub__(self, b):
        return Operation(self, "-", b)

    def __mul__(self, b):
        return Operation(self, "*", b)
    
    def __div__(self, b):
        return Operation(self, "/", b)
    
    def __eq__(self, other):
        return Operation(self, "=", other)
    
    def __ge__(self, other):
        return Operation(self, ">=", other)
    
    def __gt__(self, other):
        return Operation(self, ">", other)
    
    def __lt__(self, other):
        return Operation(self, "<", other)
    
    def __le__(self, other):
        return Operation(self, "<=", other)

class Operation(BaseOperations):
    def __init__(self, a, op, b):
        self.left = a
        self.op = op
        self.right = b
        super().__init__()

    def get_vars(self):
        yield from self.left.get_vars()
        yield from self.right.get_vars()

    def __str__(self):
        return f"({self.left}) {self.op} ({self.right})"

class Range:
    def __init__(self, low, high):
        self.high = high
        self.low = low

    def __str__(self):
        return f"{str(self.low)}..{str(self.high)}"

class Var(BaseOperations):
    def __init__(self, name, _range):
        self.name = name
        self.range = _range
        super().__init__()

    def as_decl(self):
        return f"var {str(self.range)}: {self.name}"

    def get_vars(self):
        yield self

    def __str__(self):
        return self.name

class Const(BaseOperations):
    def __init__(self, val):
        self.value = val

    def get_vars(self): return None

    def __str__(self):
        return f"{self.value}"

class MiniZincProgram:
    def __init__(self, collect_vars=True, default_range=(0, 255), vars_=None):
        vars_ = {} if vars_ == None else vars_
        self.vars = {k:Var(k,v) for k,v in vars_.items()}
        self.collect_vars = collect_vars
        self.default_range = default_range
        self.constraints = []

    def add_var(self, name: str, range_=None):
        if range_ is None: 
            (low, high) = self.default_range
            range_ = Range(low, high)
        self.vars[name] = Var(name, range_)

    def __getattr__(self, name):
        if self.collect_vars:
            if not (name in self.vars):
                (low, high) = self.default_range
                self.vars[name] = Var(name, Range(low, high))
        return self.vars[name]

    async def async_solve(self, solver="gecode", *args, **kwargs):
        model = Model()
        model.add_string(str(self))
        gecode = Solver.lookup(solver)
        instance = Instance(gecode, model)
        async for sol in instance.solutions(*args, **kwargs):
            yield sol

    def __str__(self):
        var_dict = self.vars
        minizinc_vars = "\n".join([f"{var.as_decl()};" for _, var in var_dict.items()])
        minizinc_constraints = "\n".join([f"constraint {constraint};" for constraint in map(str, self.constraints)])
        return minizinc_vars + "\n\n" + minizinc_constraints