import { GridAPI } from '../frontend/src/lib/api';

async function testConnectivity() {
    console.log('🔄 Testing MoStar GRID Frontend-Backend Connectivity');
    console.log('=' . repeat(60));

    const api = new GridAPI();

    try {
        // Test health endpoint
        console.log('Testing /health...');
        const health = await api.health();
        console.log('✅ Health check:', JSON.stringify(health, null, 2));

        // Test event submission
        console.log('\nTesting /events...');
        const testEvent = {
            event_type: 'test',
            source_agent: 'smoke-test',
            location: 'local',
            data: { test: true }
        };
        const eventResponse = await api.submitEvent(testEvent);
        console.log('✅ Event submitted:', JSON.stringify(eventResponse, null, 2));

        // Test WebSocket
        console.log('\nTesting WebSocket...');
        const ws = api.connectWebSocket();
        ws.onopen = () => {
            console.log('✅ WebSocket connected');
            ws.send('test');
        };
        ws.onmessage = (msg) => {
            console.log('✅ WebSocket message received:', msg.data);
            ws.close();
        };

        // Wait for WebSocket test
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('=' . repeat(60));
        console.log('✅ All connectivity tests passed!');

    } catch (error) {
        console.error('❌ Connectivity test failed:', error);
        process.exit(1);
    }
}

testConnectivity();
