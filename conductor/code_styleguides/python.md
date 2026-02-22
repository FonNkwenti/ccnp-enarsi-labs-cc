# Python Code Styleguide

- Follow PEP 8.
- Use type hints.
- Write docstrings for all functions.

## Tool-Call Precautions (Gemini CLI)

- **Escaping Newlines:** When using `write_file` or `replace` to insert Python code containing `\n` (newline character literals) into a file, you MUST use `\\n` (double backslash) in the tool's `content` or `new_string` parameter.
  - **Reason:** The CLI or JSON parser may interpret `\n` as a literal newline, which will cause a `SyntaxError: unterminated string literal` in the target Python file.
  - **Example:** Use `print("\\nLab complete.")` to ensure the file contains `print("\nLab complete.")`.
