export default class User {
    FirstName: string;
    LastName: string;
    Student: boolean;

    constructor(
        FirstName: string,
        LastName: string,
        Student: boolean
    ) {
        this.FirstName = FirstName;
        this.LastName = LastName;
        this.Student = Student;
    }
}