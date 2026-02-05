from flask import Flask, request, render_template_string
import ast
import operator
import re

app = Flask(__name__)

# Allowed operators
SAFE_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.Mod: operator.mod,
    ast.FloorDiv: operator.floordiv,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

def safe_eval(expression):
    try:
        expression = expression.strip()

        if not expression:
            return None, "Empty expression"

        # Strict character validation
        if not re.fullmatch(r'[\d\.\+\-\*/%\(\)\s]+', expression):
            return None, "Invalid characters in expression"

        node = ast.parse(expression, mode="eval")

        result = _eval_node(node.body)

        if isinstance(result, float) and result.is_integer():
            result = int(result)

        return round(result, 10) if isinstance(result, float) else result, None

    except ZeroDivisionError:
        return None, "Division by zero"
    except Exception:
        return None, "Invalid expression"

def _eval_node(node):
    if isinstance(node, ast.Constant):
        if isinstance(node.value, (int, float)):
            return node.value
        raise ValueError("Only numbers are allowed")

    elif isinstance(node, ast.Num):  # Python < 3.8
        return node.n

    elif isinstance(node, ast.BinOp):
        op = type(node.op)
        if op not in SAFE_OPERATORS:
            raise ValueError("Unsupported operator")
        return SAFE_OPERATORS[op](
            _eval_node(node.left),
            _eval_node(node.right)
        )

    elif isinstance(node, ast.UnaryOp):
        op = type(node.op)
        if op not in SAFE_OPERATORS:
            raise ValueError("Unsupported unary operator")
        return SAFE_OPERATORS[op](_eval_node(node.operand))

    else:
        raise ValueError("Unsupported expression")

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Secure Calculator</title>
<style>
body{
    font-family: Arial;
    background: linear-gradient(135deg,#667eea,#764ba2);
    display:flex;
    justify-content:center;
    align-items:center;
    height:100vh;
}
.box{
    background:white;
    padding:30px;
    border-radius:15px;
    width:400px;
}
input,button{
    width:100%;
    padding:12px;
    margin-top:10px;
    font-size:16px;
}
.result{
    margin-top:20px;
    font-size:22px;
}
.error{
    color:red;
}
</style>
</head>
<body>
<div class="box">
<h2>🧮 Secure Calculator</h2>
<form method="post">
<input name="expression" placeholder="2 + 3 * 5" value="{{ expression or '' }}">
<button>Calculate</button>
</form>

{% if error %}
<div class="result error">{{ error }}</div>
{% elif result is not none %}
<div class="result">Result: {{ result }}</div>
{% endif %}
</div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def calculator():
    result = error = expression = None

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
