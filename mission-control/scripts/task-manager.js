#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const os = require('os');

// --- Project Discovery ---

function findProjectRoot() {
  // Prefer explicit env var
  if (process.env.CLAUDE_PROJECT_DIR) {
    return process.env.CLAUDE_PROJECT_DIR;
  }
  // Walk up from cwd looking for .mission-control/missions/
  let dir = process.cwd();
  while (dir !== path.dirname(dir)) {
    if (fs.existsSync(path.join(dir, '.mission-control', 'missions'))) {
      return dir;
    }
    dir = path.dirname(dir);
  }
  return process.cwd(); // fallback
}

function getTasksDir() {
  return path.join(findProjectRoot(), '.mission-control', 'missions', 'tasks');
}

function getMissionsDir() {
  return path.join(findProjectRoot(), '.mission-control', 'missions');
}

// --- File I/O Helpers ---

function ensureDir(dir) {
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function atomicWrite(filePath, data) {
  const tmp = filePath + '.tmp.' + process.pid;
  fs.writeFileSync(tmp, JSON.stringify(data, null, 2) + '\n', 'utf8');
  fs.renameSync(tmp, filePath);
}

function readJSON(filePath) {
  return JSON.parse(fs.readFileSync(filePath, 'utf8'));
}
