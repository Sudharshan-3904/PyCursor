"""
Code Linter and Error Analyzer
Integrates with pyflakes, mypy, and ruff for comprehensive code analysis
Provides AI-powered error explanations and fix suggestions
"""

import subprocess
import re
import os
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    """Error severity levels"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


@dataclass
class LintError:
    """Represents a linting error or warning"""
    file_path: str
    line: int
    column: int
    severity: Severity
    code: str
    message: str
    tool: str
    
    def __str__(self):
        return f"{self.file_path}:{self.line}:{self.column}: {self.severity.value}: {self.message} [{self.tool}:{self.code}]"


class CodeLinter:
    """Comprehensive code linter with multiple tool support"""
    _AVAILABLE_TOOLS_CACHE = None
    
    def __init__(self):
        if CodeLinter._AVAILABLE_TOOLS_CACHE is None:
            CodeLinter._AVAILABLE_TOOLS_CACHE = self._detect_available_tools()
        self.available_tools = CodeLinter._AVAILABLE_TOOLS_CACHE

    def _parse_lint_line(self, line: str, pattern: str) -> Optional[tuple]:
        """Shared regex parsing logic to reduce duplication across tool handlers."""
        match = re.match(pattern, line)
        return match.groups() if match else None
    
    def _detect_available_tools(self) -> Dict[str, bool]:
        """Detect which linting tools are available in the system environment."""
        tools = {}
        for tool in ['pyflakes', 'mypy', 'ruff', 'pylint', 'flake8']:
            try:
                # Optimized check: only verify presence, don't wait for full version output if not needed
                result = subprocess.run([tool, '--version'], capture_output=True, timeout=1.5)
                tools[tool] = result.returncode == 0
            except (FileNotFoundError, subprocess.SubprocessError, Exception):
                tools[tool] = False
        return tools
    
    def lint_file(self, file_path: str, tools: Optional[List[str]] = None, python_exec: str = None) -> List[LintError]:
        """
        Lint a Python file using specified tools
        
        Args:
            file_path: Path to Python file
            tools: List of tools to use (None = use all available)
            python_exec: Path to python executable to use
            
        Returns:
            List of lint errors found
        """
        if not os.path.exists(file_path):
            return []
        
        if tools is None:
            tools = [tool for tool, available in self.available_tools.items() if available]
        
        all_errors = []
        
        for tool in tools:
            if tool == 'pyflakes':
                all_errors.extend(self._run_pyflakes(file_path, python_exec))
            elif tool == 'mypy':
                all_errors.extend(self._run_mypy(file_path, python_exec))
            elif tool == 'ruff':
                all_errors.extend(self._run_ruff(file_path, python_exec))
            elif tool == 'pylint':
                all_errors.extend(self._run_pylint(file_path, python_exec))
            elif tool == 'flake8':
                all_errors.extend(self._run_flake8(file_path, python_exec))
        
        return all_errors
    
    def lint_code(self, code: str, filename: str = '<string>') -> List[LintError]:
        """
        Lint code string without saving to file
        
        Args:
            code: Python code to lint
            filename: Virtual filename for error reporting
            
        Returns:
            List of lint errors
        """
        import tempfile
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_path = f.name
        
        try:
            errors = self.lint_file(temp_path)
            for error in errors:
                error.file_path = filename
            return errors
        finally:
            os.unlink(temp_path)
    
    def _run_pyflakes(self, file_path: str, python_exec: str = None) -> List[LintError]:
        """Run pyflakes and parse output"""
        try:
            cmd = ['pyflakes', file_path]
            if python_exec:
                cmd = [python_exec, '-m', 'pyflakes', file_path]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            pattern = r'^(.+?):(\d+):(\d+)?\s*(.+)$'
            for line in result.stdout.splitlines():
                matches = self._parse_lint_line(line, pattern)
                if matches:
                    filepath, line_num, col, message = matches
                    errors.append(LintError(
                        file_path=filepath,
                        line=int(line_num),
                        column=int(col) if col else 0,
                        severity=Severity.ERROR,
                        code='pyflakes',
                        message=message.strip(),
                        tool='pyflakes'
                    ))
            return errors
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
    
    def _run_mypy(self, file_path: str, python_exec: str = None) -> List[LintError]:
        """Run mypy and parse output"""
        try:
            cmd = ['mypy', '--show-column-numbers', '--no-error-summary', file_path]
            if python_exec:
                cmd = [python_exec, '-m', 'mypy', '--show-column-numbers', '--no-error-summary', file_path]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=15
            )
            
            pattern = r'^(.+?):(\d+):(\d+):\s*(error|warning|note):\s*(.+?)(?:\s+\[(.+?)\])?$'
            for line in result.stdout.splitlines():
                matches = self._parse_lint_line(line, pattern)
                if matches:
                    filepath, line_num, col, severity, message, code = matches
                    severity_map = {'error': Severity.ERROR, 'warning': Severity.WARNING, 'note': Severity.INFO}
                    errors.append(LintError(
                        file_path=filepath,
                        line=int(line_num),
                        column=int(col),
                        severity=severity_map.get(severity, Severity.ERROR),
                        code=code or 'mypy',
                        message=message.strip(),
                        tool='mypy'
                    ))
            return errors
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
    
    def _run_ruff(self, file_path: str, python_exec: str = None) -> List[LintError]:
        """Run ruff and parse output"""
        try:
            cmd = ['ruff', 'check', '--output-format=text', file_path]
            if python_exec:
                cmd = [python_exec, '-m', 'ruff', 'check', '--output-format=text', file_path]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            pattern = r'^(.+?):(\d+):(\d+):\s*([A-Z]\d+)\s+(.+)$'
            for line in result.stdout.splitlines():
                matches = self._parse_lint_line(line, pattern)
                if matches:
                    filepath, line_num, col, code, message = matches
                    errors.append(LintError(
                        file_path=filepath, line=int(line_num), column=int(col),
                        severity=Severity.WARNING, code=code, message=message.strip(), tool='ruff'
                    ))
            return errors
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
    
    def _run_pylint(self, file_path: str, python_exec: str = None) -> List[LintError]:
        """Run pylint and parse output"""
        try:
            cmd = ['pylint', '--output-format=text', '--score=n', file_path]
            if python_exec:
                cmd = [python_exec, '-m', 'pylint', '--output-format=text', '--score=n', file_path]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=20
            )
            
            errors = []
            pattern = r'^(.+?):(\d+):(\d+):\s*([A-Z]\d+):\s*(.+)$'
            
            for line in result.stdout.splitlines():
                match = re.match(pattern, line)
                if match:
                    filepath, line_num, col, code, message = match.groups()
                    
                    severity = Severity.INFO
                    if code.startswith('E'):
                        severity = Severity.ERROR
                    elif code.startswith('W'):
                        severity = Severity.WARNING
                    
                    errors.append(LintError(
                        file_path=filepath,
                        line=int(line_num),
                        column=int(col),
                        severity=severity,
                        code=code,
                        message=message.strip(),
                        tool='pylint'
                    ))
            
            return errors
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
    
    def _run_flake8(self, file_path: str, python_exec: str = None) -> List[LintError]:
        """Run flake8 and parse output"""
        try:
            cmd = ['flake8', file_path]
            if python_exec:
                cmd = [python_exec, '-m', 'flake8', file_path]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            errors = []
            pattern = r'^(.+?):(\d+):(\d+):\s*([A-Z]\d+)\s+(.+)$'
            
            for line in result.stdout.splitlines():
                match = re.match(pattern, line)
                if match:
                    filepath, line_num, col, code, message = match.groups()
                    errors.append(LintError(
                        file_path=filepath,
                        line=int(line_num),
                        column=int(col),
                        severity=Severity.WARNING,
                        code=code,
                        message=message.strip(),
                        tool='flake8'
                    ))
            
            return errors
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return []
    
    def get_error_context(self, file_path: str, line: int, context_lines: int = 3) -> str:
        """
        Get code context around an error
        
        Args:
            file_path: Path to file
            line: Line number with error
            context_lines: Number of lines before/after to include
            
        Returns:
            Code snippet with context
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            start = max(0, line - context_lines - 1)
            end = min(len(lines), line + context_lines)
            
            context = []
            for i in range(start, end):
                marker = '→' if i == line - 1 else ' '
                context.append(f"{marker} {i+1:4d} | {lines[i].rstrip()}")
            
            return '\n'.join(context)
        except Exception:
            return ""
    
    def create_ai_explanation_prompt(self, error: LintError, code_context: str) -> str:
        """
        Create a prompt for AI to explain an error
        
        Args:
            error: The lint error
            code_context: Code context around the error
            
        Returns:
            Prompt for AI model
        """
        prompt = f"""Explain this Python linting error and suggest how to fix it:

Error: {error.message}
Tool: {error.tool}
Code: {error.code}
Location: Line {error.line}, Column {error.column}

Code context:
```python
{code_context}
```

Please provide:
1. A clear explanation of what this error means
2. Why it's a problem
3. How to fix it with a code example
4. Best practices to avoid this error in the future

Keep the explanation concise and practical.
"""
        return prompt
    
    def create_ai_fix_prompt(self, error: LintError, code_context: str, full_code: str) -> str:
        """
        Create a prompt for AI to fix an error
        
        Args:
            error: The lint error
            code_context: Code context around the error
            full_code: Full file content
            
        Returns:
            Prompt for AI model to generate a fix
        """
        prompt = f"""Fix this Python linting error:

Error: {error.message}
Tool: {error.tool}
Code: {error.code}
Location: Line {error.line}, Column {error.column}

Full code:
```python
{full_code}
```

Please provide the corrected code that fixes this error.
Wrap your response in <<<edit>>> tags.
"""
        return prompt
    
    def group_errors_by_file(self, errors: List[LintError]) -> Dict[str, List[LintError]]:
        """Group errors by file path"""
        grouped = {}
        for error in errors:
            if error.file_path not in grouped:
                grouped[error.file_path] = []
            grouped[error.file_path].append(error)
        return grouped
    
    def filter_errors(self, errors: List[LintError], 
                     severity: Optional[Severity] = None,
                     tool: Optional[str] = None) -> List[LintError]:
        """
        Filter errors by severity and/or tool
        
        Args:
            errors: List of errors to filter
            severity: Filter by severity level
            tool: Filter by tool name
            
        Returns:
            Filtered list of errors
        """
        filtered = errors
        
        if severity:
            filtered = [e for e in filtered if e.severity == severity]
        
        if tool:
            filtered = [e for e in filtered if e.tool == tool]
        
        return filtered
