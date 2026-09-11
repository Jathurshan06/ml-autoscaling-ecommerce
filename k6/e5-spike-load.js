import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '2m', target: 10 },
        { duration: '10s', target: 150 },
        { duration: '3m', target: 150 },
        { duration: '10s', target: 10 },
        { duration: '3m', target: 10 },
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
