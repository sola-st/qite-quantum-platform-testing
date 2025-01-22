
import ast
from pathlib import Path
from generators.strategies.llm_generator import LLMGenerationStrategy
import aiexchange.tools.base_model_setup
import dspy


lm = dspy.LM('groq/llama-3.3-70b-versatile')
dspy.configure(lm=lm)


def test_load_documentation():
    """Test that the documentation content is loaded correctly."""
    path_to_documentation = Path(
        "tests/artifacts/documentation/sample_documentation.txt")
    strategy = LLMGenerationStrategy(path_to_documentation)
    expected_content = path_to_documentation.read_text()
    assert strategy.documentation_content == expected_content


def test_generate():
    """Test that the generate method returns a string."""
    path_to_documentation = Path(
        "tests/artifacts/documentation/sample_documentation.txt")
    strategy = LLMGenerationStrategy(path_to_documentation)
    generated_code = strategy.generate()
    print(generated_code)
    assert isinstance(generated_code, str)
    assert len(generated_code) > 0


def test_generate_python_parasable_code():
    """Test that the generated code is Python parsable."""
    path_to_documentation = Path(
        "tests/artifacts/documentation/sample_documentation.txt")
    strategy = LLMGenerationStrategy(path_to_documentation)
    generated_code = strategy.generate()
    try:
        root = ast.parse(generated_code)
        assert root is not None
        print(ast.dump(root))
    except Exception as e:
        raise AssertionError(
            f"Generated code is not Python parsable: {e}") from e
