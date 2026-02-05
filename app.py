from flask import Flask, request, render_template_string
import ast
import operator
import re

app = Flask(__name__)

# Safe mathematical operations
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
}

def safe_eval(expression):
    """
    Safely evaluate mathematical expressions without using eval()
    """
    try:
        # Remove whitespace
        expression = expression.strip()
        
        # Debug logging
        print(f"DEBUG: Received expression: '{expression}'")
        print(f"DEBUG: Expression repr: {repr(expression)}")
        print(f"DEBUG: Expression length: {len(expression)}")
        
        # Basic validation
        if not expression:
            print("DEBUG: Empty expression")
            return None, "Empty expression"
        
        # Check for invalid characters (allow digits, operators, parentheses, decimals, spaces)
        pattern = r'^[\d\+\-\*/\(\)\.\s%]+$'
        if not re.match(pattern, expression):
            print(f"DEBUG: Failed regex match with pattern: {pattern}")
            for i, char in enumerate(expression):
                print(f"  Char {i}: '{char}' (ord={ord(char)})")
            return None, "Invalid characters in expression"
        
        print("DEBUG: Passed regex validation")
        
        # Parse the expression into an AST
        node = ast.parse(expression, mode='eval')
        print(f"DEBUG: Successfully parsed AST")
        print(f"DEBUG: AST dump: {ast.dump(node.body)}")
        
        # Evaluate the AST safely
        result = _eval_node(node.body)
        print(f"DEBUG: Evaluation result: {result}")
        
        # Format result nicely
        if isinstance(result, float):
            if result.is_integer():
                return int(result), None
            else:
                return round(result, 10), None
        return result, None
        
    except ZeroDivisionError:
        print("DEBUG: Division by zero")
        return None, "Division by zero"
    except Exception as e:
        print(f"DEBUG: Exception: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return None, "Invalid expression"

def _eval_node(node):
    """
    Recursively evaluate AST nodes
    """
    print(f"DEBUG: Evaluating node type: {type(node).__name__}")
    
    # Handle both ast.Num (Python <3.8) and ast.Constant (Python 3.8+)
    if isinstance(node, ast.Constant):
        print(f"DEBUG: Found Constant with value: {node.value}")
        return node.value
    elif isinstance(node, ast.Num):  # For backwards compatibility
        print(f"DEBUG: Found Num with value: {node.n}")
        return node.n
    elif isinstance(node, ast.BinOp):
        print(f"DEBUG: Found BinOp with operator: {type(node.op).__name__}")
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError("Unsupported operation")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        result = SAFE_OPERATORS[op_type](left, right)
        print(f"DEBUG: BinOp result: {left} {type(node.op).__name__} {right} = {result}")
        return result
    elif isinstance(node, ast.UnaryOp):
        print(f"DEBUG: Found UnaryOp with operator: {type(node.op).__name__}")
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError("Unsupported operation")
        operand = _eval_node(node.operand)
        result = SAFE_OPERATORS[op_type](operand)
        print(f"DEBUG: UnaryOp result: {result}")
        return result
    else:
        print(f"DEBUG: Unsupported node type: {type(node).__name__}")
        raise ValueError("Unsupported expression")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Debug Calculator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h2 { color: #333; }
        input[type="text"] {
            width: 100%;
            padding: 10px;
            font-size: 16px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 5px;
        }
        button {
            width: 100%;
            padding: 12px;
            font-size: 16px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        button:hover { background: #45a049; }
        .result {
            margin-top: 20px;
            padding: 15px;
            background: #e7f4e7;
            border-left: 4px solid #4CAF50;
            border-radius: 5px;
        }
        .error {
            background: #ffe7e7;
            border-left-color: #f44336;
        }
        .debug {
            margin-top: 20px;
            padding: 15px;
            background: #f9f9f9;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-family: monospace;
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>🐛 Debug Calculator</h2>
        <p>Check browser console and terminal for debug output</p>
        
        <form method="post">
            <input 
                type="text" 
                name="expression" 
                placeholder="Enter expression (e.g., 23+44)"
                value="{{ expression or '' }}"
                autofocus
            >
            <button type="submit">Calculate</button>
        </form>
        
        {% if error %}
            <div class="result error">
                <strong>Error:</strong> {{ error }}
            </div>
        {% elif result is not none %}
            <div class="result">
                <strong>Result:</strong> {{ result }}
            </div>
        {% endif %}
        
        <div class="debug">
            <strong>Quick Tests:</strong><br>
            Try: 23+44, 2+3*5, 2**8, (10+5)/3
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def calculator():
    result = None
    error = None
    expression = None
    
    if request.method == "POST":
        expression = request.form.get("expression", "")
        print(f"\n{'='*60}")
        print(f"NEW REQUEST")
        print(f"{'='*60}")
        result, error = safe_eval(expression)
        print(f"FINAL - Result: {result}, Error: {error}")
        print(f"{'='*60}\n")
    
    return render_template_string(
        HTML, 
        result=result, 
        error=error,
        expression=expression
    )

if __name__ == "__main__":
    print("Starting debug calculator on http://localhost:5000")
    print("Watch this terminal for debug output...")
    app.run(host="0.0.0.0", port=5000, debug=True)
