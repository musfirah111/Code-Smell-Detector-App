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
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        
        return complexity

class GodClassDetector:
    """Detect God Class (Blob) using ATFD/WMC/TCC criteria.
    Detection rule (Marinescu): (ATFD > Few) AND (WMC >= Very High) AND (TCC < One Third)
    - ATFD (Access To Foreign Data): count of foreign attribute accesses across class methods
    - WMC  (Weighted Method Count): sum of cyclomatic complexities of all methods
    - TCC  (Tight Class Cohesion): fraction of method pairs that share at least one self field
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Threshold defaults from literature; allow override via config
        self.atfd_few = config.get('atfd_few', 2)              # Few ∈ [2..5]; choose upper bound 5 by default
        self.wmc_very_high = config.get('wmc_very_high', 10)    # Very High (per metrics-in-practice)
        self.tcc_one_third = config.get('tcc_one_third', 0.6) # One Third
    
    def detect(self, file_path: str, source_code: str, tree: ast.AST) -> List[SmellResult]:
        results = []
        
        for class_node in ast.walk(tree):
            if not isinstance(class_node, ast.ClassDef):
                continue
            
            method_nodes: List[ast.AST] = []
            # For each method, track self attributes used (for TCC) and complexity (for WMC)
            method_self_attrs: Dict[str, Set[str]] = {}
            wmc_sum = 0
            atfd_count = 0
            
            for item in class_node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    method_nodes.append(item)
                    # Compute cyclomatic complexity for WMC
                    wmc_sum += self._cyclomatic_complexity(item)
                    # Collect self attrs used by this method
                    self_attrs: Set[str] = set()
                    for n in ast.walk(item):
                        if isinstance(n, ast.Attribute) and isinstance(n.value, ast.Name):
                            if n.value.id == 'self':
                                # self.<attr>
                                self_attrs.add(n.attr)
                            else:
                                # foreign_obj.<attr> contributes to ATFD
                                atfd_count += 1
                    method_self_attrs[item.name] = self_attrs
            
            # Compute TCC: proportion of method pairs that share at least one self field
            tcc = self._compute_tcc(method_self_attrs)
            
            # Apply rule: (ATFD > Few) AND (WMC >= Very High) AND (TCC < One Third)
            if atfd_count > self.atfd_few and wmc_sum >= self.wmc_very_high and tcc < self.tcc_one_third:
                results.append(SmellResult(
                    smell_type="GodClass",
                    file_path=file_path,
                    line_start=class_node.lineno,
                    line_end=class_node.end_lineno or class_node.lineno,
                    severity="high",
                    message=(
                        f"Class '{class_node.name}' flagged as God Class "
                        f"(ATFD={atfd_count} > {self.atfd_few}, "
                        f"WMC={wmc_sum} >= {self.wmc_very_high}, "
                        f"TCC={tcc:.2f} < {self.tcc_one_third})"
                    ),
                    details={
                        'class_name': class_node.name,
                        'metrics': {
                            'ATFD': atfd_count,
                            'WMC': wmc_sum,
                            'TCC': tcc,
                        },
                        'thresholds': {
                            'ATFD_Few': self.atfd_few,
                            'WMC_Very_High': self.wmc_very_high,
                            'TCC_One_Third': self.tcc_one_third,
                        },
                        'methods': [m.name for m in method_nodes],
                    }
                ))
        
        return results
    
    def _cyclomatic_complexity(self, func_node: ast.AST) -> int:
        """Compute cyclomatic complexity for a single function/method.
        Mirrors the logic used in LongMethodDetector for consistency.
        """
        complexity = 1
        for child in ast.walk(func_node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += max(0, len(child.values) - 1)
        return complexity
    
    def _compute_tcc(self, method_self_attrs: Dict[str, Set[str]]) -> float:
        """Compute TCC = connected_method_pairs / total_method_pairs.
        Two methods are connected if they share at least one self field accessed.
        If fewer than 2 methods, define TCC = 1.0 (trivially cohesive).
        """
        names = list(method_self_attrs.keys())
        n = len(names)
        if n < 2:
            return 1.0
        total_pairs = n * (n - 1) // 2
        connected = 0
        for i in range(n):
            for j in range(i + 1, n):
                if method_self_attrs[names[i]] & method_self_attrs[names[j]]:
                    connected += 1
        return connected / total_pairs if total_pairs > 0 else 1.0

class DuplicatedCodeDetector:
    """Detects duplicated code blocks."""
    
    def __init__(self, config: Dict[str, Any]):
        # Only the essential knob used for both clone types
        self.min_block_lines = config.get('min_block_lines', 3)
    
    def detect(self, file_path: str, source_code: str, tree: ast.AST) -> List[SmellResult]:
        results = []
        lines = source_code.split('\n')
        
        # Extract code blocks (functions/classes and significant inner blocks)
        code_blocks = []

        def add_block(name: str, node: ast.AST):
            start_line = getattr(node, 'lineno', None)
            end_line = getattr(node, 'end_lineno', start_line)
            if start_line is None:
                return
            block_lines = []
            for i in range(start_line - 1, min(end_line, len(lines))):
                line = lines[i].strip()
                if line and not line.startswith('#'):
                    block_lines.append(line)
            if len(block_lines) < self.min_block_lines:
                return
            joined = '\n'.join(block_lines)
            code_blocks.append({
                'name': name,
                'type': type(node).__name__,
                'start_line': start_line,
                'end_line': end_line,
                'lines': block_lines,
                'exact_sig': self._normalize_exact(joined),
                'renamed_sig': self._normalize_with_placeholders(joined),
            })

        def walk_function(func: ast.AST):
            # Whole function as a block
            add_block(getattr(func, 'name', 'function'), func)
            # Significant inner blocks commonly duplicated
            for inner in ast.walk(func):
                if isinstance(inner, (ast.For, ast.While, ast.If)):
                    name = f"{getattr(func, 'name', 'function')}:{type(inner).__name__}@{inner.lineno}"
                    add_block(name, inner)

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                walk_function(node)
            elif isinstance(node, ast.ClassDef):
                add_block(node.name, node)
        
        # 1) Exact duplicates (ignoring whitespace/comments)
        seen_exact: Dict[str, List[int]] = {}
        for idx, blk in enumerate(code_blocks):
            seen_exact.setdefault(blk['exact_sig'], []).append(idx)
        for indices in seen_exact.values():
            if len(indices) > 1:
                # Pairwise report but avoid duplicates by only (i<j)
                for a in range(len(indices)):
                    for b in range(a + 1, len(indices)):
                        i = indices[a]
                        j = indices[b]
                        b1 = code_blocks[i]
                        b2 = code_blocks[j]
                        results.append(SmellResult(
                            smell_type="DuplicatedCode",
                            file_path=file_path,
                            line_start=min(b1['start_line'], b2['start_line']),
                            line_end=max(b1['end_line'], b2['end_line']),
                            severity="medium",
                            message=f"Duplicated code detected between '{self._clean_name(b1['name'])}' and '{self._clean_name(b2['name'])}'",
                            details={
                                'block1_name': self._clean_name(b1['name']),
                                'block1_type': b1['type'],
                                'block1_start_line': b1['start_line'],
                                'block1_end_line': b1['end_line'],
                                'block2_name': self._clean_name(b2['name']),
                                'block2_type': b2['type'],
                                'block2_start_line': b2['start_line'],
                                'block2_end_line': b2['end_line']
                            }
                        ))
        
        # 2) Syntactically identical except for identifiers/literals/types
        seen_renamed: Dict[str, List[int]] = {}
        for idx, blk in enumerate(code_blocks):
            seen_renamed.setdefault(blk['renamed_sig'], []).append(idx)
        for indices in seen_renamed.values():
            if len(indices) > 1:
                for a in range(len(indices)):
                    for b in range(a + 1, len(indices)):
                        i = indices[a]
                        j = indices[b]
                        b1 = code_blocks[i]
                        b2 = code_blocks[j]
                        # Skip ones already reported as exact duplicates
                        if b1['exact_sig'] == b2['exact_sig']:
                            continue
                        results.append(SmellResult(
                            smell_type="DuplicatedCode",
                            file_path=file_path,
                            line_start=min(b1['start_line'], b2['start_line']),
                            line_end=max(b1['end_line'], b2['end_line']),
                            severity="low",
                            message=f"Duplicated structure detected between '{self._clean_name(b1['name'])}' and '{self._clean_name(b2['name'])}'",
                            details={
                                'block1_name': self._clean_name(b1['name']),
                                'block1_type': b1['type'],
                                'block1_start_line': b1['start_line'],
                                'block1_end_line': b1['end_line'],
                                'block2_name': self._clean_name(b2['name']),
                                'block2_type': b2['type'],
                                'block2_start_line': b2['start_line'],
                                'block2_end_line': b2['end_line']
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

    def _normalize_exact(self, code: str) -> str:
        """Produce a canonical form ignoring comments and whitespace-only differences."""
        # Strip line comments
        code = re.sub(r'(?m)#.*$', '', code)
        # Collapse all whitespace to single spaces
        code = re.sub(r'\s+', ' ', code).strip()
        return code

    def _normalize_with_placeholders(self, code: str) -> str:
        """Produce a canonical form replacing identifiers and literals with placeholders.
        Keeps Python keywords intact so structure is preserved.
        """
        # Remove comments
        code = re.sub(r'(?m)#.*$', '', code)
        # Strings -> STR (simple heuristic, not a full parser)
        code = re.sub(r'(?:r|rb|rf|f|fr|b)?([\'\"])(?:\\.|(?!\1).)*\1', 'STR', code)
        # Numbers -> NUM
        code = re.sub(r'\b\d+(?:\.\d+)?\b', 'NUM', code)
        # Identifiers -> ID, but keep keywords
        keywords = {
            'def','class','return','if','elif','else','for','while','try','except','with','as','pass','break','continue',
            'and','or','not','in','is','from','import','lambda','yield','async','await','True','False','None'
        }
        def replace_identifier(match):
            word = match.group(0)
            return word if word in keywords else 'ID'
        code = re.sub(r'\b[A-Za-z_][A-Za-z0-9_]*\b', replace_identifier, code)
        # Normalize whitespace
        code = re.sub(r'\s+', ' ', code).strip()
        return code

    def _clean_name(self, name: str) -> str:
        """Clean generated block labels like 'func:For@102' to just 'func'."""
        try:
            if not isinstance(name, str):
                return str(name)
            # Strip trailing '@<line>' if present
            at_index = name.rfind('@')
            if at_index != -1 and name[at_index + 1:].isdigit():
                name = name[:at_index]
            # Strip ':<AstType>' if present
            if ':' in name:
                name = name.split(':', 1)[0]
            return name
        except Exception:
            return str(name)
    
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
    """Detect Feature Envy using ATFD, LAA, and FDP metrics (Marinescu, 2004).
    - ATFD (Access to Foreign Data): total number of foreign attribute accesses
    - LAA (Locality of Attribute Accesses): self_accesses / (self_accesses + foreign_accesses)
    - FDP (Foreign Data Providers): number of distinct foreign objects accessed
    A method is flagged if: ATFD > atfd_threshold AND LAA < laa_threshold AND FDP >= fdp_threshold.
    """
    
    def __init__(self, config: Dict[str, Any]):
        # Minimum method size in lines (non-empty, non-comment) to consider
        self.min_sloc = config.get('min_sloc', 10)
        # Thresholds for the three metrics (defaults from literature)
        self.atfd_threshold = config.get('atfd_threshold', 5)
        self.laa_threshold = config.get('laa_threshold', 0.33)
        self.fdp_threshold = config.get('fdp_threshold', 2)
    
    def detect(self, file_path: str, source_code: str, tree: ast.AST) -> List[SmellResult]:
        results = []
        
        # Build a map of class name -> { node, methods[], fields{} }
        classes = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                classes[node.name] = {
                    'node': node,
                    'methods': [],
                    'fields': set(),
                }
                # Collect class-level methods and fields
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        classes[node.name]['methods'].append(item)
                    elif isinstance(item, ast.Assign):
                        for target in item.targets:
                            if isinstance(target, ast.Name):
                                classes[node.name]['fields'].add(target.id)
        
        # Evaluate each method in each class
        for class_name, class_info in classes.items():
            for method in class_info['methods']:
                # Skip constructor
                if method.name == '__init__':
                    continue
                
                # Compute SLOC for the method (non-empty, non-comment lines only)
                lines = source_code.split('\n')
                start_line = method.lineno
                end_line = method.end_lineno or start_line
                sloc = 0
                for i in range(start_line - 1, min(end_line, len(lines))):
                    stripped = lines[i].strip()
                    if stripped and not stripped.startswith('#'):
                        sloc += 1
                if sloc < self.min_sloc:
                    continue
                
                # Count attribute accesses: self vs foreign (other variables)
                self_accesses = 0
                foreign_accesses = defaultdict(int)  # base_name -> count
                for node in ast.walk(method):
                    if isinstance(node, ast.Attribute) and isinstance(node.value, ast.Name):
                        if node.value.id == 'self':
                            self_accesses += 1
                        else:
                            foreign_accesses[node.value.id] += 1
                
                # Compute metrics
                atfd = sum(foreign_accesses.values())
                total_accesses = self_accesses + atfd
                laa = (self_accesses / total_accesses) if total_accesses > 0 else 0.0
                fdp = len(foreign_accesses)
                
                # Apply thresholds from Marinescu's rules
                if atfd > self.atfd_threshold and laa < self.laa_threshold and fdp >= self.fdp_threshold:
                    most_envied = max(foreign_accesses.items(), key=lambda x: x[1]) if foreign_accesses else ("unknown", 0)
                    results.append(SmellResult(
                        smell_type="FeatureEnvy",
                        file_path=file_path,
                        line_start=start_line,
                        line_end=end_line,
                        severity="medium",
                        message=(
                            f"Method '{method.name}' in class '{class_name}' shows Feature Envy "
                            f"(ATFD={atfd}, LAA={laa:.2f}, FDP={fdp})"
                        ),
                        details={
                            'method_name': method.name,
                            'class_name': class_name,
                            'sloc': sloc,
                            'atfd': atfd,
                            'laa': laa,
                            'fdp': fdp,
                            'most_envied_class': most_envied[0],
                            'most_envied_count': most_envied[1],
                            'thresholds': {
                                'min_sloc': self.min_sloc,
                                'atfd_threshold': self.atfd_threshold,
                                'laa_threshold': self.laa_threshold,
                                'fdp_threshold': self.fdp_threshold,
                            },
                        }
                    ))
        
        return results
