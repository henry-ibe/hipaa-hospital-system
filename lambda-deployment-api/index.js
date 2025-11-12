const https = require('https');

exports.handler = async (event) => {
    const headers = {
        'Access-Control-Allow-Origin': 'https://henry-ibe.github.io',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'POST, OPTIONS'
    };

    if (event.httpMethod === 'OPTIONS') {
        return { statusCode: 200, headers, body: '' };
    }

    try {
        const body = JSON.parse(event.body);
        const { city, state, hospitalName, regionCode } = body;

        if (!city || !state || !hospitalName || !regionCode) {
            return {
                statusCode: 400,
                headers,
                body: JSON.stringify({
                    error: 'Missing required fields',
                    required: ['city', 'state', 'hospitalName', 'regionCode']
                })
            };
        }

        const githubToken = process.env.GITHUB_TOKEN;
        if (!githubToken) {
            throw new Error('GitHub token not configured');
        }

        // Send just the region code (e.g., "tx" not "tx-hospital")
        const githubData = JSON.stringify({
            ref: 'master',
            inputs: {
                region: regionCode,  // Just "tx", "ny", "ca", etc.
                action: 'apply'
            }
        });

        const githubResponse = await callGitHubAPI(githubToken, githubData);

        if (githubResponse.statusCode === 204) {
            return {
                statusCode: 200,
                headers,
                body: JSON.stringify({
                    success: true,
                    message: `Deployment started for ${city}, ${state}`,
                    regionCode: regionCode,
                    workflowUrl: 'https://github.com/henry-ibe/hipaa-hospital-system/actions'
                })
            };
        } else {
            throw new Error(`GitHub API returned status ${githubResponse.statusCode}: ${githubResponse.body}`);
        }

    } catch (error) {
        console.error('Error:', error);
        return {
            statusCode: 500,
            headers,
            body: JSON.stringify({
                error: 'Deployment failed',
                message: error.message
            })
        };
    }
};

function callGitHubAPI(token, data) {
    return new Promise((resolve, reject) => {
        const options = {
            hostname: 'api.github.com',
            port: 443,
            path: '/repos/henry-ibe/hipaa-hospital-system/actions/workflows/206138235/dispatches',
            method: 'POST',
            headers: {
                'Accept': 'application/vnd.github.v3+json',
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'User-Agent': 'Hospital-Deployment-Lambda',
                'Content-Length': data.length
            }
        };

        const req = https.request(options, (res) => {
            let body = '';
            res.on('data', (chunk) => body += chunk);
            res.on('end', () => {
                resolve({
                    statusCode: res.statusCode,
                    body: body
                });
            });
        });

        req.on('error', (error) => reject(error));
        req.write(data);
        req.end();
    });
}
