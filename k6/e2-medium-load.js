import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    vus: 25,
    duration: '5m',
};

export default function () {
    const response = http.get('http://192.168.49.2:30000/api/products');

    check(response, {
        'status is 200': (r) => r.status === 200,
        'response has products': (r) => r.body.includes('Laptop Pro X1'),
    });

    sleep(1);
}
