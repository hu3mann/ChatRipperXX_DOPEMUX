#!/usr/bin/env node
'use strict';
/**
 * Expand ${VAR} placeholders in a JSON template using .env.
 * Usage: node tools/mcp/load-env.cjs <input-template.json> <output.json>
 */
const fs = require('fs');
const path = require('path');
require('dotenv').config(); // loads .env into process.env

const [, , inputPath, outputPath] = process.argv;
if (!inputPath || !outputPath) {
  console.error('Usage: node tools/mcp/load-env.cjs <input-template.json> <output.json>');
  process.exit(2);
}

const raw = JSON.parse(fs.readFileSync(inputPath, 'utf8'));

function expand(obj) {
  if (typeof obj === 'string') {
    return obj.replace(/\$\{(\w+)\}/g, (_, name) => {
      const v = process.env[name];
      if (v === undefined) {
        console.warn(`Warning: ${name} is not set in environment`);
        return '';
      }
      return v;
    });
  }
  if (Array.isArray(obj)) return obj.map(expand);
  if (obj && typeof obj === 'object') {
    return Object.fromEntries(Object.entries(obj).map(([k, v]) => [k, expand(v)]));
  }
  return obj;
}

const expanded = JSON.stringify(expand(raw), null, 2);
fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
fs.writeFileSync(outputPath, expanded, 'utf8');
console.log(`Wrote expanded config → ${outputPath}`);
