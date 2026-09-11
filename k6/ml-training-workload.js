import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '5m', target: 20 },
        { duration: '5m', target: 50 },
        { duration: '5m', target: 100 },
        { duration: '5m', target: 200 },

        { duration: '5m', target: 50 },

        { duration: '5m', target: 300 },
        { duration: '5m', target: 100 },

        { duration: '5m', target: 400 },
        { duration: '5m', target: 150 },

        { duration: '5m', target: 450 },
        { duration: '5m', target: 75 },
        { duration: '5m', target: 20 },
    ],
};

export default function () {
    const response = http.get(
        'http://192.168.49.2:30000/api/products'
    );

    check(response, {
        'status is 200': (r) => r.status === 200,
        'response has products': (r) =>
            r.body.includes('Laptop Pro X1'),
    });

    sleep(1);
}
