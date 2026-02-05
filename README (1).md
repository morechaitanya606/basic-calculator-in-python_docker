# Secure Web Calculator

A safe and modern Flask-based web calculator with an improved UI and security features.

## Key Improvements

### 🔒 Security Enhancements
- **Removed `eval()`**: The original code used `eval()` which is extremely dangerous as it can execute arbitrary Python code
- **Safe AST parsing**: Uses Python's Abstract Syntax Tree (AST) to safely parse and evaluate mathematical expressions
- **Input validation**: Validates expressions against allowed characters and operations
- **Whitelist approach**: Only allows specific mathematical operations

### ✨ Feature Improvements
- **Better error handling**: Specific error messages for different types of failures
- **Modern UI**: Beautiful gradient design with smooth animations
- **Responsive design**: Works on mobile and desktop devices
- **Input persistence**: Shows the previous expression after calculation
- **Example expressions**: Helps users understand what's supported
- **Better number formatting**: Removes unnecessary decimals for whole numbers

### 🎨 UI/UX Improvements
- Modern gradient background
- Clean card-based design
- Hover effects on buttons
- Focus states on inputs
- Color-coded results (normal vs errors)
- Mobile-responsive layout

## Supported Operations

- Addition: `+`
- Subtraction: `-`
- Multiplication: `*`
- Division: `/`
- Exponentiation: `**`
- Modulo: `%`
- Floor Division: `//`
- Parentheses: `()`

## Running the Application

### Method 1: Direct Python

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

Visit `http://localhost:5000` in your browser.

### Method 2: Docker

```bash
# Build the image
docker build -t calculator-app .

# Run the container
docker run -p 5000:5000 calculator-app
```

Visit `http://localhost:5000` in your browser.

## Example Expressions

- `2 + 3 * 5` → 17
- `(10 + 5) / 3` → 5
- `2 ** 8` → 256
- `17 % 5` → 2
- `100 // 3` → 33
- `(2 + 3) * (4 - 1)` → 15

## Security Notes

### Why the original code was dangerous:

```python
# DANGEROUS - DO NOT USE
result = eval(expression)
```

This allows users to execute ANY Python code, including:
- `__import__('os').system('rm -rf /')`  # Delete files
- `open('/etc/passwd').read()`  # Read sensitive files
- `__import__('subprocess').call(['malicious_command'])`  # Execute system commands

### How the new version is safe:

The improved version uses AST parsing which:
1. Parses the expression into a syntax tree
2. Validates each node is a safe mathematical operation
3. Only allows numbers and whitelisted operators
4. Cannot execute arbitrary code or access Python internals

## Development

To run in debug mode (for development only):

```python
app.run(host="0.0.0.0", port=5000, debug=True)
```

**Note**: Never use `debug=True` in production!

## License

Free to use and modify.
