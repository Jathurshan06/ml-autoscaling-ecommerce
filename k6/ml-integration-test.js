import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '2m', target: 50 },
        { duration: '2m', target: 200 },
        { duration: '2m', target: 350 },
        { duration: '2m', target: 80 },
        { duration: '2m', target: 20 },
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
