"""
Docstring Generator for Python code
Analyzes code and generates comprehensive docstrings
"""

import ast
import re
from typing import Optional, Dict, List
from dataclasses import dataclass


@dataclass
class FunctionInfo:
    """Information about a function for docstring generation"""
    name: str
    args: List[str]
    returns: Optional[str]
    decorators: List[str]
    is_async: bool
    line_number: int


@dataclass
class ClassInfo:
    """Information about a class for docstring generation"""
    name: str
    bases: List[str]
    methods: List[FunctionInfo]
    line_number: int


class DocstringGenerator:
    """Generate docstrings for Python code using AI"""
    
    DOCSTRING_STYLES = {
        'google': 'Google Style',
        'numpy': 'NumPy Style',
        'sphinx': 'Sphinx Style',
        'pep257': 'PEP 257 Style'
    }
    
    def __init__(self, style: str = 'google'):
        """
        Initialize docstring generator
        
        Args:
            style: Docstring style to use (google, numpy, sphinx, pep257)
        """
        if style not in self.DOCSTRING_STYLES:
            raise ValueError(f"Invalid style. Choose from: {list(self.DOCSTRING_STYLES.keys())}")
        self.style = style
    
    def analyze_code(self, code: str) -> Dict:
        """
        Analyzes Python code to extract top-level functions and classes efficiently.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return {'error': f'Syntax error: {e}', 'functions': [], 'classes': []}
        
        functions = []
        classes = []
        
        # Only analyze top-level nodes for better performance and structural clarity
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                functions.append(self._extract_function_info(node))
            elif isinstance(node, ast.ClassDef):
                classes.append(self._extract_class_info(node))
        
        return {'functions': functions, 'classes': classes}
    
    def _extract_function_info(self, node) -> FunctionInfo:
        """Extract information from a function AST node"""
        args = [arg.arg for arg in node.args.args]
        
        returns = None
        if node.returns:
            returns = ast.unparse(node.returns) if hasattr(ast, 'unparse') else 'Any'
        
        decorators = []
        for decorator in node.decorator_list:
            if hasattr(ast, 'unparse'):
                decorators.append(ast.unparse(decorator))
            elif isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
        
        return FunctionInfo(
            name=node.name,
            args=args,
            returns=returns,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
            line_number=node.lineno
        )
    
    def _extract_class_info(self, node) -> ClassInfo:
        """Extract information from a class AST node"""
        bases = []
        for base in node.bases:
            if hasattr(ast, 'unparse'):
                bases.append(ast.unparse(base))
            elif isinstance(base, ast.Name):
                bases.append(base.id)
        
        methods = []
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(self._extract_function_info(item))
        
        return ClassInfo(
            name=node.name,
            bases=bases,
            methods=methods,
            line_number=node.lineno
        )
    
    def generate_function_docstring(self, func_info: FunctionInfo, code_context: str = "") -> str:
        """
        Generates a docstring for a function or method using the configured style.
        """
        handlers = {
            'google': self._generate_google_function_docstring,
            'numpy': self._generate_numpy_function_docstring,
            'sphinx': self._generate_sphinx_function_docstring,
            'pep257': self._generate_pep257_function_docstring
        }
        handler = handlers.get(self.style, self._generate_google_function_docstring)
        return handler(func_info)
    
    def _generate_google_function_docstring(self, func_info: FunctionInfo) -> str:
        """Generate Google-style docstring"""
        lines = ['"""']
        
        lines.append(f"{func_info.name.replace('_', ' ').title()}")
        lines.append("")
        
        if func_info.args:
            args = [arg for arg in func_info.args if arg not in ('self', 'cls')]
            if args:
                lines.append("Args:")
                for arg in args:
                    lines.append(f"    {arg}: Description of {arg}")
                lines.append("")
        
        if func_info.returns:
            lines.append("Returns:")
            lines.append(f"    {func_info.returns}: Description of return value")
            lines.append("")
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _generate_numpy_function_docstring(self, func_info: FunctionInfo) -> str:
        """Generate NumPy-style docstring"""
        lines = ['"""']
        lines.append(f"{func_info.name.replace('_', ' ').title()}")
        lines.append("")
        
        if func_info.args:
            args = [arg for arg in func_info.args if arg not in ('self', 'cls')]
            if args:
                lines.append("Parameters")
                lines.append("----------")
                for arg in args:
                    lines.append(f"{arg} : type")
                    lines.append(f"    Description of {arg}")
                lines.append("")
        
        if func_info.returns:
            lines.append("Returns")
            lines.append("-------")
            lines.append(f"{func_info.returns}")
            lines.append("    Description of return value")
            lines.append("")
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _generate_sphinx_function_docstring(self, func_info: FunctionInfo) -> str:
        """Generate Sphinx-style docstring"""
        lines = ['"""']
        lines.append(f"{func_info.name.replace('_', ' ').title()}")
        lines.append("")
        
        if func_info.args:
            args = [arg for arg in func_info.args if arg not in ('self', 'cls')]
            for arg in args:
                lines.append(f":param {arg}: Description of {arg}")
                lines.append(f":type {arg}: type")
        
        if func_info.returns:
            lines.append(f":return: Description of return value")
            lines.append(f":rtype: {func_info.returns}")
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def _generate_pep257_function_docstring(self, func_info: FunctionInfo) -> str:
        """Generate PEP 257-style docstring"""
        return f'"""{func_info.name.replace("_", " ").title()}."""'
    
    def generate_class_docstring(self, class_info: ClassInfo) -> str:
        """
        Generate docstring for a class
        
        Args:
            class_info: Class information
            
        Returns:
            Generated docstring
        """
        lines = ['"""']
        lines.append(f"{class_info.name}")
        lines.append("")
        
        if class_info.bases:
            lines.append(f"Inherits from: {', '.join(class_info.bases)}")
            lines.append("")
        
        if class_info.methods:
            lines.append("Methods:")
            for method in class_info.methods:
                if not method.name.startswith('_'):
                    args_str = ', '.join(method.args)
                    lines.append(f"    {method.name}({args_str})")
            lines.append("")
        
        lines.append('"""')
        return '\n'.join(lines)
    
    def create_ai_prompt_for_docstring(self, func_info: FunctionInfo, code: str) -> str:
        """
        Create an AI prompt to generate a better docstring
        
        Args:
            func_info: Function information
            code: The actual function code
            
        Returns:
            Prompt for AI model
        """
        prompt = f"""Generate a comprehensive {self.DOCSTRING_STYLES[self.style]} docstring for this Python function:

```python
{code}
```

Function name: {func_info.name}
Arguments: {', '.join(func_info.args)}
Returns: {func_info.returns or 'None'}
Is async: {func_info.is_async}

Please provide:
1. A clear, concise description of what the function does
2. Detailed parameter descriptions with types
3. Return value description with type
4. Any exceptions that might be raised
5. Usage examples if appropriate

Format the docstring in {self.DOCSTRING_STYLES[self.style]} format.
"""
        return prompt
    
    def insert_docstring_into_code(self, code: str, line_number: int, docstring: str, indent_level: int = 1) -> str:
        """
        Insert a docstring into code at the specified line
        
        Args:
            code: Original code
            line_number: Line number where to insert (after function/class definition)
            docstring: The docstring to insert
            indent_level: Indentation level (number of tabs/4 spaces)
            
        Returns:
            Modified code with docstring inserted
        """
        lines = code.split('\n')
        
        indent = '    ' * indent_level
        
        docstring_lines = docstring.split('\n')
        indented_docstring = '\n'.join([indent + line if line.strip() else '' for line in docstring_lines])
        
        if line_number < len(lines):
            lines.insert(line_number, indented_docstring)
        
        return '\n'.join(lines)
    
    def find_missing_docstrings(self, code: str) -> List[Dict]:
        """
        Find all functions and classes missing docstrings
        
        Args:
            code: Python source code
            
        Returns:
            List of items missing docstrings with their info
        """
        missing = []
        
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return missing
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                has_docstring = (
                    node.body and
                    isinstance(node.body[0], ast.Expr) and
                    isinstance(node.body[0].value, ast.Constant) and
                    isinstance(node.body[0].value.value, str)
                )
                
                if not has_docstring:
                    item_type = 'class' if isinstance(node, ast.ClassDef) else 'function'
                    missing.append({
                        'type': item_type,
                        'name': node.name,
                        'line': node.lineno,
                        'is_async': isinstance(node, ast.AsyncFunctionDef)
                    })
        
        return missing
