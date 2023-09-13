from IPython.core.interactiveshell import InteractiveShell
from IPython.utils.capture import capture_output
from .prompts.generate_functions import finance_data_functions


class PythonInterpreter:
    def __init__(self, preset_functions=None):
        self.shell = InteractiveShell.instance()
        self.run(preset_functions)

    def run(self, code):
        with capture_output() as captured:
            try:
                self.shell.run_cell(code)
                stdout = captured.stdout
                stderr = captured.stderr
            except Exception as e:
                stdout = ""
                stderr = str(e)

        # Combine stdout and stderr
        output = f"STDOUT: {stdout}, STDERR: {stderr}"

        # Truncate output to 2000 characters
        if len(output) > 2000:
            output = output[:2000]

        return output
