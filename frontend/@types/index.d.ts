/**
 * Create an interface for the user type
 */
interface User {
    FirstName: string;
    LastName: string;
    Student: boolean;
}

/**
 * Extend Express's Request to add the type of our User interface to the user field of the request
 */
declare namespace Express {
    export interface Request {
        user: User;
    }
}