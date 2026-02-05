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
        
        # Basic validation
        if not expression:
            return None, "Empty expression"
        
        # Check for invalid characters (allow digits, operators, parentheses, decimals, spaces)
        if not re.match(r'^[\d\+\-\*/\(\)\.\s%]+$', expression):
            return None, "Invalid characters in expression"
        
        # Parse the expression into an AST
        node = ast.parse(expression, mode='eval')
        
        # Evaluate the AST safely
        result = _eval_node(node.body)
        
        # Format result nicely
        if isinstance(result, float):
            if result.is_integer():
                return int(result), None
            else:
                return round(result, 10), None
        return result, None
        
    except ZeroDivisionError:
        return None, "Division by zero"
    except Exception as e:
        return None, "Invalid expression"

def _eval_node(node):
    """
    Recursively evaluate AST nodes
    """
    # Handle both ast.Num (Python <3.8) and ast.Constant (Python 3.8+)
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.Num):  # For backwards compatibility
        return node.n
    elif isinstance(node, ast.BinOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError("Unsupported operation")
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        return SAFE_OPERATORS[op_type](left, right)
    elif isinstance(node, ast.UnaryOp):
        op_type = type(node.op)
        if op_type not in SAFE_OPERATORS:
            raise ValueError("Unsupported operation")
        operand = _eval_node(node.operand)
        return SAFE_OPERATORS[op_type](operand)
    else:
        raise ValueError("Unsupported expression")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Secure Calculator</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .calculator-container {
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            padding: 40px;
            max-width: 500px;
            width: 100%;
        }
        
        h2 {
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .subtitle {
            color: #666;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        
        form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        .input-group {
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        
        label {
            color: #555;
            font-weight: 500;
            font-size: 14px;
        }
        
        input[type="text"] {
            padding: 15px;
            font-size: 18px;
            border: 2px solid #e0e0e0;
            border-radius: 10px;
            transition: all 0.3s ease;
            font-family: 'Courier New', monospace;
        }
        
        input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        
        button {
            padding: 15px;
            font-size: 16px;
            font-weight: 600;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .result-container {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }
        
        .result-label {
            color: #666;
            font-size: 14px;
            margin-bottom: 5px;
        }
        
        .result-value {
            font-size: 32px;
            font-weight: bold;
            color: #333;
            font-family: 'Courier New', monospace;
            word-break: break-all;
        }
        
        .error {
            background: #fee;
            border-left-color: #e53e3e;
        }
        
        .error .result-value {
            color: #e53e3e;
            font-size: 18px;
        }
        
        .examples {
            margin-top: 20px;
            padding: 15px;
            background: #f0f4ff;
            border-radius: 10px;
            font-size: 13px;
            color: #555;
        }
        
        .examples strong {
            color: #667eea;
        }
        
        .examples code {
            background: white;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }
        
        .history {
            margin-top: 20px;
        }
        
        .history-title {
            font-size: 14px;
            color: #666;
            margin-bottom: 10px;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="calculator-container">
        <h2>🧮 Secure Web Calculator</h2>
        <p class="subtitle">Safe mathematical expression evaluator</p>
        
        <form method="post">
            <div class="input-group">
                <label for="expression">Enter Expression:</label>
                <input 
                    type="text" 
                    id="expression"
                    name="expression" 
                    placeholder="e.g., 2 + 3 * 5"
                    value="{{ expression or '' }}"
                    autofocus
                    autocomplete="off"
                >
            </div>
            <button type="submit">Calculate</button>
        </form>
        
        {% if error %}
            <div class="result-container error">
                <div class="result-label">Error:</div>
                <div class="result-value">{{ error }}</div>
            </div>
        {% elif result is not none %}
            <div class="result-container">
                <div class="result-label">Result:</div>
                <div class="result-value">{{ result }}</div>
            </div>
        {% endif %}
        
        <div class="examples">
            <strong>Examples:</strong><br>
            <code>2 + 3 * 5</code> → 17<br>
            <code>(10 + 5) / 3</code> → 5<br>
            <code>2 ** 8</code> → 256<br>
            <code>17 % 5</code> → 2<br>
            <code>100 // 3</code> → 33
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
        result, error = safe_eval(expression)
    
    return render_template_string(
        HTML, 
        result=result, 
        error=error,
        expression=expression
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
