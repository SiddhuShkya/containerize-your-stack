const express = require('express');

const router = express.Router();

router.get('/', (req, res) => {
    res.json({
        name: 'Task API',
        version: '1.0',
        endpoints: ['/tasks', '/health', '/docs', '/stats', '/reset'],
    });
});

router.get('/health', (req, res) => {
    res.json({ status: 'ok' });
});

module.exports = router;