#!/usr/bin/env node
'use strict';

const path = require('path');
const tm = require(path.join(__dirname, 'task-manager.js'));

// --- ANSI Colors ---

const c = {
  reset: '\x1b[0m',
  bold: '\x1b[1m',
  dim: '\x1b[2m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m',
  blue: '\x1b[34m',
  white: '\x1b[37m',
  bgGreen: '\x1b[42m',
  bgRed: '\x1b[41m',
  bgYellow: '\x1b[43m',
  bgBlue: '\x1b[44m',
};

// --- Helpers ---

function statusIcon(status) {
  switch (status) {
    case 'completed': return c.green + 'done' + c.reset;
    case 'in_progress': return c.cyan + ' run' + c.reset;
    case 'failed': return c.red + 'FAIL' + c.reset;
    case 'blocked': return c.yellow + 'wait' + c.reset;
    case 'cancelled': return c.dim + 'skip' + c.reset;
    case 'pending': default: return c.dim + '   -' + c.reset;
  }
}

function waveStatus(tasks) {
  if (tasks.every(t => t.status === 'completed')) return c.green + 'done' + c.reset;
  if (tasks.some(t => t.status === 'in_progress')) return c.cyan + 'running' + c.reset;
  if (tasks.some(t => t.status === 'failed')) return c.red + 'failed' + c.reset;
  return c.dim + 'pending' + c.reset;
}

function formatDuration(startISO, endISO) {
  if (!startISO) return '';
  const start = new Date(startISO).getTime();
  const end = endISO ? new Date(endISO).getTime() : Date.now();
  const secs = Math.floor((end - start) / 1000);
  const mins = Math.floor(secs / 60);
  const remSecs = secs % 60;
  return mins + ':' + String(remSecs).padStart(2, '0');
}

function progressBar(pct, width) {
  const filled = Math.round((pct / 100) * width);
  const empty = width - filled;
  return c.green + '\u2588'.repeat(filled) + c.dim + '\u2591'.repeat(empty) + c.reset;
}

function pad(str, len) {
  // Strip ANSI codes for length calculation
  const plain = str.replace(/\x1b\[[0-9;]*m/g, '');
  if (plain.length >= len) return str;
  return str + ' '.repeat(len - plain.length);
}

function taskDetail(task) {
  const deps = Array.isArray(task.dependencies) ? task.dependencies : [];
  if (task.status === 'in_progress' && task.startedAt) {
    return c.cyan + '[running ' + formatDuration(task.startedAt) + ']' + c.reset;
  }
  if (task.status === 'blocked' || (task.status === 'pending' && deps.length > 0)) {
    const blockers = deps.filter(dep => {
      try { return tm.getTask(dep).status !== 'completed'; } catch { return true; }
    });
    if (blockers.length > 0) return c.yellow + '[blocked by ' + blockers.join(',') + ']' + c.reset;
  }
  if ((task.status === 'completed' || task.status === 'failed') && task.startedAt) {
    return c.dim + formatDuration(task.startedAt, task.completedAt) + c.reset;
  }
  return '';
}

// --- Board View ---

function renderBoard() {
  const fs = require('fs');
  const missionsDir = tm.getMissionsDir();
  const activePath = path.join(missionsDir, 'active.json');

  let mission = { name: 'unknown', status: 'unknown', riskTier: 0 };
  if (fs.existsSync(activePath)) {
    try { mission = JSON.parse(fs.readFileSync(activePath, 'utf8')); } catch {}
  }

  const stats = tm.getStats();
  const waves = tm.getWaves();
  const critPath = tm.getCriticalPath();

  const lines = [];

  // Header
  const headerWidth = 70;
  lines.push(c.bold + '+' + '-'.repeat(headerWidth) + '+' + c.reset);
  lines.push(c.bold + '|  MISSION: ' + pad(mission.name || 'unnamed', headerWidth - 12) + '|' + c.reset);
  const statusLine = 'Status: ' + (mission.status || 'active') +
    '   Progress: ' + stats.completed + '/' + stats.total + ' (' + stats.completionPct + '%)' +
    '   Risk: Tier ' + (mission.riskTier || 0);
  lines.push(c.bold + '|  ' + pad(statusLine, headerWidth - 3) + '|' + c.reset);
  lines.push(c.bold + '|  ' + pad(progressBar(stats.completionPct, 40) + '  ' + stats.completionPct + '%', headerWidth - 3) + '|' + c.reset);
  lines.push(c.bold + '+' + '-'.repeat(headerWidth) + '+' + c.reset);
  lines.push('');

  // Waves
  if (waves.length === 0) {
    lines.push(c.dim + 'No tasks found.' + c.reset);
  }

  for (const { wave, tasks } of waves) {
    lines.push(c.bold + 'Wave ' + wave + ' ' + waveStatus(tasks) + c.reset);
    for (const task of tasks) {
      const icon = statusIcon(task.status);
      const id = pad(task.id, 4);
      const name = pad(task.name || '', 35);
      const agent = pad(task.agentType || '', 13);
      const model = pad(task.model || '', 7);
      const detail = taskDetail(task);
      lines.push('  ' + icon + ' ' + id + ' ' + name + ' ' + agent + ' ' + model + ' ' + detail);
    }
    lines.push('');
  }

  // Critical path
  if (critPath.length > 0) {
    lines.push(c.bold + 'Critical path: ' + c.reset + critPath.join(' -> '));
  }

  return lines.join('\n');
}

// --- List View ---

function renderList() {
  const tasks = tm.listTasks();
  // Sort: in_progress first, then blocked, pending, failed, cancelled, completed
  const order = { in_progress: 0, blocked: 1, pending: 2, failed: 3, cancelled: 4, completed: 5 };
  tasks.sort((a, b) => (order[a.status] || 9) - (order[b.status] || 9));
  const lines = [];
  for (const task of tasks) {
    const icon = statusIcon(task.status);
    lines.push(icon + ' ' + pad(task.id, 4) + ' ' + pad(task.name || '', 40) + ' ' + pad(task.agentType || '', 13) + ' ' + taskDetail(task));
  }
  if (lines.length === 0) lines.push(c.dim + 'No tasks found.' + c.reset);
  return lines.join('\n');
}

// --- Graph View ---

function renderGraph() {
  const tasks = tm.listTasks();
  const taskMap = {};
  for (const t of tasks) taskMap[t.id] = t;

  const lines = [];
  lines.push(c.bold + 'Task Dependency Graph' + c.reset);
  lines.push('');

  for (const task of tasks) {
    const icon = statusIcon(task.status);
    const deps = (task.dependencies || []).length > 0
      ? c.dim + ' <- [' + task.dependencies.join(', ') + ']' + c.reset
      : '';
    lines.push(icon + ' ' + task.id + ': ' + (task.name || '') + deps);

    // Show outgoing edges
    const dependents = tasks.filter(t => (t.dependencies || []).includes(task.id));
    for (let i = 0; i < dependents.length; i++) {
      const isLast = i === dependents.length - 1;
      const connector = isLast ? '  `-- -> ' : '  |-- -> ';
      lines.push(c.dim + connector + dependents[i].id + c.reset);
    }
  }
  return lines.join('\n');
}

// --- JSON View ---

function renderJSON() {
  const waves = tm.getWaves();
  const stats = tm.getStats();
  const critPath = tm.getCriticalPath();
  return JSON.stringify({ stats, waves, criticalPath: critPath }, null, 2);
}

// --- Watch Mode ---

function watchMode(renderFn) {
  const INTERVAL = 2000;
  let lastOutput = '';

  function tick() {
    const output = renderFn();
    if (output !== lastOutput) {
      // Clear screen and move cursor to top
      process.stdout.write('\x1b[2J\x1b[H');
      console.log(output);
      console.log('');
      console.log(c.dim + 'Refreshing every 2s. Press Ctrl+C to exit.' + c.reset);
      lastOutput = output;
    }

    // Auto-exit if all tasks are in terminal state
    const stats = tm.getStats();
    if (stats.total > 0 && stats.inProgress === 0 && stats.pending === 0 && stats.blocked === 0) {
      console.log('');
      console.log(c.bold + 'All tasks reached terminal state. Exiting watch mode.' + c.reset);
      process.exit(0);
    }
  }

  // Initial render
  tick();
  const interval = setInterval(tick, INTERVAL);

  process.on('SIGINT', () => {
    clearInterval(interval);
    console.log('');
    process.exit(0);
  });
}

// --- CLI ---

if (require.main === module) {
  const args = process.argv.slice(2);
  let view = 'board';
  let watch = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--view' && args[i + 1]) {
      view = args[++i];
    } else if (args[i] === '--watch' || args[i] === '-w') {
      watch = true;
    } else if (args[i] === '--help' || args[i] === '-h') {
      console.log('Usage: mission-board [--view board|list|graph|json] [--watch]');
      console.log('');
      console.log('Views:');
      console.log('  board  Wave-grouped task board with progress (default)');
      console.log('  list   Flat list sorted by status');
      console.log('  graph  ASCII dependency graph');
      console.log('  json   Raw JSON output');
      console.log('');
      console.log('Options:');
      console.log('  --watch, -w  Live mode, refreshes every 2 seconds');
      process.exit(0);
    }
  }

  const renderers = {
    board: renderBoard,
    list: renderList,
    graph: renderGraph,
    json: renderJSON,
  };

  const renderFn = renderers[view];
  if (!renderFn) {
    console.error('Unknown view: ' + view + '. Use: board, list, graph, json');
    process.exit(1);
  }

  if (watch) {
    watchMode(renderFn);
  } else {
    console.log(renderFn());
  }
}
