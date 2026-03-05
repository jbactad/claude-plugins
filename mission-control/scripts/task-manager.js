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

// --- Task CRUD ---

function nextTaskId() {
  const tasksDir = getTasksDir();
  ensureDir(tasksDir);
  const files = fs.readdirSync(tasksDir).filter(f => f.match(/^T\d+\.json$/));
  if (files.length === 0) return 'T1';
  const ids = files.map(f => parseInt(f.replace('T', '').replace('.json', ''), 10));
  return 'T' + (Math.max(...ids) + 1);
}

function createTask(data) {
  const tasksDir = getTasksDir();
  ensureDir(tasksDir);
  const id = data.id || nextTaskId();
  const now = new Date().toISOString();
  const task = {
    id,
    name: data.name || '',
    agentType: data.agentType || data.agent || 'implementer',
    model: data.model || 'sonnet',
    riskTier: data.riskTier != null ? data.riskTier : 0,
    status: 'pending',
    dependencies: data.dependencies || [],
    fileOwnership: data.fileOwnership || [],
    deliverable: data.deliverable || '',
    acceptanceCriteria: data.acceptanceCriteria || [],
    wave: data.wave != null ? data.wave : 1,
    assignedAgent: data.assignedAgent || null,
    result: null,
    retryCount: 0,
    createdAt: now,
    startedAt: null,
    completedAt: null,
    updatedAt: now,
  };
  atomicWrite(path.join(tasksDir, id + '.json'), task);
  return task;
}

function getTask(id) {
  const filePath = path.join(getTasksDir(), id + '.json');
  if (!fs.existsSync(filePath)) {
    throw new Error('Task not found: ' + id);
  }
  return readJSON(filePath);
}

function updateTask(id, updates) {
  const task = getTask(id);
  const now = new Date().toISOString();
  for (const [key, value] of Object.entries(updates)) {
    if (key === 'id' || key === 'createdAt') continue; // immutable fields
    task[key] = value;
  }
  task.updatedAt = now;
  // Auto-set timestamps based on status transitions
  if (updates.status === 'in_progress' && !task.startedAt) {
    task.startedAt = now;
  }
  if ((updates.status === 'completed' || updates.status === 'failed' || updates.status === 'cancelled') && !task.completedAt) {
    task.completedAt = now;
  }
  atomicWrite(path.join(getTasksDir(), id + '.json'), task);
  return task;
}

function listTasks(filter) {
  const tasksDir = getTasksDir();
  if (!fs.existsSync(tasksDir)) return [];
  const files = fs.readdirSync(tasksDir).filter(f => f.match(/^T\d+\.json$/));
  let tasks = files.map(f => readJSON(path.join(tasksDir, f)));
  // Sort by numeric ID
  tasks.sort((a, b) => {
    const na = parseInt(a.id.replace('T', ''), 10);
    const nb = parseInt(b.id.replace('T', ''), 10);
    return na - nb;
  });
  if (filter) {
    if (filter.status) tasks = tasks.filter(t => t.status === filter.status);
    if (filter.wave != null) tasks = tasks.filter(t => t.wave === filter.wave);
    if (filter.agentType) tasks = tasks.filter(t => t.agentType === filter.agentType);
  }
  return tasks;
}

// --- Aggregate Queries ---

function getWaves() {
  const tasks = listTasks();
  const waves = {};
  for (const task of tasks) {
    const w = task.wave || 0;
    if (!waves[w]) waves[w] = [];
    waves[w].push(task);
  }
  // Return sorted by wave number
  const sorted = Object.keys(waves)
    .map(Number)
    .sort((a, b) => a - b)
    .map(w => ({ wave: w, tasks: waves[w] }));
  return sorted;
}

function getStats() {
  const tasks = listTasks();
  const total = tasks.length;
  const byStatus = {};
  for (const t of tasks) {
    byStatus[t.status] = (byStatus[t.status] || 0) + 1;
  }
  const completed = byStatus.completed || 0;
  const cancelled = byStatus.cancelled || 0;
  const denominator = total - cancelled;
  const completionPct = denominator > 0 ? Math.round((completed / denominator) * 100) : 0;
  return {
    total,
    completed,
    inProgress: byStatus.in_progress || 0,
    pending: byStatus.pending || 0,
    blocked: byStatus.blocked || 0,
    failed: byStatus.failed || 0,
    cancelled,
    completionPct,
  };
}

function getDependencyGraph() {
  const tasks = listTasks();
  const graph = {};
  const reverse = {};
  for (const t of tasks) {
    graph[t.id] = t.dependencies || [];
    for (const dep of t.dependencies || []) {
      if (!reverse[dep]) reverse[dep] = [];
      reverse[dep].push(t.id);
    }
  }
  return { forward: graph, reverse };
}

function getCriticalPath() {
  const tasks = listTasks();
  const taskMap = {};
  for (const t of tasks) taskMap[t.id] = t;

  // Compute longest path to each node
  const longestPath = {};
  const pathParent = {};

  function computePath(id) {
    if (longestPath[id] != null) return longestPath[id];
    const deps = (taskMap[id] && taskMap[id].dependencies) || [];
    if (deps.length === 0) {
      longestPath[id] = 1;
      pathParent[id] = null;
      return 1;
    }
    let maxLen = 0;
    let maxParent = null;
    for (const dep of deps) {
      const len = computePath(dep);
      if (len > maxLen) {
        maxLen = len;
        maxParent = dep;
      }
    }
    longestPath[id] = maxLen + 1;
    pathParent[id] = maxParent;
    return longestPath[id];
  }

  for (const t of tasks) computePath(t.id);

  // Find the end of the critical path
  let endId = null;
  let maxLen = 0;
  for (const [id, len] of Object.entries(longestPath)) {
    if (len > maxLen) {
      maxLen = len;
      endId = id;
    }
  }

  // Trace back
  const criticalPath = [];
  let current = endId;
  while (current) {
    criticalPath.unshift(current);
    current = pathParent[current];
  }
  return criticalPath;
}

// --- Exports (for use as module) ---

module.exports = {
  findProjectRoot,
  getTasksDir,
  getMissionsDir,
  ensureDir,
  createTask,
  getTask,
  updateTask,
  listTasks,
  getWaves,
  getStats,
  getDependencyGraph,
  getCriticalPath,
};

// --- CLI Interface ---

if (require.main === module) {
  const args = process.argv.slice(2);
  const command = args[0];

  function parseFlags(args) {
    const flags = {};
    for (let i = 0; i < args.length; i++) {
      if (args[i].startsWith('--')) {
        const key = args[i].replace(/^--/, '');
        const val = (i + 1 < args.length && !args[i + 1].startsWith('--')) ? args[++i] : true;
        // Handle array values (comma-separated)
        if (typeof val === 'string' && val.includes(',') && (key === 'dependencies' || key === 'fileOwnership' || key === 'acceptanceCriteria')) {
          flags[key] = val.split(',').map(s => s.trim());
        } else {
          flags[key] = val;
        }
      }
    }
    return flags;
  }

  function output(data) {
    console.log(JSON.stringify(data, null, 2));
  }

  try {
    switch (command) {
      case 'create': {
        const flags = parseFlags(args.slice(1));
        const task = createTask({
          id: flags.id,
          name: flags.name,
          agentType: flags.agent || flags.agentType,
          model: flags.model,
          riskTier: flags.risk != null ? parseInt(flags.risk, 10) : undefined,
          dependencies: flags.dependencies || [],
          fileOwnership: flags.fileOwnership || [],
          deliverable: flags.deliverable,
          acceptanceCriteria: flags.acceptanceCriteria || [],
          wave: flags.wave != null ? parseInt(flags.wave, 10) : undefined,
          assignedAgent: flags.assignedAgent,
        });
        output(task);
        break;
      }
      case 'get': {
        const id = args[1];
        if (!id) { console.error('Usage: task-manager get <id>'); process.exit(1); }
        output(getTask(id));
        break;
      }
      case 'update': {
        const id = args[1];
        if (!id) { console.error('Usage: task-manager update <id> --field value'); process.exit(1); }
        const flags = parseFlags(args.slice(2));
        // Parse numeric fields
        if (flags.riskTier != null) flags.riskTier = parseInt(flags.riskTier, 10);
        if (flags.wave != null) flags.wave = parseInt(flags.wave, 10);
        if (flags.retryCount != null) flags.retryCount = parseInt(flags.retryCount, 10);
        output(updateTask(id, flags));
        break;
      }
      case 'list': {
        const flags = parseFlags(args.slice(1));
        const filter = {};
        if (flags.status) filter.status = flags.status;
        if (flags.wave != null) filter.wave = parseInt(flags.wave, 10);
        if (flags.agent || flags.agentType) filter.agentType = flags.agent || flags.agentType;
        output(listTasks(Object.keys(filter).length ? filter : undefined));
        break;
      }
      case 'stats': {
        output(getStats());
        break;
      }
      case 'waves': {
        output(getWaves());
        break;
      }
      case 'graph': {
        output(getDependencyGraph());
        break;
      }
      case 'critical-path': {
        output(getCriticalPath());
        break;
      }
      default: {
        console.error('Usage: task-manager <create|get|update|list|stats|waves|graph|critical-path> [args]');
        console.error('');
        console.error('Commands:');
        console.error('  create  --name "..." --agent <type> --model <model> --wave <N>');
        console.error('  get     <id>');
        console.error('  update  <id> --status <status> [--result "..."]');
        console.error('  list    [--status <status>] [--wave <N>] [--agent <type>]');
        console.error('  stats');
        console.error('  waves');
        console.error('  graph');
        console.error('  critical-path');
        process.exit(1);
      }
    }
  } catch (err) {
    console.error('Error: ' + err.message);
    process.exit(1);
  }
}
