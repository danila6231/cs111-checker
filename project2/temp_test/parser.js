
    const parser = require('@babel/parser');
    const fs = require('fs');

    const code = fs.readFileSync(process.argv[2], 'utf-8');
    const ast = parser.parse(code);

    const functions = {};
    ast.program.body.forEach(node => {
        if (node.type === 'FunctionDeclaration' && 
            ['validateDate', 'validateTime', 'calculatePriority'].includes(node.id.name)) {
            functions[node.id.name] = code.slice(node.start, node.end);
        }
    });

    // Add module.exports
    const exportStr = "module.exports = { validateDate, validateTime, calculatePriority };\n";
    
    const output = Object.values(functions).join('\n\n') + '\n\n' + exportStr;
    fs.writeFileSync(process.argv[3], output);
    