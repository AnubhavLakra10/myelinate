import { readFile } from 'fs';

function greet(name) {
    return `Hello, ${name}`;
}

class Logger {
    log(message) {
        console.log(message);
    }

    warn(message) {
        console.warn(message);
    }
}

function main() {
    const msg = greet('world');
    const logger = new Logger();
    logger.log(msg);
}
