from luana_engine.python_interpreter import PythonInterpreter


def test_python_interpreter():
    interpreter = PythonInterpreter()

    # First run
    stdout, stderr = interpreter.run(
        """
    a = 1
    b = 2
    c = a + b
    print(c)
    """
    )
    print("STDOUT:", stdout)
    print("STDERR:", stderr)

    # Second run, using the state from the first run
    stdout, stderr = interpreter.run(
        """
    d = c + 1
    print(d)
    """
    )
    print("STDOUT:", stdout)
    print("STDERR:", stderr)
