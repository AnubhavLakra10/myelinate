import { EventEmitter } from 'events';

interface Greeter {
    greet(name: string): string;
}

function createGreeting(name: string): string {
    return `Hello, ${name}`;
}

class WelcomeService implements Greeter {
    greet(name: string): string {
        return createGreeting(name);
    }
}

export default WelcomeService;
