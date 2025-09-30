"""
Code Smell Detection Engine
Detects the six main code smells in Python source code.
"""

import ast
import re
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class SmellResult:
    """Represents a detected code smell."""
    smell_type: str
    file_path: str
    line_start: int
    line_end: int
    severity: str
    message: str
    details: Dict[str, Any]

class CodeSmellDetector:
    """Main detector class that orchestrates all smell detection."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.detectors = {
            'LongMethod': LongMethodDetector(config.get('long_method', {})),
            'GodClass': GodClassDetector(config.get('god_class', {})),
            'DuplicatedCode': DuplicatedCodeDetector(config.get('duplicated_code', {})),
            'LargeParameterList': LargeParameterListDetector(config.get('large_parameter_list', {})),
            'MagicNumbers': MagicNumbersDetector(config.get('magic_numbers', {})),
            'FeatureEnvy': FeatureEnvyDetector(config.get('feature_envy', {}))
        }
    
    def detect_smells(self, file_path: str, source_code: str, enabled_smells: Set[str] = None) -> List[SmellResult]:
        """Detect all enabled code smells in the given source code."""
        if enabled_smells is None:
            enabled_smells = set(self.detectors.keys())
        
        results = []
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return [SmellResult(
                smell_type="SyntaxError",
                file_path=file_path,
                line_start=e.lineno or 1,
                line_end=e.lineno or 1,
                severity="error",
                message=f"Syntax error: {e.msg}",
                details={}
            )]
        
        for smell_name, detector in self.detectors.items():
            if smell_name in enabled_smells:
                smell_results = detector.detect(file_path, source_code, tree)
                results.extend(smell_results)
        
        return results

class LongMethodDetector:
    """Detects methods that are too long."""
    
    def __init__(self, config: Dict[str, Any]):
        self.sloc_threshold = config.get('sloc', 30)
        self.cyclomatic_threshold = config.get('cyclomatic', 12)
    
    def detect(self, file_path: str, source_code: str, tree: ast.AST) -> List[SmellResult]:
        results = []
        lines = source_code.split('\n')
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Calculate SLOC (Source Lines of Code)
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                
                # Count non-empty, non-comment lines
                sloc = 0
                for i in range(start_line - 1, min(end_line, len(lines))):
                    line = lines[i].strip()
                    if line and not line.startswith('#'):
                        sloc += 1
                
                # Calculate cyclomatic complexity
                complexity = self._calculate_complexity(node)
                
                if sloc > self.sloc_threshold or complexity > self.cyclomatic_threshold:
                    severity = "high" if sloc > self.sloc_threshold * 1.5 else "medium"
                    
                    results.append(SmellResult(
                        smell_type="LongMethod",
                        file_path=file_path,
                        line_start=start_line,
                        line_end=end_line,
                        severity=severity,
                        message=f"Method '{node.name}' is too long (SLOC: {sloc}, Complexity: {complexity})",
                        details={
                            'method_name': node.name,
                            'sloc': sloc,
                            'cyclomatic_complexity': complexity,
                            'sloc_threshold': self.sloc_threshold,
                            'complexity_threshold': self.cyclomatic_threshold
                        }
                    ))
        
        return results
    
    def _calculate_complexity(self, node: ast.AST) -> int:
        """Calculate cyclomatic complexity of a function."""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With, ast.AsyncWith):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

class GodClassDetector:
    """Detects classes with too many responsibilities."""
    
    def __init__(self, config: Dict[str, Any]):
        self.max_methods = config.get('max_methods', 20)
        self.max_fields = config.get('max_fields', 15)
        self.max_coupling = config.get('max_coupling', 15)
    
    def detect(self, file_path: str, source_code: str, tree: ast.AST) -> List[SmellResult]:
        results = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = []
                fields = set()
                external_dependencies = set()
                
                # Count methods and analyze dependencies
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        methods.append(item.name)
                        
                        # Analyze method for external dependencies
                        for child in ast.walk(item):
                            if isinstance(child, ast.Attribute):
                                if isinstance(child.value, ast.Name) and child.value.id != 'self':
                                    external_dependencies.add(child.value.id)
                    
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                fields.add(target.id)
                
                # Check for __init__ method to count instance variables
                for method in node.body:
                    if isinstance(method, ast.FunctionDef) and method.name == '__init__':
                        for child in ast.walk(method):
                            if isinstance(child, ast.Assign):
                                for target in child.targets:
                                    if isinstance(target, ast.Attribute) and isinstance(target.value, ast.Name) and target.value.id == 'self':
                                        fields.add(target.attr)
                
                method_count = len(methods)
                field_count = len(fields)
                coupling = len(external_dependencies)
                
                if method_count > self.max_methods or field_count > self.max_fields or coupling > self.max_coupling:
                    severity = "high" if method_count > self.max_methods * 1.5 else "medium"
                    
                    results.append(SmellResult(
                        smell_type="GodClass",
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        severity=severity,
                        message=f"Class '{node.name}' has too many responsibilities (Methods: {method_count}, Fields: {field_count}, Coupling: {coupling})",
                        details={
                            'class_name': node.name,
                            'method_count': method_count,
                            'field_count': field_count,
                            'coupling': coupling,
                            'methods': methods,
                            'thresholds': {
                                'max_methods': self.max_methods,
                                'max_fields': self.max_fields,
                                'max_coupling': self.max_coupling
                            }
                        }
                    ))
        
        return results

class DuplicatedCodeDetector:
    """Detects duplicated code blocks."""
    
    def __init__(self, config: Dict[str, Any]):
        self.shingle_size = config.get('shingle_size', 30)
        self.similarity_threshold = config.get('similarity', 0.90)
        self.min_chunk_tokens = config.get('min_chunk_tokens', 80)
    
    def detect(self, file_path: str, source_code: str, tree: ast.AST) -> List[SmellResult]:
        results = []
        lines = source_code.split('\n')
        
        # Extract code blocks (methods and classes)
        code_blocks = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                start_line = node.lineno
                end_line = node.end_lineno or start_line
                
                block_lines = []
                for i in range(start_line - 1, min(end_line, len(lines))):
                    line = lines[i].strip()
                    if line and not line.startswith('#'):
                        block_lines.append(line)
                
                if len(block_lines) >= 5:  # Only consider blocks with at least 5 lines
                    code_blocks.append({
                        'name': node.name,
                        'type': type(node).__name__,
                        'start_line': start_line,
                        'end_line': end_line,
                        'lines': block_lines,
                        'tokens': self._tokenize_code(' '.join(block_lines))
                    })
        
        # Compare blocks for similarity
        for i, block1 in enumerate(code_blocks):
            for j, block2 in enumerate(code_blocks[i+1:], i+1):
                similarity = self._calculate_similarity(block1['tokens'], block2['tokens'])
                
                if similarity >= self.similarity_threshold:
                    results.append(SmellResult(
                        smell_type="DuplicatedCode",
                        file_path=file_path,
                        line_start=min(block1['start_line'], block2['start_line']),
                        line_end=max(block1['end_line'], block2['end_line']),
                        severity="medium",
                        message=f"Duplicated code detected between '{block1['name']}' and '{block2['name']}' (similarity: {similarity:.2%})",
                        details={
                            'block1': {
                                'name': block1['name'],
                                'type': block1['type'],
                                'start_line': block1['start_line'],
                                'end_line': block1['end_line']
                            },
                            'block2': {
                                'name': block2['name'],
                                'type': block2['type'],
                                'start_line': block2['start_line'],
                                'end_line': block2['end_line']
                            },
                            'similarity': similarity
                        }
                    ))
        
        return results
    
    def _tokenize_code(self, code: str) -> List[str]:
        """Tokenize code into meaningful tokens."""
        # Remove comments and normalize whitespace
        code = re.sub(r'#.*', '', code)
        code = re.sub(r'\s+', ' ', code)
        
        # Split into tokens
        tokens = re.findall(r'\w+|[^\w\s]', code)
        return [token.lower() for token in tokens if token.strip()]
    
    def _calculate_similarity(self, tokens1: List[str], tokens2: List[str]) -> float:
        """Calculate similarity between two token lists using Jaccard similarity."""
        if not tokens1 or not tokens2:
            return 0.0
        
        set1 = set(tokens1)
        set2 = set(tokens2)
        
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        return intersection / union if union > 0 else 0.0

class LargeParameterListDetector:
    """Detects methods with too many parameters."""
    
    def __init__(self, config: Dict[str, Any]):
        self.max_params = config.get('params', 6)
    
    def detect(self, file_path: str, source_code: str, tree: ast.AST) -> List[SmellResult]:
        results = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                # Count parameters (excluding self)
                param_count = len(node.args.args)
                if node.args.args and node.args.args[0].arg == 'self':
                    param_count -= 1
                
                # Add varargs and kwargs
                if node.args.vararg:
                    param_count += 1
                if node.args.kwarg:
                    param_count += 1
                
                if param_count > self.max_params:
                    severity = "high" if param_count > self.max_params * 1.5 else "medium"
                    
                    param_names = [arg.arg for arg in node.args.args]
                    if node.args.vararg:
                        param_names.append(f"*{node.args.vararg.arg}")
                    if node.args.kwarg:
                        param_names.append(f"**{node.args.kwarg.arg}")
                    
                    results.append(SmellResult(
                        smell_type="LargeParameterList",
                        file_path=file_path,
                        line_start=node.lineno,
                        line_end=node.end_lineno or node.lineno,
                        severity=severity,
                        message=f"Method '{node.name}' has too many parameters ({param_count})",
                        details={
                            'method_name': node.name,
                            'parameter_count': param_count,
                            'parameters': param_names,
                            'threshold': self.max_params
                        }
                    ))
        
        return results

class MagicNumbersDetector:
    """Detects magic numbers in code."""
    
    def __init__(self, config: Dict[str, Any]):
        self.min_occurrences = config.get('min_occurrences', 3)
        self.whitelist = set(config.get('whitelist', [0, 1, -1]))
    
    def detect(self, file_path: str, source_code: str, tree: ast.AST) -> List[SmellResult]:
        results = []
        number_occurrences = defaultdict(list)
        
        # Collect all numeric literals
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                if node.value not in self.whitelist:
                    number_occurrences[node.value].append({
                        'line': node.lineno,
                        'col': node.col_offset
                    })
        
        # Find magic numbers (numbers that appear multiple times)
        for number, occurrences in number_occurrences.items():
            if len(occurrences) >= self.min_occurrences:
                lines = [occ['line'] for occ in occurrences]
                
                results.append(SmellResult(
                    smell_type="MagicNumbers",
                    file_path=file_path,
                    line_start=min(lines),
                    line_end=max(lines),
                    severity="medium",
                    message=f"Magic number {number} appears {len(occurrences)} times",
                    details={
                        'number': number,
                        'occurrences': len(occurrences),
                        'locations': occurrences,
                        'threshold': self.min_occurrences
                    }
                ))
        
        return results

class FeatureEnvyDetector:
    """Detects methods that use other classes' data more than their own."""
    
    def __init__(self, config: Dict[str, Any]):
        self.min_sloc = config.get('min_sloc', 10)
        self.foreign_access_ratio = config.get('foreign_access_ratio', 1.5)
        self.min_foreign_accesses = config.get('min_foreign_accesses', 3)
    
    def detect(self, file_path: str, source_code: str, tree: ast.AST) -> List[SmellResult]:
        results = []
        
        # Find all classes and their methods
        classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes[node.name] = {
                    'node': node,
                    'methods': [],
                    'fields': set()
                }
                
                # Collect class methods and fields
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        classes[node.name]['methods'].append(item)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                classes[node.name]['fields'].add(target.id)
        
        # Analyze each method for feature envy
        for class_name, class_info in classes.items():
            for method in class_info['methods']:
                if method.name == '__init__':
                    continue
                
                # Count lines of code
                lines = source_code.split('\n')
                start_line = method.lineno
                end_line = method.end_lineno or start_line
                
                sloc = 0
                for i in range(start_line - 1, min(end_line, len(lines))):
                    line = lines[i].strip()
                    if line and not line.startswith('#'):
                        sloc += 1
                
                if sloc < self.min_sloc:
                    continue
                
                # Count self vs foreign accesses
                self_accesses = 0
                foreign_accesses = defaultdict(int)
                
                for node in ast.walk(method):
                    if isinstance(node, ast.Attribute):
                        if isinstance(node.value, ast.Name):
                            if node.value.id == 'self':
                                self_accesses += 1
                            else:
                                foreign_accesses[node.value.id] += 1
                
                total_foreign = sum(foreign_accesses.values())
                
                if (total_foreign >= self.min_foreign_accesses and 
                    self_accesses > 0 and 
                    total_foreign / self_accesses >= self.foreign_access_ratio):
                    
                    most_envied = max(foreign_accesses.items(), key=lambda x: x[1]) if foreign_accesses else ("unknown", 0)
                    
                    results.append(SmellResult(
                        smell_type="FeatureEnvy",
                        file_path=file_path,
                        line_start=start_line,
                        line_end=end_line,
                        severity="medium",
                        message=f"Method '{method.name}' in class '{class_name}' shows feature envy (foreign: {total_foreign}, self: {self_accesses})",
                        details={
                            'method_name': method.name,
                            'class_name': class_name,
                            'self_accesses': self_accesses,
                            'foreign_accesses': total_foreign,
                            'most_envied_class': most_envied[0],
                            'most_envied_count': most_envied[1],
                            'ratio': total_foreign / self_accesses if self_accesses > 0 else float('inf'),
                            'threshold_ratio': self.foreign_access_ratio
                        }
                    ))
        
        return results
