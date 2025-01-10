import requests
from bs4 import BeautifulSoup
import dspy
from typing import Literal


class ClassifyModuleInstallability(dspy.Signature):
    """Classify if a module can be pip installed based on its PyPI page."""

    module_name: str = dspy.InputField(desc="Name of the module to classify")
    installable: Literal[True, False] = dspy.OutputField(
        desc="Whether the module can be pip installed")


def query_pypi(module_name: str) -> str:
    url = f"https://pypi.org/search/?q={module_name}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        return soup.get_text()
    else:
        raise Exception(f"Failed to fetch PyPI page for {module_name}")


def classify_installability(module_name: str) -> bool:
    lm = dspy.LM('your-model-name')  # Replace with your model name
    dspy.configure(lm=lm)
    classify_module_installability = dspy.ChainOfThought(
        ClassifyModuleInstallability)
    response = classify_module_installability(module_name=module_name)
    return response.installable


def main():
    module_name = "qiskit.providers.ibmq"
    pypi_page_content = query_pypi(module_name)
    installable = classify_installability(pypi_page_content)
    if installable:
        print(f"The module {module_name} can be pip installed.")
    else:
        print(f"The module {module_name} cannot be pip installed.")


if __name__ == "__main__":
    main()
