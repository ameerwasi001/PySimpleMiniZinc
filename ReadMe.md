# PySimpleMiniZinc
This is a very simple and extensible interface to MiniZinc in Python. It's built using the minizinc python module that provides a nice interface but requires you to write minizinc language in strings. Here we avoid this by simply providing a nice API that renders into a string that can be fed into the minizinc module by using Python's meta-programming capabilities. Note that it was created as a tool to be used for a larger project whch never came to fruition.

## The interface
In order to begin with the interface, you must first create a MiniZincProgram that takes several optional parameters like the default domain of a variable(This is used hen the domain is unspecified), whether it should implicitly declare variables it encounters throughout constraints with the default domain, and any existing variables you might want to begin with. Here's an example
```
program = MiniZincProgram()
program.add_var("a", Range(0, 255))
program.add_var("b", Range(0, 255))
program.add_var("c", Range(0, 255))

program.constraints.append(program.a == program.b + program.c)
program.constraints.append(program.b*2 == program.c)
```
This program can be simplified by specifying a default domain
```
program = MiniZincProgram(default_domain = Range(0, 255))
program.add_var("a")
program.add_var("b")
program.add_var("c")

program.constraints.append(program.a == program.b + program.c)
program.constraints.append(program.b*2 == program.c)
```
It can also be further simplified by enabling collect_vars
```
program = MiniZincProgram(default_domain=Range(0, 255), collect_vars=True)
program.constraints.append(program.a == program.b + program.c)
program.constraints.append(program.b*2 == program.c)
```
Note that we can use any object instead of the Range object with the catch being that its `__str__` should render to valid MiniZinc. You can also async_solve this by using the solve method of your MiniZinc proram object.
```
async def main():
    async for sol in program.async_solve(all_solutions=True):
        print(sol)

asyncio.run(main())
```
The code above would print all solutions but you can also just print a single one by not using a all_solutions.